#!/bin/bash
# PKMUD Control Script

MUDDIR="/home/bandwidth/pkwar"
PIDFILE="$MUDDIR/pkmud.pid"
LOGFILE="$MUDDIR/pkmud.log"

cd $MUDDIR

start_mud() {
    # Check for virtual environment
    if [ -d "evenv" ]; then
        echo "Activating evenv..."
        source evenv/bin/activate
    elif [ -d "venv" ]; then
        echo "Activating venv..."
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        echo "Activating .venv..."
        source .venv/bin/activate
    else
        echo "No virtual environment found, using system Python"
    fi
    
    while true; do
        echo "$(date): Starting PKMUD..." >> $LOGFILE
        python pkwar.py >> $LOGFILE 2>&1
        EXIT_CODE=$?
        
        if [ $EXIT_CODE -eq 0 ]; then
            echo "$(date): PKMUD exited cleanly (reboot)" >> $LOGFILE
            sleep 2
        else
            echo "$(date): PKMUD crashed with exit code $EXIT_CODE" >> $LOGFILE
            sleep 5
        fi
        
        echo "$(date): Restarting PKMUD..." >> $LOGFILE
    done
}

case "$1" in
    start)
        if [ -f $PIDFILE ]; then
            PID=$(cat $PIDFILE)
            if ps -p $PID > /dev/null 2>&1; then
                echo "PKMUD already running (PID: $PID)"
            else
                echo "Removing stale PID file"
                rm -f $PIDFILE
                echo "Starting PKMUD..."
                start_mud &
                echo $! > $PIDFILE
                echo "PKMUD started (PID: $!)"
            fi
        else
            echo "Starting PKMUD..."
            start_mud &
            echo $! > $PIDFILE
            echo "PKMUD started (PID: $!)"
        fi
        ;;
    stop)
        if [ -f $PIDFILE ]; then
            echo "Stopping PKMUD..."
            PID=$(cat $PIDFILE)
            # Kill the wrapper script
            kill $PID 2>/dev/null
            # Kill any python processes
            pkill -f "python pkwar.py" 2>/dev/null
            rm -f $PIDFILE
            echo "PKMUD stopped"
        else
            echo "PKMUD not running"
        fi
        ;;
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    status)
        if [ -f $PIDFILE ]; then
            PID=$(cat $PIDFILE)
            if ps -p $PID > /dev/null 2>&1; then
                # Check if actual python process is running
                if pgrep -f "python pkwar.py" > /dev/null; then
                    echo "PKMUD running (PID: $PID)"
                else
                    echo "PKMUD wrapper running but MUD process not found"
                fi
            else
                echo "PKMUD not running (stale PID file)"
                rm -f $PIDFILE
            fi
        else
            echo "PKMUD not running"
        fi
        ;;
    log|logs)
        if [ -f $LOGFILE ]; then
            tail -f $LOGFILE
        else
            echo "No log file found"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|log}"
        exit 1
        ;;
esac
