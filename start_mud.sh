#!/bin/bash
# Quick start script for PKMUD

echo "Starting PKMUD..."

# Check if running in screen/tmux
if [ -n "$STY" ] || [ -n "$TMUX" ]; then
    echo "Running in screen/tmux - good!"
else
    echo "WARNING: Not running in screen/tmux"
    echo "Consider using: screen -S pkmud ./start_mud.sh"
    echo ""
fi

# Direct Python start (no daemon)
python pkwar.py
