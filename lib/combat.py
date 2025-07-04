"""Combat system for PKMUD"""

import random
import time
from typing import Optional, Tuple, List
from lib.models.player import Player
from lib.models.creature import Creature

class CombatManager:
    """Manages combat between creatures."""
    
    # Damage emotes from the requirements
    DAMAGE_EMOTES = [
        (0, 0, "missed"),
        (1, 1, "tickled %s in the stomach"),
        (2, 3, "grazed"),
        (3, 10, "hit"),
        (10, 20, "hit %s hard"),
        (20, 30, "hit %s very hard"),
        (30, 55, "struck %s a mighty blow"),
        (55, 65, "smashed %s with a bone crushing sound"),
        (65, 110, "pulverized %s with a powerful attack"),
        (110, 160, "trounced %s up and down"),
        (160, 210, "pummeled %s into small fragments"),
        (210, 260, "massacred %s into tiny fragments"),
        (260, 325, "utterly annihilated"),
        (325, 390, "completely devastated %s with awesome force"),
        (390, float('inf'), "destroyed"),
    ]
    
    def __init__(self, game_state):
        self.game_state = game_state
        self.active_combats = {}  # attacker_id: (target, last_attack_time)
    
    def can_attack(self, attacker: Creature, target: Creature) -> Tuple[bool, str]:
        """Check if attacker can attack target."""
        # Check if both are alive
        if attacker.is_ghost:
            return False, "Ghosts cannot attack!"
        
        if target.is_ghost:
            return False, "You cannot attack ghosts!"
        
        # Check if in same room
        if attacker._location != target._location:
            return False, "They aren't here!"
        
        # Check if in war
        if not hasattr(self.game_state, 'war_system'):
            return False, "Combat is only allowed during wars!"
        
        war = self.game_state.war_system
        if war.state != war.WarState.ACTIVE:
            return False, "There is no war in progress!"
        
        # Check teams in team/bvr wars
        if war.war_type in [war.WarType.TEAM, war.WarType.BEST_VS_REST]:
            if hasattr(attacker, 'team') and hasattr(target, 'team'):
                if attacker.team == target.team:
                    return False, "You cannot attack your own team!"
        
        return True, ""
    
    def calculate_damage(self, attacker: Creature, target: Creature) -> int:
        """Calculate damage for an attack."""
        # Base damage
        base_damage = 10
        
        # Add weapon damage if wielding
        if hasattr(attacker, 'wielded_weapon') and attacker.wielded_weapon:
            base_damage += attacker.wielded_weapon.damage
        
        # Class modifiers
        if hasattr(attacker, 'war_class'):
            if attacker.war_class == 'fighter':
                base_damage = int(base_damage * 1.5)
            elif attacker.war_class == 'kamikaze':
                base_damage = int(base_damage * 3)  # Triple damage!
        
        # Add some randomness
        damage = random.randint(int(base_damage * 0.8), int(base_damage * 1.2))
        
        # Strength modifier
        if hasattr(attacker, 'abilities'):
            str_mod = attacker.get_strength_modifier()
            damage += str_mod
        
        # Minimum 0 damage
        return max(0, damage)
    
    def get_damage_emote(self, damage: int) -> str:
        """Get appropriate emote for damage amount."""
        for min_dmg, max_dmg, emote in self.DAMAGE_EMOTES:
            if min_dmg <= damage <= max_dmg:
                return emote
        return "destroyed"
    
    def apply_damage(self, target: Creature, damage: int) -> bool:
        """Apply damage to target. Returns True if target dies."""
        target.current_hp -= damage
        
        if target.current_hp <= 0:
            target.current_hp = 0
            return True
        
        # Check wimpy
        if hasattr(target, 'check_wimpy') and target.check_wimpy():
            self.flee_combat(target)
        
        return False
    
    def attack(self, attacker: Player, target_name: str) -> Tuple[bool, str]:
        """Execute an attack."""
        # Find target
        target = None
        from pkwar import rooms
        
        for uuid, entity in rooms[attacker._location].inventory.get_items():
            if hasattr(entity, 'name') and entity.name.lower() == target_name.lower():
                if isinstance(entity, (Player, Creature)):
                    target = entity
                    break
        
        if not target:
            return False, f"You don't see '{target_name}' here."
        
        # Check if can attack
        can_atk, reason = self.can_attack(attacker, target)
        if not can_atk:
            return False, reason
        
        # Calculate damage
        damage = self.calculate_damage(attacker, target)
        
        # Get emote
        emote = self.get_damage_emote(damage)
        
        # Format messages
        if "%s" in emote:
            attacker_msg = f"You {emote % target.name}."
            target_msg = f"{attacker.name} {emote % 'you'}."
            room_msg = f"{attacker.name} {emote % target.name}."
        else:
            attacker_msg = f"You {emote} {target.name}."
            target_msg = f"{attacker.name} {emote} you."
            room_msg = f"{attacker.name} {emote} {target.name}."
        
        # Apply ANSI colors if enabled
        if attacker.ansi_enabled and hasattr(attacker, 'ansi_manager'):
            attacker_msg = attacker.ansi_manager.format_combat(
                "You", target.name, damage, emote
            )
        
        if target.ansi_enabled and hasattr(target, 'ansi_manager'):
            target_msg = target.ansi_manager.format_combat(
                attacker.name, "you", damage, emote
            )
        
        # Send messages
        attacker.message(attacker_msg)
        if hasattr(target, 'message'):
            target.message(target_msg)
        
        # Room message
        for uuid, entity in rooms[attacker._location].inventory.get_items():
            if hasattr(entity, 'message') and entity != attacker and entity != target:
                if entity.ansi_enabled and hasattr(entity, 'ansi_manager'):
                    msg = entity.ansi_manager.format_combat(
                        attacker.name, target.name, damage, emote
                    )
                else:
                    msg = room_msg
                entity.message(msg)
        
        # Send to war observers
        if hasattr(self.game_state, 'war_system') and self.game_state.war_system.state == self.game_state.war_system.WarState.ACTIVE:
            observer_msg = f"[{attacker._location}] {room_msg}"
            for player in self.game_state.list_players():
                if getattr(player, 'watching_war', False) and player._location == 'observation_room':
                    player.message(observer_msg)
        
        # Apply damage
        killed = self.apply_damage(target, damage)
        
        # Handle death
        if killed:
            self.handle_death(attacker, target)
        
        # Update combat tracking
        self.active_combats[attacker.uuid] = (target, time.time())
        
        return True, ""
    
    def handle_death(self, killer: Player, victim: Creature):
        """Handle creature death."""
        from pkwar import rooms, game
        
        # Announce death
        death_msg = f"{killer.name} just killed {victim.name}!"
        game.broadcast(death_msg)
        
        # War system handling
        if hasattr(game, 'war_system'):
            game.war_system.handle_kill(killer, victim)
        
        # Track killer for corpse handling
        self._last_killer = killer
        
        # Create blood item
        from lib.models.objects import Blood
        blood = Blood(victim.name)
        killer.inventory.add_item(blood)
        
        # Handle kamikaze explosion
        if hasattr(victim, 'war_class') and victim.war_class == 'kamikaze':
            self.kamikaze_explosion(victim)
        
        # Drop corpse and items
        self.create_corpse(victim)
        
        # Make victim a ghost
        if hasattr(victim, 'die'):
            victim.die()
    
    def kamikaze_explosion(self, kamikaze: Creature):
        """Handle kamikaze death explosion."""
        from pkwar import rooms, game
        
        game.broadcast(f"{kamikaze.name} EXPLODES in a fiery blast!")
        
        # Damage everyone in room
        explosion_damage = 100
        
        for uuid, entity in rooms[kamikaze._location].inventory.get_items():
            if isinstance(entity, (Player, Creature)) and entity != kamikaze:
                if not entity.is_ghost:
                    entity.message("The explosion tears through you!")
                    killed = self.apply_damage(entity, explosion_damage)
                    if killed and hasattr(entity, 'die'):
                        entity.die()
                        game.broadcast(f"{entity.name} was killed by the explosion!")
    
    def create_corpse(self, creature: Creature):
        """Create a corpse with creature's items."""
        from pkwar import rooms
        from lib.objects.special.corpse import Corpse
        
        # Create corpse
        corpse = Corpse(creature.name, getattr(creature, 'level', 1))
        
        # Transfer inventory to corpse
        if hasattr(creature, 'inventory'):
            # Get all items including equipment
            all_items = []
            
            # Add carried items
            all_items.extend(creature.inventory.items)
            
            # Add equipped items
            for slot, item in creature.inventory.equipment.items():
                if item:
                    all_items.append(item)
            
            # Clear creature's inventory
            creature.inventory.items = []
            creature.inventory.equipment = {slot: None for slot in creature.inventory.equipment}
            creature.inventory.current_weight = 0
            
            # Add items to corpse
            for item in all_items:
                corpse.add_item(item)
        
        # Add corpse to killer's inventory automatically
        if hasattr(self, '_last_killer'):
            killer = self._last_killer
            if hasattr(killer, 'inventory'):
                # Try to add corpse to killer's inventory
                killer.message(f"You collect the corpse of {creature.name}.")
                # Since corpses are heavy and not takeable, we'll just transfer the contents
                looted = corpse.loot_all(killer)
                if looted:
                    for item in looted:
                        killer.message(f"You loot {item.name} from the corpse.")
                else:
                    killer.message("The corpse was empty.")
                
                # Drop empty corpse in room
                room = rooms[creature._location]
                room.inventory.add_item(corpse)
        else:
            # Just drop corpse in room
            room = rooms[creature._location]
            room.inventory.add_item(corpse)

    def flee_combat(self, creature: Creature):
        """Make creature flee in random direction."""
        from pkwar import rooms
        
        current_room = rooms[creature._location]
        
        # Get available exits
        exits = [exit.name for exit in current_room.exits]
        
        if not exits:
            creature.message("There's nowhere to flee!")
            return
        
        # Choose random exit
        flee_dir = random.choice(exits)
        
        # Announce fleeing
        creature.message(f"You flee {flee_dir} in panic!")
        
        for uuid, entity in current_room.inventory.get_items():
            if hasattr(entity, 'message') and entity != creature:
                entity.message(f"{creature.name} flees {flee_dir}!")
        
        # Move creature
        exit_obj = current_room.get_exit(flee_dir)
        creature.move(exit_obj.destination)
        
        # Clear combat
        if creature.uuid in self.active_combats:
            del self.active_combats[creature.uuid]
    
    def get_combat_status(self, creature: Creature) -> Optional[str]:
        """Get current combat status for creature."""
        if creature.uuid in self.active_combats:
            target, last_time = self.active_combats[creature.uuid]
            
            # Combat expires after 10 seconds of no attacks
            if time.time() - last_time > 10:
                del self.active_combats[creature.uuid]
                return None
            
            return f"Fighting: {target.name}"
        
        return None