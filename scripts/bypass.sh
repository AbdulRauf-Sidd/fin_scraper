#!/bin/bash

# Find the process IDs (PIDs) using port 8000
PIDS=$(lsof -ti:8000)

# Check if any PIDs were found
if [ -z "$PIDS" ]; then
    echo "No processes found using port 8000"
fi

# Kill the processes
echo "Killing processes using port 8000:"
for PID in $PIDS; do
    echo "Killing process $PID"
    kill -9 $PID
done

# Verify the processes are killed
REMAINING_PIDS=$(lsof -ti:8000)
if [ -z "$REMAINING_PIDS" ]; then
    echo "All processes using port 8000 have been killed"
else
    echo "Failed to kill all processes using port 8000"
fi

cd ../CloudflareBypassForScraping
nohup python3 server.py > server.log 2>&1 &
sleep 10