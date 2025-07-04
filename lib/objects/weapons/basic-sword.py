"""Basic sword weapon"""

from lib.models.objects import Weapon

def load():
    """Return the basic sword template."""
    
    def create_basic_sword(**kwargs):
        return Weapon(
            name="basic sword",
            description="A simple but functional sword, standard military issue.",
            damage=10,
            weapon_type="sword",
            weight=5,
            value=100,
            **kwargs
        )
    
    return create_basic_sword