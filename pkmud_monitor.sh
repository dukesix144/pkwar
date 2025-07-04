#!/bin/bash
# PKMUD Monitor Script - Add to crontab: */5 * * * * /path/to/pkmud_monitor.sh

MUDDIR="/home/bandwidth/pkwar"
PIDFILE="$MUDDIR/pkmud.pid"
CONTROL="$MUDDIR/pkmud_control.sh"

cd $MUDDIR

if [ -f $PIDFILE ]; then
    if ! ps -p $(cat $PIDFILE) > /dev/null; then
        echo "$(date): PKMUD crashed, restarting..." >> $MUDDIR/monitor.log
        rm $PIDFILE
        $CONTROL start
    fi
else
    echo "$(date): PKMUD not running, starting..." >> $MUDDIR/monitor.log
    $CONTROL start
fi
