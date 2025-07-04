from abc import ABC
import time
import json
import logging
from datetime import datetime

from lib.models.creature import Creature
from lib.inventory import InventoryManager

log = logging.getLogger(__name__)

class Player(Creature, ABC):
    """A connected player."""

    def __init__(self, name=None, client_id=None, location="entrance", **kwargs):
        # Mark this as a player so movement/look logic can skip it
        self.is_player = True
        """Initialize player with flexible parameters."""
        # Handle the two initialization patterns:
        # 1. From authentication: Player(name="X", client_id="Y", location="Z")
        # 2. Legacy: Player(client, server, creature)
        
        # Check if this is legacy initialization
        if hasattr(name, 'uuid'):  # name is actually a client object
            # Legacy initialization
            client = name
            server = client_id
            creature = location if location != "entrance" else None
            
            self.client = client
            self.server = server
            self.client_id = client.uuid if client else None
        else:
            # New initialization from authentication
            self.client = None
            self.server = None
            self.client_id = client_id
            creature = None
        
        # Player-specific attributes
        self.gender = kwargs.get('gender', 'male')
        self.email = kwargs.get('email', '')
        self.real_name = kwargs.get('real_name', '???')  # For finger
        self.password_hash = kwargs.get('password', '')
        
        # Spell points
        self.sp_max = kwargs.get('sp_max', 200)
        self.sp_current = kwargs.get('sp_current', 200)
        
        # Economy
        self.coins = kwargs.get('coins', 100)
        
        # Ghost/War system
        self.state = kwargs.get('state', 'ghost')  # DEFAULT TO GHOST
        self.is_ghost = self.state == 'ghost'
        self.war_enabled = kwargs.get('war_on', True)
        self.war_class = None  # Fighter, Kamikaze, Mage, Hunter, None
        self.team = None  # For team wars
        
        # Stats
        self.kills = kwargs.get('kills', 0)
        self.deaths = kwargs.get('deaths', 0)
        self.best_kill = kwargs.get('best_kill', None)
        self.best_solo = None
        self.rooms_explored = set(kwargs.get('explorer_rooms', []))
        self.new_rooms_this_session = 0
        self.exploration_session_id = None  # For SQLite tracking
        
        # War history
        self.war_history = kwargs.get('war_history', [])  # List of war participation records
        
        # Implementor system
        self.implementor_level = kwargs.get('implementor_level', 0)
        self.linked_enforcer = kwargs.get('linked_enforcer', None)  # Name of linked enforcer character
        
        # Timing - Convert string timestamps to float
        self.created_at = kwargs.get('created', time.time())
        if isinstance(self.created_at, str):
            try:
                # Try to parse ISO format first
                self.created_at = datetime.fromisoformat(self.created_at).timestamp()
            except:
                self.created_at = time.time()
        
        self.last_login = kwargs.get('last_login', time.time())
        if isinstance(self.last_login, str):
            try:
                # Try to parse ISO format first
                self.last_login = datetime.fromisoformat(self.last_login).timestamp()
            except:
                self.last_login = time.time()
                
        self.age = kwargs.get('age', 0)  # Total play time in seconds
        self.last_activity = time.time()  # For idle detection
        self.last_logout = kwargs.get('last_logout', None)
        self.last_login_info = kwargs.get('last_login_info', None)  # For finger command
        
        # Linkdead status
        self.linkdead = False
        
        # Combat
        self.wimpy_percent = kwargs.get('wimpy_percent', 30)  # Default 30%
        self.has_gerkin = False
        self.blood_inventory = []  # List of player names whose blood we carry
        self.following = None  # Who we're following
        self.wielded_weapon = None  # Current weapon
        
        # Inventory system
        self.inventory = kwargs.get('inventory', [])
        if not isinstance(self.inventory, list):
            self.inventory = InventoryManager(self)
        else:
            self.inventory = InventoryManager(self)
        
        # Equipment
        self.equipment = kwargs.get('equipment', {})
        
        # Social
        self.plan = kwargs.get('plan', '')  # One-line plan for finger
        self.watched_by = set()  # Players watching this player
        self.watching = set()  # Players this player is watching
        self.watching_war = False  # Watching war from observation room
        
        # Channels
        self.channels_on = {
            'say': True,
            'tell': True,
            'shout': True,
            'ghost': True,
            'wiz': False,  # Only for implementors
            'team': True,
            'newbie': True,
            'gossip': True
        }
        
        # ANSI settings - CHANGED: Default to enabled
        self.ansi_enabled = kwargs.get('ansi_enabled', True)  # CHANGED: Default True
        self.ansi_vars = kwargs.get('ansi_vars', {})
        self.ansi_manager = None
        
        # Brief mode settings - LOAD FROM SAVED DATA
        self.brief_mode = kwargs.get('brief_mode', False)
        self.show_mapping = kwargs.get('show_mapping', False)
        self.combat_brief = kwargs.get('combat_brief', None)
        self.monster_brief = kwargs.get('monster_brief', False)
        
        # Special modes
        self.mail_mode = None
        self.chfn_mode = False
        self.selecting_class = False
        
        # Default abilities - CHANGED TO 50!
        default_abilities = {
            'STRENGTH': 50,
            'DEXTERITY': 50,
            'WISDOM': 50,
            'INTELLIGENCE': 50,
            'CONSTITUTION': 50,
            'CHARISMA': 50
        }

        # Determine initialization values
        if creature:
            super().__init__(
                creature.name,
                creature.description,
                creature.character_class,
                creature.level,
                creature.background,
                creature.race,
                creature.alignment,
                creature.xp,
                creature.abilities,
                creature.skills,
                creature.max_hp, 
                creature.armor_class,
                creature.hd_value,
                creature.hd_total,
                creature.inventory
            )
        else:
            # Initialize with defaults or kwargs
            # CRITICAL: name must be first positional argument for Creature
            player_name = name if name and isinstance(name, str) else kwargs.get('name', 'Unknown')
            
            # Debug log
            log.info(f"Creating player with name: {player_name}, kwargs contains: {list(kwargs.keys())}")
            
            super().__init__(
                player_name,  # First positional argument
                "A mysterious figure",
                "Adventurer",
                kwargs.get('level', 1),
                "Unknown",
                kwargs.get('race', 'Human'),
                kwargs.get('alignment', 'neutral'),
                kwargs.get('experience', kwargs.get('xp', 0)),
                kwargs.get('abilities', default_abilities),
                [],
                kwargs.get('max_health', kwargs.get('max_hp', 100)),
                10,
                1,
                1,
                None
            )
            
            # Ensure name is set
            if not hasattr(self, 'name') or not self.name:
                self.name = player_name
                
            # Set current HP from saved data
            self.current_hp = kwargs.get('health', kwargs.get('current_hp', self.max_hp))
            self.health = self.current_hp  # Alias for compatibility
            
        # Set location - ghosts start in warroom
        if isinstance(location, str):
            self._location = location
        else:
            # Default location based on state
            if self.is_ghost:
                self._location = kwargs.get('location', 'warroom')
            else:
                self._location = kwargs.get('location', 'entrance')
        
        # Handle level properly - regular players can't be above 100
        saved_level = kwargs.get('level', 1)
        if saved_level > 100:
            self.implementor_level = saved_level - 100  # Store implementor level
            self.level = 1  # Reset regular level
        elif not self.implementor_level:
            self.level = saved_level

    @property
    def uuid(self):
        """Get the player's UUID - prefer client_id if available."""
        if self.client_id:
            return self.client_id
        # Fall back to the UUID set by Entity.__init__
        return getattr(self, '_uuid_backup', None)
    
    @uuid.setter
    def uuid(self, value):
        """Set the UUID - store it as backup since we prefer client_id."""
        self._uuid_backup = value

    @property
    def location(self):
        """Get the player's location."""
        return self._location

    @location.setter
    def location(self, value):
        """Set the player's location."""
        self._location = value

    def message(self, message):
        """Send a message to this player."""
        if self.server and self.client and hasattr(self.client, 'uuid'):
            self.server.send_message(self.client.uuid, message)
        else:
            # Player has no active connection
            log.debug(f"Cannot send message to {self.name} - no active client connection")

    def move(self, destination):
        """Move player to a new room."""
        # Get rooms from game state if available
        rooms = None
        game = None
        
        # Try to get rooms from server's game instance
        if self.server and hasattr(self.server, 'game_instance'):
            game = self.server.game_instance
            if hasattr(game, 'rooms'):
                rooms = game.rooms
        
        # If no rooms available, we can't move
        if not rooms:
            self._location = destination
            return
        
        # Remove from old room if in one
        if self._location and self._location in rooms:
            rooms[self._location].inventory.remove_item(self)
        
        # Track exploration with explorer system
        if game and hasattr(game, 'explorer_system') and self.exploration_session_id:
            # Only track non-arena rooms
            if not destination.startswith('arena_'):
                is_new = game.explorer_system.record_room_visit(
                    self.name, 
                    destination, 
                    self.exploration_session_id
                )
                
                if is_new:
                    self.new_rooms_this_session += 1
                    self.rooms_explored.add(destination)
                    
                    # Check for money in rooms (only RandomRoom subclasses)
                    if destination in rooms and hasattr(rooms[destination], 'check_for_money'):
                        room = rooms[destination]
                        # Only generate money if it's a RandomRoom (not backbone, warroom, etc)
                        if (hasattr(room, '__class__') and 
                            room.__class__.__name__ == 'RandomRoom' and
                            not destination.startswith('backbone_')):
                            coins = room.check_for_money()
                            if coins > 0:
                                self.message("You disturb large piles of dust....")
                                self.coins += coins
                                self.message(f"You found {coins} coins!")
        
        # Move to new location
        self._location = destination
        if destination in rooms:
            rooms[destination].inventory.add_item(self)
        
        # If ghost, show special message
        if self.is_ghost:
            self.message("You drift ethereally through the area.")
    
    def can_move_through_door(self, exit_obj):
        """Check if player can move through a door/exit."""
        if self.is_ghost:
            return True  # Ghosts can move through locked doors
        return not getattr(exit_obj, 'locked', False)
    
    def die(self):
        """Handle player death during war."""
        # Get rooms from game state if available
        rooms = None
        if self.server and hasattr(self.server, 'game_instance') and hasattr(self.server.game_instance, 'rooms'):
            rooms = self.server.game_instance.rooms
        
        self.deaths += 1
        self.is_ghost = True
        self.state = 'ghost'
        self.war_class = None
        self.team = None
        self.has_gerkin = False
        self.current_hp = self.max_hp
        self.sp_current = self.sp_max
        
        # Drop corpse and items
        if rooms and self._location in rooms:
            # Create corpse with inventory
            # TODO: Implement corpse system
            pass
        
        # Move to warroom
        self.move('warroom')
        self.message("You have died and returned as a ghost to the warroom.")
    
    def make_alive(self):
        """Transform ghost to alive state for war."""
        self.is_ghost = False
        self.state = 'alive'
        self.current_hp = self.max_hp
        self.sp_current = self.sp_max
        self.message("You feel life surge through your body!")
    
    def get_title(self):
        """Get player's title based on level."""
        titles = {
            1: "Private",
            2: "Corporal", 
            3: "Sergeant",
            4: "Lieutenant",
            5: "Captain",
            6: "Major",
            7: "Colonel",
            8: "General",
            9: "Field Marshal",
            10: "Grognard"
        }
        
        if self.implementor_level > 0:
            imp_titles = {
                1: "Implementor (Level 1)",
                2: "Implementor (Level 2)",
                3: "Implementor (Level 3)",
                4: "Implementor (Level 4)",
                5: "Implementor (Level 5)",
                9: "Administrator (Level 9)"
            }
            return imp_titles.get(self.implementor_level, "Implementor")
        elif self.linked_enforcer:
            return f"the Enforcer"
        else:
            return titles.get(self.level, "Recruit")
    
    def get_level_title(self):
        """Get level-based title for score command."""
        if self.level >= 10:
            return "Grognard"
        elif self.level >= 5:
            return "Veteran"
        else:
            return "Newbie"
    
    def get_display_name(self):
        """Get name as displayed to others."""
        if self.linkdead:
            return f"Statue of {self.name} ({self.get_title()})"
        elif self.is_ghost:
            return f"ghost of {self.name}"
        elif self.has_gerkin:
            # Would display in yellow if ANSI enabled
            return f"{self.name} *"
        else:
            return self.name
    
    def check_wimpy(self):
        """Check if player should wimpy out of combat."""
        hp_percent = (self.current_hp / self.max_hp) * 100
        return hp_percent <= self.wimpy_percent
    
    def add_kill(self, victim_name):
        """Record a kill."""
        self.kills += 1
        if not self.best_kill:
            self.best_kill = victim_name
    
    def set_war_class(self, war_class):
        """Set player's class for the war."""
        if war_class not in ['fighter', 'kamikaze', 'mage', 'hunter', None]:
            return False
            
        self.war_class = war_class
        
        # Apply class modifiers
        if war_class == 'fighter':
            self.max_hp = int(self.max_hp * 1.5)
            self.current_hp = self.max_hp
            self.sp_max = 0
            self.sp_current = 0
        elif war_class == 'kamikaze':
            # Triple damage handled in combat
            pass
        elif war_class == 'mage':
            self.sp_max = int(self.sp_max * 1.5)
            self.sp_current = self.sp_max
        
        return True
    
    def start_exploration_session(self):
        """Start tracking exploration for this session."""
        # Get game instance from server
        if self.server and hasattr(self.server, 'game_instance') and hasattr(self.server.game_instance, 'explorer_system'):
            explorer_system = self.server.game_instance.explorer_system
            self.exploration_session_id = explorer_system.start_session(self.name)
            # Load previously explored rooms
            if self.name in explorer_system.room_cache:
                self.rooms_explored = explorer_system.room_cache[self.name].copy()
    
    def end_exploration_session(self):
        """End exploration tracking for this session."""
        # Get game instance from server
        if self.server and hasattr(self.server, 'game_instance') and hasattr(self.server.game_instance, 'explorer_system') and self.exploration_session_id:
            self.server.game_instance.explorer_system.end_session(self.name, self.exploration_session_id)
            self.exploration_session_id = None
    
    def add_war_record(self, war_type, won, kills, kill_value, damage_in, damage_out, coins):
        """Add a war participation record."""
        war_record = {
            'end_time': time.time(),
            'type': war_type,  # 'F' for FFA, 'T' for Team, 'B' for BvR
            'won': won,
            'kills': kills,
            'kill_value': kill_value,
            'damage_in': damage_in,
            'damage_out': damage_out,
            'coins': coins,
            'race': self.race or 'Human',
            'class': self.war_class or 'None'
        }
        self.war_history.append(war_record)
        
        # Keep only last 1000 wars
        if len(self.war_history) > 1000:
            self.war_history = self.war_history[-1000:]
    
    def to_dict(self):
        """Convert player to dictionary for saving."""
        return {
            'name': self.name,
            'password': self.password_hash,
            'gender': self.gender,
            'email': self.email,
            'real_name': self.real_name,
            'level': self.level,
            'experience': self.xp,
            'abilities': self.abilities,
            'health': self.current_hp,
            'max_health': self.max_hp,
            'sp_current': self.sp_current,
            'sp_max': self.sp_max,
            'coins': self.coins,
            'kills': self.kills,
            'deaths': self.deaths,
            'best_kill': self.best_kill,
            'explorer_rooms': list(self.rooms_explored),  # Convert set to list
            'implementor_level': self.implementor_level,
            'linked_enforcer': self.linked_enforcer,
            'created': self.created_at,
            'last_login': self.last_login,
            'age': self.age + (time.time() - self.last_login),
            'wimpy_percent': self.wimpy_percent,
            'plan': self.plan,
            'ansi_enabled': self.ansi_enabled,
            'ansi_vars': self.ansi_vars,
            'war_history': self.war_history,
            'war_on': self.war_enabled,
            'state': self.state,
            'location': self._location,
            'inventory': [],  # TODO: Serialize inventory properly
            'equipment': self.equipment,
            'last_logout': self.last_logout,
            'last_login_info': self.last_login_info,
            'alignment': self.alignment,
            'race': self.race,
            'title': self.get_title(),
            # Save brief/combat settings
            'brief_mode': self.brief_mode,
            'show_mapping': self.show_mapping,
            'combat_brief': self.combat_brief,
            'monster_brief': self.monster_brief
        }
    
    def save(self, filepath):
        """Save player to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath):
        """Load player from JSON file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            # Create player with saved data
            return cls(**data)
        except Exception as e:
            print(f"Error loading player from {filepath}: {e}")
            return None
    
    @classmethod
    def from_dict(cls, data, client=None, server=None):
        """Create player from saved dictionary."""
        # Handle both new and legacy loading
        if client and server:
            # Legacy loading with client/server
            # Create basic creature
            creature = Creature(
                name=data['name'],
                description="A player",
                character_class="Adventurer",
                level=data.get('level', 1),
                background="Unknown",
                race=data.get('race', 'Human'),
                alignment=data.get('alignment', 'neutral'),
                xp=data.get('experience', 0),
                abilities=data.get('abilities', {
                    'STRENGTH': 50,
                    'DEXTERITY': 50,
                    'WISDOM': 50,
                    'INTELLIGENCE': 50,
                    'CONSTITUTION': 50,
                    'CHARISMA': 50
                }),
                skills=[],
                max_hp=data.get('max_health', 100),
                armor_class=10,
                hd_value=1,
                hd_total=1
            )
            
            # Create player
            player = cls(client, server, creature)
            
            # Restore saved attributes
            player.password_hash = data.get('password', data.get('password_hash'))
            player.gender = data.get('gender')
            player.email = data.get('email', '')
            player.real_name = data.get('real_name', '???')
            player.current_hp = data.get('health', data.get('current_hp', player.max_hp))
            player.sp_current = data.get('sp_current', 200)
            player.sp_max = data.get('sp_max', 200)
            player.coins = data.get('coins', 0)
            player.kills = data.get('kills', 0)
            player.deaths = data.get('deaths', 0)
            player.best_kill = data.get('best_kill')
            player.rooms_explored = set(data.get('explorer_rooms', data.get('rooms_explored', [])))
            player.implementor_level = data.get('implementor_level', 0)
            player.linked_enforcer = data.get('linked_enforcer')
            player.created_at = data.get('created', data.get('created_at', time.time()))
            player.age = data.get('age', 0)
            player.wimpy_percent = data.get('wimpy_percent', 30)
            player.plan = data.get('plan', '')
            player.ansi_enabled = data.get('ansi_enabled', True)  # CHANGED: Default True
            player.ansi_vars = data.get('ansi_vars', {})
            player.war_history = data.get('war_history', [])
            player.last_logout = data.get('last_logout')
            player.last_login_info = data.get('last_login_info')
            player.state = data.get('state', 'ghost')  # Default to ghost
            player.is_ghost = player.state == 'ghost'
            player.war_enabled = data.get('war_on', True)
            player._location = data.get('location', 'warroom' if player.is_ghost else 'entrance')
            # Load brief/combat settings
            player.brief_mode = data.get('brief_mode', False)
            player.show_mapping = data.get('show_mapping', False)
            player.combat_brief = data.get('combat_brief', None)
            player.monster_brief = data.get('monster_brief', False)
            
            return player
        else:
            # New loading - just pass all data as kwargs
            return cls(**data)
