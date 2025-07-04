"""Brief mode and combat brief commands."""

from .base import BaseCommand

class BriefCommands(BaseCommand):
    """Commands for brief mode settings."""
    
    def brief(self, player, params=None):
        """brief - Toggle brief mode for room descriptions"""
        if not params:
            # Show current brief status
            brief_status = getattr(player, 'brief_mode', False)
            mapping_status = getattr(player, 'show_mapping', False)
            
            status_text = "on" if brief_status else "off"
            mapping_text = "mapping" if mapping_status else "no mapping"
            
            player.message(f"Your brief setting is currently: [{status_text}, {mapping_text}]")
            if brief_status:
                player.message("  When traveling you will see the Short descriptions of rooms")
            else:
                player.message("  When traveling you will see the Long descriptions of rooms")
            
            if mapping_status:
                player.message("  and you will see the cardinal minimap.")
            else:
                player.message("  and you will not see the cardinal minimap.")
            
            return
        
        # Parse parameters
        parts = params.lower().split()
        
        if len(parts) == 1:
            # Simple on/off toggle
            if parts[0] == 'on':
                player.brief_mode = True
                player.message("Brief mode ON - You will see short room descriptions.")
            elif parts[0] == 'off':
                player.brief_mode = False
                player.message("Brief mode OFF - You will see full room descriptions.")
            else:
                player.message("Usage: brief [on|off] [yes|no]")
        
        elif len(parts) == 2:
            # Brief on/off with mapping yes/no
            brief_setting = parts[0]
            mapping_setting = parts[1]
            
            if brief_setting == 'on':
                player.brief_mode = True
            elif brief_setting == 'off':
                player.brief_mode = False
            else:
                player.message("Usage: brief [on|off] [yes|no]")
                return
            
            if mapping_setting == 'yes':
                player.show_mapping = True
            elif mapping_setting == 'no':
                player.show_mapping = False
            else:
                player.message("Usage: brief [on|off] [yes|no]")
                return
            
            brief_text = "on" if player.brief_mode else "off"
            mapping_text = "shown" if player.show_mapping else "hidden"
            player.message(f"Brief mode {brief_text}, mapping {mapping_text}.")
        
        else:
            player.message("Usage: brief [on|off] [yes|no]")
    
    def cbrief(self, player, params=None):
        """cbrief - Toggle combat brief mode"""
        if not params:
            # Show current combat brief status
            cbrief_mode = getattr(player, 'combat_brief', None)
            
            if not cbrief_mode:
                player.message("Combat brief is currently OFF.")
            elif cbrief_mode == 'full':
                player.message("Combat brief is ON [full] - showing no combat messages.")
            elif cbrief_mode == 'mo':
                player.message("Combat brief is ON [mo] - showing hits only, no misses.")
            else:
                player.message(f"Combat brief is ON [{cbrief_mode}].")
            
            return
        
        parts = params.lower().split()
        
        if parts[0] == 'off':
            player.combat_brief = None
            player.message("Combat brief OFF - showing all combat messages.")
        
        elif parts[0] == 'on':
            if len(parts) > 1:
                if parts[1] == 'full':
                    player.combat_brief = 'full'
                    player.message("Combat brief ON [full] - no combat messages shown.")
                elif parts[1] == 'mo':
                    player.combat_brief = 'mo'
                    player.message("Combat brief ON [mo] - misses hidden, hits shown.")
                else:
                    player.message("Usage: cbrief on [full|mo]")
            else:
                player.combat_brief = 'normal'
                player.message("Combat brief ON - simplified combat messages.")
        
        elif parts[0] == 'monster':
            # Toggle monster brief mode
            if hasattr(player, 'monster_brief'):
                player.monster_brief = not player.monster_brief
            else:
                player.monster_brief = True
            
            status = "ON" if player.monster_brief else "OFF"
            player.message(f"Monster combat brief {status}.")
        
        else:
            player.message("Usage: cbrief [on|off] [full|mo] or cbrief monster")