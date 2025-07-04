"""Communication commands."""

from .base import BaseCommand

class CommunicationCommands(BaseCommand):
    """Commands for communication between players."""
    
    def __init__(self, game_state):
        super().__init__(game_state)
        self.channel_manager = game_state.channel_manager
    
    def say(self, player, message):
        """say <message> - Say something to the room"""
        if not message:
            player.message("Say what?")
            return
        
        self.channel_manager.send_to_channel('say', player, message)

    def tell(self, player, params):
        """tell <player> <message> - Send a private message"""
        if not params or ' ' not in params:
            player.message("Usage: tell <player> <message>")
            return
        
        parts = params.split(' ', 1)
        target = parts[0]
        message = parts[1] if len(parts) > 1 else ""
        
        if not message:
            player.message("Tell them what?")
            return
        
        self.channel_manager.send_to_channel('tell', player, message, target)

    def shout(self, player, message):
        """shout <message> - Shout to all players"""
        if not message:
            player.message("Shout what?")
            return
        
        self.channel_manager.send_to_channel('shout', player, message)

    def ghost(self, player, message):
        """ghost <message> - Talk on the ghost channel"""
        if not message:
            player.message("Usage: ghost <message>")
            return
        
        self.channel_manager.send_to_channel('ghost', player, message)

    def wiz(self, player, message):
        """wiz <message> - Talk on the wizard channel"""
        if not message:
            player.message("Usage: wiz <message>")
            return
        
        self.channel_manager.send_to_channel('wiz', player, message)

    def team(self, player, message):
        """team <message> - Talk to your team during war"""
        if not message:
            player.message("Usage: team <message>")
            return
        
        self.channel_manager.send_to_channel('team', player, message)

    def gossip(self, player, message):
        """gossip <message> - General chat channel"""
        if not message:
            player.message("Usage: gossip <message>")
            return
        
        self.channel_manager.send_to_channel('gossip', player, message)

    def newbie(self, player, message):
        """newbie <message> - Newbie help channel"""
        if not message:
            player.message("Usage: newbie <message>")
            return
        
        self.channel_manager.send_to_channel('newbie', player, message)

    def channels(self, player, params=None):
        """channels - Show channel status and commands"""
        if params:
            # Parse channel command options
            parts = params.split()
            if len(parts) >= 2 and parts[0].startswith('-'):
                option = parts[0]
                channel = parts[1]
                
                if option == '-b':
                    self.channel_manager.block_channel(player, channel)
                elif option == '-h':
                    count = int(parts[2]) if len(parts) > 2 else 20
                    self.channel_manager.show_history(player, channel, count)
                elif option == '-w':
                    self.channel_manager.show_listeners(player, channel)
                else:
                    player.message(f"Unknown option '{option}'")
            else:
                # Toggle channel on/off
                self.channel_manager.toggle_channel(player, params)
        else:
            output = self.channel_manager.show_channels(player)
            player.message(output)