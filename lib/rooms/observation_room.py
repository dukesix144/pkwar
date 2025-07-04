"""Observation room for watching wars"""

from lib.models.entity import Room, Exit, DescriptionItem
from lib.models.enums import ExitType

def load():
    """Load and return the observation room."""
    room = Room(
        name='observation_room',
        description="""The Observation Room

Multiple crystal screens line the walls, showing live combat from the
current war. You can watch the battles unfold in real-time from the
safety of this mystical chamber.

Commands: 'watch' to start watching the war
          'stop' to stop watching
          'screens' to see available views""",
        description_items=[
            DescriptionItem(
                name='screens',
                aliases=['crystal screens', 'crystals', 'screen', 'crystal'],
                description='The screens shimmer with magical energy, ready to display combat.'
            ),
            DescriptionItem(
                name='walls',
                aliases=['wall'],
                description='The walls are covered with crystal screens of various sizes.'
            ),
            DescriptionItem(
                name='chamber',
                aliases=['room'],
                description='A comfortable viewing chamber with an otherworldly atmosphere.'
            )
        ],
        exits=[
            Exit(
                name='west',
                description='Back to the war room.',
                destination='warroom',
                exit_type=ExitType.DOOR
            )
        ]
    )
    
    room.special_type = 'observation'
    room.allows_war_watching = True
    return room