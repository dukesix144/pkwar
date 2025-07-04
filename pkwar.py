#!/usr/bin/env python

"""PKMUD - A Player Killing MUD with LPMud feel
Main game loop and initialization
"""

import logging
import sys
import time
import os
from pathlib import Path

# Create lib directories if they don't exist
directories = [
    'lib/players',
    'lib/areas', 
    'lib/rooms',
    'lib/wizrooms',
    'lib/wiztools',
    'lib/help',
    'lib/wizhelp',
    'lib/inherits',
    'lib/logs',  # Add logs directory
    'lib/commands'  # Add commands directory for modular commands
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)

from mudserver import MudServer
from lib.constants import DEFAULT_START_LOCATION
from lib.command import Commands
from lib.models.game_state import GameState
from lib.models.player import Player
from lib.authentication import Authentication
from lib.war_system import WarSystem
from lib.channels import ChannelManager
from lib.ansi import AnsiManager
from lib.room_loader import RoomLoader
from lib.explorer_system import ExplorerSystem
from lib.object_loader import ObjectLoader

# Global dictionaries - initialize as empty
rooms = {}
object_templates = {}

# Initialize logging
log = logging.getLogger()

def init_logging():
    """Initialize logging with both console and file handlers."""
    # Create logs directory if it doesn't exist
    log_dir = Path("lib/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    
    # Console handler - less verbose
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # File handler - all logs
    file_handler = logging.FileHandler(log_dir / "pkmud.log", mode='a')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Error file handler - errors only
    error_handler = logging.FileHandler(log_dir / "error.log", mode='a')
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # Set root logger level
    root_logger.setLevel(logging.DEBUG)
    
    # Set specific logger levels to reduce noise
    logging.getLogger("mudserver").setLevel(logging.INFO)
    logging.getLogger("lib.room_loader").setLevel(logging.WARNING)
    
    # Log that logging is configured
    root_logger.info("Logging configured - logs will be written to lib/logs/")
    
    return root_logger

def init_game_data():
    """Initialize all game data (rooms and objects)."""
    global rooms, object_templates, game
    
    # Load rooms
    log.info("Loading rooms...")
    room_loader = RoomLoader()
    rooms = room_loader.load_all_rooms()
    game.room_loader = room_loader
    log.info(f"Loaded {len(rooms)} total rooms")
    
    # CRITICAL: Update game.rooms after loading!
    game.rooms = rooms
    log.info(f"DEBUG: game.rooms now has {len(game.rooms)} rooms")
    
    # Load objects
    log.info("Loading objects...")
    object_loader = ObjectLoader()
    object_templates = object_loader.load_all_objects()
    game.object_loader = object_loader
    game.object_templates = object_templates
    log.info(f"Loaded {len(object_templates)} object templates")

# Create game instance on port 2222
server = MudServer(port=2222)
game = GameState(server)
# Store game instance in server for access from player objects
server.game_instance = game

# Initialize subsystems
auth = Authentication(game)
war_system = WarSystem(game)
explorer_system = ExplorerSystem()
channel_manager = ChannelManager(game)

# Add subsystems to game state for access
game.auth = auth
game.war_system = war_system
game.channel_manager = channel_manager
game.explorer_system = explorer_system

# Commands will be initialized after game data is loaded
commands = None

# Override DEFAULT_START_LOCATION
DEFAULT_START_LOCATION = 'entrance'

def handle_new_player_events():
    """Handle new player connections."""
    for event in game.server.get_new_player_events():
        new_client = event.client
        # Let authentication system handle the new connection
        auth.handle_new_connection(new_client)
        log.info(f"New connection from {new_client.uuid}")

def handle_disconnected_players():
    """Handle player disconnections."""
    for event in game.server.get_disconnected_player_events():
        disconnected_client = event.client
        disconnected_player = game.find_player_by_client_id(disconnected_client.uuid)
        
        if disconnected_player and disconnected_player.name:
            # Save player data
            # End exploration session
            disconnected_player.end_exploration_session()
            
            auth._save_player(disconnected_player)
            
            # Mark as linkdead
            disconnected_player.linkdead = True
            auth.linkdead_players[disconnected_player.name.lower()] = disconnected_player
            
            # Handle based on ghost/alive state
            if disconnected_player.is_ghost:
                # Ghosts disappear from the room when linkdead
                if disconnected_player._location and disconnected_player._location in game.rooms:
                    room = game.rooms[disconnected_player._location]
                    room.inventory.remove_item(disconnected_player)
                    
                    # Announce ghost disappearance
                    for uuid, item in room.inventory.get_items():
                        if hasattr(item, 'is_player') and item.is_player:
                            item.message(f"{disconnected_player.get_display_name()} fades from existence.")
                
                log.info(f"Ghost {disconnected_player.name} went linkdead and disappeared")
            else:
                # Alive players become statues (stay in room)
                # Announce they've become a statue
                if disconnected_player._location and disconnected_player._location in game.rooms:
                    room = game.rooms[disconnected_player._location]
                    for uuid, item in room.inventory.get_items():
                        if hasattr(item, 'is_player') and item.is_player and item != disconnected_player:
                            item.message(f"{disconnected_player.name} has turned to stone!")
                
                log.info(f"Alive player {disconnected_player.name} went linkdead and became a statue")
            
            # General linkdead announcement
            for p in game.list_players():
                if p != disconnected_player:
                    p.message(f"{disconnected_player.name} has gone linkdead.")
        
        # Clean up auth state
        if disconnected_client.uuid in auth.pending_logins:
            del auth.pending_logins[disconnected_client.uuid]
        if disconnected_client.uuid in auth.login_attempts:
            del auth.login_attempts[disconnected_client.uuid]

def move_player_to_room(player, room_name):
    """Directly move a player to a room without using player.move()"""
    try:
        # Verify the room exists
        if room_name not in game.rooms:
            log.error(f"Room '{room_name}' not found in game.rooms!")
            return False
        
        # Remove from old room if applicable
        if hasattr(player, '_location') and player._location and player._location in game.rooms:
            old_room = game.rooms[player._location]
            if hasattr(old_room, 'inventory'):
                try:
                    old_room.inventory.remove_item(player)
                except:
                    pass  # Ignore if player wasn't in the room's inventory
        
        # Set new location
        player._location = room_name
        
        # Add to new room
        new_room = game.rooms[room_name]
        if hasattr(new_room, 'inventory'):
            new_room.inventory.add_item(player)
        
        # Track exploration
        if hasattr(player, 'visit_room'):
            player.visit_room(room_name)
        
        log.info(f"Successfully moved {player.name} to {room_name}")
        return True
        
    except Exception as e:
        log.error(f"Error in move_player_to_room: {e}", exc_info=True)
        return False

def handle_commands():
    """Process player commands."""
    for event in game.server.get_commands():
        client = event.client
        command = event.command
        params = event.params
        
        # Check if client is in login process
        if client.uuid in auth.pending_logins:
            # For authentication, we need to handle empty input specially
            if command == "" and params == "":
                # User just pressed Enter - pass empty string
                input_data = ""
            else:
                # Normal input - combine command and params
                input_data = command + (" " + params if params else "")
            
            log.debug(f"Authentication input from {client.uuid}: {repr(input_data)}")
            
            # Process the authentication input
            player = auth.process_input(client, input_data)
            
            if player:
                # Login complete, add to game
                game.add_player(player)
                
                # Set up ANSI manager
                player.ansi_manager = AnsiManager(player)
                
                # CRITICAL: Give player reference to game state
                player.game_state = game
                
                # Start exploration session
                player.start_exploration_session()
                
                # Announce arrival
                game.broadcast(f"{player.name} enters the game.")
                
                # Send welcome messages
                player.message(f"Welcome back, {player.name}!")
                player.message("Type 'help' for a list of commands.")
                
                # Ensure player has a valid location
                if not hasattr(player, '_location') or player._location is None:
                    log.warning(f"{player.name} has no location, setting to entrance")
                    player._location = 'entrance'
                
                # Debug info
                log.info(f"{player.name} current location: {player._location}")
                log.info(f"Total rooms available: {len(game.rooms)}")
                log.info(f"Entrance room exists: {'entrance' in game.rooms}")
                log.info(f"Warroom exists: {'warroom' in game.rooms}")
                
                # Move to appropriate location using direct method
                target_location = 'warroom' if player.is_ghost else DEFAULT_START_LOCATION
                
                # Use direct room movement instead of player.move()
                if not move_player_to_room(player, target_location):
                    # Fallback if move failed
                    log.error(f"Failed to move {player.name} to {target_location}")
                    if target_location != 'entrance':
                        # Try entrance as fallback
                        if not move_player_to_room(player, 'entrance'):
                            log.critical(f"Failed to move {player.name} to entrance!")
                            player._location = 'entrance'  # Force location anyway
                
                # Force a look command to show the room
                try:
                    commands.execute_command(player, 'look', '')
                except Exception as e:
                    log.error(f"Error executing look command for {player.name}: {e}")
                    player.message("Error displaying room. Type 'look' to see your surroundings.")
                
                log.info(f"{player.name} logged in successfully at location {player._location}")
            
            continue
        
        # Find player
        player = game.find_player_by_client_id(client.uuid)
        if not player:
            continue
        
        # Log command for debugging
        log.debug(f"{player.name} executed: {command} {params}")
        
        # Execute command
        try:
            commands.execute_command(player, command, params)
        except Exception as e:
            log.error(f"Error executing command '{command}' for {player.name}: {e}", exc_info=True)
            player.message("An error occurred while processing your command.")

def periodic_updates():
    """Handle periodic game updates."""
    current_time = time.time()
    
    # Update player ages
    for player in game.list_players():
        if hasattr(player, 'last_activity'):
            idle_time = current_time - player.last_activity
            if idle_time > 300:  # 5 minutes
                player.idle = True
            else:
                player.idle = False
    
    # Import random here to avoid circular import issues
    import random
    
    # Gerkin random messages
    if hasattr(war_system, 'state') and war_system.state == war_system.WarState.ACTIVE and war_system.gerkin_holder:
        if random.random() < 0.01:  # 1% chance per update
            messages = [
                "Gerkin whispers: 'The blood... I need more blood!'",
                "Gerkin cackles madly: 'Kill them all!'",
                "Gerkin mutters: 'So many wars... so much death...'",
                "Gerkin screams: 'DEATH! DEATH TO ALL!'"
            ]
            war_system.gerkin_holder.message(random.choice(messages))
    
    # Shop keeper messages
    if 'shop' in rooms and rooms['shop'].inventory.get_items():
        if random.random() < 0.005:  # 0.5% chance
            shop_messages = [
                "Gerkin mutters: 'They think they can win... fools!'",
                "Gerkin says: 'Buy my wares! You'll need them to survive!'",
                "Gerkin cackles: 'Another war coming... I can smell it!'",
                "Gerkin whispers: 'The spirit... it speaks to me...'"
            ]
            for uuid, entity in rooms['shop'].inventory.get_items():
                if isinstance(entity, Player):
                    entity.message(random.choice(shop_messages))

if __name__ == '__main__':
    # Initialize logging first
    init_logging()
    
    log.info("Starting PKMUD...")
    log.info(f"Python version: {sys.version}")
    log.info(f"Working directory: {os.getcwd()}")
    
    # Initialize game data (rooms and objects) - MUST be done before other initialization
    init_game_data()
    
    # Now initialize commands after game data is loaded
    commands = Commands(game)
    game.commands = commands
    
    log.info("PKMUD initialization complete")
    
    last_update = time.time()
    
    try:
        # Main game loop
        while True:
            # Small delay to prevent CPU spinning
            time.sleep(0.1)
            
            # Update server
            game.update()
            
            # Handle new connections
            handle_new_player_events()
            
            # Handle disconnections  
            handle_disconnected_players()
            
            # Handle commands
            handle_commands()
            
            # Periodic updates (every second)
            if time.time() - last_update > 1.0:
                periodic_updates()
                last_update = time.time()
                
    except KeyboardInterrupt:
        log.info("Shutdown signal received...")
        
        # Save all players
        for player in game.list_players():
            if player.name:
                auth._save_player(player)
                log.info(f"Saved {player.name}")
        
        # Shutdown server
        game.server.shutdown()
        
        log.info("PKMUD shutdown complete.")
        sys.exit(0)
    except Exception as e:
        log.critical(f"Fatal error in main loop: {e}", exc_info=True)
        raise