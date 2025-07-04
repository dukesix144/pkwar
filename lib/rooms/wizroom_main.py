"""Main wizard room"""

from lib.models.entity import Room, Exit, DescriptionItem
from lib.models.enums import ExitType

def load():
    """Load and return the main wizard room."""
    room = Room(
        name='wizroom_main',
        description="""The Implementors' Sanctum

A place of power where the implementors gather. The air hums with
creative energy. Arcane symbols float in the air, and the walls seem
to shift with possibility. From here, implementors can access their
tools and shape the world.

Wizard Commands: 'goto <room>' to teleport
                'trans <player>' to transport a player here
                'load <file>' to load code
                See 'wizhelp' for more""",
        description_items=[
            DescriptionItem(
                name='tools',
                aliases=['wizard tools', 'implements', 'arcane tools'],
                description='Ethereal tools of creation float in the air, awaiting use.'
            ),
            DescriptionItem(
                name='symbols',
                aliases=['arcane symbols', 'symbol', 'runes'],
                description='Glowing symbols of power drift through the air.'
            ),
            DescriptionItem(
                name='walls',
                aliases=['wall', 'shifting walls'],
                description='The walls shimmer with potential, ready to be shaped.'
            ),
            DescriptionItem(
                name='energy',
                aliases=['creative energy', 'power'],
                description='Creative energy crackles through the room.'
            )
        ],
        exits=[
            Exit(
                name='south',
                description='To the promotion chamber.',
                destination='promotion_room',
                exit_type=ExitType.DOOR
            ),
            Exit(
                name='north',
                description='To the wizard feedback room.',
                destination='wiz_feedback_room',
                exit_type=ExitType.DOOR
            ),
            Exit(
                name='down',
                description='To the mortal realm.',
                destination='entrance',
                exit_type=ExitType.PATH
            )
        ]
    )
    
    room.special_type = 'wizard'
    room.implementor_only = True
    return room