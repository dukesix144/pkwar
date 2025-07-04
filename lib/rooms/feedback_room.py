"""Feedback room with bulletin board"""

from lib.models.entity import Room, Exit, DescriptionItem
from lib.models.enums import ExitType

def load():
    """Load and return the feedback room."""
    room = Room(
        name='feedback_room',
        description="""The Feedback Room

A large bulletin board dominates the room, covered with notes and 
suggestions from players. This is where you can leave feedback about
the game and read what others have written.

Commands: 'read board' to read messages
          'post <message>' to leave feedback
          'read <number>' to read specific message""",
        description_items=[
            DescriptionItem(
                name='board',
                aliases=['bulletin board', 'bulletin', 'notes'],
                description='A cork board covered with player feedback, suggestions, and comments.'
            ),
            DescriptionItem(
                name='room',
                aliases=['feedback room'],
                description='A quiet room dedicated to player communication with the implementors.'
            ),
            DescriptionItem(
                name='pins',
                aliases=['pin', 'thumbtacks'],
                description='Colorful pins hold the various notes to the board.'
            )
        ],
        exits=[
            Exit(
                name='east',
                description='Back to the war room.',
                destination='warroom',
                exit_type=ExitType.DOOR
            )
        ]
    )
    
    room.special_type = 'feedback'
    room.has_board = True
    return room