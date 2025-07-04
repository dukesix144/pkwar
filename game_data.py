"""Game data - rooms are now loaded dynamically from files"""

# This file is kept for backwards compatibility
# Rooms are now loaded from individual files in lib/rooms/

# The rooms dictionary is populated by pkwar.py at startup
rooms = {}

def add_room(room):
    """Legacy function for adding rooms - kept for compatibility"""
    rooms[room.name] = room