#!/bin/bash

echo "========================================"
echo "  Starting HunDeaBot v3.0"
echo "========================================"
echo ""

# Check if config exists
if [ ! -f config.json ]; then
    echo "[ERROR] config.json not found!"
    echo "Please run ./setup.sh first."
    exit 1
fi

# Run the bot
echo "[INFO] Launching bot..."
echo ""
python3 hundea_v3.py

# Check exit code
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Bot crashed or stopped with errors"
    exit 1
fi
