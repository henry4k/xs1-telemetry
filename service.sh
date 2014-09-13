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

case $1 in
    status)
        if $0 is_running; then
            echo "$NAME is running."
        else
            echo "$NAME is not running."
        fi
    ;;
    start)
        if $0 start_; then
            echo "Started $NAME."
        else
            echo "$NAME seems to be running already."
        fi
    ;;
    stop)
        if $0 stop_; then
            echo "Stopped $NAME."
        else
            echo "$NAME is not running."
        fi
    ;;
    restart)
        $0 stop_
        if $0 start_; then
            echo "Restarted $NAME"
        else
            echo "Restarting of $NAME failed."
        fi
    ;;
    is_running)
        if [ ! -e "$PID_FILE" ]; then
            return 1
        else
            return 0
        fi
    ;;
    start_)
        if $0 is_running; then
            return 1
        else
            nohup $COMMAND >"$LOG_FILE" &
            echo $! > "$PID_FILE"
            return 0
        fi
    ;;
    stop_)
        if $0 is_running; then
            local pid=$(cat "$PID_FILE")
            kill $pid
            rm "$PID_FILE"
            return 0
        else
            return 1
        fi
    ;;
esac
