"""Inventory management system for players"""

class InventoryManager:
    """Manages player inventory and equipment."""
    
    def __init__(self, player):
        self.player = player
        self.items = []  # List of items in inventory
        self.kept_items = set()  # Set of item IDs that are kept
        self.equipment = {
            'wielded': None,
            'head': None,
            'neck': None,
            'heavy_body': None,
            'upper_body': None,
            'legs': None,
            'light_body': None,
            'hands': None,
            'feet': None,
            'fingers': None,
            'shield': None,
            'other': None
        }
        self.max_weight = 1000  # Base carrying capacity
        self.current_weight = 0
    
    def add_item(self, item):
        """Add an item to inventory."""
        if self.can_carry(item):
            self.items.append(item)
            self.current_weight += getattr(item, 'weight', 0)
            
            # Auto-combine heals and wands
            self._auto_combine(item)
            return True
        return False
    
    def remove_item(self, item):
        """Remove an item from inventory."""
        if item in self.items:
            self.items.remove(item)
            self.current_weight -= getattr(item, 'weight', 0)
            return True
        return False
    
    def get_item(self, name):
        """Find an item by name."""
        name_lower = name.lower()
        for item in self.items:
            if (item.name.lower() == name_lower or 
                name_lower in item.name.lower()):
                return item
        return None
    
    def can_carry(self, item):
        """Check if player can carry this item."""
        item_weight = getattr(item, 'weight', 0)
        return self.current_weight + item_weight <= self.max_weight
    
    def keep_item(self, item):
        """Mark an item as kept (won't be sold)."""
        if item in self.items:
            self.kept_items.add(id(item))
            return True
        return False
    
    def unkeep_item(self, item):
        """Unmark an item as kept."""
        if id(item) in self.kept_items:
            self.kept_items.remove(id(item))
            return True
        return False
    
    def is_kept(self, item):
        """Check if item is marked as kept."""
        return id(item) in self.kept_items
    
    def get_sellable_items(self):
        """Get items that can be sold (not kept, not blood)."""
        sellable = []
        for item in self.items:
            if (not self.is_kept(item) and 
                not getattr(item, 'is_blood', False)):
                sellable.append(item)
        return sellable
    
    def equip_item(self, item, slot):
        """Equip an item to a specific slot."""
        if slot not in self.equipment:
            return False
        
        # Unequip current item in slot
        if self.equipment[slot]:
            current = self.equipment[slot]
            self.add_item(current)
        
        # Equip new item
        self.equipment[slot] = item
        self.remove_item(item)
        return True
    
    def unequip_item(self, slot):
        """Unequip an item from a slot."""
        if slot in self.equipment and self.equipment[slot]:
            item = self.equipment[slot]
            self.equipment[slot] = None
            return self.add_item(item)
        return False
    
    def get_burden_level(self):
        """Get encumbrance level."""
        percent = (self.current_weight / self.max_weight) * 100
        if percent < 25:
            return "not burdened"
        elif percent < 50:
            return "lightly burdened"
        elif percent < 75:
            return "burdened"
        elif percent < 90:
            return "heavily burdened"
        else:
            return "overloaded"
    
    def get_inventory_display(self):
        """Get formatted inventory display."""
        output = []
        output.append("# Item")
        output.append("-" * 50)
        
        # Group similar items
        item_counts = {}
        for item in self.items:
            key = item.name
            if key in item_counts:
                item_counts[key] += 1
            else:
                item_counts[key] = 1
        
        for name, count in item_counts.items():
            kept_marker = ""
            # Check if any of this type are kept
            for item in self.items:
                if item.name == name and self.is_kept(item):
                    kept_marker = " *"
                    break
            
            if count > 1:
                output.append(f"{count} {name}{kept_marker}")
            else:
                output.append(f"1 {name}{kept_marker}")
        
        # Add coins
        output.append(f"{self.player.coins} coins (weightless)")
        
        # Add burden level
        output.append(f"You are {self.get_burden_level()}.")
        
        return output
    
    def get_equipment_display(self):
        """Get formatted equipment display."""
        output = []
        output.append("Wielded: " + (self.equipment['wielded'].name if self.equipment['wielded'] else "none"))
        output.append("Head: " + (self.equipment['head'].name if self.equipment['head'] else "none"))
        output.append("Around neck: " + (self.equipment['neck'].name if self.equipment['neck'] else "none"))
        output.append("Heavy body: " + (self.equipment['heavy_body'].name if self.equipment['heavy_body'] else "none"))
        output.append("Upper body: " + (self.equipment['upper_body'].name if self.equipment['upper_body'] else "none"))
        output.append("On legs: " + (self.equipment['legs'].name if self.equipment['legs'] else "none"))
        output.append("Light body: " + (self.equipment['light_body'].name if self.equipment['light_body'] else "none"))
        output.append("Hands: " + (self.equipment['hands'].name if self.equipment['hands'] else "none"))
        output.append("Feet: " + (self.equipment['feet'].name if self.equipment['feet'] else "none"))
        output.append("On fingers: " + (self.equipment['fingers'].name if self.equipment['fingers'] else "none"))
        output.append("Shield: " + (self.equipment['shield'].name if self.equipment['shield'] else "none"))
        output.append("Other: " + (self.equipment['other'].name if self.equipment['other'] else "none"))
        
        return output
    
    def _auto_combine(self, new_item):
        """Automatically combine heals and wands."""
        if not hasattr(new_item, 'combinable') or not new_item.combinable:
            return
        
        # Find existing items of same type
        for existing_item in self.items:
            if (existing_item != new_item and 
                existing_item.name.startswith(new_item.base_name) and
                hasattr(existing_item, 'combinable') and existing_item.combinable):
                
                # Combine the items
                existing_item.amount += new_item.amount
                existing_item.name = f"{existing_item.base_name} [{existing_item.amount}]"
                
                # Remove the new item
                self.items.remove(new_item)
                self.current_weight -= getattr(new_item, 'weight', 0)
                break