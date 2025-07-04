"""Combat-related commands."""

from .base import BaseCommand
import random
import threading
import time

class CombatCommands(BaseCommand):
    """Commands for combat and combat-related actions."""
    
    def __init__(self, game_state):
        super().__init__(game_state)
        self.combat_manager = game_state.combat_manager
        
        # Gerkin power tracking - moved from main Commands
        self.gerkin_timers = {}  # player_uuid: timer
        self.gerkin_last_used = {}  # player_uuid: time
    
    def kill(self, player, params=None):
        """kill <target> - Attack someone"""
        if not params:
            player.message("Kill whom?")
            return
        
        success, message = self.combat_manager.attack(player, params)
        if message:
            player.message(message)
    
    def blick(self, player, params=None):
        """blick - Lick the blood of your victim for full heal"""
        # Find first blood item in inventory
        blood_item = None
        for item in player.inventory.get_all_items():
            if hasattr(item, 'victim_name'):  # It's a blood item
                blood_item = item
                break
        
        if not blood_item:
            player.message("You have no blood to lick.")
            return
        
        # Full heal
        player.current_hp = player.max_hp
        player.sp_current = player.sp_max
        
        # Remove blood
        player.inventory.remove_item(blood_item)
        
        # Message with proper formatting
        if player.ansi_enabled and hasattr(player, 'ansi_manager'):
            msg = player.ansi_manager.color_text(
                f"You lick the {blood_item.name} and feel completely restored!",
                'yellow'
            )
        else:
            msg = f"You lick the {blood_item.name} and feel completely restored!"
        
        player.message(msg)
        
        # Room message
        self.broadcast_to_room(player, f"{player.name} licks some blood and looks rejuvenated!")
    
    def follow(self, player, params=None):
        """follow <player> - Follow someone (hunters and gerkin)"""
        if not params:
            if player.following:
                player.message(f"You are following {player.following.name}.")
            else:
                player.message("Follow whom?")
            return
        
        # Check if player is a hunter
        if player.war_class != 'hunter' and not player.has_gerkin:
            player.message("Only hunters can follow other players.")
            return
        
        # Find target
        target = self.find_target_in_room(player, params)
        
        if not target:
            player.message("They aren't here.")
            return
        
        if target == player:
            player.message("You can't follow yourself!")
            return
        
        if target.is_ghost:
            player.message("You can't follow ghosts.")
            return
        
        # SP cost for hunters
        if player.war_class == 'hunter' and not player.has_gerkin:
            sp_cost = 10
            if player.sp_current < sp_cost:
                player.message(f"You need {sp_cost} spell points to follow.")
                return
            player.sp_current -= sp_cost
        
        player.following = target
        player.message(f"You begin following {target.name}.")
        target.message(f"{player.name} begins following you!")
    
    def lose(self, player, params=None):
        """lose - Try to lose someone following you"""
        # Check if anyone is following this player
        followers = []
        for p in self.game_state.list_players():
            if getattr(p, 'following', None) == player:
                followers.append(p)
        
        if not followers:
            player.message("No one is following you.")
            return
        
        # 25% chance to lose each follower
        lost = []
        for follower in followers:
            if random.random() < 0.25:
                follower.following = None
                follower.message(f"You lose track of {player.name}!")
                lost.append(follower.name)
        
        if lost:
            player.message(f"You successfully lose: {', '.join(lost)}")
        else:
            player.message("You fail to lose your followers.")
    
    def gerkin_command(self, player, params=None):
        """gerkin kill <player> - Use Gerkin's power to hunt"""
        if not player.has_gerkin:
            player.message("You don't have the Spirit of Gerkin.")
            return
        
        if not params or not params.startswith("kill "):
            player.message("Usage: gerkin kill <player>")
            return
        
        # Check if gerkin power is ready
        last_used = self.gerkin_last_used.get(player.client.uuid, 0)
        cooldown = random.randint(120, 180)  # 2-3 minutes
        time_left = (last_used + cooldown) - time.time()
        
        if time_left > 0:
            player.message(f"Gerkin is impatient! Wait {int(time_left)} more seconds.")
            return
        
        target_name = params[5:].strip()
        
        # Find target
        target = None
        for p in self.game_state.list_players():
            if p.name.lower() == target_name.lower() and not p.is_ghost:
                target = p
                break
        
        if not target:
            player.message("That player is not alive in the war.")
            return
        
        # Teleport to target
        old_location = player._location
        player.move(target._location)
        
        # Announce with yellow if ANSI enabled
        if player.ansi_enabled and hasattr(player, 'ansi_manager'):
            msg = player.ansi_manager.color_text(
                f"Gerkin teleports you to {target.name}!",
                'yellow'
            )
            player.message(msg)
            
            target_msg = player.ansi_manager.color_text(
                f"{player.name} appears with the power of Gerkin!",
                'yellow'
            )
        else:
            player.message(f"Gerkin teleports you to {target.name}!")
            target_msg = f"{player.name} appears with the power of Gerkin!"
        
        target.message(target_msg)
        
        # Auto-follow
        player.following = target
        player.message(f"You begin following {target.name}.")
        
        # Update last used time
        self.gerkin_last_used[player.client.uuid] = time.time()
        
        # Set up 30-second timer to stop helping
        def stop_gerkin_help():
            if player.following == target:
                player.following = None
                if player.ansi_enabled and hasattr(player, 'ansi_manager'):
                    msg = player.ansi_manager.color_text(
                        "Gerkin grows bored and stops helping you!",
                        'yellow'
                    )
                else:
                    msg = "Gerkin grows bored and stops helping you!"
                player.message(msg)
        
        timer = threading.Timer(30.0, stop_gerkin_help)
        timer.start()
        
        # Store timer to cancel if needed
        if player.client.uuid in self.gerkin_timers:
            self.gerkin_timers[player.client.uuid].cancel()
        self.gerkin_timers[player.client.uuid] = timer
    
    def gate(self, player, params=None):
        """gate <teammate> - Teleport to teammate (mage only)"""
        if player.war_class != 'mage':
            player.message("Only mages can gate to teammates.")
            return
        
        if not params:
            player.message("Gate to whom?")
            return
        
        # Check SP cost
        sp_cost = 50
        if player.sp_current < sp_cost:
            player.message(f"You need {sp_cost} spell points to gate.")
            return
        
        # Find teammate
        target = None
        for p in self.game_state.list_players():
            if (p.name.lower() == params.lower() and 
                not p.is_ghost and 
                p.team == player.team):
                target = p
                break
        
        if not target:
            player.message("That teammate is not alive in the war.")
            return
        
        # Check if target room allows teleportation
        target_room = self.rooms.get(target._location)
        if target_room and getattr(target_room, 'no_teleport', False):
            player.message("You cannot gate to that location.")
            return
        
        # Perform gate
        player.sp_current -= sp_cost
        player.move(target._location)
        player.message(f"You gate to {target.name}!")
        target.message(f"{player.name} gates to your location!")
    
    def fireball(self, player, params=None):
        """fireball <target> - Cast fireball spell (mage only)"""
        if player.war_class != 'mage':
            player.message("Only mages can cast fireball.")
            return
        
        if not params:
            player.message("Cast fireball at whom?")
            return
        
        # Check SP cost
        sp_cost = 30
        if player.sp_current < sp_cost:
            player.message(f"You need {sp_cost} spell points to cast fireball.")
            return
        
        # Find target
        target = self.find_target_in_room(player, params)
        
        if not target:
            player.message("They aren't here.")
            return
        
        # Check if can attack (team restrictions etc)
        can_atk, reason = self.combat_manager.can_attack(player, target)
        if not can_atk:
            player.message(reason)
            return
        
        # Cast fireball
        player.sp_current -= sp_cost
        damage = random.randint(40, 80)  # Fireball damage
        
        # Apply damage
        killed = self.combat_manager.apply_damage(target, damage)
        
        # Messages
        player.message(f"You cast a fireball at {target.name} for {damage} damage!")
        target.message(f"{player.name} blasts you with a fireball for {damage} damage!")
        
        # Room message
        self.broadcast_to_room(player, 
            f"{player.name} blasts {target.name} with a fireball!")
        
        # Handle death
        if killed:
            self.combat_manager.handle_death(player, target)