"""War room - the heart of PKMUD"""

from lib.models.entity import Room, Exit, DescriptionItem
from lib.models.enums import ExitType

def load():
    """Load and return the war room."""
    room = Room(
        name='warroom',
        description="""The War Room

This is the heart of PKMUD - where wars begin and end. The walls are 
lined with the names of past champions, and a massive WAR BUTTON sits 
in the center of the room. Ghosts drift through here between battles.

Commands: 'push button' to start a war (if eligible)
          'war on/off' to toggle war participation
          'vote <ffa|team|bvr>' to vote for war type
          'warstatus' to check current war status""",
        description_items=[
            DescriptionItem(
                name='button',
                aliases=['war button', 'massive button'],
                description='A massive red button that pulses with energy. Push it to start a war!'
            ),
            DescriptionItem(
                name='walls',
                aliases=['names', 'champions', 'wall'],
                description='The walls display the names of legendary warriors who have won past wars.'
            ),
            DescriptionItem(
                name='ghosts',
                aliases=['ghost'],
                description='Ethereal ghosts drift through the room, waiting for the next war.'
            )
        ],
        exits=[
            Exit(
                name='south',
                description='Into the backbone complex.',
                destination='backbone_entrance',
                exit_type=ExitType.PATH
            ),
            Exit(
                name='east',
                description='To the observation room.',
                destination='observation_room',
                exit_type=ExitType.DOOR
            ),
            Exit(
                name='west',
                description='To the feedback room.',
                destination='feedback_room',
                exit_type=ExitType.DOOR
            ),
            Exit(
                name='north',
                description='To the records room.',
                destination='records_room',
                exit_type=ExitType.DOOR
            ),
            Exit(
                name='up',
                description='A hidden passage for ghosts only.',
                destination='entrance',
                exit_type=ExitType.PATH
            )
        ]
    )
    
    # Mark as special room
    room.special_type = 'warroom'
    room.allow_war_button = True
    room.no_coins = True
    
    return room