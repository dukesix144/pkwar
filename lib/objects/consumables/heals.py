"""Healing potions"""

from lib.models.objects import Heal

def load():
    """Return heal templates."""
    
    return {
        "heal_50": lambda **kwargs: Heal(amount=50, **kwargs),
        "heal_100": lambda **kwargs: Heal(amount=100, **kwargs),
        "heal_200": lambda **kwargs: Heal(amount=200, **kwargs)
    }