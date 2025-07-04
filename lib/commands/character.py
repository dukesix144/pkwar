"""Character information commands."""

from .base import BaseCommand
import time
import json
import os

class CharacterCommands(BaseCommand):
    """Commands for character information and statistics."""
    
    def score(self, player, params=None):
        """score - Show your character information"""
        title = player.get_title()
        
        output = []
        output.append(f" {player.name} the {title} ({player.alignment or 'neutral'})")
        
        # Stats in two columns
        output.append(f"Str: {player.abilities.get('STRENGTH', 50):>3} ({player.abilities.get('STRENGTH', 50)})    Level    : {player.get_level_title()} ({player.level}){' ' * 9}Exp    : {player.xp}")
        output.append(f"Dex: {player.abilities.get('DEXTERITY', 50):>3} ({player.abilities.get('DEXTERITY', 50)})    Age      : {self._format_age(player)}{' ' * 9}Money  : {player.coins}")
        output.append(f"Wis: {player.abilities.get('WISDOM', 50):>3} ({player.abilities.get('WISDOM', 50)})    Guild    : Adventurer{' ' * 12}Bank   : 0")
        output.append(f"Int: {player.abilities.get('INTELLIGENCE', 50):>3} ({player.abilities.get('INTELLIGENCE', 50)})    Status   : None{' ' * 18}Quests : 0(0/0/0)")
        output.append(f"Con: {player.abilities.get('CONSTITUTION', 50):>3} ({player.abilities.get('CONSTITUTION', 50)})    Arch foe : None")
        output.append(f"Cha: {player.abilities.get('CHARISMA', 50):>3} ({player.abilities.get('CHARISMA', 50)})    Best kill: {player.best_kill or 'None'}")
        output.append(f"Expl:{len(player.rooms_explored):>7}  Best solo: None")
        
        # Status bars
        output.append(f"Hps  : {player.current_hp:>5} / {player.max_hp:<5}  Deaths   : {player.deaths}{' ' * 16}You are: Sober")
        output.append(f"Sps  : {player.sp_current:>5} / {player.sp_max:<5}  Kills    : {player.kills}{' ' * 16}You are: Able to drink tons")
        output.append(f"Gps  :  None         Hunted by: No-one{' ' * 11}You are: Able to eat tons")
        output.append(f"Wimpy: {player.wimpy_percent:>5} ({player.wimpy_percent:>3}%)  Defense  : None")
        output.append("Resistances:   None  None  None  None  None  None  None  None  None  None")
        
        player.message("\n".join(output))

    def hp(self, player, params=None):
        """hp - Show your health and spell points"""
        player.message(f"HP: {player.current_hp}/{player.max_hp} SP: {player.sp_current}/{player.sp_max}")

    def stats(self, player, params=None):
        """stats - Show your ability statistics"""
        output = [f"Ability Stats for {player.name}"]
        output.append("Stat           Value  Real  Adj")
        output.append("-" * 31)
        
        for ability_name in ['STRENGTH', 'DEXTERITY', 'WISDOM', 'INTELLIGENCE', 'CONSTITUTION', 'CHARISMA']:
            value = player.abilities.get(ability_name, 50)
            output.append(f"{ability_name:<12} : {value:>5}  ({value})    -")
        
        output.append("You have no current modifications to your stats")
        player.message("\n".join(output))

    def who(self, player, params=None):
        """who - List all players online"""
        output = []
        output.append("----------------------==* PKWAR.ORG  *==----------------------")
        
        # Separate implementors and players
        implementors = []
        players = []
        
        for p in self.game_state.list_players():
            if p.implementor_level > 0:
                implementors.append(p)
            else:
                players.append(p)
        
        # Show implementors first
        if implementors:
            for imp in sorted(implementors, key=lambda x: -x.implementor_level):
                title = self._get_implementor_title(imp.implementor_level)
                area = self._get_implementor_area(imp.implementor_level)
                idle_str = f" [idle {self._format_idle_time(imp)}]" if getattr(imp, 'idle', False) else ""
                if getattr(imp, 'linkdead', False):
                    idle_str = f" [ld {self._format_idle_time(imp)}]"
                output.append(f" <{title:<10}> [{area}] {imp.name}{idle_str}")
        
        # Separator line
        if implementors and players:
            output.append("-" * 78)
        
        # Show players
        for p in sorted(players, key=lambda x: -x.level):
            status = ""
            
            # Check linkdead FIRST
            if getattr(p, 'linkdead', False):
                if p.is_ghost:
                    status = " (ghost) (linkdead)"
                else:
                    status = " (linkdead)"
            elif p.is_ghost:
                status = " (ghost)"
            elif getattr(p, 'idle', False):
                status = f" [idle {self._format_idle_time(p)}]"
            
            # Check if player is in another realm (war arena)
            if self.game_state.war_system.state == self.game_state.war_system.WarState.ACTIVE:
                if p._location.startswith('arena_'):
                    output.append(f">[ {p.level:>3} ]  << {p.name}@3s is in another realm{status}")
                else:
                    output.append(f" [ {p.level:>3} ]  {p.name} the {p.get_title()}{status}")
            else:
                output.append(f" [ {p.level:>3} ]  {p.name} the {p.get_title()}{status}")
        
        player.message("\n".join(output))

    def finger(self, player, params=None):
        """finger <player> - Get information about a player"""
        if not params:
            params = player.name
        
        # Find target player
        target = self.find_player_by_name(params)
        
        if not target:
            # Check if offline player exists - use .json extension
            if os.path.exists(f"lib/players/{params.lower()}.json"):
                # Load offline player data
                with open(f"lib/players/{params.lower()}.json", 'r') as f:
                    player_data = json.load(f)
                    
                output = []
                output.append(f"User: {player_data['name']} the {player_data.get('title', 'Unknown')}")
                output.append(f"In real life: {player_data.get('real_name', '???')}")
                output.append(f"Position: {player_data.get('title', 'Unknown')} (Level {player_data.get('level', 1)})")
                output.append(f"Age: {self._format_offline_age(player_data.get('age', 0))}")
                output.append(f"Email: {player_data.get('email', '???')}")
                output.append(f"Gender: {player_data.get('gender', 'Neuter').capitalize()}")
                
                if player_data.get('linked_enforcer'):
                    output.append(f"Alternate character: {player_data['linked_enforcer']}")
                
                # War stats from history
                if 'war_history' in player_data:
                    last_100, last_15 = self._calculate_war_stats(player_data['war_history'])
                    output.append(f"Last 100 wars: {last_100}")
                    output.append(f"Last  15 wars: {last_15}")
                
                # Login info
                if 'last_login_info' in player_data:
                    login_info = player_data['last_login_info']
                    output.append(f"Last login:  {login_info['time']} from {login_info.get('from', 'telnet')}")
                if 'last_logout' in player_data:
                    output.append(f"Last logout: {player_data['last_logout']}")
                
                output.append("No unread mail")  # TODO: Check mail system
                
                if player_data.get('plan'):
                    output.append(player_data['plan'])
                else:
                    output.append("No description")
                
                player.message("\n".join(output))
            else:
                player.message(f"No such player '{params}'")
            return
        
        # Online player
        output = []
        output.append(f"User: {target.name} the {target.get_title()}")
        output.append(f"In real life: {getattr(target, 'real_name', '???')}")
        output.append(f"Position: {target.get_title()} (Level {target.level})")
        output.append(f"Age: {self._format_age(target)}")
        output.append(f"Email: {target.email or '???'}")
        output.append(f"Gender: {target.gender.capitalize()}")
        
        if target.linked_enforcer:
            output.append(f"Alternate character: {target.linked_enforcer}")
        
        # War stats
        if hasattr(target, 'war_history'):
            last_100, last_15 = self._calculate_war_stats(target.war_history)
            output.append(f"Last 100 wars: {last_100}")
            output.append(f"Last  15 wars: {last_15}")
        
        # Status
        if target.is_ghost:
            output.append("Status: Ghost")
        else:
            output.append("Status: Alive")
        
        # Mail status
        if hasattr(self.game_state, 'mail_system'):
            mail_status = self.game_state.mail_system.get_unread_summary(target.name)
            output.append(mail_status)
        else:
            output.append("No unread mail")
        
        if target.plan:
            output.append(target.plan)
        else:
            output.append("No description")
        
        player.message("\n".join(output))

    def history(self, player, params=None):
        """history [player] - Show last 15 wars for a player"""
        # Default to self
        target_name = params if params else player.name
        
        # Find target
        target = self.find_player_by_name(target_name)
        
        if not target:
            # Try loading offline player - use .json extension
            player_file = f"lib/players/{target_name.lower()}.json"
            if os.path.exists(player_file):
                with open(player_file, 'r') as f:
                    player_data = json.load(f)
                war_history = player_data.get('war_history', [])
                name = player_data['name']
            else:
                player.message(f"No such player '{target_name}'")
                return
        else:
            war_history = getattr(target, 'war_history', [])
            name = target.name
        
        if not war_history:
            player.message(f"{name} has no war history.")
            return
        
        # Show last 15 wars
        output = []
        output.append(f"{name}'s last 15 wars (first is most recent):")
        output.append("")
        output.append(" # War End Time   T W/D   C   K (KV)   DI     DT     Race         Class")
        output.append("-- -------------- - ----- --- -------- ------ ------ ------------ ------------")
        
        # Get last 15 wars
        recent_wars = war_history[-15:]
        recent_wars.reverse()  # Most recent first
        
        totals = {'coins': 0, 'kills': 0, 'kill_value': 0, 'damage_in': 0, 'damage_out': 0}
        wins = 0
        
        for i, war in enumerate(recent_wars, 1):
            end_time = time.strftime('%m/%d/%y %H:%M', time.localtime(war['end_time']))
            war_type = war.get('type', 'F')[0].upper()  # F=FFA, T=Team, B=BvR
            result = 'Win' if war.get('won', False) else 'Death'
            if result == 'Win':
                wins += 1
            
            coins = war.get('coins', 0)
            kills = war.get('kills', 0)
            kill_value = war.get('kill_value', 0)
            damage_in = war.get('damage_in', 0)
            damage_out = war.get('damage_out', 0)
            race = war.get('race', 'Human')[:12]  # Truncate to fit
            war_class = war.get('class', 'None')[:12]
            
            totals['coins'] += coins
            totals['kills'] += kills
            totals['kill_value'] += kill_value
            totals['damage_in'] += damage_in
            totals['damage_out'] += damage_out
            
            output.append(f"{i:2} {end_time} {war_type} {result:<5} {coins:<3} {kills:<1} ({kill_value:<3}) "
                         f"{damage_in:<6} {damage_out:<6} {race:<12} {war_class:<12}")
        
        # Totals and averages
        output.append("-- -------------- - ----- --- -------- ------ ------ ------------ ------------")
        total_wars = len(recent_wars)
        output.append(f"To{' '*27} {totals['coins']:<3} {totals['kills']:<1} ({totals['kill_value']:<3}) "
                     f"{totals['damage_in']:<6} {totals['damage_out']:<6}")
        
        # Averages
        if total_wars > 0:
            avg_coins = totals['coins'] // total_wars
            avg_kills = totals['kills'] / total_wars
            avg_kv = totals['kill_value'] // total_wars
            avg_di = totals['damage_in'] // total_wars
            avg_do = totals['damage_out'] // total_wars
            
            output.append(f"Av{' '*27} {avg_coins:<3} {int(avg_kills):<1} ({avg_kv:<3}) "
                         f"{avg_di:<6} {avg_do:<6}")
        
        player.message("\n".join(output))

    def coins(self, player, params=None):
        """coins - Show how much money you have"""
        player.message(f"You are carrying {player.coins} coins in loose change.")

    # Helper methods
    def _format_age(self, player):
        """Format player age for display."""
        # Ensure last_login is a float timestamp
        if hasattr(player, 'last_login') and player.last_login:
            if isinstance(player.last_login, (int, float)):
                total_seconds = int(player.age + (time.time() - player.last_login))
            else:
                # If it's still a string somehow, just use age
                total_seconds = int(player.age)
        else:
            total_seconds = int(player.age)
            
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{days} d {hours} h {minutes} m"
    
    def _format_offline_age(self, age_seconds):
        """Format age for offline players."""
        total_seconds = int(age_seconds)
        weeks = total_seconds // 604800
        days = (total_seconds % 604800) // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{weeks}w {days}d {hours}h {minutes}m {seconds}s"
    
    def _format_idle_time(self, player):
        """Format idle/ld time for who list."""
        if hasattr(player, 'last_activity'):
            idle_seconds = int(time.time() - player.last_activity)
        else:
            idle_seconds = 0
        
        if idle_seconds < 60:
            return f"{idle_seconds}s"
        elif idle_seconds < 3600:
            return f"{idle_seconds // 60}m"
        else:
            return f"{idle_seconds // 3600}h"
    
    def _get_implementor_title(self, level):
        """Get implementor title by level."""
        titles = {
            1: "High Wizar",
            2: "Ascendant",
            3: "Solar",
            4: "Elder",
            5: "Archon"
        }
        return titles.get(level, "Implementor")
    
    def _get_implementor_area(self, level):
        """Get implementor area of responsibility."""
        areas = {
            1: "Areas",
            2: "Guilds",
            3: "Mudlib",
            4: "Balance",
            5: "Mudlib"
        }
        return areas.get(level, "General")
    
    def _calculate_war_stats(self, war_history):
        """Calculate war statistics for finger command."""
        if not war_history:
            return "0 D 0 W 0.00 C/D 0 (0) K 0k ADI 0k ADT", "0 D 0 W 0.00 C/D 0 (0) K 0k ADI 0k ADT"
        
        # Last 100 wars
        last_100 = war_history[-100:] if len(war_history) >= 100 else war_history
        deaths_100 = sum(1 for w in last_100 if not w.get('won', False))
        wins_100 = sum(1 for w in last_100 if w.get('won', False))
        coins_100 = sum(w.get('coins', 0) for w in last_100)
        kills_100 = sum(w.get('kills', 0) for w in last_100)
        kill_value_100 = sum(w.get('kill_value', 0) for w in last_100)
        damage_in_100 = sum(w.get('damage_in', 0) for w in last_100)
        damage_out_100 = sum(w.get('damage_out', 0) for w in last_100)
        cpd_100 = coins_100 / deaths_100 if deaths_100 > 0 else 0
        
        last_100_str = (f"{deaths_100} D {wins_100} W {cpd_100:.2f} C/D "
                       f"{kills_100} ({kill_value_100}) K "
                       f"{damage_in_100/1000:.2f}k ADI {damage_out_100/1000:.2f}k ADT")
        
        # Last 15 wars
        last_15 = war_history[-15:] if len(war_history) >= 15 else war_history
        deaths_15 = sum(1 for w in last_15 if not w.get('won', False))
        wins_15 = sum(1 for w in last_15 if w.get('won', False))
        coins_15 = sum(w.get('coins', 0) for w in last_15)
        kills_15 = sum(w.get('kills', 0) for w in last_15)
        kill_value_15 = sum(w.get('kill_value', 0) for w in last_15)
        damage_in_15 = sum(w.get('damage_in', 0) for w in last_15)
        damage_out_15 = sum(w.get('damage_out', 0) for w in last_15)
        cpd_15 = coins_15 / deaths_15 if deaths_15 > 0 else 0
        
        last_15_str = (f"{deaths_15} D {wins_15} W {cpd_15:.2f} C/D "
                      f"{kills_15} ({kill_value_15:>3}) K "
                      f"{damage_in_15/1000:.2f}k ADI {damage_out_15/1000:.2f}k ADT")
        
        return last_100_str, last_15_str
