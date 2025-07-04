"""Base classes for game objects"""

import uuid
from typing import Optional, Dict, Any
from enum import Enum

class ObjectType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    CONTAINER = "container"
    MISC = "misc"
    SPECIAL = "special"

class ArmorSlot(Enum):
    HEAD = "head"
    NECK = "neck"
    BODY_HEAVY = "heavy body"
    BODY_UPPER = "upper body"
    BODY_LIGHT = "light body"
    LEGS = "legs"
    HANDS = "hands"
    FEET = "feet"
    FINGER = "finger"
    SHIELD = "shield"
    OTHER = "other"

class GameObject:
    """Base class for all game objects."""
    
    def __init__(self, 
                 name: str,
                 description: str,
                 weight: int = 1,
                 value: int = 0,
                 object_type: ObjectType = ObjectType.MISC,
                 kept: bool = False):
        self.uuid = uuid.uuid4()
        self.name = name
        self.description = description
        self.weight = weight
        self.value = value
        self.object_type = object_type
        self.kept = kept  # Marked with * in inventory
        self.owner = None  # Player/container holding this
        
    def get_display_name(self) -> str:
        """Get name as displayed in inventory."""
        if self.kept:
            return f"* {self.name}"
        return self.name
    
    def examine(self) -> str:
        """Return detailed examination text."""
        return self.description

class Weapon(GameObject):
    """Weapon objects."""
    
    def __init__(self,
                 name: str,
                 description: str,
                 damage: int,
                 weapon_type: str = "sword",
                 weight: int = 5,
                 value: int = 100,
                 **kwargs):
        super().__init__(name, description, weight, value, ObjectType.WEAPON, **kwargs)
        self.damage = damage
        self.weapon_type = weapon_type
        self.wielded = False
    
    def examine(self) -> str:
        return f"{self.description}\nDamage rating: {self.damage}"

class Armor(GameObject):
    """Armor objects."""
    
    def __init__(self,
                 name: str,
                 description: str,
                 armor_class: int,
                 slot: ArmorSlot,
                 weight: int = 10,
                 value: int = 100,
                 **kwargs):
        super().__init__(name, description, weight, value, ObjectType.ARMOR, **kwargs)
        self.armor_class = armor_class
        self.slot = slot
        self.worn = False
    
    def examine(self) -> str:
        return f"{self.description}\nArmor class: {self.armor_class}\nWorn on: {self.slot.value}"

class Consumable(GameObject):
    """Consumable items like heals and wands."""
    
    def __init__(self,
                 name: str,
                 description: str,
                 charges: int = 1,
                 weight: int = 1,
                 value: int = 50,
                 **kwargs):
        super().__init__(name, description, weight, value, ObjectType.CONSUMABLE, **kwargs)
        self.charges = charges
        self.max_charges = charges
    
    def use(self, user) -> tuple[bool, str]:
        """Use the consumable. Return (success, message)."""
        if self.charges <= 0:
            return False, f"The {self.name} is depleted."
        
        self.charges -= 1
        return True, f"You use the {self.name}."
    
    def combine_with(self, other: 'Consumable') -> bool:
        """Combine with another consumable of same type."""
        if self.name != other.name:
            return False
        
        self.charges += other.charges
        return True
    
    def get_display_name(self) -> str:
        """Show charges in name."""
        base_name = super().get_display_name()
        if self.max_charges > 1:
            return f"{base_name} [{self.charges}]"
        return base_name

class Heal(Consumable):
    """Healing items."""
    
    def __init__(self,
                 amount: int,
                 **kwargs):
        name = f"Heal [{amount}]"
        description = f"A healing potion that restores {amount} hit points."
        super().__init__(name, description, charges=1, value=amount, **kwargs)
        self.heal_amount = amount
    
    def use(self, user) -> tuple[bool, str]:
        if self.charges <= 0:
            return False, f"The {self.name} is empty."
        
        self.charges -= 1
        
        # Heal the user
        healed = min(self.heal_amount, user.max_hp - user.current_hp)
        user.current_hp += healed
        
        if healed > 0:
            return True, f"You drink the heal and recover {healed} hit points."
        else:
            return True, "You drink the heal but you're already at full health."

class Wand(Consumable):
    """Wand items with charges."""
    
    def __init__(self,
                 charges: int = 10,
                 sp_cost: int = 5,
                 damage: int = 50,
                 **kwargs):
        name = f"Wand [{charges}]"
        description = f"A magical wand with {charges} charges."
        super().__init__(name, description, charges=charges, value=charges*20, **kwargs)
        self.sp_cost = sp_cost
        self.damage = damage
    
    def use(self, user, target=None) -> tuple[bool, str]:
        if self.charges <= 0:
            return False, "The wand is out of charges."
        
        if user.sp_current < self.sp_cost:
            return False, f"You need {self.sp_cost} spell points to use the wand."
        
        if not target:
            return False, "Use wand on whom?"
        
        self.charges -= 1
        user.sp_current -= self.sp_cost
        
        # TODO: Apply damage to target
        return True, f"You zap {target.name} with the wand! [{self.charges} charges left]"

class Blood(GameObject):
    """Blood items from kills - cannot be sold."""
    
    def __init__(self, victim_name: str, **kwargs):
        name = f"blood of {victim_name}"
        description = f"The mystical blood of {victim_name}, still warm with life force."
        super().__init__(name, description, weight=0, value=0, object_type=ObjectType.SPECIAL, **kwargs)
        self.victim_name = victim_name
        self.sellable = False
    
    def use(self, user) -> tuple[bool, str]:
        """Lick the blood for full heal (Kamikaze only)."""
        if getattr(user, 'war_class', None) != 'kamikaze':
            return False, "Only kamikazes can lick blood for healing."
        
        # Full heal
        user.current_hp = user.max_hp
        user.sp_current = user.sp_max
        
        # Remove the blood
        if self.owner:
            self.owner.inventory.remove_item(self)
        
        return True, f"You lick the {self.name} and feel completely restored!"

class Container(GameObject):
    """Container objects that can hold other items."""
    
    def __init__(self,
                 name: str,
                 description: str,
                 capacity: int = 10,
                 **kwargs):
        super().__init__(name, description, object_type=ObjectType.CONTAINER, **kwargs)
        self.capacity = capacity
        self.contents = []
    
    def add_item(self, item: GameObject) -> bool:
        """Add item to container."""
        if len(self.contents) >= self.capacity:
            return False
        
        self.contents.append(item)
        item.owner = self
        return True
    
    def remove_item(self, item: GameObject) -> bool:
        """Remove item from container."""
        if item in self.contents:
            self.contents.remove(item)
            item.owner = None
            return True
        return False
    
    def examine(self) -> str:
        """Show contents when examined."""
        text = self.description
        if self.contents:
            text += "\nIt contains:"
            for item in self.contents:
                text += f"\n  {item.get_display_name()}"
        else:
            text += "\nIt is empty."
        return text