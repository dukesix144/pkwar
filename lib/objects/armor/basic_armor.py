"""Basic armor templates for PKMUD"""

from lib.models.objects import Armor, ArmorSlot

def load():
    """Return armor templates."""
    
    return {
        # Head
        "leather_cap": lambda **kwargs: Armor(
            name="leather cap",
            description="A simple leather cap providing basic protection.",
            armor_class=1,
            slot=ArmorSlot.HEAD,
            weight=2,
            value=20,
            **kwargs
        ),
        
        # Neck
        "wool_cloak": lambda **kwargs: Armor(
            name="wool cloak", 
            description="A thick woolen cloak that provides warmth and protection.",
            armor_class=1,
            slot=ArmorSlot.NECK,
            weight=3,
            value=30,
            **kwargs
        ),
        
        # Body Heavy
        "chainmail": lambda **kwargs: Armor(
            name="chainmail armor",
            description="Interlocking metal rings provide excellent protection.",
            armor_class=5,
            slot=ArmorSlot.BODY_HEAVY,
            weight=40,
            value=200,
            **kwargs
        ),
        
        # Body Upper
        "leather_vest": lambda **kwargs: Armor(
            name="leather vest",
            description="A sturdy leather vest.",
            armor_class=2,
            slot=ArmorSlot.BODY_UPPER,
            weight=10,
            value=50,
            **kwargs
        ),
        
        # Body Light
        "cloth_shirt": lambda **kwargs: Armor(
            name="cloth shirt",
            description="A simple cloth shirt.",
            armor_class=0,
            slot=ArmorSlot.BODY_LIGHT,
            weight=1,
            value=5,
            **kwargs
        ),
        
        # Legs
        "leather_pants": lambda **kwargs: Armor(
            name="leather pants",
            description="Durable leather pants.",
            armor_class=2,
            slot=ArmorSlot.LEGS,
            weight=5,
            value=40,
            **kwargs
        ),
        
        # Hands
        "leather_gloves": lambda **kwargs: Armor(
            name="leather gloves",
            description="Soft leather gloves.",
            armor_class=1,
            slot=ArmorSlot.HANDS,
            weight=1,
            value=15,
            **kwargs
        ),
        
        # Feet
        "leather_boots": lambda **kwargs: Armor(
            name="leather boots",
            description="Sturdy leather boots.",
            armor_class=1,
            slot=ArmorSlot.FEET,
            weight=3,
            value=25,
            **kwargs
        ),
        
        # Shield
        "wooden_shield": lambda **kwargs: Armor(
            name="wooden shield",
            description="A round wooden shield.",
            armor_class=2,
            slot=ArmorSlot.SHIELD,
            weight=8,
            value=35,
            **kwargs
        ),
        
        # Ring
        "iron_ring": lambda **kwargs: Armor(
            name="iron ring",
            description="A simple iron ring.",
            armor_class=0,
            slot=ArmorSlot.FINGER,
            weight=0,
            value=10,
            **kwargs
        ),
    }
