"""Movement and navigation commands."""

from .base import BaseCommand

class MovementCommands(BaseCommand):
    """Commands for movement and looking around."""
    
    def show_brief_room(self, player):
        """Show brief room description (just name and exits)."""
        current_location = self.get_player_room(player)
        
        if not current_location:
            return
        
        # Get exits
        exits = [ex.name for ex in current_location.exits]
        exits_str = ",".join(exits) if exits else "none"
        
        # Format: Room Name (exits)
        if player.ansi_enabled and hasattr(player, 'ansi_manager'):
            # Show exits in yellow
            brief_output = f"{current_location.name} ({player.ansi_manager.yellow}{exits_str}{player.ansi_manager.reset})"
        else:
            brief_output = f"{current_location.name} ({exits_str})"
        
        player.message(brief_output)
        
        # Show players in room (excluding self)
        for uuid, item in current_location.inventory.get_items():
            if hasattr(item, 'is_player') and item.is_player:
                # Skip self - compare multiple ways to be sure
                if (item == player or 
                    (hasattr(item, 'uuid') and hasattr(player, 'uuid') and item.uuid == player.uuid) or
                    (hasattr(item, 'client_id') and hasattr(player, 'client_id') and item.client_id == player.client_id) or
                    (hasattr(item, 'name') and hasattr(player, 'name') and item.name == player.name and item is player)):
                    continue
                    
                display_name = item.get_display_name() if hasattr(item, 'get_display_name') else str(item.name)
                if display_name and display_name != 'None':
                    player.message(f"{display_name}.")
        
        # Show items in room
        for uuid, item in current_location.inventory.get_items():
            if not hasattr(item, 'is_player') or not item.is_player:
                if hasattr(item, 'get_display_name'):
                    item_name = item.get_display_name()
                elif hasattr(item, 'name'):
                    item_name = str(item.name)
                else:
                    item_name = None
                    
                if item_name and item_name != 'None':
                    player.message(f"{item_name}.")
    
    def look(self, player, params=None):
        """look - Examine your surroundings"""
        current_location = self.get_player_room(player)
        
        # Check if player has a valid location
        if not current_location:
            player.message("You are nowhere! Moving you to the entrance...")
            # Move player to entrance
            player.move('entrance')
            current_location = self.get_player_room(player)
            
            # If still no location, there's a bigger problem
            if not current_location:
                player.message("Error: Cannot find the entrance room. Please contact an admin.")
                return
        
        # Format room data for ANSI
        room_data = {
            'name': current_location.name.upper(),
            'description': current_location.description,
            'players': [],
            'objects': [],
            'exits': [ex.name for ex in current_location.exits]
        }
        
        # Get players in room (excluding self)
        for uuid, item in current_location.inventory.get_items():
            if hasattr(item, 'is_player') and item.is_player:
                # Skip self - compare multiple ways to be sure
                if (item == player or 
                    (hasattr(item, 'uuid') and hasattr(player, 'uuid') and item.uuid == player.uuid) or
                    (hasattr(item, 'client_id') and hasattr(player, 'client_id') and item.client_id == player.client_id) or
                    (hasattr(item, 'name') and hasattr(player, 'name') and item.name == player.name and item is player)):
                    continue
                    
                display_name = item.get_display_name() if hasattr(item, 'get_display_name') else str(item.name)
                if display_name and display_name != 'None':
                    room_data['players'].append(display_name)
        
        # Get items in room
        room_items = []
        for uuid, item in current_location.inventory.get_items():
            if not hasattr(item, 'is_player') or not item.is_player:
                if hasattr(item, 'get_display_name'):
                    item_name = item.get_display_name()
                elif hasattr(item, 'name'):
                    item_name = str(item.name)
                else:
                    item_name = None
                    
                # Only add non-None items
                if item_name and item_name != 'None':
                    room_items.append(item_name)
        
        if room_items:
            room_data['objects'] = room_items
        
        # Display with ANSI if enabled
        if player.ansi_enabled and hasattr(player, 'ansi_manager'):
            output = player.ansi_manager.format_room(room_data)
            player.message(output)
        else:
            # Plain text display
            player.message(room_data['name'])
            player.message(room_data['description'])
            if room_data['players']:
                for p in room_data['players']:
                    player.message(p)
            player.message("Exits: " + ", ".join(room_data['exits']))
            # Only show items if there are any
            if room_data.get('objects'):
                for obj in room_data['objects']:
                    player.message(obj)
    
    def glance(self, player, params=None):
        """glance - Quick look at the room"""
        # Glance always shows brief format regardless of brief mode setting
        self.show_brief_room(player)

    def go(self, player, params):
        """go <direction> - Move in a direction"""
        if not params:
            player.message("Go where?")
            return
        
        direction = params.lower()
        current_location = self.get_player_room(player)
        
        # Check if player has a valid location
        if not current_location:
            player.message("You must have a location before you can move!")
            return
        
        # Check if exit exists
        if not current_location.has_exit(direction):
            player.message(f"You can't go '{direction}'")
            return
        
        exit_obj = current_location.get_exit(direction)
        
        # Check if player can move through (ghosts can go through locked doors)
        if not player.can_move_through_door(exit_obj):
            player.message("That way is locked.")
            return
        
        # Handle following
        if player.following:
            player.following = None
            player.message("You stop following.")
        
        # Announce departure
        for uuid, item in current_location.inventory.get_items():
            if hasattr(item, 'is_player') and item.is_player and item != player:
                if player.is_ghost:
                    item.message(f"{player.get_display_name()} drifts {direction}.")
                else:
                    item.message(f"{player.name} leaves {direction}.")
        
        # Move player
        destination = exit_obj.destination
        player.move(destination)
        
        # Announce arrival
        new_location = self.rooms[destination]
        for uuid, item in new_location.inventory.get_items():
            if hasattr(item, 'is_player') and item.is_player and item != player:
                if player.is_ghost:
                    item.message(f"{player.get_display_name()} drifts in.")
                else:
                    item.message(f"{player.name} arrives.")
        
        # Handle followers
        for p in self.game_state.list_players():
            if getattr(p, 'following', None) == player and p._location == player._location:
                # They follow
                p.move(destination)
                p.message(f"You follow {player.name} {direction}.")
        
        # Show the new room based on brief setting
        if getattr(player, 'brief_mode', False):
            # Brief mode - show only short description and exits
            self.show_brief_room(player)
        else:
            # Full look
            self.look(player, None)
    
    # Direction shortcuts
    def north(self, player, params=None):
        """north - Move north"""
        self.go(player, "north")
    
    def south(self, player, params=None):
        """south - Move south"""
        self.go(player, "south")
    
    def east(self, player, params=None):
        """east - Move east"""
        self.go(player, "east")
    
    def west(self, player, params=None):
        """west - Move west"""
        self.go(player, "west")
    
    def up(self, player, params=None):
        """up - Move up"""
        self.go(player, "up")
    
    def down(self, player, params=None):
        """down - Move down"""
        self.go(player, "down")
    
    def northeast(self, player, params=None):
        """northeast - Move northeast"""
        self.go(player, "northeast")
    
    def northwest(self, player, params=None):
        """northwest - Move northwest"""
        self.go(player, "northwest")
    
    def southeast(self, player, params=None):
        """southeast - Move southeast"""
        self.go(player, "southeast")
    
    def southwest(self, player, params=None):
        """southwest - Move southwest"""
        self.go(player, "southwest")