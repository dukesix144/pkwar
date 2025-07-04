"""Explorer system commands."""

from .base import BaseCommand
import os
import json

class ExplorerCommands(BaseCommand):
    """Commands for the explorer system."""
    
    def explorer(self, player, params=None):
        """explorer - Show your exploration statistics"""
        # Get total rooms from game.rooms
        total_rooms = len(self.game_state.rooms) if hasattr(self.game_state, 'rooms') else 0
        
        explored = len(player.rooms_explored) if hasattr(player, 'rooms_explored') else 0
        percent = (explored / total_rooms * 100) if total_rooms > 0 else 0
        
        # Calculate rank
        rank = self._get_explorer_rank(percent)
        
        output = []
        output.append(f"You have visited {player.new_rooms_this_session} rooms this login.")
        output.append("")
        output.append("You have explored:")
        output.append(f"This login : {player.new_rooms_this_session} rooms.")
        output.append(f"Lifetime : {explored} of {total_rooms} rooms ({percent:.3f}%)")
        output.append(f"Rank: {rank}")
        
        if player.new_rooms_this_session > 0:
            # Show when last new room was found this session
            output.append(f"Last new room found this login.")
        
        player.message("\n".join(output))

    def explorers(self, player, params=None):
        """explorers - Show top explorers"""
        # Get total rooms from game.rooms
        total_rooms = len(self.game_state.rooms) if hasattr(self.game_state, 'rooms') else 0
        
        output = []
        output.append("@" + "-" * 58 + "@")
        output.append("| PKWAR Top Explorers                                     |")
        output.append(f"| Total Rooms: {total_rooms:<43} |")
        output.append("@" + "-" * 58 + "@")
        output.append(f"{'Rank':<6} {'Name':<20} {'Rooms':<10} {'Percent':<10} {'Status':<10}")
        output.append("-" * 60)
        
        # Gather explorer data from all players
        explorer_data = []
        
        # Check online players
        for p in self.game_state.list_players():
            if hasattr(p, 'rooms_explored'):
                explored = len(p.rooms_explored)
                if explored > 0:
                    explorer_data.append((p.name, explored, True))
        
        # Check offline players
        player_dir = "lib/players"
        if os.path.exists(player_dir):
            for filename in os.listdir(player_dir):
                if filename.endswith('.json'):
                    name = filename[:-5]  # Remove .json extension
                    # Skip online players
                    if any(p.name and p.name.lower() == name for p in self.game_state.list_players()):
                        continue
                    
                    # Load player data
                    try:
                        with open(os.path.join(player_dir, filename), 'r') as f:
                            data = json.load(f)
                        explored = len(data.get('explorer_rooms', []))
                        if explored > 0:
                            explorer_data.append((data['name'], explored, False))
                    except Exception as e:
                        # Skip files that can't be loaded
                        pass
        
        # Sort by rooms explored (descending)
        explorer_data.sort(key=lambda x: x[1], reverse=True)
        
        # Display top 20
        for i, (name, rooms_explored, online) in enumerate(explorer_data[:20], 1):
            percent = (rooms_explored / total_rooms * 100) if total_rooms > 0 else 0
            status = "ON" if online else ""
            
            # Highlight current player
            if player.name and name.lower() == player.name.lower():
                output.append(f"{i:<6} {name:<20} {rooms_explored:<10} {percent:>6.1f}%     {status} *")
            else:
                output.append(f"{i:<6} {name:<20} {rooms_explored:<10} {percent:>6.1f}%     {status}")
        
        if not explorer_data:
            output.append("No exploration data available.")
        
        # Show player's own stats if not in top 20
        player_rooms = len(player.rooms_explored) if hasattr(player, 'rooms_explored') else 0
        player_found = False
        
        for name, _, _ in explorer_data[:20]:
            if player.name and name.lower() == player.name.lower():
                player_found = True
                break
        
        if not player_found and player_rooms > 0:
            percent = (player_rooms / total_rooms * 100) if total_rooms > 0 else 0
            output.append("-" * 60)
            output.append(f"Your rank: {player.name:<17} {player_rooms:<10} {percent:>6.1f}%")
        
        output.append("@" + "-" * 58 + "@")
        
        player.message("\n".join(output))
    
    def arealist(self, player, params=None):
        """arealist - List all available areas"""
        areas_dir = "lib/areas"
        if not os.path.exists(areas_dir):
            player.message("No areas directory found.")
            return
        
        areas = []
        area_info = {}
        
        for item in os.listdir(areas_dir):
            item_path = os.path.join(areas_dir, item)
            if (os.path.isdir(item_path) and 
                not item.startswith('.')):
                areas.append(item)
                
                # Count rooms in this area from game.rooms
                room_count = 0
                if hasattr(self.game_state, 'rooms'):
                    for room_name in self.game_state.rooms:
                        # Check if room belongs to this area
                        if room_name.startswith(f"{item}_") or room_name.startswith(f"area_{item}_"):
                            room_count += 1
                
                area_info[item] = room_count
        
        if not areas:
            player.message("No custom areas have been created yet.")
            player.message("Implementors can create areas in /areas/<areaname>/")
            return
        
        output = []
        output.append("=== Available Areas ===")
        output.append("(These areas connect to various backbone rooms)")
        output.append("")
        
        # Special handling for backbone
        if 'backbone' in areas:
            backbone_rooms = sum(1 for r in self.game_state.rooms if r.startswith('backbone_'))
            output.append(f"{'backbone':<20} ({backbone_rooms} rooms) - Main highway")
            areas.remove('backbone')
        
        # Display other areas
        for area in sorted(areas):
            room_count = area_info.get(area, 0)
            output.append(f"{area:<20} ({room_count} rooms)")
        
        output.append("")
        output.append("Use 'explorer' to see your exploration progress.")
        output.append("Use 'explorers' to see the top explorers.")
        output.append("Areas are created by implementors and connect to the backbone.")
        
        player.message("\n".join(output))
    
    def _get_explorer_rank(self, percent):
        """Get explorer rank based on percentage explored."""
        if percent >= 100:
            return "Master Explorer"
        elif percent >= 90:
            return "Grand Explorer"
        elif percent >= 75:
            return "Expert Explorer"
        elif percent >= 50:
            return "Veteran Explorer"
        elif percent >= 25:
            return "Seasoned Explorer"
        elif percent >= 10:
            return "Explorer"
        elif percent >= 5:
            return "Wanderer"
        elif percent >= 1:
            return "Tourist"
        else:
            return "Newbie"