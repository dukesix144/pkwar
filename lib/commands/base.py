"""Base class for command modules."""

class BaseCommand:
    """Base class for all command modules."""
    
    def __init__(self, game_state):
        """Initialize with game state reference."""
        self.game_state = game_state
        self.rooms = game_state.rooms
        
    def get_player_room(self, player):
        """Get the room object for a player's location."""
        return self.rooms.get(player._location)
    
    def get_room_players(self, player, include_self=True):
        """Get all players in the same room."""
        room = self.get_player_room(player)
        if not room:
            return []
        
        players = []
        for uuid, entity in room.inventory.get_items():
            if hasattr(entity, 'is_player') and entity.is_player:
                if include_self or entity != player:
                    players.append(entity)
        return players
    
    def broadcast_to_room(self, player, message, include_self=False):
        """Send a message to all players in the room."""
        room = self.get_player_room(player)
        if not room:
            return
            
        for uuid, entity in room.inventory.get_items():
            if hasattr(entity, 'message') and entity != player:
                entity.message(message)
        
        if include_self:
            player.message(message)
    
    def find_player_by_name(self, name):
        """Find an online player by name."""
        for p in self.game_state.list_players():
            if p.name.lower() == name.lower():
                return p
        return None
    
    def find_target_in_room(self, player, target_name):
        """Find a target player in the same room."""
        room = self.get_player_room(player)
        if not room:
            return None
            
        for uuid, entity in room.inventory.get_items():
            if (hasattr(entity, 'name') and 
                entity.name.lower() == target_name.lower() and
                hasattr(entity, 'is_player') and entity.is_player):
                return entity
        return None