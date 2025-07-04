"""Player settings and configuration commands."""

from .base import BaseCommand
from lib.ansi import AnsiManager

class SettingsCommands(BaseCommand):
    """Commands for player settings and preferences."""
    
    def ansi(self, player, params=None):
        """ansi on/off/full - Configure ANSI colors"""
        if not params:
            status = "on" if player.ansi_enabled else "off"
            player.message(f"ANSI is currently: {status}")
            player.message("Usage: ansi on/off/full/colors/default/wipe")
            return
        
        if not hasattr(player, 'ansi_manager'):
            player.ansi_manager = AnsiManager(player)
        
        cmd = params.lower().split()[0]
        
        if cmd == 'on':
            player.ansi_manager.enable()
            player.ansi_enabled = True
        elif cmd == 'full':
            player.ansi_manager.enable(full=True)
            player.ansi_enabled = True
        elif cmd == 'off':
            player.ansi_manager.disable()
            player.ansi_enabled = False
        elif cmd == 'colors':
            output = player.ansi_manager.show_colors()
            player.message(output)
        elif cmd == 'default':
            player.ansi_manager.set_default()
        elif cmd == 'wipe':
            player.ansi_manager.wipe()
            player.ansi_enabled = False
        else:
            player.message(f"Unknown ansi command: {cmd}")

    def aset(self, player, params=None):
        """aset <variable> <color> - Set ANSI color for variable"""
        if not params:
            if hasattr(player, 'ansi_manager'):
                output = player.ansi_manager.show_variables()
                player.message(output)
            else:
                player.message("ANSI not configured. Use 'ansi on' first.")
            return
        
        parts = params.split()
        if len(parts) != 2:
            player.message("Usage: aset <variable> <color>")
            return
        
        var, color = parts
        
        if not hasattr(player, 'ansi_manager'):
            player.ansi_manager = AnsiManager(player)
        
        if player.ansi_manager.set_variable(var, color):
            player.message(f"Set {var} to {color}")
        else:
            player.message(f"Invalid color: {color}")

    def wimpy(self, player, params=None):
        """wimpy <percent> - Set wimpy percentage"""
        if not params:
            player.message(f"Current wimpy: {player.wimpy_percent}%")
            return
        
        try:
            percent = int(params.strip('%'))
            if 0 <= percent <= 100:
                player.wimpy_percent = percent
                player.message(f"Wimpy set to {percent}%")
            else:
                player.message("Wimpy must be between 0 and 100")
        except ValueError:
            player.message("Usage: wimpy <percent>")

    def set_plan(self, player, params=None):
        """plan <message> - Set your one-line plan"""
        if not params:
            player.plan = ""
            player.message("Plan cleared.")
        else:
            player.plan = params[:80]  # Limit to 80 chars
            player.message(f"Plan set to: {player.plan}")

    def chfn(self, player, params=None):
        """chfn - Change finger information"""
        player.message("=== Change Finger Information ===")
        player.message("1. Real name (currently: " + getattr(player, 'real_name', 'Not set') + ")")
        player.message("2. Email (currently: " + getattr(player, 'email', 'Not set') + ")")
        player.message("Enter choice (1-2) or 'q' to quit:")
        
        # Set up chfn state - this will be handled by main Commands class
        player.chfn_mode = True
        return {'chfn_mode': True}