# Dashboard Quick Start Guide

Quick guide to set up and use the Trading Bot Dashboard.

## 🎯 Quick Setup (2 minutes)

### 1. Install Flask

```bash
# Activate virtual environment
source venv/bin/activate

# Install Flask if not already installed
pip install Flask>=3.0.0
```

### 2. Run Dashboard

**Option A: Dashboard Only** (view existing data)

```bash
python run_dashboard.py
```

**Option B: Bot + Dashboard** (run both services)

```bash
./run_all.sh
```

**Option C: Dry-Run Mode** (no real trades)

```bash
./run_all.sh --dry-run
```

### 3. Access Dashboard

Open your browser:

```
http://localhost:5000
```

Or from another device on the same network:

```
http://<your-server-ip>:5000
```

## 📊 Dashboard Features

### Real-Time Metrics

- **Capital**: Current account balance
- **PnL**: Total profit/loss with percentage
- **Total Trades**: Number of trades executed
- **Win Rate**: Percentage of profitable trades
- **Open Positions**: Current active positions
- **Profit Factor**: Ratio of gross profit to gross loss

### Charts

- **Equity Curve**: Track capital growth over time
- **PnL Distribution**: Visualize individual trade results

### Trading Signal

- Latest AI prediction (BUY/SELL/HOLD)
- Confidence level
- Timestamp

### Trade History

- Recent trades with entry/exit prices
- PnL per trade
- Return percentage

### Auto-Refresh

Dashboard automatically updates every 5 seconds to show latest data.

## 🔧 Configuration

### Change Port

```bash
python run_dashboard.py --port 8080
```

### Change Host (allow external access)

```bash
python run_dashboard.py --host 0.0.0.0 --port 5000
```

### Debug Mode

```bash
python run_dashboard.py --debug
```

## 🚀 Advanced Usage

### Run on VPS

1. **Install as systemd service:**

Create `/etc/systemd/system/trading-dashboard.service`:

```ini
[Unit]
Description=Trading Bot Dashboard
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/bot-trade
ExecStart=/path/to/bot-trade/venv/bin/python run_dashboard.py --host 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. **Start service:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-dashboard
sudo systemctl start trading-dashboard
```

### Using Nginx Reverse Proxy

Create nginx config:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Secure with HTTPS

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

## 🔒 Security Tips

1. **Don't expose dashboard publicly** without authentication
2. **Use VPN** to access dashboard remotely
3. **Set firewall rules** to restrict access:
   ```bash
   sudo ufw allow from <your-ip> to any port 5000
   ```
4. **Consider adding authentication** (basic auth or OAuth)

## 📱 Mobile Access

Dashboard is responsive and works on mobile browsers. Simply access the dashboard URL from your phone's browser.

## 🐛 Troubleshooting

### Dashboard not loading

**Check if Flask is installed:**

```bash
pip show Flask
```

**Check if dashboard is running:**

```bash
ps aux | grep dashboard
```

**Check logs:**

```bash
tail -f logs/dashboard.log
```

### No data showing

**Verify bot is running:**

```bash
ps aux | grep main.py
```

**Check dashboard data file:**

```bash
cat monitoring/dashboard_data.json
```

**Manually initialize data:**

```bash
python -c "from monitoring.dashboard import DashboardData; d = DashboardData(); print('Initialized')"
```

### Port already in use

**Use different port:**

```bash
python run_dashboard.py --port 5001
```

**Kill process on port 5000:**

```bash
lsof -ti:5000 | xargs kill -9
```

## 💡 Tips

1. **Monitor from anywhere**: Set up VPN for secure remote access
2. **Keep it running**: Use systemd service for auto-restart
3. **Multiple screens**: Open dashboard on second monitor while coding
4. **Screenshot alerts**: Set up automated screenshots for record-keeping
5. **Performance**: Dashboard is lightweight and won't affect bot performance

## 📞 Need Help?

- Check main README.md for full documentation
- Review bot logs in `logs/` directory
- Ensure .env configuration is correct
- Verify bot is running and generating data

## 🎨 Customization

Dashboard code is in `monitoring/dashboard.py` and `monitoring/templates/dashboard.html`. Feel free to customize colors, layout, or add new features!

Example customizations:

- Add more charts (RSI, MACD indicators)
- Add email alerts for big wins/losses
- Show funding rate data
- Display market sentiment
- Add trade execution buttons

Happy Trading! 🚀📈
