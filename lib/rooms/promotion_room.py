"""Promotion and linking room"""

from lib.models.entity import Room, Exit, DescriptionItem
from lib.models.enums import ExitType

def load():
    """Load and return the promotion room."""
    room = Room(
        name='promotion_room',
        description="""The Chamber of Ascension

Here, worthy players can ascend to become implementors, and implementors
can link their enforcer characters. A glowing altar dominates the center
of the room, pulsing with transformative power. The walls are inscribed
with the names of all who have ascended.

Commands: 'promotemenow' - Promote to implementor (level 10+ only)
          'link <character>' - Link an enforcer character""",
        description_items=[
            DescriptionItem(
                name='altar',
                aliases=['ascension altar', 'glowing altar'],
                description='A glowing altar of transformation, radiating power.'
            ),
            DescriptionItem(
                name='walls',
                aliases=['wall', 'inscriptions', 'names'],
                description='The walls bear the names of all who have ascended to implementor status.'
            ),
            DescriptionItem(
                name='power',
                aliases=['transformative power', 'energy'],
                description='Waves of transformative energy emanate from the altar.'
            )
        ],
        exits=[
            Exit(
                name='north',
                description='Back to the wizard room.',
                destination='wizroom_main',
                exit_type=ExitType.DOOR
            )
        ]
    )
    
    room.special_type = 'promotion'
    return room