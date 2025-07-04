"""Basic weapon templates for PKMUD"""

from lib.models.objects import Weapon

def load():
    """Return weapon templates."""
    
    return {
        "wooden_sword": lambda **kwargs: Weapon(
            name="wooden sword",
            description="A basic training sword made of wood.",
            damage=10,
            weapon_type="sword",
            weight=3,
            value=20,
            **kwargs
        ),
        
        "iron_sword": lambda **kwargs: Weapon(
            name="iron sword",
            description="A standard iron sword with a sharp edge.",
            damage=20,
            weapon_type="sword", 
            weight=5,
            value=100,
            **kwargs
        ),
        
        "steel_sword": lambda **kwargs: Weapon(
            name="steel sword",
            description="A well-crafted steel sword.",
            damage=30,
            weapon_type="sword",
            weight=4,
            value=250,
            **kwargs
        ),
        
        "dagger": lambda **kwargs: Weapon(
            name="dagger",
            description="A small, quick blade.",
            damage=8,
            weapon_type="dagger",
            weight=1,
            value=30,
            **kwargs
        ),
        
        "battle_axe": lambda **kwargs: Weapon(
            name="battle axe",
            description="A heavy two-handed axe.",
            damage=35,
            weapon_type="axe",
            weight=10,
            value=300,
            **kwargs
        ),
        
        "mace": lambda **kwargs: Weapon(
            name="mace",
            description="A heavy crushing weapon.",
            damage=25,
            weapon_type="mace",
            weight=8,
            value=150,
            **kwargs
        ),
        
        "spear": lambda **kwargs: Weapon(
            name="spear",
            description="A long thrusting weapon.",
            damage=22,
            weapon_type="spear",
            weight=6,
            value=80,
            **kwargs
        ),
    }
