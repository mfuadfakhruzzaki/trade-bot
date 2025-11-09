# AI Trading Bot - Bitget SOLUSDT Futures

Bot trading otomatis berbasis AI untuk Bitget SOLUSDT Futures dengan modal kecil dan scalable.

## 🚀 Features

- ✅ **AI-Powered Trading**: Multiple ML models (Logistic Regression, Random Forest, XGBoost)
- ✅ **Technical Analysis**: 50+ indicators (MA, EMA, RSI, MACD, Bollinger Bands, dll)
- ✅ **Risk Management**: Position sizing, leverage control, stop loss, take profit
- ✅ **Real-time Monitoring**: Telegram notifications & structured logging
- ✅ **Backtesting**: Comprehensive performance analysis
- ✅ **Dry Run Mode**: Test strategies without real money
- ✅ **Testnet Support**: Practice with Bitget testnet

## 📋 Prerequisites

- Python 3.10+
- Bitget account (testnet or mainnet)
- Telegram Bot (optional, for notifications)

## 🛠️ Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd bot-trade
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: TA-Lib memerlukan instalasi binary terlebih dahulu:

**Linux/Mac:**

```bash
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install TA-Lib
```

**Windows:**

- Download TA-Lib binary dari [ini](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib)
- Install: `pip install TA_Lib‑0.4.xx‑cp310‑cp310‑win_amd64.whl`

### 4. Setup Environment Variables

Copy `.env.example` ke `.env`:

```bash
cp .env.example .env
```

Edit `.env` dan isi dengan credentials Anda:

```env
# Bitget API Configuration
BITGET_API_KEY=your_api_key_here
BITGET_API_SECRET=your_api_secret_here
BITGET_PASSWORD=your_api_password_here

# Trading Configuration
TRADING_PAIR=SOL/USDT:USDT
INITIAL_CAPITAL=100
LEVERAGE=5

# Telegram Notifications (optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

### 5. Configure Bot Settings

Edit `config/config.yaml` sesuai kebutuhan:

```yaml
# Exchange Configuration
exchange:
  name: bitget
  type: futures
  testnet: true # Set false untuk mainnet

# Trading Configuration
trading:
  pair: SOL/USDT:USDT
  initial_capital: 100
  leverage: 5
  interval: 300 # 5 minutes

# Risk Management
risk_management:
  risk_per_trade: 2 # percentage
  max_loss_per_day: 10 # percentage
  stop_loss_percent: 2.0
  take_profit_percent: 4.0
```

## 📊 Training the Model

Sebelum menjalankan bot, Anda perlu melatih model AI:

```bash
python model/train.py
```

Script ini akan:

1. Mengambil data historical dari Bitget
2. Ekstraksi fitur teknikal
3. Train multiple models
4. Save model terbaik ke folder `model/`

**Output:**

- `model/xgboost_YYYYMMDD_HHMMSS.pkl` - Trained model
- `data/raw_data_*.csv` - Raw OHLCV data
- `data/processed_data_*.csv` - Processed features

## 🤖 Running the Bot

### Dry Run Mode (Recommended for Testing)

```bash
python main.py --dry-run
```

Bot akan berjalan dalam mode simulasi tanpa eksekusi order real.

### Live Trading (Testnet)

```bash
python main.py
```

Pastikan `testnet: true` di `config.yaml`.

### Live Trading (Mainnet - REAL MONEY!)

⚠️ **WARNING: USE AT YOUR OWN RISK!**

1. Set `testnet: false` di `config.yaml`
2. Gunakan API key mainnet
3. Run:

```bash
python main.py
```

### Stop the Bot

Press `Ctrl+C` untuk graceful shutdown.

## 📈 Backtesting

Test strategi pada data historical:

```bash
python backtest/backtester.py
```

Output:

- Performance metrics (win rate, profit factor, Sharpe ratio)
- Equity curve visualization
- Drawdown analysis
- Trade distribution

## 📁 Project Structure

```
bot-trade/
├── config/
│   └── config.yaml           # Bot configuration
├── data/                      # Historical & processed data
├── model/                     # Trained AI models
│   ├── ai_model.py           # Model implementation
│   └── train.py              # Training pipeline
├── utils/
│   ├── data_collector.py     # Bitget API data fetching
│   ├── feature_engineering.py # Technical indicators
│   ├── risk_manager.py       # Risk management
│   ├── trade_executor.py     # Order execution
│   ├── logger.py             # Logging system
│   └── notifier.py           # Telegram notifications
├── backtest/
│   └── backtester.py         # Backtesting framework
├── logs/                      # Log files
├── main.py                    # Main bot engine
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🔧 Configuration Guide

### Exchange Settings

```yaml
exchange:
  testnet: true # true = testnet, false = mainnet
```

### Trading Parameters

```yaml
trading:
  pair: SOL/USDT:USDT # Trading pair
  initial_capital: 100 # Starting capital (USDT)
  leverage: 5 # Leverage multiplier (1-125)
  interval: 300 # Trading interval (seconds)
```

### Risk Management

```yaml
risk_management:
  risk_per_trade: 2 # Risk per trade (%)
  max_loss_per_day: 10 # Max daily loss (%)
  max_open_positions: 3 # Max concurrent positions
  stop_loss_percent: 2.0 # Stop loss (%)
  take_profit_percent: 4.0 # Take profit (%)
  trailing_stop: false # Enable trailing stop
  cooldown_period: 600 # Cooldown after loss (seconds)
```

### AI Model

```yaml
ai_model:
  type: xgboost # Model type: logistic, random_forest, xgboost
  confidence_threshold: 0.60 # Min confidence to trade
  model_path: model/xgboost_latest.pkl # Path to trained model
```

### Indicators

```yaml
indicators:
  moving_averages:
    - period: 7
      type: EMA
    - period: 25
      type: EMA
  rsi:
    period: 14
  macd:
    fast: 12
    slow: 26
    signal: 9
```

## 📱 Telegram Notifications

### Setup Telegram Bot

1. Chat dengan [@BotFather](https://t.me/botfather)
2. Create bot: `/newbot`
3. Copy bot token
4. Get chat ID:
   - Chat dengan bot Anda
   - Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   - Copy `chat.id`

### Enable Notifications

```yaml
notifications:
  telegram:
    enabled: true
    on_trade: true
    on_error: true
    daily_summary: true
```

## 🔍 Monitoring & Logs

### Web Dashboard

Bot dilengkapi dengan web dashboard real-time untuk monitoring:

```bash
# Run dashboard saja
python run_dashboard.py

# Run bot + dashboard bersamaan
./run_all.sh

# Run dengan dry-run mode
./run_all.sh --dry-run
```

Dashboard features:

- ✅ Real-time bot status monitoring
- ✅ Live equity curve chart
- ✅ PnL distribution visualization
- ✅ Trade history table
- ✅ Current open positions
- ✅ Last trading signal with confidence
- ✅ Performance metrics (win rate, profit factor)
- ✅ Auto-refresh every 5 seconds

**Access dashboard**: `http://localhost:5000`

![Dashboard Preview](https://via.placeholder.com/800x400?text=Trading+Bot+Dashboard)

### Log Files

- `logs/trading_bot.log` - All bot activities
- `logs/trading_bot_error.log` - Errors only
- `logs/dashboard.log` - Dashboard activities

### Log Levels

Set di `config.yaml`:

```yaml
logging:
  level: INFO # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### View Logs

```bash
tail -f logs/trading_bot.log
```

## 🐛 Troubleshooting

### TA-Lib Installation Error

**Error:** `fatal error: ta-lib/ta_defs.h: No such file or directory`

**Solution:** Install TA-Lib binary first (see Installation section)

### Bitget API Error

**Error:** `ccxt.AuthenticationError`

**Solution:**

- Verify API credentials di `.env`
- Check API permissions (futures trading enabled)
- Ensure testnet/mainnet setting matches API key

### Model Not Found

**Error:** `No pre-trained model found`

**Solution:** Train model first:

```bash
python model/train.py
```

### Insufficient Capital

**Error:** `Insufficient capital (50% drawdown reached)`

**Solution:**

- Wait for capital to recover
- Adjust `max_loss_per_day` di config
- Reset bot with new capital

## 📊 Performance Tips

### Optimize Model

1. Collect more historical data (30+ days)
2. Try different models (Random Forest, XGBoost)
3. Tune hyperparameters
4. Adjust confidence threshold

### Risk Management

1. Start with small capital (testnet)
2. Use lower leverage (3-5x)
3. Set conservative stop loss (2-3%)
4. Limit max open positions (1-3)

### Monitoring

1. Enable Telegram notifications
2. Check logs regularly
3. Monitor daily PnL
4. Backtest before going live

## ⚠️ Disclaimer

**THIS BOT IS FOR EDUCATIONAL PURPOSES ONLY.**

- Trading crypto futures is **extremely risky**
- You can lose **all your capital**
- Past performance ≠ future results
- Test thoroughly on testnet first
- Never invest more than you can afford to lose
- No guarantee of profit

**USE AT YOUR OWN RISK!**

## 🚀 Deployment (VPS)

### Setup on Ubuntu VPS

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10
sudo apt install python3.10 python3.10-venv python3-pip -y

# Install TA-Lib
sudo apt install build-essential wget -y
cd /tmp
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
sudo ldconfig

# Clone & setup bot
cd ~
git clone <repository-url> bot-trade
cd bot-trade
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup .env
nano .env  # Edit credentials

# Train model
python model/train.py

# Run bot in background
nohup python main.py > output.log 2>&1 &

# Check logs
tail -f logs/trading_bot.log
```

### Using systemd (Recommended)

Create service file: `/etc/systemd/system/trading-bot.service`

```ini
[Unit]
Description=AI Trading Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/bot-trade
Environment="PATH=/home/ubuntu/bot-trade/venv/bin"
ExecStart=/home/ubuntu/bot-trade/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable & start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
sudo systemctl status trading-bot
```

View logs:

```bash
sudo journalctl -u trading-bot -f
```

### 🐳 Deployment on Dokploy (Docker PaaS)

Dokploy is a modern PaaS platform for easy Docker deployments.

**Quick Deploy:**

```bash
# 1. Push to Git
git init
git add .
git commit -m "Initial commit"
git push origin main

# 2. Create app in Dokploy Dashboard
# 3. Connect repository
# 4. Set environment variables
# 5. Deploy!
```

**Files included:**

- `Dockerfile` - Container image definition
- `docker-compose.yml` - Multi-service setup
- `dokploy.yml` - Dokploy configuration
- `.dockerignore` - Exclude unnecessary files

**Full guide**: See [DOKPLOY_DEPLOYMENT.md](DOKPLOY_DEPLOYMENT.md)

**Benefits:**

- ✅ Zero-downtime deployments
- ✅ Auto-scaling
- ✅ Built-in monitoring
- ✅ SSL certificates (Let's Encrypt)
- ✅ Easy rollbacks
- ✅ Environment management

**Deploy modes:**

```bash
# Dashboard only (monitoring)
RUN_MODE=dashboard

# Bot + Dashboard
RUN_MODE=all

# Bot only
RUN_MODE=bot
```

**Access dashboard:**

```
https://trading-bot-xxxx.dokploy.app
```

## 📝 TODO / Future Improvements

- [ ] Add LSTM model support
- [ ] Multiple trading pairs
- [x] Web dashboard for monitoring ✅
- [ ] Advanced order types (trailing stop, OCO)
- [ ] Portfolio rebalancing
- [ ] Sentiment analysis integration
- [ ] Auto-retraining scheduler

## 🤝 Contributing

Contributions welcome! Please:

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## 📄 License

MIT License - See LICENSE file

## 💬 Support

For issues or questions:

- Open GitHub issue
- Email: [your-email]
- Telegram: [@your-telegram]

---

**Happy Trading! 🚀📈**

Remember: Always test on testnet first!
