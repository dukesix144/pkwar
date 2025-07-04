"""Example wizard room with money generation"""

from lib.models.entity import Room, Exit, DescriptionItem
from lib.models.enums import ExitType
from lib.special_rooms import RandomRoom

def load():
    """Load this room - using RandomRoom for money drops."""
    room = RandomRoom(
        name='wizard_example_room',
        description="""A Wizard's Creation

This room was created by a wizard and will generate coins on first entry.
The dust here looks particularly thick and undisturbed.""",
        
        description_items=[
            DescriptionItem(
                name='dust',
                aliases=['thick dust', 'piles'],
                description='Thick piles of dust that look like they haven\'t been disturbed in ages.'
            )
        ],
        
        exits=[
            Exit(
                name='out',
                description='Back to the backbone.',
                destination='backbone_10',  # Connect to backbone
                exit_type=ExitType.PATH
            )
        ]
    )
    
    # Optional: Customize coin range (default is 200-500)
    # room.base_coin_range = (100, 300)
    
    return room
