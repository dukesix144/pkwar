#!/usr/bin/env python
"""PKMUD startup wrapper with error logging"""

import sys
import os
import datetime
import traceback

# Set up paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Log file
startup_log = "lib/logs/startup.log"
error_log = "lib/logs/error.log"

# Ensure log directory exists
os.makedirs("lib/logs", exist_ok=True)

def log_startup(message, is_error=False):
    """Log startup messages."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = error_log if is_error else startup_log
    
    with open(log_file, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")
        if is_error:
            f.write("-" * 60 + "\n")

try:
    log_startup("Starting PKMUD...")
    
    # Import and run the main module
    import pkwar
    
except Exception as e:
    # Log the full error
    error_msg = f"Startup failed: {type(e).__name__}: {str(e)}"
    log_startup(error_msg, is_error=True)
    
    # Log full traceback
    with open(error_log, 'a') as f:
        f.write("Full traceback:\n")
        traceback.print_exc(file=f)
        f.write("\n" + "=" * 60 + "\n\n")
    
    # Also print to console
    print(f"PKMUD startup failed! Check {error_log} for details")
    print(f"Error: {error_msg}")
    
    sys.exit(1)
