#!/bin/bash

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
LOG="$SCRIPT_DIR/server-watch-build.log"
PID_FILE="$SCRIPT_DIR/server-watch-build.pid"

# 防止重复启动
if [ -f "$PID_FILE" ] && kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
  echo "server-watch-build.py is already running (pid=$(cat $PID_FILE))"
  exit 0
fi

nohup python3 -u "$SCRIPT_DIR/server-watch-build.py" \
  > "$LOG" 2>&1 &

echo $! > "$PID_FILE"
echo "started server-watch-build.py (pid=$!)"

