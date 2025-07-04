"""Board system commands."""

from .base import BaseCommand
import time
import json
import os

class BoardCommands(BaseCommand):
    """Commands for the board system."""
    
    def __init__(self, game_state):
        super().__init__(game_state)
        self.board_file = "lib/board_messages.json"
        self._load_messages()
    
    def _load_messages(self):
        """Load board messages from file."""
        if os.path.exists(self.board_file):
            try:
                with open(self.board_file, 'r') as f:
                    self.messages = json.load(f)
            except:
                self.messages = []
        else:
            self.messages = []
    
    def _save_messages(self):
        """Save board messages to file."""
        os.makedirs(os.path.dirname(self.board_file), exist_ok=True)
        with open(self.board_file, 'w') as f:
            json.dump(self.messages, f, indent=2)
    
    def read_board(self, player, params=None):
        """read board - Read board messages (in board room only)"""
        if player._location != 'board_room':
            player.message("There's no board here to read.")
            return
        
        if not self.messages:
            player.message("The board is empty.")
            return
        
        output = ["=== Bulletin Board ==="]
        output.append(f"Total messages: {len(self.messages)}")
        output.append("")
        
        # Show last 20 messages
        start = max(0, len(self.messages) - 20)
        for i, msg in enumerate(self.messages[start:], start=start+1):
            timestamp = time.strftime("%m/%d %H:%M", time.localtime(msg['time']))
            output.append(f"{i:3}. [{timestamp}] {msg['author']}: {msg['title']}")
        
        output.append("")
        output.append("Use 'read <number>' to read a specific message.")
        player.message("\n".join(output))
    
    def read_message(self, player, params=None):
        """read <number> - Read a specific board message"""
        if player._location != 'board_room':
            player.message("There's no board here.")
            return
        
        if not params:
            # Show board list
            self.read_board(player)
            return
        
        try:
            msg_num = int(params)
        except ValueError:
            player.message("Usage: read <number>")
            return
        
        if msg_num < 1 or msg_num > len(self.messages):
            player.message(f"Invalid message number. Board has {len(self.messages)} messages.")
            return
        
        msg = self.messages[msg_num - 1]
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(msg['time']))
        
        output = []
        output.append(f"Message #{msg_num}")
        output.append(f"From: {msg['author']}")
        output.append(f"Date: {timestamp}")
        output.append(f"Subject: {msg['title']}")
        output.append("-" * 40)
        output.append(msg['content'])
        
        player.message("\n".join(output))
    
    def post_message(self, player, params=None):
        """post <message> - Post a message to the board"""
        if player._location != 'board_room':
            player.message("There's no board here to post on.")
            return
        
        if not params:
            player.message("Post what?")
            return
        
        # Parse title from message (first line is title)
        lines = params.strip().split('\n', 1)
        title = lines[0][:50]  # Max 50 chars for title
        content = lines[1] if len(lines) > 1 else lines[0]
        
        # Create message
        message = {
            'author': player.name,
            'title': title,
            'content': content,
            'time': time.time()
        }
        
        self.messages.append(message)
        self._save_messages()
        
        player.message(f"Message posted: {title}")
        
        # Notify others in the room
        room = self.game_state.get_room(player._location)
        if room:
            for other_id in room.creatures:
                if other_id != player.id:
                    other = self.game_state.get_creature(other_id)
                    if other:
                        other.message(f"{player.name} posts a message on the board.")
    
    def remove_message(self, player, params=None):
        """remove <number> - Remove a board message (own messages or wizard)"""
        if player._location != 'board_room':
            player.message("There's no board here.")
            return
        
        if not params:
            player.message("Remove which message?")
            return
        
        try:
            msg_num = int(params)
        except ValueError:
            player.message("Usage: remove <number>")
            return
        
        if msg_num < 1 or msg_num > len(self.messages):
            player.message(f"Invalid message number. Board has {len(self.messages)} messages.")
            return
        
        msg = self.messages[msg_num - 1]
        
        # Check permissions - only author or wizard can remove
        if msg['author'] != player.name and player.wizard_level < 1:
            player.message("You can only remove your own messages.")
            return
        
        removed_msg = self.messages.pop(msg_num - 1)
        self._save_messages()
        
        player.message(f"Removed message #{msg_num}: {removed_msg['title']}")
