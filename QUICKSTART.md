# Quick Start Guide

Panduan cepat untuk menjalankan bot dalam 5 menit!

## 🚀 Quick Setup

### 1. Install Dependencies (5 menit)

```bash
# Clone repository
git clone <repo-url>
cd bot-trade

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Setup Credentials (2 menit)

```bash
# Copy .env template
cp .env.example .env

# Edit dengan credentials Anda
nano .env
```

**Minimal config di `.env`:**

```env
BITGET_API_KEY=your_testnet_key
BITGET_API_SECRET=your_testnet_secret
BITGET_PASSWORD=your_testnet_password
```

### 3. Train Model (10-15 menit)

```bash
python model/train.py
```

Tunggu hingga selesai. Output: `model/xgboost_*.pkl`

### 4. Test Bot (Dry Run)

```bash
python main.py --dry-run
```

Bot akan berjalan dalam mode simulasi. Check logs:

```bash
tail -f logs/trading_bot.log
```

### 5. Go Live (Testnet)

Edit `config/config.yaml`:

```yaml
exchange:
  testnet: true # Ensure this is true
```

Run bot:

```bash
python main.py
```

## 📋 Checklist Sebelum Live

- [ ] API key testnet sudah benar
- [ ] Model sudah trained
- [ ] Config sudah sesuai (leverage, risk, etc)
- [ ] Dry run berjalan tanpa error
- [ ] Telegram notification setup (optional)
- [ ] Monitor logs selama 1-2 jam pertama

## ⚡ Commands Cheat Sheet

```bash
# Train model
python model/train.py

# Dry run (simulation)
python main.py --dry-run

# Live trading
python main.py

# Backtest
python backtest/backtester.py

# View logs
tail -f logs/trading_bot.log

# Stop bot
Ctrl+C
```

## 🆘 Common Issues

### TA-Lib error?

Install binary first:

```bash
# Ubuntu/Debian
sudo apt install build-essential
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib && ./configure && make && sudo make install
```

### API authentication error?

- Check credentials di `.env`
- Verify testnet/mainnet setting
- Ensure API has futures permission

### Model not found?

Run training first:

```bash
python model/train.py
```

## 📞 Need Help?

Read full documentation: [README.md](README.md)

---

**Ready to trade! 🚀**
