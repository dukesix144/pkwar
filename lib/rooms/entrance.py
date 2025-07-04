"""Entrance room for PKMUD"""

from lib.models.entity import Room, Exit, DescriptionItem
from lib.models.enums import ExitType

def load():
    """Load and return the entrance room."""
    return Room(
        name='entrance',
        description="""Welcome to PKMUD!

You stand in the entrance hall, a grand chamber with vaulted ceilings 
and flickering torches. The air crackles with anticipation of battles 
to come. A stairway leads down to the war room, where the real action begins.

New players should read 'help newbie' to get started.""",
        description_items=[
            DescriptionItem(
                name='torches',
                aliases=['torch', 'flickering torches'],
                description='The torches cast dancing shadows on the walls.'
            ),
            DescriptionItem(
                name='stairway',
                aliases=['stairs', 'down'],
                description='A wide stone stairway descends into darkness.'
            ),
            DescriptionItem(
                name='ceiling',
                aliases=['vaulted ceiling', 'ceilings'],
                description='The vaulted ceiling rises high above, lost in shadows.'
            )
        ],
        exits=[
            Exit(
                name='down',
                description='The stairway leads down to the war room.',
                destination='warroom',
                exit_type=ExitType.PATH
            )
        ]
    )