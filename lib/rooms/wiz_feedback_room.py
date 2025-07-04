"""Wizard feedback room"""

from lib.models.entity import Room, Exit, DescriptionItem
from lib.models.enums import ExitType

def load():
    """Load and return the wizard feedback room."""
    room = Room(
        name='wiz_feedback_room',
        description="""The Implementors' Feedback Chamber

A quiet room where implementors can review feedback and communicate
about development. A large magical board displays bug reports and
feature requests. The atmosphere encourages thoughtful discussion.

Commands: 'read board' to see implementor messages
          'post <message>' to leave a note for other implementors
          'bugs' to see recent bug reports
          'ideas' to see player suggestions""",
        description_items=[
            DescriptionItem(
                name='board',
                aliases=['magical board', 'feedback board'],
                description='A magical board that organizes feedback into categories.'
            ),
            DescriptionItem(
                name='atmosphere',
                aliases=['room'],
                description='The room has a contemplative atmosphere perfect for planning.'
            ),
            DescriptionItem(
                name='reports',
                aliases=['bug reports', 'bugs'],
                description='Bug reports glow red on the board.'
            ),
            DescriptionItem(
                name='suggestions',
                aliases=['ideas', 'feature requests'],
                description='Player suggestions shimmer blue on the board.'
            )
        ],
        exits=[
            Exit(
                name='south',
                description='Back to the main wizard room.',
                destination='wizroom_main',
                exit_type=ExitType.DOOR
            )
        ]
    )
    
    room.special_type = 'wiz_feedback'
    room.implementor_only = True
    room.has_board = True
    return room