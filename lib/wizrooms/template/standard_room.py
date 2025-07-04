"""Example standard wizard room (no money)"""

from lib.models.entity import Room, Exit, DescriptionItem
from lib.models.enums import ExitType

def load():
    """Load this room - standard Room, no money generation."""
    room = Room(
        name='wizard_standard_room',
        description="""A Standard Room

This is a normal room that does not generate coins.
Use this template for rooms that shouldn't have money.""",
        
        description_items=[
            DescriptionItem(
                name='walls',
                aliases=['wall'],
                description='The walls are made of solid stone.'
            )
        ],
        
        exits=[
            Exit(
                name='out',
                description='Back to where you came from.',
                destination='backbone_10',
                exit_type=ExitType.PATH
            )
        ]
    )
    
    return room
