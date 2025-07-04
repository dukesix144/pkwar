import logging
from server.server_enums import ReadState, TelnetCodes, TELNET_OPTION_CODES

# Set up logging
log = logging.getLogger(__name__)

def normal_read_state(message, state, buffer, character):
    """Handle normal telnet input processing."""
    # Log what we're receiving for debugging
    log.debug(f"Received character: {repr(character)} (ord: {ord(character)})")
    if buffer:
        log.debug(f"Current buffer: {repr(''.join(buffer))}")

    # Handle special telnet command code
    if ord(character) == TelnetCodes.INTERPRET_AS_COMMAND:
        state = ReadState.COMMAND
    # Handle end of line - both \n and \r should trigger message processing
    elif character == "\n" or character == "\r":
        # Always process on newline/carriage return, even if buffer is empty
        # This handles the case where user just hits Enter
        message = ''.join(buffer) if buffer else ""
        # Clear the buffer by removing all elements
        buffer[:] = []  # This modifies the list in place
        log.debug(f"Message complete: {repr(message)}")
    # Handle backspace characters
    elif character == "\x08" or character == "\x7f":  # Handle both backspace codes
        if buffer:  # Only delete if there's something to delete
            deleted = buffer.pop()  # Remove last character
            log.debug(f"Backspace: deleted '{deleted}'")
    # Regular character - add to buffer
    else:
        buffer.append(character)
        log.debug(f"Added to buffer: {repr(character)}")
    
    return message, state, buffer


def subneg_read_state(message, state, buffer, character):
    """Handle telnet subnegotiation state."""
    # if we reach an 'end of subnegotiation' command, this ends the
    # list of options and we can return to 'normal' state.
    # Otherwise we must remain in this state
    if ord(character) == TelnetCodes.SUBNEGOTIATION_END:
        state = ReadState.NORMAL
    return message, state, buffer


def command_read_state(message, state, buffer, character):
    """Handle telnet command state."""
    # the special 'start of subnegotiation' command code indicates
    # that the following characters are a list of options until
    # we're told otherwise. We switch into 'subnegotiation' state
    # to handle this
    if ord(character) == TelnetCodes.SUBNEGOTIATION_START:
        state = ReadState.SUBNEG
    # if the command code is one of the 'will', 'wont', 'do' or
    # 'dont' commands, the following character will be an option
    # code so we must remain in the 'command' state
    elif ord(character) in TELNET_OPTION_CODES:
        state = ReadState.COMMAND
    # for all other command codes, there is no accompanying data so
    # we can return to 'normal' state.
    else:
        state = ReadState.NORMAL
    return message, state, buffer