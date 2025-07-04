"""Main command dispatcher for PKMUD."""

from lib.models.game_state import GameState
from lib.models.player import Player
from lib.souls import SoulManager
from lib.combat import CombatManager
from lib.shop_system import ShopInventory, GerkinNPC
from lib.mail_system import MailSystem, MailComposer
from lib.ansi import AnsiManager
import time
import threading
import os
import json

# Import all command modules
from lib.commands.character import CharacterCommands
from lib.commands.war import WarCommands
from lib.commands.combat import CombatCommands
from lib.commands.inventory import InventoryCommands
from lib.commands.explorer import ExplorerCommands
from lib.commands.communication import CommunicationCommands
from lib.commands.movement import MovementCommands
from lib.commands.wizard import WizardCommands
from lib.commands.settings import SettingsCommands
from lib.commands.shop import ShopCommands
from lib.commands.mail import MailCommands
from lib.commands.social import SocialCommands
from lib.commands.system import SystemCommands
from lib.commands.brief import BriefCommands
from lib.commands.board import BoardCommands

class Commands(object):
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        
        # Initialize managers that are used across multiple modules
        self.soul_manager = SoulManager()
        self.combat_manager = CombatManager(game_state)
        self.shop_inventory = ShopInventory(game_state)
        self.gerkin_npc = GerkinNPC()
        self.mail_system = MailSystem(game_state)
        
        # Store these in game_state for module access
        game_state.soul_manager = self.soul_manager
        game_state.combat_manager = self.combat_manager
        game_state.shop_inventory = self.shop_inventory
        game_state.gerkin_npc = self.gerkin_npc
        game_state.mail_system = self.mail_system
        
        # Initialize command modules
        self.character_cmds = CharacterCommands(game_state)
        self.war_cmds = WarCommands(game_state)
        self.combat_cmds = CombatCommands(game_state)
        self.inventory_cmds = InventoryCommands(game_state)
        self.explorer_cmds = ExplorerCommands(game_state)
        self.communication_cmds = CommunicationCommands(game_state)
        self.movement_cmds = MovementCommands(game_state)
        self.wizard_cmds = WizardCommands(game_state)
        self.settings_cmds = SettingsCommands(game_state)
        self.shop_cmds = ShopCommands(game_state)
        self.mail_cmds = MailCommands(game_state)
        self.social_cmds = SocialCommands(game_state)
        self.system_cmds = SystemCommands(game_state)
        self.brief_cmds = BriefCommands(game_state)
        self.board_cmds = BoardCommands(game_state)
        
        # Build command dictionary
        self._build_commands()
        
        # Shared state for special input modes
        self.mail_composers = self.mail_cmds.mail_composers
        self.gerkin_timers = self.combat_cmds.gerkin_timers
        self.gerkin_last_used = self.combat_cmds.gerkin_last_used
        self.class_selection_timers = {}
        
        # Track last command time for idle detection
        self.last_activity = {}

    def _build_commands(self):
        """Build the main command dictionary from all modules."""
        self.commands = {
            # System commands
            "quit": self.system_cmds.quit,
            "help": self.system_cmds.help,
            "commands": self.system_cmds.help,
            "mudinfo": self.system_cmds.mudinfo,
            
            # Character commands
            "score": self.character_cmds.score,
            "hp": self.character_cmds.hp,
            "stats": self.character_cmds.stats,
            "who": self.character_cmds.who,
            "finger": self.character_cmds.finger,
            "history": self.character_cmds.history,
            "coins": self.character_cmds.coins,
            
            # War commands
            "war": self.war_cmds.war_toggle,
            "push": self.war_cmds.push_button,
            "alive": self.war_cmds.alive,
            "warstatus": self.war_cmds.warstatus,
            "vote": self.war_cmds.vote,
            "class": self.war_cmds.select_class,
            "watch": self.war_cmds.watch_war,
            "stop": self.war_cmds.stop_watching,
            "wars": self.war_cmds.show_wars,
            "topkillers": self.war_cmds.topkillers,
            
            # Communication commands
            "say": self.communication_cmds.say,
            "'": self.communication_cmds.say,
            "tell": self.communication_cmds.tell,
            "shout": self.communication_cmds.shout,
            "ghost": self.communication_cmds.ghost,
            "wiz": self.communication_cmds.wiz,
            "team": self.communication_cmds.team,
            "gossip": self.communication_cmds.gossip,
            "newbie": self.communication_cmds.newbie,
            "channels": self.communication_cmds.channels,
            "chatlines": self.communication_cmds.channels,
            
            # Movement commands
            "look": self.movement_cmds.look,
            "l": self.movement_cmds.look,
            "glance": self.movement_cmds.glance,
            "go": self.movement_cmds.go,
            "north": self.movement_cmds.north,
            "south": self.movement_cmds.south,
            "east": self.movement_cmds.east,
            "west": self.movement_cmds.west,
            "up": self.movement_cmds.up,
            "down": self.movement_cmds.down,
            "northeast": self.movement_cmds.northeast,
            "northwest": self.movement_cmds.northwest,
            "southeast": self.movement_cmds.southeast,
            "southwest": self.movement_cmds.southwest,
            "n": self.movement_cmds.north,
            "s": self.movement_cmds.south,
            "e": self.movement_cmds.east,
            "w": self.movement_cmds.west,
            "u": self.movement_cmds.up,
            "d": self.movement_cmds.down,
            "ne": self.movement_cmds.northeast,
            "nw": self.movement_cmds.northwest,
            "se": self.movement_cmds.southeast,
            "sw": self.movement_cmds.southwest,
            
            # Brief commands
            "brief": self.brief_cmds.brief,
            "cbrief": self.brief_cmds.cbrief,
            
            # Inventory commands
            "inventory": self.inventory_cmds.inventory,
            "i": self.inventory_cmds.inventory,
            "eq": self.inventory_cmds.equipment,
            "get": self.inventory_cmds.get_item,
            "drop": self.inventory_cmds.drop_item,
            "give": self.inventory_cmds.give_item,
            "wear": self.inventory_cmds.wear,
            "wield": self.inventory_cmds.wield,
            "remove": self.inventory_cmds.remove,
            "equip": self.inventory_cmds.equip_all,
            "unequip": self.inventory_cmds.remove_all,
            "use": self.inventory_cmds.use_item,
            "heal": self.inventory_cmds.heal,
            "keep": self.inventory_cmds.keep,
            "unkeep": self.inventory_cmds.unkeep,
            
            # Combat commands
            "kill": self.combat_cmds.kill,
            "k": self.combat_cmds.kill,
            "blick": self.combat_cmds.blick,
            "follow": self.combat_cmds.follow,
            "lose": self.combat_cmds.lose,
            "gerkin": self.combat_cmds.gerkin_command,
            "gate": self.combat_cmds.gate,
            "fireball": self.combat_cmds.fireball,
            
            # Social commands
            "emote": self.social_cmds.emote,
            ":": self.social_cmds.emote,
            "soul": self.social_cmds.soul,
            "feelings": self.social_cmds.feelings,
            
            # Mail commands
            "mail": self.mail_cmds.mail,
            "delete": self.mail_cmds.delete_mail,
            
            # Board commands - read is context sensitive
            "post": self.board_cmds.post_message,
            
            # Settings commands
            "ansi": self.settings_cmds.ansi,
            "aset": self.settings_cmds.aset,
            "setcolor": self.settings_cmds.aset,
            "wimpy": self.settings_cmds.wimpy,
            "plan": self.settings_cmds.set_plan,
            "set_plan": self.settings_cmds.set_plan,
            "chfn": self.settings_cmds.chfn,
            
            # Explorer commands
            "explorer": self.explorer_cmds.explorer,
            "explorers": self.explorer_cmds.explorers,
            "arealist": self.explorer_cmds.arealist,
            
            # Shop commands
            "list": self.shop_cmds.shop_list,
            "buy": self.shop_cmds.buy,
            "sell": self.shop_cmds.sell,
            "value": self.shop_cmds.value,
            
            # Wizard commands
            "goto": self.wizard_cmds.wiz_goto,
            "trans": self.wizard_cmds.wiz_trans,
            "load": self.wizard_cmds.wiz_load,
            "dest": self.wizard_cmds.wiz_dest,
            "clone": self.wizard_cmds.wiz_clone,
            "wizhelp": self.wizard_cmds.wizhelp,
            "promotemenow": self.wizard_cmds.promote,
            "link": self.wizard_cmds.link_enforcer,
        }
        
        # Special handling for 'read' command - context sensitive
        self.commands["read"] = self._handle_read_command

    def _handle_read_command(self, player, params):
        """Context-sensitive read command."""
        if player._location == 'board_room':
            # In board room, read board messages
            if params and params.lower() == 'board':
                self.board_cmds.read_board(player)
            else:
                self.board_cmds.read_message(player, params)
        else:
            # Elsewhere, read mail
            self.mail_cmds.read_mail(player, params)

    def execute_command(self, player, command, param):
        """Execute a command for a player."""
        # Update activity
        player.last_activity = time.time()
        
        # Check if in special input mode
        if hasattr(player, 'mail_mode') and player.mail_mode:
            self.handle_mail_input(player, command + (" " + param if param else ""))
            return
        
        if hasattr(player, 'chfn_mode') and player.chfn_mode:
            self.handle_chfn_input(player, command + (" " + param if param else ""))
            return
        
        if hasattr(player, 'selecting_class') and player.selecting_class:
            self.handle_class_selection(player, command)
            return
        
        # Check if it's a soul command first
        if command.lower() in self.soul_manager.souls:
            self.soul_manager.execute_soul(player, command, param)
            return
        
        # Check regular commands
        if self.commands.get(command):
            result = self.commands[command](player, param)
            
            # Handle special returns from command modules
            if isinstance(result, dict):
                self._handle_command_result(player, result)
        else:
            player.message(f"There is no reason to '{command}' here.")
    
    def _handle_command_result(self, player, result):
        """Handle special return values from command modules."""
        if 'select_class' in result:
            # Handle class selection
            player.selecting_class = True
            self.handle_class_selection(player, result['select_class'])
        
        elif 'mail_mode' in result:
            # Handle mail composition
            player.mail_mode = result['mail_mode']
            if 'composer' in result:
                self.mail_composers[player.client.uuid] = result['composer']
        
        elif 'chfn_mode' in result:
            # Handle chfn mode
            player.chfn_mode = True
        
        elif 'help_lookup' in result:
            # Handle help lookup
            cmd_name = result['help_lookup']
            cmd = self.commands.get(cmd_name.lower())
            if cmd and cmd.__doc__:
                player.message(cmd.__doc__)
            else:
                player.message(f"No help available for '{cmd_name}'")
    
    # Input handling methods remain in main Commands class
    def handle_mail_input(self, player, input_text):
        """Handle input during mail composition."""
        composer = self.mail_composers.get(player.client.uuid)
        if not composer:
            player.mail_mode = None
            return
        
        if player.mail_mode == "CC":
            if input_text.strip():
                # Add CC recipients - case insensitive
                cc_list = input_text.split(',')
                player_dir = "lib/players"
                for cc in cc_list:
                    cc = cc.strip()
                    
                    # Find player file case-insensitively
                    found = False
                    if os.path.exists(player_dir):
                        for filename in os.listdir(player_dir):
                            if filename.endswith('.json') and filename[:-5].lower() == cc.lower():
                                # Found the player - get actual name
                                with open(os.path.join(player_dir, filename), 'r') as f:
                                    player_data = json.load(f)
                                    actual_name = player_data.get('name', filename[:-5])
                                composer.add_cc(actual_name)
                                found = True
                                break
                    
                    if not found:
                        player.message(f"Unknown player: {cc}")
                        
            player.message("Subject:")
            player.mail_mode = "SUBJECT"
        
        elif player.mail_mode == "SUBJECT":
            if not input_text.strip():
                player.message("Mail cancelled - no subject.")
                del self.mail_composers[player.client.uuid]
                player.mail_mode = None
                return
            composer.set_subject(input_text)
            player.message("Enter message. End with '.' on a line by itself:")
            player.mail_mode = "BODY"
        
        elif player.mail_mode == "BODY":
            if input_text == ".":
                # Send mail
                success = self.mail_system.send_mail(
                    composer.sender,
                    composer.recipients,
                    composer.cc,
                    composer.subject,
                    composer.get_body()
                )
                if success:
                    player.message("Mail sent.")
                else:
                    player.message("Mail failed.")
                del self.mail_composers[player.client.uuid]
                player.mail_mode = None
            else:
                composer.add_body_line(input_text)
    
    def handle_chfn_input(self, player, input_text):
        """Handle input during chfn."""
        if input_text.lower() == 'q':
            player.chfn_mode = False
            player.message("Finger information update cancelled.")
            return
        
        if input_text == '1':
            player.message("Enter new real name:")
            player.chfn_field = 'real_name'
        elif input_text == '2':
            player.message("Enter new email:")
            player.chfn_field = 'email'
        elif hasattr(player, 'chfn_field'):
            # Setting the field
            if player.chfn_field == 'real_name':
                player.real_name = input_text[:50]  # Limit length
                player.message(f"Real name set to: {player.real_name}")
            elif player.chfn_field == 'email':
                player.email = input_text[:100]
                player.message(f"Email set to: {player.email}")
            
            # Save player
            if hasattr(self.game_state, 'auth'):
                self.game_state.auth._save_player(player)
            
            delattr(player, 'chfn_field')
            player.chfn_mode = False
            player.message("Finger information updated.")
        else:
            player.message("Invalid choice. Enter 1-2 or 'q' to quit:")
    
    def handle_class_selection(self, player, class_name):
        """Handle class selection during war prep."""
        valid_classes = ['fighter', 'kamikaze', 'mage', 'hunter']
        
        if class_name.lower() not in valid_classes:
            player.message(f"Invalid class. Choose: {', '.join(valid_classes)}")
            return
        
        if player.set_war_class(class_name.lower()):
            player.message(f"You are now a {class_name.capitalize()}!")
            player.selecting_class = False
            
            # Cancel timeout timer
            if player.client.uuid in self.class_selection_timers:
                self.class_selection_timers[player.client.uuid].cancel()
                del self.class_selection_timers[player.client.uuid]
        else:
            player.message("Failed to set class.")