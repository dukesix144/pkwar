"""Gerkin's Shop - War Supplies"""

from lib.models.entity import Room, Exit, DescriptionItem
from lib.models.enums import ExitType

def load():
    """Load Gerkin's shop."""
    room = Room(
        name='shop',
        description="""Gerkin's War Supplies

This cramped shop is filled with the tools of war. Weapons hang from 
every available wall space, and armor is stacked in corners. Shelves 
hold healing potions and magical wands, their labels handwritten in 
Gerkin's manic scrawl.

Behind the counter stands Gerkin himself - a wild-eyed man who seems 
to twitch at every sound. His eyes follow you with an unsettling 
intensity, and he mutters constantly under his breath about blood, 
death, and the endless wars that rage outside.

The air smells of oil, metal, and something indefinably sinister.""",
        
        description_items=[
            DescriptionItem(
                name='weapons',
                aliases=['weapon', 'sword', 'swords'],
                description='Various weapons of war hang from hooks and stands.'
            ),
            DescriptionItem(
                name='armor',
                aliases=['armour', 'protection', 'gear'],
                description='Protective gear stacked and displayed throughout the shop.'
            ),
            DescriptionItem(
                name='shelves',
                aliases=['shelf', 'potions', 'wands'],
                description='Shelves lined with healing potions and magical wands.'
            ),
            DescriptionItem(
                name='counter',
                aliases=['shop counter'],
                description='A worn wooden counter stained with suspicious dark marks.'
            ),
            DescriptionItem(
                name='gerkin',
                aliases=['shopkeeper', 'merchant', 'man'],
                description='A wild-eyed man with twitchy movements and bloodshot eyes. He radiates an aura of barely contained madness.'
            ),
            DescriptionItem(
                name='labels',
                aliases=['scrawl', 'writing'],
                description='Handwritten price tags in manic, barely legible handwriting.'
            )
        ],
        
        exits=[
            Exit(
                name='west',
                description='Back to the backbone entrance.',
                destination='backbone_entrance',
                exit_type=ExitType.PATH
            )
        ]
    )
    
    # Mark as special room
    room.special_type = 'shop'
    room.no_coins = True
    
    return room