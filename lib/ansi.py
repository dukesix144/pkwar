"""ANSI color support for PKMUD"""

class AnsiColors:
    """ANSI color codes and utilities."""
    
    # Basic colors
    COLORS = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'gray': '\033[90m',
        'bright_red': '\033[91m',
        'bright_green': '\033[92m',
        'bright_yellow': '\033[93m',
        'bright_blue': '\033[94m',
        'bright_magenta': '\033[95m',
        'bright_cyan': '\033[96m',
        'bright_white': '\033[97m',
        'reset': '\033[0m',
        'bold': '\033[1m',
        'underline': '\033[4m',
        'blink': '\033[5m',
        'reverse': '\033[7m'
    }
    
    # Default color mappings for game elements
    DEFAULT_VARS = {
        'armour': 'cyan',
        'attack': 'bright_red',
        'attacked': 'red',
        'gossip': 'bright_magenta',
        'kill': 'bright_yellow',
        'inumbers': 'green',
        'look_monster': 'red',
        'look_weapon': 'cyan',
        'look_object': 'green',
        'look_armor': 'blue',
        'look_player': 'bright_white',
        'look_other': 'white',
        'melee': 'yellow',
        'notify': 'bright_green',
        'numbers': 'green',
        'party': 'bright_cyan',
        'room_exits': 'green',
        'room_long': 'white',
        'room_short': 'bright_white',
        'say': 'bright_cyan',
        'spouse': 'bright_magenta',
        'shout': 'bright_yellow',
        'soul': 'magenta',
        'tell': 'bright_green',
        'watch': 'bright_blue',
        'wimpy': 'bright_red',
        'ghost': 'gray',
        'wiz': 'bright_yellow',
        'team': 'bright_blue',
        'newbie': 'bright_green',
        'gerkin': 'yellow'  # Special color for Gerkin
    }
    
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Apply color to text."""
        if color in cls.COLORS:
            return f"{cls.COLORS[color]}{text}{cls.COLORS['reset']}"
        return text
    
    @classmethod
    def strip_ansi(cls, text: str) -> str:
        """Remove all ANSI codes from text."""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

class AnsiManager:
    """Manages ANSI settings for a player."""
    
    def __init__(self, player):
        self.player = player
        self.enabled = getattr(player, 'ansi_enabled', True)  # Default to enabled
        self.full_line = False
        self.custom_colors = {}
        self.variables = AnsiColors.DEFAULT_VARS.copy()
    
    # Color properties that movement commands expect
    @property
    def yellow(self):
        """Yellow color code."""
        return AnsiColors.COLORS['yellow'] if self.enabled else ""
    
    @property
    def reset(self):
        """Reset color code."""
        return AnsiColors.COLORS['reset'] if self.enabled else ""
    
    @property
    def red(self):
        """Red color code."""
        return AnsiColors.COLORS['red'] if self.enabled else ""
    
    @property
    def green(self):
        """Green color code."""
        return AnsiColors.COLORS['green'] if self.enabled else ""
    
    @property
    def blue(self):
        """Blue color code."""
        return AnsiColors.COLORS['blue'] if self.enabled else ""
    
    @property
    def white(self):
        """White color code."""
        return AnsiColors.COLORS['white'] if self.enabled else ""
    
    @property
    def cyan(self):
        """Cyan color code."""
        return AnsiColors.COLORS['cyan'] if self.enabled else ""
    
    @property
    def magenta(self):
        """Magenta color code."""
        return AnsiColors.COLORS['magenta'] if self.enabled else ""
    
    @property
    def gray(self):
        """Gray color code."""
        return AnsiColors.COLORS['gray'] if self.enabled else ""
    
    @property
    def bright_red(self):
        """Bright red color code."""
        return AnsiColors.COLORS['bright_red'] if self.enabled else ""
    
    @property
    def bright_green(self):
        """Bright green color code."""
        return AnsiColors.COLORS['bright_green'] if self.enabled else ""
    
    @property
    def bright_yellow(self):
        """Bright yellow color code."""
        return AnsiColors.COLORS['bright_yellow'] if self.enabled else ""
    
    @property
    def bright_blue(self):
        """Bright blue color code."""
        return AnsiColors.COLORS['bright_blue'] if self.enabled else ""
    
    @property
    def bright_white(self):
        """Bright white color code."""
        return AnsiColors.COLORS['bright_white'] if self.enabled else ""
    
    @property
    def bright_cyan(self):
        """Bright cyan color code."""
        return AnsiColors.COLORS['bright_cyan'] if self.enabled else ""
    
    @property
    def bright_magenta(self):
        """Bright magenta color code."""
        return AnsiColors.COLORS['bright_magenta'] if self.enabled else ""
    
    @property
    def bold(self):
        """Bold style code."""
        return AnsiColors.COLORS['bold'] if self.enabled else ""
    
    def enable(self, full=False):
        """Enable ANSI colors."""
        self.enabled = True
        self.full_line = full
        self.player.ansi_enabled = True  # Update player setting
        self.player.message("ANSI colors enabled." + (" (full line mode)" if full else ""))
    
    def disable(self):
        """Disable ANSI colors."""
        self.enabled = False
        self.player.ansi_enabled = False  # Update player setting
        self.player.message("ANSI colors disabled.")
    
    def set_default(self):
        """Set default color scheme."""
        self.variables = AnsiColors.DEFAULT_VARS.copy()
        self.custom_colors = {}
        self.player.message("Default color scheme installed.")
    
    def wipe(self):
        """Remove all ANSI settings."""
        self.enabled = False
        self.full_line = False
        self.custom_colors = {}
        self.variables = {}
        self.player.ansi_enabled = False
        self.player.message("All ANSI settings wiped.")
    
    def set_variable(self, var: str, color: str):
        """Set a specific variable's color."""
        if color in AnsiColors.COLORS:
            self.variables[var] = color
            self.player.message(f"{var} color set to {color}")
            return True
        return False
    
    def format_text(self, text: str, var_type: str) -> str:
        """Format text with appropriate color based on variable type."""
        if not self.enabled:
            return text
        
        color = self.variables.get(var_type)
        if not color:
            return text
        
        if self.full_line:
            # Color entire line
            return AnsiColors.colorize(text, color)
        else:
            # Color just the important part
            # This would need more sophisticated parsing
            return AnsiColors.colorize(text, color)
    
    def format_channel(self, channel: str, sender: str, message: str) -> str:
        """Format a channel message with colors."""
        if not self.enabled:
            return f"[{channel}] {sender}: {message}"
        
        color = self.variables.get(channel, 'white')
        
        if channel == 'tell':
            return AnsiColors.colorize(f"{sender} tells you: {message}", color)
        elif channel == 'say':
            return AnsiColors.colorize(f"{sender} says: {message}", color)
        elif channel == 'shout':
            return AnsiColors.colorize(f"{sender} shouts: {message}", color)
        elif channel == 'ghost':
            return AnsiColors.colorize(f"(Ghost) {sender}: {message}", color)
        elif channel == 'wiz':
            return AnsiColors.colorize(f"[Wiz] {sender}: {message}", color)
        elif channel == 'team':
            return AnsiColors.colorize(f"(Team) {sender}: {message}", color)
        else:
            return AnsiColors.colorize(f"[{channel}] {sender}: {message}", color)
    
    def format_combat(self, attacker: str, defender: str, damage: int, emote: str) -> str:
        """Format combat messages with colors."""
        if not self.enabled:
            return f"{attacker} {emote} {defender}."
        
        # Determine if this is an attack or being attacked
        is_player_attacking = attacker == self.player.name
        is_player_defending = defender == self.player.name
        
        if is_player_attacking:
            color = self.variables.get('attack', 'bright_red')
        elif is_player_defending:
            color = self.variables.get('attacked', 'red')
        else:
            color = self.variables.get('melee', 'yellow')
        
        return AnsiColors.colorize(f"{attacker} {emote} {defender}.", color)
    
    def format_room(self, room_data: dict) -> str:
        """Format room display with colors."""
        if not self.enabled:
            return self._format_room_plain(room_data)
        
        output = []
        
        # Room title
        title_color = self.variables.get('room_short', 'bright_white')
        output.append(AnsiColors.colorize(room_data['name'], title_color))
        
        # Room description
        desc_color = self.variables.get('room_long', 'white')
        output.append(AnsiColors.colorize(room_data['description'], desc_color))
        
        # Players in room
        if room_data.get('players'):
            player_color = self.variables.get('look_player', 'bright_white')
            for player_name in room_data['players']:
                output.append(AnsiColors.colorize(player_name, player_color))
        
        # Objects in room
        if room_data.get('objects'):
            object_color = self.variables.get('look_object', 'green')
            for obj in room_data['objects']:
                output.append(AnsiColors.colorize(obj, object_color))
        
        # Exits
        if room_data.get('exits'):
            exit_color = self.variables.get('room_exits', 'green')
            exits_text = "Exits: " + ", ".join(room_data['exits'])
            output.append(AnsiColors.colorize(exits_text, exit_color))
        
        return "\n".join(output)
    
    def _format_room_plain(self, room_data: dict) -> str:
        """Format room without colors."""
        output = []
        output.append(room_data['name'])
        output.append(room_data['description'])
        
        if room_data.get('players'):
            for player_name in room_data['players']:
                output.append(player_name)
        
        if room_data.get('objects'):
            for obj in room_data['objects']:
                output.append(obj)
        
        if room_data.get('exits'):
            output.append("Exits: " + ", ".join(room_data['exits']))
        
        return "\n".join(output)
    
    def show_colors(self) -> str:
        """Display all standard colors."""
        output = ["Your standard colors:"]
        output.append("-" * 40)
        
        for color_name, color_code in AnsiColors.COLORS.items():
            if color_name not in ['reset', 'bold', 'underline', 'blink', 'reverse']:
                sample = AnsiColors.colorize(f"Sample text in {color_name}", color_name)
                output.append(f"{color_name:<20} {sample}")
        
        return "\n".join(output)
    
    def show_variables(self) -> str:
        """Display all color variables."""
        output = ["Your color variables:"]
        output.append("-" * 50)
        
        for var, color in sorted(self.variables.items()):
            sample = AnsiColors.colorize(var, color)
            output.append(f"{var:<20} -> {color:<15} {sample}")
        
        return "\n".join(output)