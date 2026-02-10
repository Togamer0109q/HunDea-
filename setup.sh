#!/bin/bash

echo "========================================"
echo "  HunDeaBot v3.0 - Setup Installer"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not found! Please install Python 3.8+"
    exit 1
fi

echo "[1/4] Python found:"
python3 --version
echo ""

# Install dependencies
echo "[2/4] Installing dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi
echo ""

# Create config from example
if [ ! -f config.json ]; then
    echo "[3/4] Creating config.json from example..."
    cp config_v3.example.json config.json
    echo "[!] Please edit config.json with your webhooks and API keys"
else
    echo "[3/4] config.json already exists, skipping..."
fi
echo ""

# Create cache file if missing
if [ ! -f cache.json ]; then
    echo "[4/4] Creating cache.json..."
    echo "{}" > cache.json
else
    echo "[4/4] cache.json already exists"
fi
echo ""

echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Edit config.json with your Discord webhooks"
echo "  2. (Optional) Add RAWG API key for better scoring"
echo "  3. Run: python3 hundea_v3.py"
echo ""
echo "For help, see README.md"
