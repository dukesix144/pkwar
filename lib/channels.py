"""Communication channels system for PKMUD"""

from typing import List, Dict, Optional
from collections import deque
import time

class Channel:
    """Base class for communication channels."""
    
    def __init__(self, name: str, description: str, color_var: str = None):
        self.name = name
        self.description = description
        self.color_var = color_var or name
        self.history = deque(maxlen=100)  # Last 100 messages
        self.blocked_by = set()  # Players who have blocked this channel
    
    def can_use(self, player) -> tuple[bool, str]:
        """Check if player can use this channel."""
        return True, ""
    
    def format_message(self, sender, message: str) -> str:
        """Format message for display."""
        return f"{sender.name}: {message}"
    
    def add_to_history(self, sender, message: str):
        """Add message to channel history."""
        self.history.append({
            'time': time.time(),
            'sender': sender.name,
            'message': message,
            'formatted': self.format_message(sender, message)
        })
    
    def get_history(self, count: int = 20) -> List[str]:
        """Get recent history."""
        if count == -1:
            count = len(self.history)
        
        messages = []
        for entry in list(self.history)[-count:]:
            timestamp = time.strftime("%H:%M", time.localtime(entry['time']))
            messages.append(f"[{timestamp}] {entry['formatted']}")
        
        return messages
    
    def get_listeners(self, game_state) -> List:
        """Get list of players listening to this channel."""
        listeners = []
        for player in game_state.list_players():
            if (player.channels_on.get(self.name, False) and 
                player.name not in self.blocked_by):
                listeners.append(player)
        return listeners

class SayChannel(Channel):
    """Local room communication."""
    
    def __init__(self):
        super().__init__('say', 'Speak to others in the same room', 'say')
    
    def format_message(self, sender, message: str) -> str:
        return f"{sender.name} says: {message}"
    
    def get_listeners(self, game_state, sender) -> List:
        """Only players in same room hear say."""
        listeners = []
        for player in game_state.list_players():
            if (player._location == sender._location and 
                player != sender and
                player.channels_on.get('say', True)):
                listeners.append(player)
        return listeners

class TellChannel(Channel):
    """Private messages between players."""
    
    def __init__(self):
        super().__init__('tell', 'Private messages to another player', 'tell')
    
    def format_message(self, sender, message: str, target=None) -> str:
        if target:
            return f"{sender.name} tells you: {message}"
        return f"You tell {target}: {message}"

class ShoutChannel(Channel):
    """Mud-wide announcements."""
    
    def __init__(self):
        super().__init__('shout', 'Shout to all players', 'shout')
    
    def format_message(self, sender, message: str) -> str:
        return f"{sender.name} shouts: {message}"

class GhostChannel(Channel):
    """Channel for dead players only."""
    
    def __init__(self):
        super().__init__('ghost', 'Ghost communication', 'ghost')
    
    def can_use(self, player) -> tuple[bool, str]:
        if not player.is_ghost:
            return False, "Only ghosts can use the ghost channel."
        return True, ""
    
    def format_message(self, sender, message: str) -> str:
        return f"(Ghost) {sender.name}: {message}"
    
    def get_listeners(self, game_state) -> List:
        """Only ghosts hear ghost channel."""
        listeners = []
        for player in game_state.list_players():
            if (player.is_ghost and 
                player.channels_on.get('ghost', True) and
                player.name not in self.blocked_by):
                listeners.append(player)
        return listeners

class WizChannel(Channel):
    """Channel for implementors only."""
    
    def __init__(self):
        super().__init__('wiz', 'Implementor communication', 'wiz')
    
    def can_use(self, player) -> tuple[bool, str]:
        if player.implementor_level == 0:
            return False, "Only implementors can use the wiz channel."
        return True, ""
    
    def format_message(self, sender, message: str) -> str:
        return f"[Wiz] {sender.name}: {message}"
    
    def get_listeners(self, game_state) -> List:
        """Only implementors hear wiz channel."""
        listeners = []
        for player in game_state.list_players():
            if (player.implementor_level > 0 and 
                player.channels_on.get('wiz', True) and
                player.name not in self.blocked_by):
                listeners.append(player)
        return listeners

class TeamChannel(Channel):
    """Channel for team communication during wars."""
    
    def __init__(self):
        super().__init__('team', 'Team communication during wars', 'team')
    
    def can_use(self, player) -> tuple[bool, str]:
        if not player.team:
            return False, "You are not on a team."
        return True, ""
    
    def format_message(self, sender, message: str) -> str:
        return f"(Team) {sender.name}: {message}"
    
    def get_listeners(self, game_state, sender) -> List:
        """Only same team members hear team channel."""
        listeners = []
        for player in game_state.list_players():
            if (player.team == sender.team and 
                player != sender and
                player.channels_on.get('team', True)):
                listeners.append(player)
        return listeners

class ChannelManager:
    """Manages all communication channels."""
    
    def __init__(self, game_state):
        self.game_state = game_state
        self.channels = {
            'say': SayChannel(),
            'tell': TellChannel(),
            'shout': ShoutChannel(),
            'ghost': GhostChannel(),
            'wiz': WizChannel(),
            'team': TeamChannel(),
            'gossip': Channel('gossip', 'General chat channel', 'gossip'),
            'newbie': Channel('newbie', 'Help channel for new players', 'newbie'),
            'ooc': Channel('ooc', 'Out of character chat', 'ooc')
        }
    
    def send_to_channel(self, channel_name: str, sender, message: str, target=None) -> bool:
        """Send a message to a channel."""
        if channel_name not in self.channels:
            sender.message(f"Unknown channel: {channel_name}")
            return False
        
        channel = self.channels[channel_name]
        
        # Check if player can use channel
        can_use, reason = channel.can_use(sender)
        if not can_use:
            sender.message(reason)
            return False
        
        # Check if player has channel on
        if not sender.channels_on.get(channel_name, True):
            sender.message(f"You have the {channel_name} channel turned off.")
            return False
        
        # Handle tell specially
        if channel_name == 'tell' and target:
            return self._handle_tell(sender, target, message)
        
        # Add to history
        channel.add_to_history(sender, message)
        
        # Format message
        formatted = channel.format_message(sender, message)
        
        # Send to sender with different formatting
        if sender.ansi_enabled and hasattr(sender, 'ansi_manager'):
            sender_msg = sender.ansi_manager.format_channel(channel_name, "You", message)
        else:
            sender_msg = f"You {channel_name}: {message}"
        sender.message(sender_msg)
        
        # Get listeners
        if hasattr(channel, 'get_listeners') and channel_name in ['say', 'team']:
            listeners = channel.get_listeners(self.game_state, sender)
        else:
            listeners = channel.get_listeners(self.game_state)
        
        # Send to all listeners
        for player in listeners:
            if player.ansi_enabled and hasattr(player, 'ansi_manager'):
                msg = player.ansi_manager.format_channel(channel_name, sender.name, message)
            else:
                msg = formatted
            player.message(msg)
        
        return True
    
    def _handle_tell(self, sender, target_name: str, message: str) -> bool:
        """Handle private tell messages."""
        # Find target player
        target = None
        for player in self.game_state.list_players():
            if player.name.lower() == target_name.lower():
                target = player
                break
        
        if not target:
            sender.message(f"Player '{target_name}' not found.")
            return False
        
        if not target.channels_on.get('tell', True):
            sender.message(f"{target.name} is not accepting tells.")
            return False
        
        # Send to target
        if target.ansi_enabled and hasattr(target, 'ansi_manager'):
            target_msg = target.ansi_manager.format_channel('tell', sender.name, message)
        else:
            target_msg = f"{sender.name} tells you: {message}"
        target.message(target_msg)
        
        # Confirm to sender
        if sender.ansi_enabled and hasattr(sender, 'ansi_manager'):
            sender_msg = sender.ansi_manager.format_channel('tell', f"You tell {target.name}", message)
        else:
            sender_msg = f"You tell {target.name}: {message}"
        sender.message(sender_msg)
        
        # Add to history
        self.channels['tell'].add_to_history(sender, f"to {target.name}: {message}")
        
        return True
    
    def toggle_channel(self, player, channel_name: str) -> bool:
        """Toggle a channel on/off for a player."""
        if channel_name not in self.channels:
            player.message(f"Unknown channel: {channel_name}")
            return False
        
        current = player.channels_on.get(channel_name, True)
        player.channels_on[channel_name] = not current
        
        status = "on" if player.channels_on[channel_name] else "off"
        player.message(f"{channel_name.capitalize()} channel turned {status}.")
        
        return True
    
    def block_channel(self, player, channel_name: str) -> bool:
        """Block/unblock a channel entirely."""
        if channel_name not in self.channels:
            player.message(f"Unknown channel: {channel_name}")
            return False
        
        channel = self.channels[channel_name]
        
        if player.name in channel.blocked_by:
            channel.blocked_by.remove(player.name)
            player.message(f"{channel_name.capitalize()} channel unblocked.")
        else:
            channel.blocked_by.add(player.name)
            player.message(f"{channel_name.capitalize()} channel blocked.")
        
        return True
    
    def show_history(self, player, channel_name: str, count: int = 20) -> bool:
        """Show channel history to player."""
        if channel_name not in self.channels:
            player.message(f"Unknown channel: {channel_name}")
            return False
        
        channel = self.channels[channel_name]
        
        # Check if player can see this channel
        can_use, reason = channel.can_use(player)
        if not can_use:
            player.message(reason)
            return False
        
        history = channel.get_history(count)
        
        if not history:
            player.message(f"No history for {channel_name} channel.")
        else:
            player.message(f"\n=== {channel_name.upper()} History ===")
            for msg in history:
                player.message(msg)
            player.message("=== End History ===\n")
        
        return True
    
    def show_listeners(self, player, channel_name: str) -> bool:
        """Show who is listening to a channel."""
        if channel_name not in self.channels:
            player.message(f"Unknown channel: {channel_name}")
            return False
        
        channel = self.channels[channel_name]
        
        # Check if player can see this channel
        can_use, reason = channel.can_use(player)
        if not can_use:
            player.message(reason)
            return False
        
        # Get listeners
        if hasattr(channel, 'get_listeners'):
            if channel_name in ['say', 'team']:
                listeners = channel.get_listeners(self.game_state, player)
            else:
                listeners = channel.get_listeners(self.game_state)
        else:
            listeners = []
        
        if not listeners:
            player.message(f"No one is listening to {channel_name} channel.")
        else:
            names = [p.name for p in listeners]
            player.message(f"Listening to {channel_name}: {', '.join(names)}")
        
        return True
    
    def show_channels(self, player) -> str:
        """Show all channels and their status for a player."""
        output = ["Your communication channels:"]
        output.append("-" * 60)
        output.append(f"{'Channel':<15} {'Status':<10} {'Listeners':<10} {'Command':<20}")
        output.append("-" * 60)
        
        for name, channel in sorted(self.channels.items()):
            # Check if player can use
            can_use, _ = channel.can_use(player)
            if not can_use and name not in ['wiz', 'ghost']:
                continue
            
            # Status
            if player.name in channel.blocked_by:
                status = "BLOCKED"
            elif player.channels_on.get(name, True):
                status = "ON"
            else:
                status = "OFF"
            
            # Listener count
            if hasattr(channel, 'get_listeners'):
                if name in ['say', 'team']:
                    listeners = channel.get_listeners(self.game_state, player)
                else:
                    listeners = channel.get_listeners(self.game_state)
                count = len(listeners)
            else:
                count = 0
            
            # Command syntax
            if name == 'tell':
                cmd = f"{name} <player> <msg>"
            elif name == 'say':
                cmd = f"say <msg> or '<msg>"
            else:
                cmd = f"{name} <msg>"
            
            output.append(f"{name:<15} {status:<10} {count:<10} {cmd:<20}")
        
        return "\n".join(output)