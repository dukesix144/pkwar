"""System commands."""

from .base import BaseCommand

class SystemCommands(BaseCommand):
    """Basic system commands."""
    
    def quit(self, player, params=None):
        """quit - Disconnect from the game"""
        player.message("Thanks for playing! Come back soon!")
        self.game_state.server.disconnect(player.client)

    def help(self, player, params=None):
        """help - Show available commands"""
        if params:
            # Show help for specific command
            # This needs access to the main command dictionary
            # which will be passed from main Commands class
            player.message(f"Help for '{params}' - check main command handler")
            return {'help_lookup': params}
        
        player.message("=== Available Commands ===")
        player.message("System: help, quit, commands, mudinfo")
        player.message("Communication: say ('), tell, shout, channels")
        player.message("Movement: look (l), go <dir>, n/s/e/w/u/d, ne/nw/se/sw")
        player.message("Character: score, hp, stats, who, finger, inventory (i), eq, history")
        player.message("Combat: kill (k) <target>, blick, follow, lose")
        player.message("Items: get, drop, give, wear, wield, remove, equip all, use, heal")
        player.message("Shop: list, buy, sell, value, keep, unkeep")
        player.message("War: war on/off, push button, alive, warstatus, vote, class")
        player.message("   : watch (obs room), wars/topkillers (records room)")
        player.message("Mail: mail <player>, read <id>, delete <id>")
        player.message("Social: emote (:), soul <feeling>, feelings")
        player.message("Settings: ansi, wimpy, plan, chfn")
        player.message("Explorer: explorer, explorers, arealist")
        player.message("Type 'help <command>' for more info")
    
    def mudinfo(self, player, params=None):
        """mudinfo - Show MUD information"""
        output = []
        output.append("PKMUD is currently operating from the site:")
        output.append("pkmud.org (127.0.0.1), port 2222")
        output.append("")
        output.append("The mud is currently running PyMUD Version: 1.0")
        output.append("Based on the LPMud look and feel")
        player.message("\n".join(output))