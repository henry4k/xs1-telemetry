# Miniservice v1

# NAME (defaults to basename)
# COMMAND
# PID_FILE (defaults to ${NAME}.pid)
# LOG_FILE (defaults to ${NAME}.log)

set -e

if [ -z "$NAME" ]; then
    NAME="$(basename "$0")"
fi

if [ -z "$COMMAND" ]; then
    echo "$NAME did not configure a command."
    exit 1
fi

if [ -z "$PID_FILE" ]; then
    PID_FILE="${NAME}.pid"
fi

if [ -z "$LOG_FILE" ]; then
    LOG_FILE="${NAME}.log"
fi

RESTART_WAIT=2

case $1 in
    status)
        if "$0" is_running; then
            echo "$NAME is running."
        else
            echo "$NAME is not running."
        fi
        exit 0
    ;;
    start)
        if "$0" start_; then
            echo "Started $NAME."
            exit 0
        else
            echo "$NAME seems to be running already."
            exit 1
        fi
    ;;
    stop)
        if "$0" stop_; then
            echo "Stopped $NAME."
            exit 0
        else
            echo "$NAME is not running."
            exit 1
        fi
    ;;
    restart)
        "$0" stop
        sleep $RESTART_WAIT
        "$0" start
    ;;
    is_running)
        if [ ! -e "$PID_FILE" ]; then
            exit 1
        else
            pid=$(cat "$PID_FILE")
            if test -n "$(ps | grep -E "^\\s$pid")"; then
                exit 0
            else
                exit 1
            fi
        fi
    ;;
    start_)
        if "$0" is_running; then
            exit 1
        else
            nohup $COMMAND >"$LOG_FILE" &
            echo $! > "$PID_FILE"
            exit 0
        fi
    ;;
    stop_)
        if "$0" is_running; then
            pid=$(cat "$PID_FILE")
            kill $pid
            rm "$PID_FILE"
            exit 0
        else
            exit 1
        fi
    ;;
esac
