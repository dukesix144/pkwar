"""War-related commands."""

from .base import BaseCommand
import time

class WarCommands(BaseCommand):
    """Commands for war system interaction."""
    
    def __init__(self, game_state):
        super().__init__(game_state)
        self.war_system = game_state.war_system
    
    def war_toggle(self, player, params=None):
        """war on/off - Toggle war participation"""
        if not params or params.lower() not in ['on', 'off']:
            status = "on" if player.war_enabled else "off"
            player.message(f"War participation is currently: {status}")
            player.message("Usage: war on/off")
            return
        
        if params.lower() == 'on':
            if not player.is_ghost:
                player.message("You can only enable war participation as a ghost.")
                return
            player.war_enabled = True
            player.message("War participation enabled. You will join the next war!")
        else:
            player.war_enabled = False
            player.message("War participation disabled.")

    def push_button(self, player, params=None):
        """push button - Start a war (in warroom only)"""
        if params != "button":
            player.message("Push what?")
            return
        
        if player._location != 'warroom':
            player.message("You don't see any button here.")
            return
        
        if not player.is_ghost:
            player.message("Only ghosts can push the war button.")
            return
        
        success, message = self.war_system.start_war_countdown(player.name)
        if not success:
            player.message(message)

    def alive(self, player, params=None):
        """alive - List living players during war"""
        if self.war_system.state not in [
            self.war_system.WarState.ACTIVE,
            self.war_system.WarState.ARENA_SHRINKING
        ]:
            player.message("No war in progress.")
            return
        
        alive_data = self.war_system.get_alive_list()
        
        if isinstance(alive_data, list):
            # Free for all
            output = ["=== Alive Players ==="]
            for p in alive_data:
                gerkin = " *" if p['has_gerkin'] else ""
                output.append(f"{p['name']}{gerkin} (Level {p['level']})")
        else:
            # Team war
            output = ["=== Alive Players by Team ==="]
            for team, players in alive_data.items():
                output.append(f"\n{team.upper()}:")
                for p in players:
                    gerkin = " *" if p['has_gerkin'] else ""
                    class_str = f" [{p['class']}]" if p['class'] != 'none' else ""
                    output.append(f"  {p['name']}{gerkin} (Level {p['level']}){class_str}")
        
        player.message("\n".join(output))

    def warstatus(self, player, params=None):
        """warstatus - Show current war status"""
        status = self.war_system.get_war_status()
        player.message(status)

    def vote(self, player, params=None):
        """vote <ffa|team|bvr> - Vote for war type"""
        if not params:
            player.message("Vote for: ffa (free for all), team, or bvr (best vs rest)")
            return
        
        if self.war_system.vote_war_type(player.name, params):
            player.message(f"You voted for {params}.")
        else:
            player.message("Invalid vote. Choose: ffa, team, or bvr")
    
    def select_class(self, player, params=None):
        """class <fighter|kamikaze|mage|hunter> - Select war class"""
        if player.is_ghost:
            player.message("You must be alive to select a class.")
            return
        
        if self.war_system.state != self.war_system.WarState.ACTIVE:
            player.message("You can only select a class during war preparation.")
            return
        
        if self.war_system.war_type == self.war_system.WarType.FREE_FOR_ALL:
            player.message("Classes are only available in team and best vs rest wars.")
            return
        
        if player.war_class:
            player.message(f"You are already a {player.war_class}!")
            return
        
        if not params:
            player.message("Choose class: fighter, kamikaze, mage, hunter")
            return
        
        # Pass to main command handler which has the selection logic
        return {'select_class': params}  # Signal to handle in main Commands

    def watch_war(self, player, params=None):
        """watch - Watch the war from observation room"""
        if player._location != 'observation_room':
            player.message("You can only watch wars from the observation room.")
            return
        
        if self.war_system.state != self.war_system.WarState.ACTIVE:
            player.message("There is no war in progress to watch.")
            return
        
        player.watching_war = True
        player.message("You begin watching the war on the crystal screens.")
        player.message("All combat in the war will be displayed here.")
    
    def stop_watching(self, player, params=None):
        """stop - Stop watching the war"""
        if not getattr(player, 'watching_war', False):
            player.message("You're not watching anything.")
            return
        
        player.watching_war = False
        player.message("You stop watching the crystal screens.")
    
    def show_wars(self, player, params=None):
        """wars - Show recent war history"""
        if player._location != 'records_room':
            player.message("You can only view war records in the records room.")
            return
        
        count = 10  # Default
        if params:
            try:
                count = int(params)
            except ValueError:
                player.message("Usage: wars <number>")
                return
        
        history = self.war_system.war_history[-count:]
        
        if not history:
            player.message("No wars have been fought yet.")
            return
        
        output = ["=== Recent Wars ==="]
        output.append(f"{'Date':<20} {'Type':<10} {'Winner':<15} {'Duration':<10}")
        output.append("-" * 60)
        
        for war in reversed(history):
            date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(war['time']))
            duration = f"{int(war['duration'])}s"
            output.append(f"{date_str:<20} {war['type']:<10} {war['winner']:<15} {duration:<10}")
        
        player.message("\n".join(output))
    
    def topkillers(self, player, params=None):
        """topkillers - Show all-time kill leaders"""
        if player._location != 'records_room':
            player.message("You can only view records in the records room.")
            return
        
        # Gather kill stats from all players
        kill_stats = []
        
        # Check online players
        for p in self.game_state.list_players():
            kill_stats.append((p.name, p.kills, True))
        
        # Check offline players
        import os
        import json
        player_dir = "lib/players"
        if os.path.exists(player_dir):
            for filename in os.listdir(player_dir):
                if filename.endswith('.py'):
                    name = filename[:-3]
                    # Skip online players
                    if any(p.name.lower() == name for p in self.game_state.list_players()):
                        continue
                    
                    # Load player data
                    try:
                        with open(os.path.join(player_dir, filename), 'r') as f:
                            data = json.load(f)
                        kills = data.get('kills', 0)
                        if kills > 0:
                            kill_stats.append((data['name'], kills, False))
                    except:
                        pass
        
        # Sort by kills
        kill_stats.sort(key=lambda x: x[1], reverse=True)
        
        output = ["=== Top Killers ==="]
        output.append(f"{'Rank':<6} {'Name':<20} {'Kills':<10} {'Status':<10}")
        output.append("-" * 50)
        
        for i, (name, kills, online) in enumerate(kill_stats[:20], 1):
            status = "ONLINE" if online else ""
            output.append(f"{i:<6} {name:<20} {kills:<10} {status:<10}")
        
        player.message("\n".join(output))