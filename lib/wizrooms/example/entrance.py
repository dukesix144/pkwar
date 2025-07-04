"""Example wizard area entrance - template for wizard creation"""

from lib.special_rooms import RandomRoom
from lib.models.entity import Exit, DescriptionItem
from lib.models.enums import ExitType

def load():
    """Load the entrance to the example area."""
    room = RandomRoom(  # RandomRoom for money drops
        name='example_entrance',
        description="""Example Area - Entrance

This is a template room showing how wizards can create their own areas.
Notice how this room inherits from RandomRoom, which means players can
find coins here on their first visit after each reboot.

The room has detailed descriptions for everything mentioned in the main
description, proper exits, and follows the PKMUD room standards.""",
        
        description_items=[
            DescriptionItem(
                name='template',
                aliases=['template room', 'example'],
                description='This room serves as a template for wizard creation.'
            ),
            DescriptionItem(
                name='coins',
                aliases=['coin', 'money'],
                description='Coins might be hidden here if you\'re the first to arrive.'
            ),
            DescriptionItem(
                name='standards',
                aliases=['pkmud standards', 'room standards'],
                description='Every room should have descriptions, items, and proper exits.'
            )
        ],
        
        exits=[
            Exit(
                name='north',
                description='Back to the backbone.',
                destination='backbone_10',  # Connect to backbone
                exit_type=ExitType.PATH
            ),
            Exit(
                name='south',
                description='Deeper into the example area.',
                destination='example_hall',
                exit_type=ExitType.PATH
            )
        ]
    )
    
    # Optional: Set custom coin range for this room
    room.base_coin_range = (100, 300)  # Less coins than default
    
    return room