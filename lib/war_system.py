import time
import random
import threading
from typing import List, Dict, Optional
from enum import Enum

class WarSystem:
    """Manages the war game mechanics."""
    
    # Define enums as class attributes so they can be accessed as war_system.WarState
    class WarType(Enum):
        FREE_FOR_ALL = "free for all"
        TEAM = "team"
        BEST_VS_REST = "best vs rest"
    
    class WarState(Enum):
        INACTIVE = "inactive"
        COUNTDOWN = "countdown"
        ACTIVE = "active"
        ARENA_SHRINKING = "arena_shrinking"
        ENDING = "ending"
    
    def __init__(self, game_state):
        self.game_state = game_state
        self.state = self.WarState.INACTIVE
        self.war_type = None
        self.countdown_start = None
        self.war_start_time = None
        self.arena_size = 9  # 9x9 down to 1x1
        self.last_shrink_time = None
        self.participants = []
        self.teams = {'team1': [], 'team2': []}
        self.votes = {}  # player_name: WarType
        self.last_war_end = 0
        self.war_history = []
        self.first_blood = False
        self.gerkin_holder = None
        
        # Timer threads
        self.countdown_timer = None
        self.arena_timer = None
        self.reboot_timer = None
    
    def can_start_war(self) -> tuple[bool, str]:
        """Check if war can be started."""
        # Check time since last reboot
        if time.time() - self.last_war_end < 60:
            return False, "Must wait 60 seconds between wars."
        
        # Count eligible players
        eligible_players = [p for p in self.game_state.list_players() 
                           if p.war_enabled and p.is_ghost]
        
        if len(eligible_players) < 2:
            return False, "Need at least 2 players with 'war on' to start."
        
        if self.state != self.WarState.INACTIVE:
            return False, "War already in progress."
        
        return True, ""
    
    def start_war_countdown(self, player_name: str):
        """Start the 60-second war countdown."""
        can_start, reason = self.can_start_war()
        if not can_start:
            return False, reason
        
        self.state = self.WarState.COUNTDOWN
        self.countdown_start = time.time()
        
        # Determine war type based on votes
        self.war_type = self._determine_war_type()
        
        # Announce countdown
        self.game_state.broadcast(f"{player_name} has pushed the war button!")
        self.game_state.broadcast(f"WAR TYPE: {self.war_type.value.upper()}")
        self.game_state.broadcast("60 seconds until war begins!")
        self.game_state.broadcast("Set 'war on' to participate!")
        
        # Start countdown timer
        self.countdown_timer = threading.Timer(60.0, self._start_war)
        self.countdown_timer.start()
        
        # Periodic countdown announcements
        for seconds in [30, 10, 5, 3, 2, 1]:
            threading.Timer(60 - seconds, self._announce_countdown, args=[seconds]).start()
        
        return True, ""
    
    def _announce_countdown(self, seconds: int):
        """Announce countdown remaining."""
        if self.state == self.WarState.COUNTDOWN:
            self.game_state.broadcast(f"{seconds} seconds until war!")
    
    def _determine_war_type(self) -> 'WarSystem.WarType':
        """Determine war type based on votes and RNG."""
        if not self.votes:
            return random.choice(list(self.WarType))
        
        # Count votes
        vote_counts = {}
        for vote in self.votes.values():
            vote_counts[vote] = vote_counts.get(vote, 0) + 1
        
        # Add some RNG
        war_types = []
        for war_type, count in vote_counts.items():
            war_types.extend([war_type] * count)
        
        # Add each type once more for RNG
        war_types.extend(list(self.WarType))
        
        return random.choice(war_types)
    
    def _start_war(self):
        """Actually start the war."""
        if self.state != self.WarState.COUNTDOWN:
            return
        
        # Gather participants
        self.participants = [p for p in self.game_state.list_players() 
                           if p.war_enabled and p.is_ghost]
        
        if len(self.participants) < 2:
            self.game_state.broadcast("Not enough players! War cancelled.")
            self.state = self.WarState.INACTIVE
            return
        
        self.state = self.WarState.ACTIVE
        self.war_start_time = time.time()
        self.first_blood = False
        
        # Set up teams if needed
        if self.war_type == self.WarType.TEAM:
            self._setup_teams()
        elif self.war_type == self.WarType.BEST_VS_REST:
            self._setup_best_vs_rest()
        
        # Make players alive and spawn them
        for player in self.participants:
            player.make_alive()
            
            # Ask for class selection in team/best vs rest
            if self.war_type in [self.WarType.TEAM, self.WarType.BEST_VS_REST]:
                player.message("Choose your class: fighter, kamikaze, mage, hunter")
                player.message("You have 30 seconds to choose or you'll be classless.")
                # TODO: Handle class selection timeout
            
            # Spawn on random backbone room
            backbone_room = self._get_random_backbone_room()
            player.move(backbone_room)
            player.message("The war has begun! Kill or be killed!")
        
        self.game_state.broadcast("THE WAR HAS BEGUN!")
        
        # Start arena shrink timer
        shrink_time = 900 if len(self.participants) < 30 else 1800  # 15 or 30 minutes
        self.arena_timer = threading.Timer(shrink_time, self._shrink_arena)
        self.arena_timer.start()
    
    def _setup_teams(self):
        """Set up teams for team war."""
        # Sort by level for balance
        sorted_players = sorted(self.participants, key=lambda p: p.level, reverse=True)
        
        # Alternate assignment for balance
        for i, player in enumerate(sorted_players):
            if i % 2 == 0:
                self.teams['team1'].append(player)
                player.team = 'team1'
            else:
                self.teams['team2'].append(player)
                player.team = 'team2'
        
        # Announce teams
        self.game_state.broadcast("TEAM 1: " + ", ".join([p.name for p in self.teams['team1']]))
        self.game_state.broadcast("TEAM 2: " + ", ".join([p.name for p in self.teams['team2']]))
    
    def _setup_best_vs_rest(self):
        """Set up enforcers vs players."""
        enforcers = [p for p in self.participants if p.linked_enforcer]
        players = [p for p in self.participants if not p.linked_enforcer]
        
        for enforcer in enforcers:
            enforcer.team = 'enforcers'
            self.teams['team1'].append(enforcer)
        
        for player in players:
            player.team = 'players'
            self.teams['team2'].append(player)
        
        self.game_state.broadcast("ENFORCERS: " + ", ".join([p.name for p in enforcers]))
        self.game_state.broadcast("PLAYERS: " + ", ".join([p.name for p in players]))
    
    def _get_random_backbone_room(self) -> str:
        """Get random room from the backbone."""
        # TODO: Implement actual backbone rooms
        backbone_rooms = [f"backbone_{i}" for i in range(1, 31)]
        return random.choice(backbone_rooms)
    
    def _shrink_arena(self):
        """Shrink the arena and move players."""
        if self.state != self.WarState.ACTIVE:
            return
        
        self.state = self.WarState.ARENA_SHRINKING
        self.arena_size -= 1
        
        if self.arena_size < 1:
            self.arena_size = 1
        
        self.game_state.broadcast(f"DEATH grows impatient! Arena shrinking to {self.arena_size}x{self.arena_size}!")
        
        # Move all alive players to arena
        alive_players = [p for p in self.participants if not p.is_ghost]
        for player in alive_players:
            arena_room = self._get_arena_room()
            player.move(arena_room)
            player.message("You have been transported to the arena!")
        
        # Continue shrinking
        if self.arena_size > 1:
            shrink_interval = random.randint(120, 180)  # 2-3 minutes
            self.arena_timer = threading.Timer(shrink_interval, self._shrink_arena)
            self.arena_timer.start()
        else:
            # Release dogs of war after 2-3 minutes in 1x1
            dog_timer = random.randint(120, 180)
            threading.Timer(dog_timer, self._release_dogs).start()
        
        self.state = self.WarState.ACTIVE
    
    def _get_arena_room(self) -> str:
        """Get room in current arena size."""
        x = random.randint(1, self.arena_size)
        y = random.randint(1, self.arena_size)
        return f"arena_{x}_{y}"
    
    def _release_dogs(self):
        """Release dogs of war in final arena."""
        if self.state != self.WarState.ACTIVE or self.arena_size != 1:
            return
        
        self.game_state.broadcast("DEATH releases the DOGS OF WAR!")
        
        alive_players = [p for p in self.participants if not p.is_ghost]
        for player in alive_players:
            # TODO: Spawn dog to attack player
            player.message("A vicious war dog appears and attacks you!")
    
    def handle_kill(self, killer, victim):
        """Handle a player kill during war."""
        if self.state != self.WarState.ACTIVE:
            return
        
        # Announce kill
        self.game_state.broadcast(f"{killer.name} just killed {victim.name}!")
        
        # Handle first blood / Gerkin
        if not self.first_blood:
            self.first_blood = True
            if self.war_type == self.WarType.FREE_FOR_ALL:
                self.grant_gerkin(killer)
            elif self.war_type in [self.WarType.TEAM, self.WarType.BEST_VS_REST]:
                # First kill from each team gets gerkin
                if killer.team == 'team1' and not any(p.has_gerkin for p in self.teams['team1']):
                    self.grant_gerkin(killer)
                elif killer.team == 'team2' and not any(p.has_gerkin for p in self.teams['team2']):
                    self.grant_gerkin(killer)
        
        # Transfer Gerkin if victim had it
        if victim.has_gerkin and not killer.has_gerkin:
            victim.has_gerkin = False
            self.grant_gerkin(killer)
            self.game_state.broadcast(f"The spirit of Gerkin transfers to {killer.name}!")
        
        # Add blood to killer's inventory
        killer.blood_inventory.append(victim.name)
        killer.message(f"You collect the blood of {victim.name}.")
        
        # Update stats
        killer.add_kill(victim.name)
        
        # Make victim a ghost
        victim.die()
        
        # Check for war end
        self.check_war_end()
    
    def grant_gerkin(self, player):
        """Grant the spirit of Gerkin to a player."""
        player.has_gerkin = True
        self.gerkin_holder = player
        player.message("The spirit of Gerkin descends from the sky to aid you!")
        self.game_state.broadcast(f"{player.name} has been blessed by the spirit of Gerkin!")
    
    def check_war_end(self):
        """Check if the war should end."""
        if self.state != self.WarState.ACTIVE:
            return
        
        alive_players = [p for p in self.participants if not p.is_ghost]
        
        if self.war_type == self.WarType.FREE_FOR_ALL:
            if len(alive_players) <= 1:
                self.end_war(alive_players[0] if alive_players else None)
        
        elif self.war_type == self.WarType.TEAM:
            alive_team1 = [p for p in alive_players if p.team == 'team1']
            alive_team2 = [p for p in alive_players if p.team == 'team2']
            
            if not alive_team1:
                self.end_war(None, winning_team='team2')
            elif not alive_team2:
                self.end_war(None, winning_team='team1')
        
        elif self.war_type == self.WarType.BEST_VS_REST:
            alive_enforcers = [p for p in alive_players if p.team == 'enforcers']
            alive_players_team = [p for p in alive_players if p.team == 'players']
            
            if not alive_enforcers:
                self.end_war(None, winning_team='players')
            elif not alive_players_team:
                self.end_war(None, winning_team='enforcers')
    
    def end_war(self, winner=None, winning_team=None):
        """End the war and prepare for reboot."""
        self.state = self.WarState.ENDING
        
        # Cancel timers
        if self.arena_timer:
            self.arena_timer.cancel()
        
        # Announce winner
        if winner:
            self.game_state.broadcast(f"{winner.name} has won the war!")
            winner.kills += 5  # Bonus for winning
        elif winning_team:
            self.game_state.broadcast(f"Team {winning_team.upper()} has won the war!")
            # Give bonus to winning team
            for player in self.participants:
                if player.team == winning_team:
                    player.kills += 1
        
        # Save war history
        war_record = {
            'time': time.time(),
            'type': self.war_type.value,
            'participants': [p.name for p in self.participants],
            'winner': winner.name if winner else winning_team,
            'duration': time.time() - self.war_start_time
        }
        self.war_history.append(war_record)
        
        # Update total wars stat
        if hasattr(self.game_state, 'auth'):
            self.game_state.auth.stats['total_wars'] += 1
            self.game_state.auth.save_stats()
        
        # Reset war state
        self.state = self.WarState.INACTIVE
        self.last_war_end = time.time()
        self.participants = []
        self.teams = {'team1': [], 'team2': []}
        self.first_blood = False
        self.gerkin_holder = None
        
        # Announce reboot
        self.game_state.broadcast("The mud will reboot in 60 seconds!")
        
        # Schedule reboot
        self.reboot_timer = threading.Timer(60.0, self._reboot_mud)
        self.reboot_timer.start()
        
        # Countdown announcements
        for seconds in [30, 10, 5, 3, 2, 1]:
            threading.Timer(60 - seconds, lambda s=seconds: 
                          self.game_state.broadcast(f"Rebooting in {s} seconds!")).start()
    
    def _reboot_mud(self):
        """Perform the actual reboot."""
        import os
        import sys
        
        self.game_state.broadcast("Rebooting NOW!")
        
        # Save all players
        for player in self.game_state.list_players():
            if hasattr(self.game_state, 'auth'):
                self.game_state.auth._save_player(player)
        
        # Reset boot login count
        if hasattr(self.game_state, 'auth'):
            self.game_state.auth.stats['boot_logins'] = 0
            self.game_state.auth.save_stats()
        
        # Clean up explorer sessions
        if hasattr(self.game_state, 'explorer_system'):
            for player in self.game_state.list_players():
                if player.exploration_session_id:
                    player.end_exploration_session()
        
        # Disconnect all players
        for player in self.game_state.list_players():
            player.message("=== MUD REBOOTING ===")
            self.game_state.server.disconnect(player.client)
        
        # Give server time to send final messages
        time.sleep(1)
        
        # Perform actual restart using execv
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def vote_war_type(self, player_name: str, war_type: str) -> bool:
        """Register a vote for war type."""
        war_type_map = {
            'ffa': self.WarType.FREE_FOR_ALL,
            'team': self.WarType.TEAM,
            'bvr': self.WarType.BEST_VS_REST,
            'best': self.WarType.BEST_VS_REST
        }
        
        if war_type.lower() not in war_type_map:
            return False
        
        self.votes[player_name] = war_type_map[war_type.lower()]
        return True
    
    def get_alive_list(self) -> List[Dict]:
        """Get list of alive players for 'alive' command."""
        if self.state not in [self.WarState.ACTIVE, self.WarState.ARENA_SHRINKING]:
            return []
        
        alive_players = [p for p in self.participants if not p.is_ghost]
        
        if self.war_type == self.WarType.FREE_FOR_ALL:
            return [{'name': p.get_display_name(), 
                    'level': p.level,
                    'has_gerkin': p.has_gerkin} for p in alive_players]
        else:
            # Organize by teams
            result = {
                'team1': [],
                'team2': []
            }
            for player in alive_players:
                team_data = {
                    'name': player.get_display_name(),
                    'level': player.level,
                    'class': player.war_class or 'none',
                    'has_gerkin': player.has_gerkin
                }
                result[player.team].append(team_data)
            return result
    
    def get_war_status(self) -> str:
        """Get current war status."""
        if self.state == self.WarState.INACTIVE:
            time_since = int(time.time() - self.last_war_end)
            if time_since < 60:
                return f"War cooldown: {60 - time_since} seconds remaining."
            else:
                return "No war in progress. Push the button to start!"
        elif self.state == self.WarState.COUNTDOWN:
            remaining = 60 - int(time.time() - self.countdown_start)
            return f"War starting in {remaining} seconds! Type: {self.war_type.value}"
        elif self.state == self.WarState.ACTIVE:
            duration = int(time.time() - self.war_start_time)
            alive_count = len([p for p in self.participants if not p.is_ghost])
            return f"War in progress! Type: {self.war_type.value}, Duration: {duration}s, Alive: {alive_count}"
        elif self.state == self.WarState.ARENA_SHRINKING:
            return f"Arena shrinking! Current size: {self.arena_size}x{self.arena_size}"
        elif self.state == self.WarState.ENDING:
            return "War ended! Rebooting soon..."
        
        return "Unknown war state."