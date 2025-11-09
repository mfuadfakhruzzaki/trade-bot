#!/bin/bash

# Deployment script untuk VPS/Server
# Run: bash deploy.sh

echo "=========================================="
echo "Bot Trading Deployment Script"
echo "=========================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "⚠️  Don't run as root. Run as normal user."
    exit 1
fi

# Update system
echo ""
echo "1. Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.10
echo ""
echo "2. Installing Python 3.10..."
sudo apt install -y python3.10 python3.10-venv python3-pip build-essential wget git

# Install TA-Lib
echo ""
echo "3. Installing TA-Lib..."
if [ ! -f "/usr/lib/libta_lib.so" ]; then
    cd /tmp
    wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
    tar -xzf ta-lib-0.4.0-src.tar.gz
    cd ta-lib/
    ./configure --prefix=/usr
    make
    sudo make install
    sudo ldconfig
    echo "✓ TA-Lib installed"
else
    echo "✓ TA-Lib already installed"
fi

# Go back to project directory
cd ~/bot-trade || exit

# Create virtual environment
echo ""
echo "4. Creating virtual environment..."
python3.10 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo ""
echo "5. Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup .env if not exists
echo ""
echo "6. Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API credentials"
    echo "   Run: nano .env"
else
    echo "✓ .env file already exists"
fi

# Create systemd service
echo ""
echo "7. Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/trading-bot.service"

sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=AI Trading Bot for Bitget Futures
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/bot-trade
Environment="PATH=$HOME/bot-trade/venv/bin"
ExecStart=$HOME/bot-trade/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=append:$HOME/bot-trade/logs/systemd.log
StandardError=append:$HOME/bot-trade/logs/systemd_error.log

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Systemd service created"

# Reload systemd
sudo systemctl daemon-reload

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env with your credentials:"
echo "   nano .env"
echo ""
echo "2. Edit config if needed:"
echo "   nano config/config.yaml"
echo ""
echo "3. Train the model:"
echo "   source venv/bin/activate"
echo "   python model/train.py"
echo ""
echo "4. Test with dry run:"
echo "   python main.py --dry-run"
echo ""
echo "5. Enable and start service:"
echo "   sudo systemctl enable trading-bot"
echo "   sudo systemctl start trading-bot"
echo ""
echo "6. Check status:"
echo "   sudo systemctl status trading-bot"
echo ""
echo "7. View logs:"
echo "   tail -f logs/trading_bot.log"
echo "   sudo journalctl -u trading-bot -f"
echo ""
echo "=========================================="
