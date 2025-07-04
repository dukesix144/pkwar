"""Special room classes for PKMUD"""

import random
from lib.models.entity import Room

class SpecialRoom(Room):
    """Base class for special rooms with additional functionality."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.special_type = None
        self.money_dropped = False  # For random rooms
        self.base_coin_range = (200, 500)  # Default coin range

class RandomRoom(SpecialRoom):
    """Room that drops random money on first entry per boot."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.special_type = 'random'
        self.money_dropped = False
    
    def check_for_money(self) -> int:
        """Check if room should drop money."""
        if not self.money_dropped:
            self.money_dropped = True
            return random.randint(*self.base_coin_range)
        return 0