"""Corpse container for dead players"""

import time
from lib.models.objects import Container, GameObject

class Corpse(Container):
    """A corpse that holds a dead player's inventory."""
    
    def __init__(self, player_name: str, player_level: int = 1, **kwargs):
        name = f"corpse of {player_name}"
        description = f"The corpse of {player_name} lies here, slowly decaying."
        
        # Corpses can hold a lot
        super().__init__(name, description, capacity=100, **kwargs)
        
        self.player_name = player_name
        self.player_level = player_level
        self.decay_time = 300  # 5 minutes to decay
        self.created_at = time.time()
        self.weight = 50  # Corpses are heavy
        self.value = 0  # Can't sell corpses
        self.sellable = False
        self.takeable = False  # Can't pick up corpses (too heavy)
        
        # Decay stages
        self.decay_messages = [
            (60, f"The corpse of {player_name} is still warm."),
            (120, f"The corpse of {player_name} has started to cool."),
            (180, f"The corpse of {player_name} is cold and stiff."),
            (240, f"The corpse of {player_name} is starting to decay."),
            (300, f"The corpse of {player_name} has decayed into dust.")
        ]
    
    def get_description(self) -> str:
        """Get description based on decay state."""
        elapsed = time.time() - self.created_at
        
        for decay_time, message in self.decay_messages:
            if elapsed < decay_time:
                return message
        
        return self.decay_messages[-1][1]
    
    def is_decayed(self) -> bool:
        """Check if corpse has fully decayed."""
        return (time.time() - self.created_at) >= self.decay_time
    
    def examine(self) -> str:
        """Examine the corpse."""
        text = self.get_description()
        
        if self.contents:
            text += "\nThe corpse contains:"
            for item in self.contents:
                text += f"\n  {item.get_display_name()}"
        else:
            text += "\nThe corpse is empty."
        
        return text
    
    def loot_all(self, looter) -> list:
        """Loot all items from corpse."""
        looted = []
        items_to_loot = self.contents.copy()
        
        for item in items_to_loot:
            if looter.inventory.add_item(item):
                self.remove_item(item)
                looted.append(item)
            else:
                break  # Inventory full
        
        return looted

def load():
    """Return corpse template."""
    return {
        "corpse": lambda player_name, player_level=1, **kwargs: 
            Corpse(player_name, player_level, **kwargs)
    }
