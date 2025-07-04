"""Authentication system for PKMUD."""

import hashlib
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime

from lib.models.player import Player
from lib.models.client import Client
import logging

log = logging.getLogger(__name__)


class Authentication:
    """Handles player authentication and character creation."""
    
    def __init__(self, game_state):
        self.game_state = game_state
        self.pending_logins: Dict[str, Dict[str, Any]] = {}
        self.linkdead_players: Dict[str, Player] = {}  # Add linkdead tracking
        self.login_attempts: Dict[str, int] = {}  # Add login attempts tracking
        
    def start_auth(self, client: Client) -> None:
        """Start the authentication process for a client."""
        log.info(f"Starting authentication for client {client.uuid}")
        
        # Initialize pending login data
        self.pending_logins[client.uuid] = {
            'state': 'ASK_NAME',
            'attempts': 0,
            'client': client  # Store client reference
        }
        
        # Send welcome message - simplified version
        self.game_state.server.send_message(client.uuid,
            "\r\nWelcome to pkmud.org 2222.\r\n\r\n")
        self.game_state.server.send_message(client.uuid, "Name: ")
        
    def handle_new_connection(self, client: Client) -> None:
        """Handle a new client connection - alias for start_auth."""
        self.start_auth(client)
        
    def process_input(self, client: Client, data: str) -> Optional[Player]:
        """Process input during authentication."""
        if client.uuid not in self.pending_logins:
            return None
            
        state = self.pending_logins[client.uuid]['state']
        
        # Log raw input for debugging
        log.debug(f"Auth process_input - state: {state}, raw data: {repr(data)}")
        
        # DON'T strip whitespace - pass it as-is to handlers
        # Individual handlers will decide how to process empty input
        
        if state == 'ASK_NAME':
            return self.handle_name_input(client, data.strip())  # Names need stripping
        elif state == 'ASK_CREATE':
            return self.handle_create_input(client, data)  # Don't strip - need to detect empty
        elif state == 'ASK_PASSWORD':
            return self.handle_password_input(client, data.strip())  # Passwords need stripping
        elif state == 'ASK_PASSWORD_REPEAT':
            return self.handle_password_repeat_input(client, data.strip())
        elif state == 'CHECK_PASSWORD':
            return self.handle_login_password(client, data.strip())
        elif state == 'ASK_GENDER':
            return self.handle_gender_input(client, data)  # Don't strip - need to detect empty
        elif state == 'ASK_EMAIL':
            return self.handle_email_input(client, data)  # Don't strip - need to detect empty
        elif state == 'ASK_REPLACE':
            return self.handle_replace_input(client, data)  # Handle replace connection prompt
            
        return None
        
    def handle_name_input(self, client: Client, name: str) -> Optional[Player]:
        """Handle character name input."""
        if not name:
            self.game_state.server.send_message(client.uuid, "Name: ")
            return None
            
        # Validate name
        if len(name) < 3 or len(name) > 12:
            self.game_state.server.send_message(client.uuid,
                "Names must be between 3 and 12 characters.\r\nName: ")
            return None
            
        if not name.isalpha():
            self.game_state.server.send_message(client.uuid,
                "Names can only contain letters.\r\nName: ")
            return None
            
        # Capitalize name
        name = name.capitalize()
        self.pending_logins[client.uuid]['name'] = name
        
        # Check if player exists
        player_file = f"lib/players/{name.lower()}.json"
        if os.path.exists(player_file):
            # Check if player is linkdead
            if name.lower() in self.linkdead_players:
                # Reconnect linkdead player
                player = self.linkdead_players[name.lower()]
                player.client = client
                player.client_id = client.uuid
                player.server = self.game_state.server
                player.linkdead = False  # No longer linkdead
                
                # If ghost, add them back to their room
                if player.is_ghost and player._location and player._location in self.game_state.rooms:
                    room = self.game_state.rooms[player._location]
                    room.inventory.add_item(player)
                    
                    # Announce ghost return
                    for uuid, item in room.inventory.get_items():
                        if hasattr(item, 'is_player') and item.is_player and item != player:
                            item.message(f"{player.get_display_name()} shimmers back into existence.")
                
                # If alive (statue), they just animate
                elif not player.is_ghost and player._location and player._location in self.game_state.rooms:
                    room = self.game_state.rooms[player._location]
                    # Announce statue coming back to life
                    for uuid, item in room.inventory.get_items():
                        if hasattr(item, 'is_player') and item.is_player and item != player:
                            item.message(f"The statue of {player.name} comes back to life!")
                
                # Remove from linkdead list
                del self.linkdead_players[name.lower()]
                
                # Clean up pending login
                del self.pending_logins[client.uuid]
                
                # Announce reconnection
                self.game_state.broadcast(f"{player.name} has reconnected.")
                
                log.info(f"Player {name} reconnected from linkdead state")
                return player
            else:
                # Check if player is already connected
                for existing_player in self.game_state.players.values():
                    if existing_player.name.lower() == name.lower():
                        # Player is already connected!
                        self.pending_logins[client.uuid]['existing_player'] = existing_player
                        self.pending_logins[client.uuid]['state'] = 'ASK_REPLACE'
                        self.game_state.server.send_message(client.uuid,
                            f"{name} is already connected. Replace connection? [Y/n]: ")
                        return None
                
                # Not currently connected, existing player - ask for password
                self.pending_logins[client.uuid]['state'] = 'CHECK_PASSWORD'
                self.game_state.server.send_message(client.uuid, "Password: ")
        else:
            # New player - ask if they want to create (default to NO)
            self.pending_logins[client.uuid]['state'] = 'ASK_CREATE'
            self.game_state.server.send_message(client.uuid,
                f"Character '{name}' does not exist. Create? [y/N]: ")
                
        return None
        
    def handle_replace_input(self, client: Client, response: str) -> Optional[Player]:
        """Handle response to replace connection prompt."""
        # Strip the response to check it
        response = response.strip()
        
        log.debug(f"handle_replace_input - response: {repr(response)}")
        
        # Check if response is 'n' or 'no' (case-insensitive)
        if response.lower() in ['n', 'no']:
            # User explicitly said no - deny login
            self.game_state.server.send_message(client.uuid,
                "Login denied. Goodbye.\r\n")
            self.game_state.server.disconnect_client(client.uuid)
            
            # Clean up pending login
            del self.pending_logins[client.uuid]
            return None
        else:
            # Empty response (""), 'y', 'yes', or anything else - default to YES
            # Continue to password check
            self.pending_logins[client.uuid]['state'] = 'CHECK_PASSWORD'
            self.game_state.server.send_message(client.uuid, "Password: ")
            return None
        
    def handle_create_input(self, client: Client, response: str) -> Optional[Player]:
        """Handle response to create character prompt."""
        # Strip the response to check it
        response = response.strip()
        
        log.debug(f"handle_create_input - response: {repr(response)}")
        
        # Check if response is 'y' or 'yes' (case-insensitive)
        if response.lower() in ['y', 'yes']:
            # User explicitly said yes - start character creation
            self.pending_logins[client.uuid]['state'] = 'ASK_PASSWORD'
            self.game_state.server.send_message(client.uuid, "Password: ")
        else:
            # Empty response ("") or anything other than yes - default to NO
            # This includes: "", "n", "no", or any other input
            self.pending_logins[client.uuid]['state'] = 'ASK_NAME'
            self.game_state.server.send_message(client.uuid, "Name: ")
            
        return None
        
    def handle_password_input(self, client: Client, password: str) -> Optional[Player]:
        """Handle new password input."""
        if not password:
            self.game_state.server.send_message(client.uuid,
                "Password cannot be empty.\r\nPassword: ")
            return None
            
        if len(password) < 4:
            self.game_state.server.send_message(client.uuid,
                "Password must be at least 4 characters.\r\nPassword: ")
            return None
            
        # Store password temporarily
        self.pending_logins[client.uuid]['password'] = password
        self.pending_logins[client.uuid]['state'] = 'ASK_PASSWORD_REPEAT'
        self.game_state.server.send_message(client.uuid, "Repeat password: ")
        
        return None
        
    def handle_password_repeat_input(self, client: Client, password: str) -> Optional[Player]:
        """Handle password confirmation."""
        stored_password = self.pending_logins[client.uuid].get('password')
        
        if password != stored_password:
            self.game_state.server.send_message(client.uuid,
                "Passwords don't match. Try again.\r\nPassword: ")
            self.pending_logins[client.uuid]['state'] = 'ASK_PASSWORD'
            return None
            
        # Passwords match - continue to gender
        self.pending_logins[client.uuid]['state'] = 'ASK_GENDER'
        self.game_state.server.send_message(client.uuid,
            "Gender [M/f]: ")
        
        return None
        
    def handle_gender_input(self, client: Client, gender: str) -> Optional[Player]:
        """Handle gender selection."""
        # Strip to check
        gender = gender.strip()
        
        log.debug(f"handle_gender_input - gender: {repr(gender)}")
        
        # Default to male if empty (just hit enter)
        if not gender or gender == "":
            gender = "male"
        else:
            # Check the input
            gender_lower = gender.lower()
            if gender_lower in ['f', 'female']:
                gender = 'female'
            else:
                # Everything else defaults to male (including 'm', 'male', or any other input)
                gender = 'male'
            
        self.pending_logins[client.uuid]['gender'] = gender
        self.pending_logins[client.uuid]['state'] = 'ASK_EMAIL'
        self.game_state.server.send_message(client.uuid,
            "Email address (press enter for none): ")
        
        return None
        
    def handle_email_input(self, client: Client, email: str) -> Optional[Player]:
        """Handle email input and create new player."""
        # Strip to check
        email = email.strip()
        
        log.debug(f"handle_email_input - email: {repr(email)}")
        
        # Default to "none" if empty (just hit enter)
        if not email or email == "":
            email = "none"
        else:
            # Also convert explicit "none" entry to "none"
            if email.lower() == "none":
                email = "none"
            
        self.pending_logins[client.uuid]['email'] = email
        
        # Get stored data
        name = self.pending_logins[client.uuid]['name']
        password = self.pending_logins[client.uuid]['password']
        gender = self.pending_logins[client.uuid]['gender']
        client = self.pending_logins[client.uuid]['client']
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Create player data - NEW PLAYERS START AS GHOSTS!
        player_data = {
            "name": name,
            "password": password_hash,
            "gender": gender,
            "email": email,
            "level": 1,
            "experience": 0,
            "health": 100,
            "max_health": 100,
            "sp_current": 200,
            "sp_max": 200,
            "coins": 100,
            "location": "warroom",  # Ghosts start in warroom
            "state": "ghost",  # NEW PLAYERS START AS GHOSTS
            "created": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat(),
            "kills": 0,
            "deaths": 0,
            "war_on": True,
            "explorer_rooms": [],
            "inventory": [],
            "equipment": {},
            "wimpy_percent": 30,
            "plan": "",
            "ansi_enabled": False,
            "ansi_vars": {},
            "war_history": [],
            "brief_mode": False,
            "show_mapping": False,
            "combat_brief": None,
            "monster_brief": False,
            "abilities": {
                "STRENGTH": 50,
                "DEXTERITY": 50,
                "WISDOM": 50,
                "INTELLIGENCE": 50,
                "CONSTITUTION": 50,
                "CHARISMA": 50
            }
        }
        
        # Save player file
        player_file = f"lib/players/{name.lower()}.json"
        os.makedirs(os.path.dirname(player_file), exist_ok=True)
        
        with open(player_file, 'w') as f:
            json.dump(player_data, f, indent=2)
            
        # Create player object with proper client/server references
        # CRITICAL: Don't pass location as both positional and keyword argument!
        # Remove both name and location from player_data_copy
        player_data_copy = player_data.copy()
        if 'name' in player_data_copy:
            del player_data_copy['name']
        if 'location' in player_data_copy:
            del player_data_copy['location']
            
        player = Player(
            name=name,
            client_id=client.uuid,
            location="warroom",  # Pass location as positional arg
            **player_data_copy  # Pass all other data as kwargs
        )
        
        # Set client and server references
        player.client = client
        player.server = self.game_state.server
        player.client_id = client.uuid
        
        # Clean up pending login
        del self.pending_logins[client.uuid]
        
        log.info(f"Created new player {name} as ghost in warroom")
        
        return player
        
    def handle_login_password(self, client: Client, password: str) -> Optional[Player]:
        """Handle password check for existing player."""
        name = self.pending_logins[client.uuid]['name']
        stored_client = self.pending_logins[client.uuid]['client']
        
        # Load player data
        player_file = f"lib/players/{name.lower()}.json"
        try:
            with open(player_file, 'r') as f:
                player_data = json.load(f)
        except:
            self.game_state.server.send_message(client.uuid,
                "Error loading player data.\r\nName: ")
            self.pending_logins[client.uuid]['state'] = 'ASK_NAME'
            return None
            
        # Check password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != player_data.get('password'):
            self.pending_logins[client.uuid]['attempts'] += 1
            
            if self.pending_logins[client.uuid]['attempts'] >= 3:
                # Too many attempts
                self.game_state.server.send_message(client.uuid,
                    "Too many failed attempts. Goodbye.\r\n")
                self.game_state.server.disconnect_client(client.uuid)
                return None
                
            self.game_state.server.send_message(client.uuid,
                "Incorrect password.\r\nPassword: ")
            return None
            
        # Password correct - check if we need to replace existing connection
        if 'existing_player' in self.pending_logins[client.uuid]:
            existing_player = self.pending_logins[client.uuid]['existing_player']
            
            # Disconnect the old connection
            log.info(f"Replacing existing connection for {name}")
            
            # Notify the old connection
            if existing_player.client:
                existing_player.message("You have been replaced by a new connection.")
                self.game_state.server.disconnect_client(existing_player.client_id)
                
            # Remove the old player from game state
            if existing_player.uuid in self.game_state.players:
                del self.game_state.players[existing_player.uuid]
                
            # Remove from room if they're in one
            if existing_player._location and existing_player._location in self.game_state.rooms:
                room = self.game_state.rooms[existing_player._location]
                room.inventory.remove_item(existing_player.uuid)
        
        # Create player object from saved data
        # Remove name and location from player_data since we're passing them separately
        player_data_copy = player_data.copy()
        if 'name' in player_data_copy:
            del player_data_copy['name']
        
        # Get location before deleting it
        saved_location = player_data_copy.get('location', 'warroom' if player_data.get('state') == 'ghost' else 'entrance')
        if 'location' in player_data_copy:
            del player_data_copy['location']
        
        player = Player(
            name=name,
            client_id=client.uuid,
            location=saved_location,  # Pass location as positional arg
            **player_data_copy  # Pass all other saved data
        )
        
        # Set client and server references
        player.client = stored_client
        player.server = self.game_state.server
        player.client_id = client.uuid
        
        # Update attributes that might have changed
        player.is_ghost = player.state == 'ghost'
        
        # Ensure name is set if it wasn't loaded properly
        if not player.name or player.name == 'None':
            player.name = name
        
        # Debug log to check what was loaded
        log.info(f"Loaded player data - name: {player.name}, state: {player.state}, is_ghost: {player.is_ghost}, coins: {getattr(player, 'coins', 'NO_COINS')}")
        
        # Update last login info for finger command
        player.last_login_info = {
            'time': datetime.now().isoformat(),
            'from': 'telnet'  # Could track IP if needed
        }
        
        # Update last login time
        player.last_login = datetime.now().timestamp()
        
        # Save updated login time
        player_data['last_login'] = datetime.now().isoformat()
        player_data['last_login_info'] = player.last_login_info
        with open(player_file, 'w') as f:
            json.dump(player_data, f, indent=2)
            
        # Clean up pending login
        del self.pending_logins[client.uuid]
        
        log.info(f"Player {name} logged in successfully at location {player.location}")
        
        return player
        
    def _save_player(self, player: Player) -> None:
        """Save player data to file."""
        if not player.name:
            return
            
        # Calculate total age
        total_age = player.age
        if hasattr(player, 'last_login'):
            total_age += (datetime.now().timestamp() - player.last_login)
            
        player_data = {
            "name": player.name,
            "password": getattr(player, 'password_hash', ''),
            "gender": getattr(player, 'gender', 'male'),
            "email": getattr(player, 'email', ''),
            "real_name": getattr(player, 'real_name', '???'),
            "level": player.level,
            "experience": getattr(player, 'xp', player.experience) if hasattr(player, 'experience') else 0,
            "health": getattr(player, 'current_hp', player.health) if hasattr(player, 'health') else 100,
            "max_health": player.max_hp if hasattr(player, 'max_hp') else 100,
            "sp_current": getattr(player, 'sp_current', 200),
            "sp_max": getattr(player, 'sp_max', 200),
            "coins": getattr(player, 'coins', 0),
            "location": player.location,
            "state": getattr(player, 'state', 'ghost'),  # Default to ghost
            "created": getattr(player, 'created_at', datetime.now().timestamp()),
            "last_login": datetime.now().isoformat(),
            "last_logout": datetime.now().isoformat(),
            "age": total_age,
            "kills": getattr(player, 'kills', 0),
            "deaths": getattr(player, 'deaths', 0),
            "best_kill": getattr(player, 'best_kill', None),
            "war_on": getattr(player, 'war_enabled', True),
            "explorer_rooms": list(getattr(player, 'rooms_explored', [])),
            "inventory": [],  # TODO: Serialize inventory
            "equipment": getattr(player, 'equipment', {}),
            "wimpy_percent": getattr(player, 'wimpy_percent', 30),
            "plan": getattr(player, 'plan', ''),
            "ansi_enabled": getattr(player, 'ansi_enabled', False),
            "ansi_vars": getattr(player, 'ansi_vars', {}),
            "war_history": getattr(player, 'war_history', []),
            "last_login_info": getattr(player, 'last_login_info', None),
            "alignment": getattr(player, 'alignment', 'neutral'),
            "race": getattr(player, 'race', 'Human'),
            "implementor_level": getattr(player, 'implementor_level', 0),
            "linked_enforcer": getattr(player, 'linked_enforcer', None),
            # Save brief/combat settings
            "brief_mode": getattr(player, 'brief_mode', False),
            "show_mapping": getattr(player, 'show_mapping', False),
            "combat_brief": getattr(player, 'combat_brief', None),
            "monster_brief": getattr(player, 'monster_brief', False),
            # Save abilities
            "abilities": getattr(player, 'abilities', {
                "STRENGTH": 50,
                "DEXTERITY": 50,
                "WISDOM": 50,
                "INTELLIGENCE": 50,
                "CONSTITUTION": 50,
                "CHARISMA": 50
            })
        }
        
        player_file = f"lib/players/{player.name.lower()}.json"
        with open(player_file, 'w') as f:
            json.dump(player_data, f, indent=2)
            
        log.debug(f"Saved player data for {player.name}")