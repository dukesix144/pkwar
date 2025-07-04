"""Room loader system for PKMUD"""

import os
import importlib.util
import logging
from typing import Dict, Optional
from lib.models.entity import Room

log = logging.getLogger(__name__)

class RoomLoader:
    """Loads rooms from individual Python files."""
    
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.room_dirs = [
            'lib/rooms',
            'lib/areas',
            'lib/wizrooms'
        ]
    
    def load_all_rooms(self) -> Dict[str, Room]:
        """Load all rooms from all directories."""
        total_loaded = 0
        
        for room_dir in self.room_dirs:
            if os.path.exists(room_dir):
                loaded = self._load_directory(room_dir)
                total_loaded += loaded
                log.info(f"Loaded {loaded} rooms from {room_dir}")
        
        # Load backbone rooms
        self._create_backbone_rooms()
        
        # Load arena rooms
        self._create_arena_rooms()
        
        log.info(f"Total rooms loaded: {len(self.rooms)}")
        return self.rooms
    
    def _load_directory(self, directory: str, recursive: bool = True) -> int:
        """Load all room files from a directory."""
        loaded = 0
        
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            # Handle subdirectories
            if os.path.isdir(item_path) and recursive:
                # Skip __pycache__
                if item == '__pycache__':
                    continue
                loaded += self._load_directory(item_path, recursive=True)
            
            # Handle Python files
            elif item.endswith('.py') and item != '__init__.py':
                try:
                    room = self._load_room_file(item_path)
                    if room:
                        self.rooms[room.name] = room
                        loaded += 1
                except Exception as e:
                    log.error(f"Error loading room from {item_path}: {e}")
        
        return loaded
    
    def _load_room_file(self, filepath: str) -> Optional[Room]:
        """Load a single room from a Python file."""
        # Get module name from filepath
        module_name = os.path.splitext(os.path.basename(filepath))[0]
        
        # Load the module
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        if not spec or not spec.loader:
            return None
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Look for load() function
        if hasattr(module, 'load'):
            room = module.load()
            if isinstance(room, Room):
                # Store the source file for debugging
                room.source_file = filepath
                return room
            else:
                log.warning(f"{filepath} load() did not return a Room object")
        else:
            log.warning(f"{filepath} does not have a load() function")
        
        return None
    
    def _create_backbone_rooms(self):
        """Create the 30 backbone rooms."""
        from lib.special_rooms import RandomRoom
        from lib.models.entity import Exit, DescriptionItem
        from lib.models.enums import ExitType
        
        # Room descriptions for variety
        descriptions = [
            "A dusty crossroads on the backbone.",
            "A windswept path along the backbone.",
            "The backbone stretches endlessly here.",
            "Ancient stones mark this part of the backbone.",
            "The backbone continues through barren terrain.",
            "Mist swirls around this section of the backbone.",
            "The backbone passes through a small grove.",
            "Crumbling ruins line the backbone here.",
            "The backbone crosses a dried riverbed.",
            "This part of the backbone feels particularly ancient."
        ]
        
        # Create 30 interconnected rooms
        for i in range(1, 31):
            # Cycle through descriptions
            desc = descriptions[(i-1) % len(descriptions)]
            
            room = RandomRoom(
                name=f'backbone_{i}',
                description=f"Backbone - Section {i}\n\n{desc}",
                description_items=[
                    DescriptionItem(
                        name='backbone',
                        aliases=['path', 'road'],
                        description='The ancient backbone that connects all areas.'
                    )
                ],
                exits=[]
            )
            
            # Add exits to connect rooms
            if i > 1:
                room.exits.append(Exit(
                    name='west',
                    description='The backbone continues west.',
                    destination=f'backbone_{i-1}',
                    exit_type=ExitType.PATH
                ))
            
            if i < 30:
                room.exits.append(Exit(
                    name='east',
                    description='The backbone continues east.',
                    destination=f'backbone_{i+1}',
                    exit_type=ExitType.PATH
                ))
            
            # Connect first room to warroom
            if i == 1:
                room.exits.append(Exit(
                    name='north',
                    description='Back to the war room.',
                    destination='warroom',
                    exit_type=ExitType.PATH
                ))
            
            # Add shop connection
            if i == 15:
                room.exits.append(Exit(
                    name='south',
                    description='Gerkin\'s shop is to the south.',
                    destination='shop',
                    exit_type=ExitType.DOOR
                ))
            
            # Add some random exits to future areas
            if i % 5 == 0 and i != 15:
                room.exits.append(Exit(
                    name='south',
                    description='A path leads to a wizard area.',
                    destination=f'area_entrance_{i//5}',
                    exit_type=ExitType.PATH
                ))
            
            self.rooms[room.name] = room
    
    def _create_arena_rooms(self):
        """Create the shrinking arena rooms (9x9 down to 1x1)."""
        from lib.models.entity import Room, Exit, DescriptionItem
        from lib.models.enums import ExitType
        
        for size in range(1, 10):  # 1x1 up to 9x9
            for x in range(1, size + 1):
                for y in range(1, size + 1):
                    room = Room(
                        name=f'arena_{x}_{y}',
                        description=f"""The Arena - Position ({x},{y})

You are in the mystical arena. The walls shimmer with an otherworldly
energy, preventing escape. {'The space feels incredibly cramped!' if size == 1 else ''}

Current arena size: {size}x{size}""",
                        description_items=[
                            DescriptionItem(
                                name='walls',
                                aliases=['arena walls', 'energy', 'wall'],
                                description='The walls pulse with magical energy, keeping warriors trapped inside.'
                            )
                        ],
                        exits=[]
                    )
                    
                    room.special_type = 'arena'
                    room.arena_size = size
                    
                    # Add exits within arena bounds
                    if x > 1:
                        room.exits.append(Exit(
                            name='west',
                            description='West in the arena.',
                            destination=f'arena_{x-1}_{y}',
                            exit_type=ExitType.PATH
                        ))
                    
                    if x < size:
                        room.exits.append(Exit(
                            name='east',
                            description='East in the arena.',
                            destination=f'arena_{x+1}_{y}',
                            exit_type=ExitType.PATH
                        ))
                    
                    if y > 1:
                        room.exits.append(Exit(
                            name='north',
                            description='North in the arena.',
                            destination=f'arena_{x}_{y-1}',
                            exit_type=ExitType.PATH
                        ))
                    
                    if y < size:
                        room.exits.append(Exit(
                            name='south',
                            description='South in the arena.',
                            destination=f'arena_{x}_{y+1}',
                            exit_type=ExitType.PATH
                        ))
                    
                    self.rooms[room.name] = room
    
    def reload_room(self, room_name: str) -> bool:
        """Reload a specific room from its source file."""
        if room_name not in self.rooms:
            log.error(f"Room {room_name} not found")
            return False
        
        room = self.rooms[room_name]
        if not hasattr(room, 'source_file'):
            log.error(f"Room {room_name} has no source file")
            return False
        
        try:
            new_room = self._load_room_file(room.source_file)
            if new_room:
                # Preserve any runtime state
                if hasattr(room, 'inventory'):
                    new_room.inventory = room.inventory
                
                self.rooms[room_name] = new_room
                log.info(f"Reloaded room {room_name}")
                return True
        except Exception as e:
            log.error(f"Error reloading room {room_name}: {e}")
        
        return False