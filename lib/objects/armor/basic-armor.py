"""Basic armor set"""

from lib.models.objects import Armor, ArmorSlot

def load():
    """Return templates for basic armor pieces."""
    
    return {
        "basic_helmet": lambda **kwargs: Armor(
            name="basic helmet",
            description="A standard military helmet, dented but serviceable.",
            armor_class=1,
            slot=ArmorSlot.HEAD,
            weight=3,
            value=50,
            **kwargs
        ),
        
        "basic_chestplate": lambda **kwargs: Armor(
            name="basic chestplate",
            description="A military-issue chest plate with minor rust spots.",
            armor_class=3,
            slot=ArmorSlot.BODY_HEAVY,
            weight=15,
            value=200,
            **kwargs
        ),
        
        "basic_boots": lambda **kwargs: Armor(
            name="basic boots",
            description="Heavy military boots, worn but sturdy.",
            armor_class=1,
            slot=ArmorSlot.FEET,
            weight=2,
            value=30,
            **kwargs
        ),
        
        "basic_gloves": lambda **kwargs: Armor(
            name="basic gloves",
            description="Leather combat gloves with reinforced knuckles.",
            armor_class=1,
            slot=ArmorSlot.HANDS,
            weight=1,
            value=25,
            **kwargs
        ),
        
        "basic_shield": lambda **kwargs: Armor(
            name="basic shield",
            description="A round military shield, scarred from combat.",
            armor_class=2,
            slot=ArmorSlot.SHIELD,
            weight=8,
            value=75,
            **kwargs
        )
    }