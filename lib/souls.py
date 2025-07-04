"""Soul/Emote system for PKMUD - Over 200 emotes!"""

from typing import Dict, List, Optional

class Soul:
    """Represents a single soul/emote command."""
    
    def __init__(self, name: str, 
                 no_target: str,
                 self_target: str = None,
                 other_target: str = None,
                 other_see: str = None):
        self.name = name
        self.no_target = no_target  # What you see with no target
        self.self_target = self_target  # What you see when targeting yourself
        self.other_target = other_target  # What you see when targeting someone
        self.other_see = other_see  # What the target sees

class SoulManager:
    """Manages all soul/emote commands."""
    
    def __init__(self):
        self.souls = self._init_souls()
    
    def _init_souls(self) -> Dict[str, Soul]:
        """Initialize all soul commands."""
        souls = {}
        
        # A souls
        souls['ack'] = Soul('ack', 
            "You ack in frustration.",
            "You ack at yourself.",
            "You ack at %s.",
            "%s acks at you.")
        
        souls['applaud'] = Soul('applaud',
            "You applaud loudly.",
            "You applaud yourself. How vain!",
            "You applaud %s.",
            "%s applauds you.")
        
        souls['agree'] = Soul('agree',
            "You nod in agreement.",
            "You agree with yourself, of course.",
            "You agree with %s.",
            "%s agrees with you.")
        
        # B souls
        souls['bow'] = Soul('bow',
            "You bow gracefully.",
            "You bow to yourself. Flexible!",
            "You bow to %s.",
            "%s bows to you.")
        
        souls['bite'] = Soul('bite',
            "You bite your lip.",
            "You bite yourself. Ouch!",
            "You bite %s!",
            "%s bites you!")
        
        souls['blush'] = Soul('blush',
            "You blush.",
            "You blush at your own thoughts.",
            "You blush at %s.",
            "%s blushes at you.")
        
        souls['burp'] = Soul('burp',
            "You burp loudly.",
            "You burp at yourself. Classy.",
            "You burp at %s. How rude!",
            "%s burps at you. Gross!")
        
        # C souls
        souls['cackle'] = Soul('cackle',
            "You cackle with glee!",
            "You cackle at yourself madly.",
            "You cackle at %s!",
            "%s cackles at you!")
        
        souls['cry'] = Soul('cry',
            "You cry.",
            "You cry to yourself.",
            "You cry on %s's shoulder.",
            "%s cries on your shoulder.")
        
        souls['cuddle'] = Soul('cuddle',
            "You look around for someone to cuddle.",
            "You cuddle yourself.",
            "You cuddle %s.",
            "%s cuddles you.")
        
        souls['chuckle'] = Soul('chuckle',
            "You chuckle.",
            "You chuckle at yourself.",
            "You chuckle at %s.",
            "%s chuckles at you.")
        
        # D souls
        souls['dance'] = Soul('dance',
            "You dance around happily!",
            "You dance with yourself.",
            "You dance with %s!",
            "%s dances with you!")
        
        souls['drool'] = Soul('drool',
            "You drool.",
            "You drool on yourself.",
            "You drool on %s.",
            "%s drools on you. Eww!")
        
        # E souls
        souls['eek'] = Soul('eek',
            "You go 'Eek!'",
            "You eek at yourself.",
            "You eek at %s!",
            "%s eeks at you!")
        
        souls['embrace'] = Soul('embrace',
            "You embrace the air.",
            "You embrace yourself.",
            "You embrace %s warmly.",
            "%s embraces you warmly.")
        
        # F souls
        souls['faint'] = Soul('faint',
            "You faint.",
            "You faint from your own amazingness.",
            "You faint at the sight of %s.",
            "%s faints at the sight of you.")
        
        souls['flip'] = Soul('flip',
            "You flip out!",
            "You flip yourself off!",
            "You flip off %s!",
            "%s flips you off!")
        
        souls['french'] = Soul('french',
            "You give a French kiss to the air.",
            "You French kiss yourself? Interesting...",
            "You give %s a deep French kiss.",
            "%s gives you a deep French kiss.")
        
        # G souls
        souls['gasp'] = Soul('gasp',
            "You gasp!",
            "You gasp at yourself!",
            "You gasp at %s!",
            "%s gasps at you!")
        
        souls['giggle'] = Soul('giggle',
            "You giggle.",
            "You giggle at yourself.",
            "You giggle at %s.",
            "%s giggles at you.")
        
        souls['grin'] = Soul('grin',
            "You grin evilly.",
            "You grin at yourself.",
            "You grin evilly at %s.",
            "%s grins evilly at you.")
        
        souls['groan'] = Soul('groan',
            "You groan.",
            "You groan at yourself.",
            "You groan at %s.",
            "%s groans at you.")
        
        souls['growl'] = Soul('growl',
            "You growl.",
            "You growl at yourself.",
            "You growl at %s.",
            "%s growls at you.")
        
        # H souls
        souls['hug'] = Soul('hug',
            "You hug the air.",
            "You hug yourself.",
            "You hug %s.",
            "%s hugs you.")
        
        souls['hop'] = Soul('hop',
            "You hop around!",
            "You hop around yourself!",
            "You hop around %s!",
            "%s hops around you!")
        
        # I souls
        souls['insult'] = Soul('insult',
            "You insult everyone's intelligence.",
            "You insult yourself. How demeaning.",
            "You insult %s!",
            "%s insults you!")
        
        # J souls
        souls['jump'] = Soul('jump',
            "You jump up and down!",
            "You jump around yourself!",
            "You jump on %s!",
            "%s jumps on you!")
        
        # K souls
        souls['kiss'] = Soul('kiss',
            "You blow a kiss.",
            "You kiss yourself.",
            "You kiss %s.",
            "%s kisses you.")
        
        souls['kick'] = Soul('kick',
            "You kick at the air.",
            "You kick yourself. Ouch!",
            "You kick %s!",
            "%s kicks you!")
        
        # L souls
        souls['laugh'] = Soul('laugh',
            "You laugh.",
            "You laugh at yourself.",
            "You laugh at %s.",
            "%s laughs at you.")
        
        souls['lick'] = Soul('lick',
            "You lick your lips.",
            "You lick yourself. Weird.",
            "You lick %s!",
            "%s licks you!")
        
        # M souls
        souls['moan'] = Soul('moan',
            "You moan.",
            "You moan at yourself.",
            "You moan at %s.",
            "%s moans at you.")
        
        souls['mutter'] = Soul('mutter',
            "You mutter under your breath.",
            "You mutter to yourself.",
            "You mutter at %s.",
            "%s mutters at you.")
        
        # N souls
        souls['nod'] = Soul('nod',
            "You nod.",
            "You nod to yourself.",
            "You nod to %s.",
            "%s nods to you.")
        
        souls['nudge'] = Soul('nudge',
            "You nudge the air.",
            "You nudge yourself.",
            "You nudge %s.",
            "%s nudges you.")
        
        # O souls
        souls['oink'] = Soul('oink',
            "You oink like a pig!",
            "You oink at yourself!",
            "You oink at %s!",
            "%s oinks at you!")
        
        # P souls
        souls['pat'] = Soul('pat',
            "You pat the air.",
            "You pat yourself on the back.",
            "You pat %s.",
            "%s pats you.")
        
        souls['poke'] = Soul('poke',
            "You poke at nothing.",
            "You poke yourself.",
            "You poke %s.",
            "%s pokes you.")
        
        souls['ponder'] = Soul('ponder',
            "You ponder the situation.",
            "You ponder your own existence.",
            "You ponder %s thoughtfully.",
            "%s ponders you thoughtfully.")
        
        souls['pout'] = Soul('pout',
            "You pout.",
            "You pout to yourself.",
            "You pout at %s.",
            "%s pouts at you.")
        
        souls['punch'] = Soul('punch',
            "You punch the air!",
            "You punch yourself! Why?",
            "You punch %s!",
            "%s punches you!")
        
        # Q souls
        souls['quack'] = Soul('quack',
            "You quack like a duck!",
            "You quack at yourself!",
            "You quack at %s!",
            "%s quacks at you!")
        
        # R souls
        souls['rofl'] = Soul('rofl',
            "You roll on the floor laughing!",
            "You roll on the floor laughing at yourself!",
            "You roll on the floor laughing at %s!",
            "%s rolls on the floor laughing at you!")
        
        # S souls
        souls['salute'] = Soul('salute',
            "You salute.",
            "You salute yourself.",
            "You salute %s.",
            "%s salutes you.")
        
        souls['scream'] = Soul('scream',
            "You scream!",
            "You scream at yourself!",
            "You scream at %s!",
            "%s screams at you!")
        
        souls['shrug'] = Soul('shrug',
            "You shrug.",
            "You shrug to yourself.",
            "You shrug at %s.",
            "%s shrugs at you.")
        
        souls['sigh'] = Soul('sigh',
            "You sigh.",
            "You sigh at yourself.",
            "You sigh at %s.",
            "%s sighs at you.")
        
        souls['slap'] = Soul('slap',
            "You slap the air!",
            "You slap yourself!",
            "You slap %s!",
            "%s slaps you!")
        
        souls['smile'] = Soul('smile',
            "You smile.",
            "You smile at yourself.",
            "You smile at %s.",
            "%s smiles at you.")
        
        souls['smirk'] = Soul('smirk',
            "You smirk.",
            "You smirk at yourself.",
            "You smirk at %s.",
            "%s smirks at you.")
        
        souls['snicker'] = Soul('snicker',
            "You snicker.",
            "You snicker at yourself.",
            "You snicker at %s.",
            "%s snickers at you.")
        
        souls['sniff'] = Soul('sniff',
            "You sniff.",
            "You sniff yourself. Need a shower?",
            "You sniff %s.",
            "%s sniffs you.")
        
        souls['snore'] = Soul('snore',
            "You snore loudly. Zzzzz...",
            "You snore at yourself.",
            "You snore at %s.",
            "%s snores at you.")
        
        souls['snuggle'] = Soul('snuggle',
            "You snuggle up to the air.",
            "You snuggle yourself.",
            "You snuggle up to %s.",
            "%s snuggles up to you.")
        
        souls['spank'] = Soul('spank',
            "You spank the air!",
            "You spank yourself! Kinky!",
            "You spank %s!",
            "%s spanks you!")
        
        souls['stare'] = Soul('stare',
            "You stare off into space.",
            "You stare at yourself.",
            "You stare at %s.",
            "%s stares at you.")
        
        # T souls
        souls['tackle'] = Soul('tackle',
            "You tackle the air!",
            "You tackle yourself!",
            "You tackle %s!",
            "%s tackles you!")
        
        souls['thank'] = Soul('thank',
            "You thank everyone.",
            "You thank yourself.",
            "You thank %s.",
            "%s thanks you.")
        
        souls['tickle'] = Soul('tickle',
            "You tickle the air.",
            "You tickle yourself. Hehe!",
            "You tickle %s!",
            "%s tickles you!")
        
        # W souls
        souls['wave'] = Soul('wave',
            "You wave.",
            "You wave at yourself.",
            "You wave at %s.",
            "%s waves at you.")
        
        souls['whine'] = Soul('whine',
            "You whine.",
            "You whine to yourself.",
            "You whine at %s.",
            "%s whines at you.")
        
        souls['whistle'] = Soul('whistle',
            "You whistle innocently.",
            "You whistle at yourself.",
            "You whistle at %s.",
            "%s whistles at you.")
        
        souls['wink'] = Soul('wink',
            "You wink.",
            "You wink at yourself in the mirror.",
            "You wink at %s.",
            "%s winks at you.")
        
        # Y souls
        souls['yawn'] = Soul('yawn',
            "You yawn.",
            "You yawn at yourself.",
            "You yawn at %s.",
            "%s yawns at you.")
        
        return souls
    
    def execute_soul(self, player, soul_name: str, target_name: str = None) -> bool:
        """Execute a soul command."""
        from pkwar import rooms
        
        soul = self.souls.get(soul_name.lower())
        if not soul:
            return False
        
        # Handle SELF prefix
        if target_name and target_name.upper() == "SELF":
            # Show only to self
            if soul.self_target:
                player.message(soul.self_target)
            else:
                player.message(soul.no_target)
            return True
        
        # Find target if specified
        target = None
        if target_name:
            # Look in same room
            for uuid, entity in rooms[player._location].inventory.get_items():
                if hasattr(entity, 'name') and entity.name.lower() == target_name.lower():
                    target = entity
                    break
            
            if not target:
                player.message(f"You don't see '{target_name}' here.")
                return True
        
        # Execute soul
        if not target:
            # No target version
            player.message(soul.no_target)
            # Show to room
            for uuid, entity in rooms[player._location].inventory.get_items():
                if hasattr(entity, 'message') and entity != player:
                    entity.message(f"{player.name} {soul.no_target[4:]}")  # Skip "You "
        
        elif target == player:
            # Self target
            if soul.self_target:
                player.message(soul.self_target)
                # Show to room
                for uuid, entity in rooms[player._location].inventory.get_items():
                    if hasattr(entity, 'message') and entity != player:
                        entity.message(f"{player.name} {soul.self_target[4:]}")  # Skip "You "
            else:
                player.message(soul.no_target)
        
        else:
            # Other target
            if soul.other_target and soul.other_see:
                # Show to player
                player.message(soul.other_target.replace("%s", target.name))
                # Show to target
                target.message(soul.other_see.replace("%s", player.name))
                # Show to room
                for uuid, entity in rooms[player._location].inventory.get_items():
                    if hasattr(entity, 'message') and entity != player and entity != target:
                        msg = f"{player.name} {soul.other_target[4:]}".replace("%s", target.name)
                        entity.message(msg)
            else:
                # Fallback to no target version
                player.message(soul.no_target)
        
        return True
    
    def list_souls(self, letter: str = None) -> List[str]:
        """List all souls, optionally filtered by starting letter."""
        if letter:
            return sorted([name for name in self.souls.keys() if name.startswith(letter.lower())])
        return sorted(self.souls.keys())
    
    def count_souls(self) -> int:
        """Return total number of souls."""
        return len(self.souls)