"""Shop system commands."""

from .base import BaseCommand

class ShopCommands(BaseCommand):
    """Commands for interacting with shops."""
    
    def __init__(self, game_state):
        super().__init__(game_state)
        self.shop_inventory = game_state.shop_inventory
        self.gerkin_npc = game_state.gerkin_npc
    
    def shop_list(self, player, params=None):
        """list - List items in shop (shop only)"""
        if player._location != 'shop':
            player.message("You're not in a shop.")
            return
        
        output = ["=== Gerkin's War Supplies ==="]
        output.append(f"{'Item':<30} {'Price':<10}")
        output.append("-" * 40)
        
        for template_name, price in self.shop_inventory.get_items_for_sale():
            # Create temp item to get display name
            item = self.game_state.object_loader.create_object(template_name)
            if item:
                output.append(f"{item.name:<30} {price:<10} coins")
        
        output.append("\nCommands: buy <item>, buy max <heal/wand>, sell <item>, sell all")
        player.message("\n".join(output))
        
        # Random Gerkin message
        msg = self.gerkin_npc.get_random_message()
        if msg:
            player.message(f"\n{msg}")

    def buy(self, player, params=None):
        """buy <item> - Purchase an item"""
        if player._location != 'shop':
            player.message("You're not in a shop.")
            return
        
        if not params:
            player.message("Buy what?")
            return
        
        # Handle "buy max"
        if params.startswith("max "):
            item_type = params[4:]
            success, message = self.shop_inventory.buy_max(player, item_type)
            player.message(message)
            return
        
        success, message = self.shop_inventory.buy_item(player, params)
        player.message(message)

    def sell(self, player, params=None):
        """sell <item> - Sell an item"""
        if player._location != 'shop':
            player.message("You're not in a shop.")
            return
        
        if not params:
            player.message("Sell what?")
            return
        
        # Handle "sell all"
        if params.lower() == "all":
            success, message = self.shop_inventory.sell_all(player)
            player.message(message)
            return
        
        # Find item
        item = player.inventory.get_item(params)
        if not item:
            player.message("You don't have that.")
            return
        
        success, message = self.shop_inventory.sell_item(player, item)
        player.message(message)

    def value(self, player, params=None):
        """value <item> - Check item value"""
        if player._location != 'shop':
            player.message("You're not in a shop.")
            return
        
        if not params:
            player.message("Value what?")
            return
        
        item = player.inventory.get_item(params)
        if not item:
            player.message("You don't have that.")
            return
        
        value = self.shop_inventory.value_item(item)
        if value > 0:
            player.message(f"I'll give you {value} coins for {item.name}.")
        else:
            player.message("I won't buy that.")