"""Mail system for PKMUD"""

import os
import json
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

@dataclass
class Mail:
    """A mail message."""
    id: int
    sender: str
    recipients: List[str]
    cc: List[str]
    subject: str
    body: str
    timestamp: float
    read: bool = False

class MailSystem:
    """Handles player mail."""
    
    MAIL_DIR = "lib/mail"
    
    def __init__(self, game_state):
        self.game_state = game_state
        self.next_mail_id = 1
        
        # Ensure mail directory exists
        os.makedirs(self.MAIL_DIR, exist_ok=True)
        
        # Load next mail ID
        id_file = os.path.join(self.MAIL_DIR, "next_id.txt")
        if os.path.exists(id_file):
            with open(id_file, 'r') as f:
                self.next_mail_id = int(f.read().strip())
    
    def save_next_id(self):
        """Save the next mail ID."""
        id_file = os.path.join(self.MAIL_DIR, "next_id.txt")
        with open(id_file, 'w') as f:
            f.write(str(self.next_mail_id))
    
    def get_player_mailbox_path(self, player_name: str) -> str:
        """Get path to player's mailbox file."""
        return os.path.join(self.MAIL_DIR, f"{player_name.lower()}.json")
    
    def load_player_mail(self, player_name: str) -> List[Mail]:
        """Load all mail for a player."""
        mailbox_path = self.get_player_mailbox_path(player_name)
        
        if not os.path.exists(mailbox_path):
            return []
        
        with open(mailbox_path, 'r') as f:
            mail_data = json.load(f)
        
        return [Mail(**data) for data in mail_data]
    
    def save_player_mail(self, player_name: str, mail_list: List[Mail]):
        """Save player's mail."""
        mailbox_path = self.get_player_mailbox_path(player_name)
        
        mail_data = [asdict(mail) for mail in mail_list]
        
        with open(mailbox_path, 'w') as f:
            json.dump(mail_data, f, indent=2)
    
    def send_mail(self, sender: str, recipients: List[str], cc: List[str], 
                  subject: str, body: str) -> bool:
        """Send mail to recipients."""
        mail = Mail(
            id=self.next_mail_id,
            sender=sender,
            recipients=recipients,
            cc=cc,
            subject=subject,
            body=body,
            timestamp=time.time(),
            read=False
        )
        
        self.next_mail_id += 1
        self.save_next_id()
        
        # Deliver to all recipients
        all_recipients = recipients + cc
        for recipient in all_recipients:
            # Check if player exists
            player_file = os.path.join("lib/players", f"{recipient.lower()}.py")
            if not os.path.exists(player_file):
                continue
            
            # Load recipient's mail
            mail_list = self.load_player_mail(recipient)
            mail_list.append(mail)
            
            # Save mail
            self.save_player_mail(recipient, mail_list)
            
            # Notify if online
            for player in self.game_state.list_players():
                if player.name.lower() == recipient.lower():
                    player.message(f"\nYou have new mail from {sender}!")
                    break
        
        return True
    
    def get_unread_count(self, player_name: str) -> int:
        """Get count of unread mail."""
        mail_list = self.load_player_mail(player_name)
        return sum(1 for mail in mail_list if not mail.read)
    
    def get_unread_summary(self, player_name: str) -> Optional[str]:
        """Get summary of unread mail for finger."""
        mail_list = self.load_player_mail(player_name)
        unread = [mail for mail in mail_list if not mail.read]
        
        if not unread:
            return "No unread mail"
        
        # Get date of oldest unread
        oldest = min(unread, key=lambda m: m.timestamp)
        date_str = time.strftime("%b %d", time.localtime(oldest.timestamp))
        
        return f"Unread mail from {date_str}"
    
    def list_mail(self, player_name: str, show_all: bool = False) -> List[str]:
        """List mail for player."""
        mail_list = self.load_player_mail(player_name)
        
        if not show_all:
            mail_list = [m for m in mail_list if not m.read]
        
        if not mail_list:
            return ["No mail to display."]
        
        output = ["ID  From            Subject                    Date"]
        output.append("-" * 60)
        
        for mail in sorted(mail_list, key=lambda m: m.timestamp, reverse=True):
            status = " " if mail.read else "*"
            date_str = time.strftime("%m/%d", time.localtime(mail.timestamp))
            subject = mail.subject[:25] + "..." if len(mail.subject) > 25 else mail.subject
            
            output.append(f"{status}{mail.id:<3} {mail.sender:<15} {subject:<25} {date_str}")
        
        return output
    
    def read_mail(self, player_name: str, mail_id: int) -> Optional[str]:
        """Read a specific mail."""
        mail_list = self.load_player_mail(player_name)
        
        for mail in mail_list:
            if mail.id == mail_id:
                # Mark as read
                mail.read = True
                self.save_player_mail(player_name, mail_list)
                
                # Format mail
                output = []
                output.append(f"From: {mail.sender}")
                output.append(f"To: {', '.join(mail.recipients)}")
                if mail.cc:
                    output.append(f"Cc: {', '.join(mail.cc)}")
                output.append(f"Date: {time.strftime('%Y-%m-%d %H:%M', time.localtime(mail.timestamp))}")
                output.append(f"Subject: {mail.subject}")
                output.append("-" * 40)
                output.append(mail.body)
                
                return "\n".join(output)
        
        return None
    
    def delete_mail(self, player_name: str, mail_id: int) -> bool:
        """Delete a mail."""
        mail_list = self.load_player_mail(player_name)
        
        for i, mail in enumerate(mail_list):
            if mail.id == mail_id:
                mail_list.pop(i)
                self.save_player_mail(player_name, mail_list)
                return True
        
        return False

class MailComposer:
    """Helper for composing mail."""
    
    def __init__(self, sender: str):
        self.sender = sender
        self.recipients = []
        self.cc = []
        self.subject = ""
        self.body_lines = []
        self.state = "RECIPIENTS"
    
    def add_recipient(self, name: str):
        """Add a recipient."""
        if name not in self.recipients:
            self.recipients.append(name)
    
    def add_cc(self, name: str):
        """Add a CC recipient."""
        if name not in self.cc:
            self.cc.append(name)
    
    def set_subject(self, subject: str):
        """Set the subject."""
        self.subject = subject
    
    def add_body_line(self, line: str):
        """Add a line to the body."""
        self.body_lines.append(line)
    
    def get_body(self) -> str:
        """Get the complete body."""
        return "\n".join(self.body_lines)
    
    def is_complete(self) -> bool:
        """Check if mail is ready to send."""
        return bool(self.recipients and self.subject and self.body_lines)