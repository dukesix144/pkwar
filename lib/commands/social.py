"""Social and emote commands."""

from .base import BaseCommand

class SocialCommands(BaseCommand):
    """Commands for social interactions and emotes."""
    
    def __init__(self, game_state):
        super().__init__(game_state)
        self.soul_manager = game_state.soul_manager
    
    def emote(self, player, message):
        """emote <action> - Perform an action"""
        if not message:
            player.message("Emote what?")
            return
        
        # Handle SELF prefix
        if message.upper().startswith("SELF "):
            message = message[5:]
            player.message(f"{player.name} {message}")
            return
        
        # Show to everyone in room
        self.broadcast_to_room(player, f"{player.name} {message}", include_self=True)

    def soul(self, player, params=None):
        """soul <letter> - List soul commands starting with letter"""
        if not params:
            player.message("Usage: soul <letter>")
            return
        
        letter = params[0].lower()
        souls = self.soul_manager.list_souls(letter)
        
        if not souls:
            player.message(f"No soul commands starting with '{letter}'")
            return
        
        # Format in columns
        output = []
        row = []
        for soul in souls:
            row.append(soul)
            if len(row) >= 5:
                output.append("  ".join(f"{s:<12}" for s in row))
                row = []
        
        if row:
            output.append("  ".join(f"{s:<12}" for s in row))
        
        player.message(f"Soul commands starting with '{letter}':")
        player.message("\n".join(output))

    def feelings(self, player, params=None):
        """feelings - Show number of soul commands"""
        count = self.soul_manager.count_souls()
        player.message(f"PKMUD has {count} soul commands!")
        player.message("Use 'soul <letter>' to list souls by letter.")