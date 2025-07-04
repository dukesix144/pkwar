from server.telnet_actions.actions import *

_MAPPINGS = {
    ReadState.NORMAL: normal_read_state,
    ReadState.SUBNEG: subneg_read_state,
    ReadState.COMMAND: command_read_state
}

# Store buffers per connection to handle partial messages
_BUFFERS = {}

def process(data, connection_id=None):
    # the Telnet protocol allows special command codes to be inserted into
    # messages. For our very simple server we don't need to response to
    # any of these codes, but we must at least detect and skip over them
    # so that we don't interpret them as text data.
    # More info on the Telnet protocol can be found here:
    # http://pcmicro.com/netfoss/telnet.html

    # start with no message and in the normal state
    message = None
    state = ReadState.NORMAL

    # Get or create buffer for this connection
    if connection_id is None:
        buffer = []
    else:
        if connection_id not in _BUFFERS:
            _BUFFERS[connection_id] = []
        buffer = _BUFFERS[connection_id]
    
    for character in data:
        message, state, buffer = _MAPPINGS[state](message, state, buffer, character)
        if message:
            # Clear buffer when message is complete
            if connection_id and connection_id in _BUFFERS:
                _BUFFERS[connection_id] = []
            break
    
    return message
