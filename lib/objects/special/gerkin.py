"""Spirit of Gerkin - Special war object"""

from lib.models.objects import GameObject, ObjectType
import time
import random
from typing import Optional

class SpiritOfGerkin(GameObject):
    """The Spirit of Gerkin - grants special powers during war."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="Spirit of Gerkin",
            description="The ethereal spirit of Gerkin hovers nearby, eager for bloodshed. "
                       "Its yellow glow pulses with barely contained violence.",
            weight=0,  # Weightless
            value=0,   # Priceless
            object_type=ObjectType.SPECIAL,
            **kwargs
        )
        self.last_power_use = 0
        self.power_cooldown = random.randint(120, 180)  # 2-3 minutes
        self.active_hunt = None
        self.hunt_start_time = None
        self.messages = [
            "Gerkin whispers: 'Blood... I need blood!'",
            "Gerkin cackles: 'Kill them all!'",
            "Gerkin mutters: 'So many wars... so much death...'",
            "Gerkin screams: 'DEATH! DEATH TO ALL!'",
            "Gerkin moans: 'The hunger... it never ends...'",
            "Gerkin giggles madly: 'Paint the ground red!'",
            "Gerkin hisses: 'Weak... they're all so weak...'"
        ]
    
    def can_use_power(self) -> bool:
        """Check if Gerkin's power is ready."""
        return time.time() - self.last_power_use >= self.power_cooldown
    
    def use_power(self, user, target_name: str) -> tuple[bool, str]:
        """Use Gerkin's hunt power."""
        if not self.can_use_power():
            remaining = int(self.power_cooldown - (time.time() - self.last_power_use))
            return False, f"Gerkin is not ready yet. ({remaining} seconds remaining)"
        
        # Find target
        from pkwar import game
        target = None
        for player in game.list_players():
            if player.name.lower() == target_name.lower() and not player.is_ghost:
                target = player
                break
        
        if not target:
            return False, f"Gerkin cannot find '{target_name}' among the living."
        
        if target == user:
            return False, "Gerkin refuses to hunt you!"
        
        # Activate hunt
        self.active_hunt = target
        self.hunt_start_time = time.time()
        self.last_power_use = time.time()
        self.power_cooldown = random.randint(120, 180)  # Reset cooldown
        
        # Teleport user to target
        user.move(target._location)
        
        # Make user follow target
        user.following = target
        
        return True, f"Gerkin teleports you to {target.name} and compels you to follow!"
    
    def check_hunt_status(self, user) -> Optional[str]:
        """Check if hunt is still active and provide direction hints."""
        if not self.active_hunt:
            return None
        
        # Hunt expires after 30 seconds
        if time.time() - self.hunt_start_time > 30:
            self.active_hunt = None
            user.following = None
            return "Gerkin grows bored and stops helping."
        
        # If target escaped and is within 5 rooms, give directions
        if user._location != self.active_hunt._location:
            # TODO: Implement pathfinding for directions
            return f"Gerkin senses {self.active_hunt.name} is nearby..."
        
        return None
    
    def get_random_message(self) -> str:
        """Get a random Gerkin message."""
        return random.choice(self.messages)
    
    def examine(self) -> str:
        """Detailed examination."""
        text = self.description
        if self.can_use_power():
            text += "\n\nGerkin seems eager and ready to hunt!"
        else:
            remaining = int(self.power_cooldown - (time.time() - self.last_power_use))
            text += f"\n\nGerkin seems tired. ({remaining} seconds until ready)"
        
        text += "\n\nUse: 'gerkin kill <player>' to activate the hunt."
        return text

def load():
    """Return Gerkin template."""
    return {
        "spirit_of_gerkin": lambda **kwargs: SpiritOfGerkin(**kwargs)
    }