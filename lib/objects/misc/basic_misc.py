"""Misc object templates for PKMUD"""

from lib.models.objects import GameObject, ObjectType

def load():
    """Return misc object templates."""
    
    return {
        "adventurer_handbook": lambda **kwargs: GameObject(
            name="Adventurer's Handbook",
            description="A worn handbook containing advice for new adventurers. Type 'read handbook' to read it.",
            weight=1,
            value=5,
            object_type=ObjectType.MISC,
            **kwargs
        ),
        
        "torch": lambda **kwargs: GameObject(
            name="torch",
            description="A wooden torch that provides light.",
            weight=2,
            value=10,
            object_type=ObjectType.MISC,
            **kwargs
        ),
        
        "rope": lambda **kwargs: GameObject(
            name="rope",
            description="A coil of sturdy rope.",
            weight=5,
            value=20,
            object_type=ObjectType.MISC,
            **kwargs
        ),
    }
