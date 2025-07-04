"""Mail system commands."""

from .base import BaseCommand
from lib.mail_system import MailComposer
import os

class MailCommands(BaseCommand):
    """Commands for the mail system."""
    
    def __init__(self, game_state):
        super().__init__(game_state)
        self.mail_system = game_state.mail_system
        self.mail_composers = {}  # player_uuid: MailComposer
    
    def mail(self, player, params=None):
        """mail <player> - Send mail to someone"""
        if not params:
            # List mail
            output = self.mail_system.list_mail(player.name)
            player.message("\n".join(output))
            return
        
        # Check if already composing
        if player.client.uuid in self.mail_composers:
            player.message("You are already composing mail. Send or cancel it first.")
            return
        
        # Start composing mail
        recipients = params.split(',')
        composer = MailComposer(player.name)
        
        # Validate recipients - case insensitive
        valid_recipients = []
        for recipient in recipients:
            recipient = recipient.strip()
            
            # Find player file case-insensitively
            found = False
            player_dir = "lib/players"
            if os.path.exists(player_dir):
                for filename in os.listdir(player_dir):
                    if filename.endswith('.json') and filename[:-5].lower() == recipient.lower():
                        # Found the player - use the actual case from filename
                        actual_name = filename[:-5]
                        # Load the file to get the proper capitalized name
                        with open(os.path.join(player_dir, filename), 'r') as f:
                            import json
                            player_data = json.load(f)
                            actual_name = player_data.get('name', actual_name)
                        
                        composer.add_recipient(actual_name)
                        valid_recipients.append(actual_name)
                        found = True
                        break
            
            if not found:
                player.message(f"Unknown player: {recipient}")
        
        if not valid_recipients:
            player.message("No valid recipients. Mail cancelled.")
            return
        
        self.mail_composers[player.client.uuid] = composer
        player.message(f"To: {', '.join(valid_recipients)}")
        player.message("Cc: (press enter for none)")
        player.mail_mode = "CC"
        
        # Return signal to main command handler
        return {'mail_mode': "CC", 'composer': composer}
    
    def read_mail(self, player, params=None):
        """read <id> - Read a mail message"""
        if not params:
            player.message("Read which mail? Use 'mail' to list.")
            return
        
        try:
            mail_id = int(params)
        except ValueError:
            player.message("Invalid mail ID.")
            return
        
        content = self.mail_system.read_mail(player.name, mail_id)
        if content:
            player.message(content)
        else:
            player.message("No such mail.")
    
    def delete_mail(self, player, params=None):
        """delete <id> - Delete a mail message"""
        if not params:
            player.message("Delete which mail? Use 'mail' to list.")
            return
        
        try:
            mail_id = int(params)
        except ValueError:
            player.message("Invalid mail ID.")
            return
        
        if self.mail_system.delete_mail(player.name, mail_id):
            player.message("Mail deleted.")
        else:
            player.message("No such mail.")