#!/bin/bash
# Script to STOP the bot completely

echo "🛑 Stopping Watchdog Script..."
pkill -f run_forever.sh

echo "🛑 Stopping Python Bot..."
pkill -f main.py

echo "✅ Bot successfully stopped. You can now make changes."
