"""Records room for war history"""

from lib.models.entity import Room, Exit, DescriptionItem
from lib.models.enums import ExitType

def load():
    """Load and return the records room."""
    room = Room(
        name='records_room',
        description="""The Hall of Records

Ancient tomes line the shelves, recording every war that has ever been
fought in PKMUD. The air is thick with the weight of history. You can 
review past battles and statistics here.

Commands: 'wars' to see recent wars
          'wars <number>' to see specific number of recent wars
          'topkillers' to see all-time kill leaders
          'stats <player>' to see player statistics""",
        description_items=[
            DescriptionItem(
                name='tomes',
                aliases=['books', 'records', 'tome', 'book'],
                description='Massive leather-bound books containing detailed war records.'
            ),
            DescriptionItem(
                name='shelves',
                aliases=['shelf', 'bookshelf', 'bookshelves'],
                description='Floor-to-ceiling shelves packed with historical records.'
            ),
            DescriptionItem(
                name='air',
                aliases=['atmosphere'],
                description='The air feels heavy with the weight of countless battles.'
            )
        ],
        exits=[
            Exit(
                name='south',
                description='Back to the war room.',
                destination='warroom',
                exit_type=ExitType.DOOR
            )
        ]
    )
    
    room.special_type = 'records'
    return room