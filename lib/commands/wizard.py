"""Wizard/Implementor commands."""

from .base import BaseCommand
import os
import time
import json

class WizardCommands(BaseCommand):
    """Commands for implementors/wizards."""
    
    def wiz_goto(self, player, params=None):
        """goto <room/player> - Teleport to a room or player (implementors only)"""
        if player.implementor_level == 0:
            player.message("Huh?")
            return
        
        if not params:
            player.message("Goto where?")
            return
        
        # Try to find a player first
        target_player = self.find_player_by_name(params)
        
        if target_player:
            # Goto player
            destination = target_player._location
            player.message(f"Going to {target_player.name} at {destination}.")
        else:
            # Check if room exists
            if params not in self.rooms:
                player.message(f"No such room or player: {params}")
                return
            destination = params
        
        # Announce departure
        self.broadcast_to_room(player, f"{player.name} vanishes in a puff of smoke!")
        
        # Move
        player.move(destination)
        
        # Announce arrival
        self.broadcast_to_room(player, f"{player.name} appears in a puff of smoke!")

    def wiz_trans(self, player, params=None):
        """trans <player> - Transport player to you (implementors only)"""
        if player.implementor_level == 0:
            player.message("Huh?")
            return
        
        if not params:
            player.message("Transport who?")
            return
        
        # Find target
        target = self.find_player_by_name(params)
        
        if not target:
            player.message(f"Player '{params}' not found.")
            return
        
        if target == player:
            player.message("You're already here!")
            return
        
        # Announce to target's room
        target_room = self.get_player_room(target)
        for uuid, item in target_room.inventory.get_items():
            if hasattr(item, 'message') and item != target:
                item.message(f"{target.name} vanishes in a puff of smoke!")
        
        # Move target
        target.move(player._location)
        target.message(f"{player.name} has transported you!")
        
        # Announce arrival
        self.broadcast_to_room(player, f"{target.name} appears in a puff of smoke!")

    def wiz_load(self, player, params=None):
        """load <file> - Load a file (implementors only)"""
        if player.implementor_level == 0:
            player.message("Huh?")
            return
        
        if not params:
            player.message("Load what file?")
            return
        
        # Check implementor level for permissions
        if player.implementor_level == 1:
            # Level 1 can only load from their own directory
            if not params.startswith(f"wizrooms/{player.name.lower()}/"):
                player.message("You can only load files from your own directory.")
                return
        elif player.implementor_level < 3:
            # Level 2 can't load from main directories
            if params.startswith(("lib/models/", "lib/", "server/")):
                player.message("You don't have permission to load system files.")
                return
        
        # Try to load the file
        filepath = f"lib/{params}"
        if not filepath.endswith('.py'):
            filepath += '.py'
        
        if not os.path.exists(filepath):
            player.message(f"File not found: {filepath}")
            return
        
        try:
            # Reload room if it's a room file
            if 'rooms' in filepath or 'areas' in filepath:
                room_name = os.path.basename(filepath)[:-3]  # Remove .py
                if hasattr(self.game_state, 'room_loader'):
                    if self.game_state.room_loader.reload_room(room_name):
                        player.message(f"Successfully loaded {filepath}")
                    else:
                        player.message(f"Failed to load {filepath}")
                else:
                    player.message("Room loader not available.")
            else:
                player.message(f"Loading of {filepath} not implemented yet.")
        except Exception as e:
            player.message(f"Error loading file: {str(e)}")
            
            # Log to wizard's debug file
            debug_file = f"lib/wizrooms/{player.name.lower()}/debug.log"
            os.makedirs(os.path.dirname(debug_file), exist_ok=True)
            with open(debug_file, 'a') as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Load error in {filepath}: {str(e)}\n")

    def wiz_dest(self, player, params=None):
        """dest <object> - Destroy an object (implementors only)"""
        if player.implementor_level == 0:
            player.message("Huh?")
            return
        
        if not params:
            player.message("Destroy what?")
            return
        
        # Find item in player's inventory
        item = player.inventory.get_item(params)
        if item:
            player.inventory.remove_item(item)
            player.message(f"You destroy {item.name}.")
            return
        
        # Find item in room
        room = self.get_player_room(player)
        for uuid, entity in room.inventory.get_items():
            if hasattr(entity, 'name') and entity.name.lower() == params.lower():
                room.inventory.remove_item(entity)
                player.message(f"You destroy {entity.name}.")
                
                # Announce to room
                self.broadcast_to_room(player, f"{player.name} destroys {entity.name}.")
                return
        
        player.message(f"Can't find '{params}' to destroy.")

    def wiz_clone(self, player, params=None):
        """clone <object> - Clone an object (implementors only)"""
        if player.implementor_level == 0:
            player.message("Huh?")
            return
        
        if not params:
            player.message("Clone what?")
            return
        
        # Try to create object from template
        if hasattr(self.game_state, 'object_loader'):
            obj = self.game_state.object_loader.create_object(params)
            if obj:
                player.inventory.add_item(obj)
                player.message(f"You clone {obj.name}.")
                return
        
        player.message(f"Can't find template for '{params}'.")

    def wizhelp(self, player, params=None):
        """wizhelp - Show implementor commands"""
        if player.implementor_level == 0:
            player.message("Huh?")
            return
        
        output = ["=== Implementor Commands ==="]
        output.append("goto <room/player> - Teleport to a room or player")
        output.append("trans <player> - Transport player to you")
        output.append("load <file> - Load a code file")
        output.append("dest <object> - Destroy an object")
        output.append("clone <object> - Clone an object")
        
        if player.implementor_level >= 3:
            output.append("\nLevel 3+ Commands:")
            output.append("shutdown - Shutdown the mud")
            output.append("reboot - Reboot the mud")
        
        if player.implementor_level >= 5:
            output.append("\nLevel 5+ Commands:")
            output.append("promote <player> <level> - Promote implementor")
        
        output.append("\nYour wizard directory: /wizrooms/" + player.name.lower() + "/")
        output.append("Debug log: /wizrooms/" + player.name.lower() + "/debug.log")
        
        player.message("\n".join(output))

    def promote(self, player, params=None):
        """promotemenow - Become an implementor (level 10+ only)"""
        if player.level < 10:
            player.message("You must be level 10 to become an implementor.")
            return
        
        if player.implementor_level > 0:
            player.message("You are already an implementor!")
            return
        
        # Promote to implementor level 1
        player.implementor_level = 1
        player.message("Congratulations! You are now a Level 1 Implementor!")
        player.message(f"Your wizard directory has been created: /wizrooms/{player.name.lower()}/")
        player.message("See 'wizhelp' for available commands.")
        
        # Create wizard directory
        wiz_dir = f"lib/wizrooms/{player.name.lower()}"
        os.makedirs(wiz_dir, exist_ok=True)
        
        # Create default workroom
        workroom_code = f'''"""Workroom for {player.name}"""

from lib.models.entity import Room, Exit
from lib.models.enums import ExitType

def load():
    return Room(
        name='{player.name.lower()}_workroom',
        description="""{player.name}'s Workroom
        
This is your personal workspace. From here you can create and test
new rooms, objects, and code. Use 'load' to load your creations.

A door leads back to the wizard room.""",
        exits=[
            Exit(
                name='out',
                description='Back to the wizard room.',
                destination='wizroom_main',
                exit_type=ExitType.DOOR
            )
        ]
    )
'''
        
        with open(f"{wiz_dir}/workroom.py", 'w') as f:
            f.write(workroom_code)
        
        # Save player data
        self.game_state.auth._save_player(player)
        
        # Announce to other wizards
        self.game_state.channel_manager.send_to_channel('wiz', player, 
            f"{player.name} has been promoted to Implementor Level 1!")

    def link_enforcer(self, player, params=None):
        """link <character> - Link an enforcer character"""
        if player.implementor_level == 0:
            player.message("Only implementors can link enforcer characters.")
            return
        
        if not params:
            player.message("Link which character?")
            return
        
        if player.linked_enforcer:
            player.message(f"You already have a linked enforcer: {player.linked_enforcer}")
            return
        
        # Check if character exists
        char_file = f"lib/players/{params.lower()}.py"
        if not os.path.exists(char_file):
            player.message(f"Character '{params}' does not exist.")
            return
        
        # Check if character is already linked
        with open(char_file, 'r') as f:
            char_data = json.load(f)
        
        if char_data.get('linked_enforcer'):
            player.message(f"Character '{params}' is already linked to someone else.")
            return
        
        # Link the characters
        player.linked_enforcer = params.capitalize()
        char_data['linked_enforcer'] = player.name
        
        # Save both files
        with open(char_file, 'w') as f:
            json.dump(char_data, f, indent=2)
        
        self.game_state.auth._save_player(player)
        
        player.message(f"Successfully linked enforcer character: {params.capitalize()}")
        player.message("This character will now appear as an Enforcer.")
                