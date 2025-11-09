# 🚀 Complete Usage Guide - Trading Bot + Dashboard

## 📋 Quick Reference

### Essential Commands

```bash
# Run dashboard only (view data)
python run_dashboard.py

# Run bot + dashboard together
./run_all.sh

# Run in dry-run mode (no real trades)
./run_all.sh --dry-run

# Run dashboard on different port
python run_dashboard.py --port 8080

# Stop all services
Ctrl + C
```

### URLs

```
Dashboard:        http://localhost:5000
Dashboard (VPS):  http://<your-ip>:5000
```

## 🎯 Step-by-Step Workflows

### Workflow 1: First Time Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
nano .env  # Add your API keys

# 3. Train model
python -c "from model.train import ModelTrainer; trainer = ModelTrainer(); trainer.run_full_pipeline()"

# 4. Test with dry-run
./run_all.sh --dry-run

# 5. Monitor on dashboard
# Open http://localhost:5000 in browser
```

### Workflow 2: Daily Trading

```bash
# Morning: Check configuration
cat config/config.yaml

# Start bot with dashboard
./run_all.sh

# Monitor throughout day
# Keep dashboard open: http://localhost:5000

# Evening: Check logs and stop
cat logs/trading_bot.log
Ctrl + C  # Stop bot
```

### Workflow 3: Backtesting Strategy

```bash
# 1. Prepare historical data
python -c "from utils.data_collector import DataCollector; dc = DataCollector(...); data = dc.fetch_historical_data('SOL/USDT:USDT', '5m', days=30)"

# 2. Run backtest
python -c "from backtest.backtester import Backtester; bt = Backtester(); bt.run_backtest(); bt.plot_results()"

# 3. Review results
# Check generated charts and metrics

# 4. Adjust parameters in config.yaml
nano config/config.yaml

# 5. Repeat until satisfied
```

### Workflow 4: Live Deployment on VPS

```bash
# 1. Deploy to VPS
./deploy.sh

# 2. Setup systemd service
sudo nano /etc/systemd/system/trading-bot.service
# (See DASHBOARD.md for service file)

sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot

# 3. Setup dashboard service
sudo nano /etc/systemd/system/trading-dashboard.service
sudo systemctl enable trading-dashboard
sudo systemctl start trading-dashboard

# 4. Configure firewall
sudo ufw allow 5000/tcp
sudo ufw enable

# 5. Monitor remotely
# Access http://<vps-ip>:5000
```

## 📊 Dashboard Usage Scenarios

### Scenario 1: Monitoring Active Trading

**What to watch:**

1. **Bot Status Badge** - Should show "Running"
2. **PnL** - Track profit/loss in real-time
3. **Last Signal** - See what AI is predicting
4. **Open Positions** - Monitor active trades
5. **Equity Curve** - Ensure upward trend

**Actions:**

- ✅ Keep browser tab open
- ✅ Set alerts for significant changes
- ✅ Check every hour during active trading
- ⚠️ If PnL drops significantly, review logs
- ⚠️ If bot stops, check main.py logs

### Scenario 2: Post-Trade Analysis

**What to review:**

1. **Recent Trades Table** - Review last 20 trades
2. **PnL Distribution** - Check win/loss pattern
3. **Win Rate** - Should be >50% ideally
4. **Profit Factor** - Should be >1.0
5. **Trade History** - Identify losing patterns

**Actions:**

- 📊 Export trade data (screenshot or manual)
- 📝 Note any unusual patterns
- 🔧 Adjust config.yaml if needed
- 🎯 Retrain model with new data
- 📈 Compare with backtesting results

### Scenario 3: Troubleshooting Issues

**Dashboard shows "Stopped":**

```bash
# Check if bot is running
ps aux | grep main.py

# Check logs
tail -f logs/trading_bot.log
tail -f logs/trading_bot_error.log

# Restart bot
./run_all.sh
```

**No trades showing:**

```bash
# Check dashboard data
cat monitoring/dashboard_data.json

# Verify bot is executing trades
grep "Executing" logs/trading_bot.log

# Check risk manager
grep "Trade not executed" logs/trading_bot.log
```

**Charts not updating:**

```bash
# Check dashboard logs
tail -f logs/dashboard.log

# Restart dashboard
pkill -f dashboard.py
python run_dashboard.py
```

## 🔧 Configuration Tuning

### Aggressive Trading (Higher Risk)

```yaml
# config/config.yaml
trading:
  leverage: 10 # Higher leverage

risk_management:
  risk_per_trade: 3 # 3% risk per trade
  max_loss_per_day: 15 # 15% max daily loss
  stop_loss_percent: 1.5 # Tighter stop loss
  take_profit_percent: 5.0 # Higher profit target

ai_model:
  confidence_threshold: 0.55 # Lower threshold = more trades
```

**Expected Dashboard Behavior:**

- More frequent trades
- Higher PnL volatility
- Potentially higher returns
- Requires close monitoring

### Conservative Trading (Lower Risk)

```yaml
# config/config.yaml
trading:
  leverage: 3 # Lower leverage

risk_management:
  risk_per_trade: 1 # 1% risk per trade
  max_loss_per_day: 5 # 5% max daily loss
  stop_loss_percent: 3.0 # Wider stop loss
  take_profit_percent: 3.0 # Lower profit target

ai_model:
  confidence_threshold: 0.75 # Higher threshold = fewer trades
```

**Expected Dashboard Behavior:**

- Fewer trades
- Lower PnL volatility
- Steadier equity curve
- Less monitoring needed

## 📱 Mobile Monitoring

### Using Phone Browser

1. **Connect to same WiFi** as bot server
2. **Open browser** on phone
3. **Navigate to** `http://<server-ip>:5000`
4. **Add to home screen** for quick access

### Using VPN (Remote Access)

1. **Setup VPN** on server (WireGuard/OpenVPN)
2. **Connect phone** to VPN
3. **Access dashboard** via VPN IP
4. **Bookmark** for easy access

### Using SSH Tunnel (Secure)

```bash
# On phone using Termux or similar
ssh -L 5000:localhost:5000 user@server-ip

# Then access
http://localhost:5000
```

## 🔔 Alert Setup

### Telegram Notifications

Already integrated! Configure in `.env`:

```env
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

Receives alerts for:

- ✅ New trades executed
- ✅ Significant PnL changes
- ✅ Daily summaries
- ✅ Errors and warnings
- ✅ Bot start/stop

### Email Alerts (Optional)

Add to `utils/notifier.py`:

```python
import smtplib
from email.mime.text import MIMEText

def send_email_alert(subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = 'bot@yourdomain.com'
    msg['To'] = 'your@email.com'

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('bot@yourdomain.com', 'password')
        server.send_message(msg)
```

## 📊 Performance Monitoring

### Key Metrics to Track

**Daily:**

- Total PnL
- Number of trades
- Win rate
- Largest win/loss

**Weekly:**

- Average daily PnL
- Consistency of returns
- Drawdown periods
- Model accuracy

**Monthly:**

- Total return %
- Sharpe ratio
- Max drawdown
- Compare vs. HODL

### Export Data for Analysis

```bash
# Export trade history
cat monitoring/dashboard_data.json | jq '.trades' > trades_export.json

# Convert to CSV (using Python)
python -c "
import json
import pandas as pd
with open('monitoring/dashboard_data.json') as f:
    data = json.load(f)
df = pd.DataFrame(data['trades'])
df.to_csv('trades_export.csv', index=False)
"
```

## 🐛 Common Issues & Solutions

### Issue 1: Dashboard shows old data

**Solution:**

```bash
# Check data file timestamp
ls -lh monitoring/dashboard_data.json

# Verify bot is updating it
tail -f logs/trading_bot.log | grep -i dashboard

# Force refresh browser
Ctrl + Shift + R
```

### Issue 2: Bot not executing trades

**Check these in order:**

1. Is confidence threshold too high? (config.yaml)
2. Are we in cooldown period? (check logs)
3. Have we hit max daily loss? (check logs)
4. Is model trained? (check model/ folder)
5. Are API credentials correct? (.env file)

### Issue 3: Charts not displaying

**Solution:**

```bash
# Check browser console for errors
F12 → Console tab

# Verify Chart.js is loading
curl -I https://cdn.jsdelivr.net/npm/chart.js

# Clear browser cache
Ctrl + Shift + Delete
```

## 🎓 Best Practices

### DO ✅

- Always start with dry-run mode
- Test on testnet before mainnet
- Monitor dashboard regularly
- Keep logs for analysis
- Backup configuration files
- Review trades weekly
- Retrain model monthly
- Set realistic profit targets
- Use proper risk management
- Keep initial capital small

### DON'T ❌

- Don't use real money without testing
- Don't set leverage too high
- Don't ignore max loss limits
- Don't trade during high volatility without preparation
- Don't change config during active trades
- Don't expose dashboard publicly without auth
- Don't rely solely on AI predictions
- Don't skip backtesting
- Don't over-optimize parameters
- Don't trade with money you can't lose

## 📚 Learning Resources

### Understanding the Dashboard

- **Equity Curve**: [Investopedia - Equity Curve](https://www.investopedia.com/terms/e/equity-curve.asp)
- **Profit Factor**: [Investopedia - Profit Factor](https://www.investopedia.com/terms/p/profit-factor.asp)
- **Sharpe Ratio**: [Investopedia - Sharpe Ratio](https://www.investopedia.com/terms/s/sharperatio.asp)
- **Win Rate**: [Investopedia - Win Rate](https://www.investopedia.com/terms/w/win-rate.asp)

### Technical Analysis

- **Moving Averages**: [Investopedia - MA](https://www.investopedia.com/terms/m/movingaverage.asp)
- **RSI**: [Investopedia - RSI](https://www.investopedia.com/terms/r/rsi.asp)
- **MACD**: [Investopedia - MACD](https://www.investopedia.com/terms/m/macd.asp)
- **Bollinger Bands**: [Investopedia - BB](https://www.investopedia.com/terms/b/bollingerbands.asp)

### Risk Management

- **Position Sizing**: [Investopedia - Position Sizing](https://www.investopedia.com/terms/p/positionsizing.asp)
- **Stop Loss**: [Investopedia - Stop Loss](https://www.investopedia.com/terms/s/stop-lossorder.asp)
- **Risk/Reward Ratio**: [Investopedia - Risk Reward](https://www.investopedia.com/terms/r/riskrewardratio.asp)

## 🎯 Success Checklist

Before going live with real money:

- [ ] Completed dry-run testing (at least 1 week)
- [ ] Backtested strategy with 3+ months data
- [ ] Win rate > 50% in backtesting
- [ ] Profit factor > 1.2 in backtesting
- [ ] Tested on testnet (at least 2 weeks)
- [ ] Dashboard working and monitored
- [ ] Telegram notifications configured
- [ ] Logs reviewed and understood
- [ ] Risk parameters set conservatively
- [ ] Stop loss and take profit configured
- [ ] Max daily loss limit set
- [ ] API keys secured (.env permissions)
- [ ] Backup of configuration files
- [ ] Emergency stop procedure practiced
- [ ] Understanding of all bot features

If all checked, you're ready to trade! 🚀

## 💬 Support

For issues or questions:

1. Check logs: `logs/trading_bot.log`
2. Review README.md and DASHBOARD.md
3. Check configuration: `config/config.yaml`
4. Test modules: `./test_modules.sh`
5. Verify environment: `.env` file

Happy Trading! 📈💰
