"""Inventory and item management commands."""

from .base import BaseCommand

class InventoryCommands(BaseCommand):
    """Commands for managing inventory and items."""
    
    def inventory(self, player, params=None):
        """inventory - Show what you're carrying"""
        output = player.inventory.get_inventory_display()
        player.message("\n".join(output))

    def equipment(self, player, params=None):
        """eq - Show equipped items"""
        output = player.inventory.get_equipment_display()
        player.message("\n".join(output))

    def get_item(self, player, params=None):
        """get <item> [from <container>] - Pick up an item"""
        if not params:
            player.message("Get what?")
            return
        
        current_room = self.get_player_room(player)
        
        # Handle "get all"
        if params.lower() == "all":
            items_gotten = []
            items_to_get = []
            
            # Get list of items first (avoid modifying while iterating)
            for uuid, item in current_room.inventory.get_items():
                if hasattr(item, 'takeable') and not item.takeable:
                    continue  # Can't take this (like corpses)
                if not isinstance(item, player.__class__):  # Don't pick up players!
                    items_to_get.append(item)
            
            # Now get the items
            for item in items_to_get:
                if player.inventory.add_item(item):
                    current_room.inventory.remove_item(item)
                    items_gotten.append(item.name)
                else:
                    player.message("You can't carry any more.")
                    break
            
            if items_gotten:
                player.message(f"You get: {', '.join(items_gotten)}")
            else:
                player.message("There's nothing here to get.")
            return
        
        # Handle "get <item> from <container>"
        if " from " in params:
            parts = params.split(" from ", 1)
            item_name = parts[0].strip()
            container_name = parts[1].strip()
            
            # Find container
            container = None
            for uuid, obj in current_room.inventory.get_items():
                if hasattr(obj, 'name') and container_name.lower() in obj.name.lower():
                    if hasattr(obj, 'contents'):  # It's a container
                        container = obj
                        break
            
            if not container:
                player.message(f"You don't see any '{container_name}' here.")
                return
            
            # Find item in container
            target_item = None
            for item in container.contents:
                if item_name.lower() in item.name.lower():
                    target_item = item
                    break
            
            if not target_item:
                player.message(f"The {container.name} doesn't contain '{item_name}'.")
                return
            
            # Try to get item
            if player.inventory.add_item(target_item):
                container.remove_item(target_item)
                player.message(f"You get {target_item.name} from {container.name}.")
            else:
                player.message("You can't carry that much weight.")
            return
        
        # Normal get
        target_item = None
        for uuid, item in current_room.inventory.get_items():
            if hasattr(item, 'name') and params.lower() in item.name.lower():
                if not isinstance(item, player.__class__):  # Don't pick up players!
                    target_item = item
                    break
        
        if not target_item:
            player.message(f"You don't see '{params}' here.")
            return
        
        # Check if item can be taken
        if hasattr(target_item, 'takeable') and not target_item.takeable:
            player.message(f"You can't take the {target_item.name}.")
            return
        
        # Try to add to inventory
        if player.inventory.add_item(target_item):
            current_room.inventory.remove_item(target_item)
            player.message(f"You get {target_item.name}.")
            
            # Announce to room
            self.broadcast_to_room(player, f"{player.name} gets {target_item.name}.")
        else:
            player.message("You can't carry that much weight.")

    def drop_item(self, player, params=None):
        """drop <item> - Drop an item"""
        if not params:
            player.message("Drop what?")
            return
        
        # Check for blood - can't drop blood
        if "blood" in params.lower():
            item = player.inventory.get_item(params)
            if item and hasattr(item, 'victim_name'):
                player.message("You can't drop blood!")
                return
        
        # Handle "drop all"
        if params.lower() == "all":
            current_room = self.get_player_room(player)
            
            items_dropped = []
            items_to_drop = []
            
            # Get droppable items
            for item in player.inventory.items:
                if not hasattr(item, 'victim_name'):  # Not blood
                    items_to_drop.append(item)
            
            # Drop the items
            for item in items_to_drop:
                player.inventory.remove_item(item)
                current_room.inventory.add_item(item)
                items_dropped.append(item.name)
            
            if items_dropped:
                player.message(f"You drop: {', '.join(items_dropped)}")
                
                # Announce to room
                self.broadcast_to_room(player, 
                    f"{player.name} drops: {', '.join(items_dropped)}")
            else:
                player.message("You have nothing to drop.")
            return
        
        # Find item
        item = player.inventory.get_item(params)
        if not item:
            player.message("You don't have that.")
            return
        
        # Drop it
        current_room = self.get_player_room(player)
        
        player.inventory.remove_item(item)
        current_room.inventory.add_item(item)
        player.message(f"You drop {item.name}.")
        
        # Announce to room
        self.broadcast_to_room(player, f"{player.name} drops {item.name}.")

    def give_item(self, player, params=None):
        """give <item> to <player> - Give an item to someone"""
        if not params or ' to ' not in params:
            player.message("Give what to whom?")
            player.message("Usage: give <item> to <player>")
            return
        
        parts = params.split(' to ', 1)
        item_name = parts[0].strip()
        target_name = parts[1].strip()
        
        # Check for blood - can't give blood
        if "blood" in item_name.lower():
            item = player.inventory.get_item(item_name)
            if item and hasattr(item, 'victim_name'):
                player.message("You can't give away blood!")
                return
        
        # Find item
        item = player.inventory.get_item(item_name)
        if not item:
            player.message("You don't have that.")
            return
        
        # Find target player
        target_player = self.find_target_in_room(player, target_name)
        
        if not target_player:
            player.message(f"You don't see '{target_name}' here.")
            return
        
        if target_player == player:
            player.message("You can't give items to yourself!")
            return
        
        # Try to give
        if target_player.inventory.add_item(item):
            player.inventory.remove_item(item)
            player.message(f"You give {item.name} to {target_player.name}.")
            target_player.message(f"{player.name} gives you {item.name}.")
            
            # Announce to others
            self.broadcast_to_room(player, 
                f"{player.name} gives {item.name} to {target_player.name}.")
        else:
            player.message(f"{target_player.name} can't carry that much weight.")

    def wear(self, player, params=None):
        """wear <item> - Wear armor"""
        if not params:
            player.message("Wear what?")
            return
        
        item = player.inventory.get_item(params)
        if not item:
            player.message("You don't have that.")
            return
        
        success, message = player.inventory.equip_item(item)
        player.message(message)

    def wield(self, player, params=None):
        """wield <weapon> - Wield a weapon"""
        if not params:
            player.message("Wield what?")
            return
        
        item = player.inventory.get_item(params)
        if not item:
            player.message("You don't have that.")
            return
        
        success, message = player.inventory.equip_item(item)
        player.message(message)

    def remove(self, player, params=None):
        """remove <item> - Remove equipped item"""
        if not params:
            player.message("Remove what?")
            return
        
        item = player.inventory.get_item(params)
        if not item:
            player.message("You don't have that.")
            return
        
        success, message = player.inventory.unequip_item(item)
        player.message(message)

    def equip_all(self, player, params=None):
        """equip all - Equip all armor and weapons"""
        messages = player.inventory.equip_all()
        if messages:
            for msg in messages:
                player.message(msg)
        else:
            player.message("You have nothing to equip.")

    def remove_all(self, player, params=None):
        """unequip all - Remove all equipment"""
        messages = player.inventory.remove_all()
        if messages:
            for msg in messages:
                player.message(msg)
        else:
            player.message("You're not wearing anything.")

    def use_item(self, player, params=None):
        """use <item> - Use an item"""
        if not params:
            player.message("Use what?")
            return
        
        item = player.inventory.get_item(params)
        if not item:
            player.message("You don't have that.")
            return
        
        if hasattr(item, 'use'):
            success, message = item.use(player)
            player.message(message)
            if success and hasattr(item, 'charges') and item.charges <= 0:
                player.inventory.remove_item(item)
        else:
            player.message("You can't use that.")
    
    def heal(self, player, params=None):
        """heal [hp|sp|both] - Use healing potions"""
        if not params:
            params = "both"  # Default to healing both
        
        heal_type = params.lower()
        if heal_type not in ['hp', 'sp', 'both']:
            player.message("Usage: heal [hp|sp|both]")
            return
        
        # Find heal items in inventory
        heals = []
        for item in player.inventory.get_all_items():
            if hasattr(item, 'heal_amount'):
                heals.append(item)
        
        if not heals:
            player.message("You have no healing potions.")
            return
        
        # Use first heal found
        heal = heals[0]
        
        if heal_type == 'hp':
            healed = min(heal.heal_amount, player.max_hp - player.current_hp)
            player.current_hp += healed
            player.message(f"You drink the heal and recover {healed} hit points.")
        elif heal_type == 'sp':
            healed = min(heal.heal_amount, player.sp_max - player.sp_current)
            player.sp_current += healed
            player.message(f"You drink the heal and recover {healed} spell points.")
        else:  # both
            hp_healed = min(heal.heal_amount, player.max_hp - player.current_hp)
            sp_healed = min(heal.heal_amount, player.sp_max - player.sp_current)
            player.current_hp += hp_healed
            player.sp_current += sp_healed
            player.message(f"You drink the heal and recover {hp_healed} HP and {sp_healed} SP.")
        
        # Remove the heal
        player.inventory.remove_item(heal)

    def keep(self, player, params=None):
        """keep <item> - Mark item to keep"""
        if not params:
            player.message("Keep what?")
            return
        
        item = player.inventory.get_item(params)
        if not item:
            player.message("You don't have that.")
            return
        
        if player.inventory.keep_item(item):
            player.message(f"You mark {item.name} as kept.")
        else:
            player.message("You can't keep that.")

    def unkeep(self, player, params=None):
        """unkeep <item> - Unmark kept item"""
        if not params:
            player.message("Unkeep what?")
            return
        
        item = player.inventory.get_item(params)
        if not item:
            player.message("You don't have that.")
            return
        
        if player.inventory.unkeep_item(item):
            player.message(f"You unmark {item.name} as kept.")
        else:
            player.message("That item isn't kept.")