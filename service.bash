# NAME
# COMMAND
# PID_FILE
# LOG_FILE

if [ -z "$NAME" ]; then
    NAME="$(basename $0)"
fi

if [ -z "$COMMAND" ]; then
    echo "$NAME did not configure a command."
fi

if [ -z "$PID_FILE" ]; then
    PID_FILE="${NAME}.pid"
fi

if [ -z "$LOG_FILE" ]; then
    LOG_FILE="${NAME}.log"
fi


function is_running
{
    if [ ! -e "$PID_FILE" ]; then
        return 1
    else
        return 0
    fi
}

function start
{
    if is_running; then
        return 1
    else
        nohup $COMMAND >"$LOG_FILE" &
        echo $! > "$PID_FILE"
        return 0
    fi
}

function stop
{
    if is_running; then
        local pid=$(cat "$PID_FILE")
        kill $pid
        rm "$PID_FILE"
        return 0
    else
        return 1
    fi
}

case $1 in
    status)
        if is_running; then
            echo "$NAME is running."
        else
            echo "$NAME is not running."
        fi
    ;;
    start)
        if start; then
            echo "Started $NAME."
        else
            echo "$NAME seems to be running already."
        fi
    ;;
    stop)
        if stop; then
            echo "Stopped $NAME."
        else
            echo "$NAME is not running."
        fi
    ;;
    restart)
        stop
        if start; then
            echo "Restarted $NAME"
        else
            echo "Restarting of $NAME failed."
        fi
    ;;
esac
