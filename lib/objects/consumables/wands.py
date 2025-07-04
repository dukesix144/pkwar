"""Magical wands"""

from lib.models.objects import Wand

def load():
    """Return wand templates."""
    
    return {
        "wand_10": lambda **kwargs: Wand(
            charges=10,
            sp_cost=5,
            damage=50,
            **kwargs
        ),
        
        "wand_20": lambda **kwargs: Wand(
            charges=20,
            sp_cost=5,
            damage=50,
            **kwargs
        ),
        
        "wand_combat": lambda **kwargs: Wand(
            charges=5,
            sp_cost=10,
            damage=100,
            **kwargs
        )
    }