"""Shop system for PKMUD"""

import random
import time
from typing import Dict, List, Tuple, Optional
from lib.models.objects import GameObject, Weapon, Armor, Heal, Wand

class ShopInventory:
    """Shop inventory and pricing."""
    
    def __init__(self, game_state):
        self.game_state = game_state
        self.base_items = {
            # Weapons
            'wooden_sword': {'price': 20, 'stock': -1},
            'iron_sword': {'price': 100, 'stock': -1},
            'steel_sword': {'price': 250, 'stock': -1},
            'dagger': {'price': 30, 'stock': -1},
            
            # Armor set
            'leather_cap': {'price': 20, 'stock': -1},
            'wool_cloak': {'price': 30, 'stock': -1},
            'leather_vest': {'price': 50, 'stock': -1},
            'leather_pants': {'price': 40, 'stock': -1},
            'leather_gloves': {'price': 15, 'stock': -1},
            'leather_boots': {'price': 25, 'stock': -1},
            'wooden_shield': {'price': 35, 'stock': -1},
            
            # Consumables
            'heal_50': {'price': 50, 'stock': -1},
            'heal_100': {'price': 100, 'stock': -1},
            'wand_10': {'price': 200, 'stock': -1},
        }
        
        # Buy prices are 50% of sell prices
        self.buy_multiplier = 0.5
    
    def get_items_for_sale(self) -> List[Tuple[str, int]]:
        """Get list of items and prices."""
        items = []
        for template_name, info in self.base_items.items():
            if info['stock'] != 0:  # 0 = out of stock
                items.append((template_name, info['price']))
        return items
    
    def buy_item(self, player, item_name: str) -> Tuple[bool, str]:
        """Player buys item from shop."""
        # Find item
        template_name = None
        for name in self.base_items.keys():
            if item_name.lower() in name.lower():
                template_name = name
                break
        
        if not template_name:
            return False, "We don't sell that here."
        
        info = self.base_items[template_name]
        
        # Check stock
        if info['stock'] == 0:
            return False, "That item is out of stock."
        
        # Check money
        if player.coins < info['price']:
            return False, f"You need {info['price']} coins. You only have {player.coins}."
        
        # Create item
        item = self.game_state.object_loader.create_object(template_name)
        if not item:
            return False, "Error creating item."
        
        # Try to add to inventory
        if not player.inventory.add_item(item):
            return False, "You can't carry that much weight!"
        
        # Deduct money
        player.coins -= info['price']
        
        # Reduce stock if limited
        if info['stock'] > 0:
            info['stock'] -= 1
        
        return True, f"You buy {item.name} for {info['price']} coins."
    
    def buy_max(self, player, item_type: str) -> Tuple[bool, str]:
        """Buy maximum amount player can carry/afford."""
        # Determine what to buy
        if 'heal' in item_type.lower():
            template_name = 'heal_50'  # Default to cheaper heals
        elif 'wand' in item_type.lower():
            template_name = 'wand_10'
        else:
            return False, "You can only 'buy max' for heals or wands."
        
        info = self.base_items[template_name]
        bought = 0
        total_cost = 0
        
        while True:
            # Check if can afford
            if player.coins < info['price']:
                break
            
            # Try to create and add item
            item = self.game_state.object_loader.create_object(template_name)
            if not item:
                break
            
            # Check weight
            if player.inventory.get_current_weight() + item.weight > player.inventory.get_max_weight():
                break
            
            # Buy it
            if player.inventory.add_item(item):
                player.coins -= info['price']
                total_cost += info['price']
                bought += 1
            else:
                break
        
        if bought == 0:
            return False, "You can't buy any more of those."
        
        return True, f"You buy {bought} items for {total_cost} coins."
    
    def sell_item(self, player, item: GameObject) -> Tuple[bool, str]:
        """Sell item to shop."""
        # Check if sellable
        if not getattr(item, 'sellable', True):
            return False, "I won't buy that."
        
        if item.kept:
            return False, "You have that item marked as kept."
        
        # Calculate price
        sell_price = int(item.value * self.buy_multiplier)
        
        # Remove from inventory
        if not player.inventory.remove_item(item):
            return False, "Error selling item."
        
        # Give money
        player.coins += sell_price
        
        return True, f"You sell {item.name} for {sell_price} coins."
    
    def sell_all(self, player) -> Tuple[bool, str]:
        """Sell all non-kept items."""
        items_to_sell = player.inventory.get_sellable_items()
        
        if not items_to_sell:
            return False, "You have nothing to sell."
        
        total_value = 0
        sold_count = 0
        
        for item in items_to_sell[:]:  # Copy list
            sell_price = int(item.value * self.buy_multiplier)
            if player.inventory.remove_item(item):
                total_value += sell_price
                sold_count += 1
        
        player.coins += total_value
        
        return True, f"You sell {sold_count} items for {total_value} coins."
    
    def value_item(self, item: GameObject) -> int:
        """Get shop's buying price for an item."""
        if not getattr(item, 'sellable', True):
            return 0
        return int(item.value * self.buy_multiplier)

class GerkinNPC:
    """Gerkin the mad shopkeeper."""
    
    def __init__(self):
        self.last_message_time = 0
        self.message_cooldown = 30  # Seconds between messages
        self.messages = [
            "Gerkin mutters: 'They think they can win... fools!'",
            "Gerkin says: 'Buy my wares! You'll need them to survive!'",
            "Gerkin cackles: 'Another war coming... I can smell it!'",
            "Gerkin whispers: 'The spirit... it speaks to me...'",
            "Gerkin shouts: 'Death! DEATH COMES FOR ALL!'",
            "Gerkin mumbles: 'I've seen thousands die... thousands...'",
            "Gerkin laughs madly: 'The blood never washes off!'",
            "Gerkin says: 'Heals won't save you, but buy them anyway!'",
            "Gerkin grins: 'I remember when that armor was new... and bloody.'",
            "Gerkin whispers: 'The ghosts... they never stop screaming.'",
            "Gerkin mutters: 'War... war never changes...'",
            "Gerkin cackles: 'I'll outlive you all! ALL OF YOU!'"
        ]
    
    def get_random_message(self) -> Optional[str]:
        """Get a random message if cooldown allows."""
        current_time = time.time()
        
        if current_time - self.last_message_time < self.message_cooldown:
            return None
        
        self.last_message_time = current_time
        return random.choice(self.messages)
    
    def greet_customer(self, player_name: str) -> str:
        """Greet a customer entering the shop."""
        greetings = [
            f"Gerkin looks up at {player_name} with mad eyes. 'Another one for the slaughter!'",
            f"Gerkin grins at {player_name}. 'Come to buy your death implements?'",
            f"Gerkin cackles as {player_name} enters. 'The spirit told me you'd come!'",
            f"Gerkin stares at {player_name}. 'I can smell the death on you already.'"
        ]
        return random.choice(greetings)
    
    def farewell_customer(self, player_name: str) -> str:
        """Say goodbye to leaving customer."""
        farewells = [
            f"Gerkin waves at {player_name}. 'See you in the next war... if you survive!'",
            f"Gerkin mutters as {player_name} leaves. 'Another ghost in the making...'",
            f"Gerkin shouts after {player_name}. 'You'll be back! They always come back!'",
            f"Gerkin whispers: 'The spirit follows {player_name}...'"
        ]
        return random.choice(farewells)