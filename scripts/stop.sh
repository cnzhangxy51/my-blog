#!/bin/bash

PID_FILE="$(cd "$(dirname "$0")" && pwd)/server-watch-build.pid"

if [ ! -f "$PID_FILE" ]; then
  echo "not running"
  exit 0
fi

PID=$(cat "$PID_FILE")

if kill -0 "$PID" 2>/dev/null; then
  kill "$PID"
  echo "stopped (pid=$PID)"
else
  echo "process not found, cleaning pid file"
fi

rm -f "$PID_FILE"

