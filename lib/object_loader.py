"""Object loader system for PKMUD"""

import os
import importlib.util
import logging
from typing import Dict, Optional, Type

log = logging.getLogger(__name__)

class ObjectLoader:
    """Loads objects from individual Python files."""
    
    def __init__(self):
        self.object_templates = {}  # name -> object class/factory
        self.object_dirs = [
            'lib/objects/weapons',
            'lib/objects/armor',
            'lib/objects/consumables',
            'lib/objects/special',
            'lib/objects/misc'
        ]
    
    def load_all_objects(self) -> Dict[str, Type]:
        """Load all object templates from all directories."""
        total_loaded = 0
        
        # Create directories if they don't exist
        for obj_dir in self.object_dirs:
            os.makedirs(obj_dir, exist_ok=True)
        
        for obj_dir in self.object_dirs:
            if os.path.exists(obj_dir):
                loaded = self._load_directory(obj_dir)
                total_loaded += loaded
                log.info(f"Loaded {loaded} objects from {obj_dir}")
        
        log.info(f"Total object templates loaded: {len(self.object_templates)}")
        return self.object_templates
    
    def _load_directory(self, directory: str, recursive: bool = True) -> int:
        """Load all object files from a directory."""
        loaded = 0
        
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            # Handle subdirectories
            if os.path.isdir(item_path) and recursive:
                if item == '__pycache__':
                    continue
                loaded += self._load_directory(item_path, recursive=True)
            
            # Handle Python files
            elif item.endswith('.py') and item != '__init__.py':
                try:
                    obj_template = self._load_object_file(item_path)
                    if obj_template:
                        # Objects can register multiple templates
                        if isinstance(obj_template, dict):
                            for name, template in obj_template.items():
                                self.object_templates[name] = template
                                loaded += 1
                        else:
                            # Single object
                            name = os.path.splitext(os.path.basename(item_path))[0]
                            self.object_templates[name] = obj_template
                            loaded += 1
                except Exception as e:
                    log.error(f"Error loading object from {item_path}: {e}")
        
        return loaded
    
    def _load_object_file(self, filepath: str):
        """Load object template(s) from a Python file."""
        module_name = os.path.splitext(os.path.basename(filepath))[0]
        
        # Load the module
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        if not spec or not spec.loader:
            return None
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Look for load() function
        if hasattr(module, 'load'):
            return module.load()
        else:
            log.warning(f"{filepath} does not have a load() function")
            return None
    
    def create_object(self, template_name: str, **kwargs):
        """Create an instance of an object from a template."""
        if template_name not in self.object_templates:
            log.error(f"Unknown object template: {template_name}")
            return None
        
        template = self.object_templates[template_name]
        
        # If template is a class, instantiate it
        if isinstance(template, type):
            return template(**kwargs)
        # If template is a factory function, call it
        elif callable(template):
            return template(**kwargs)
        else:
            log.error(f"Invalid template type for {template_name}")
            return None
    
    def reload_object(self, template_name: str) -> bool:
        """Reload a specific object template."""
        # Find which file contains this template
        for obj_dir in self.object_dirs:
            if not os.path.exists(obj_dir):
                continue
                
            for item in os.listdir(obj_dir):
                if item.endswith('.py') and item != '__init__.py':
                    item_path = os.path.join(obj_dir, item)
                    try:
                        # Load and check if it contains our template
                        obj_template = self._load_object_file(item_path)
                        if isinstance(obj_template, dict) and template_name in obj_template:
                            self.object_templates[template_name] = obj_template[template_name]
                            log.info(f"Reloaded object template {template_name}")
                            return True
                        elif os.path.splitext(item)[0] == template_name:
                            self.object_templates[template_name] = obj_template
                            log.info(f"Reloaded object template {template_name}")
                            return True
                    except:
                        pass
        
        return False