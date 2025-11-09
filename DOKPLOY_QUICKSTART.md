# 🚀 Dokploy Quick Start - 5 Menit Deploy!

Deploy trading bot + dashboard ke Dokploy dalam 5 menit.

## ⚡ Step 1: Persiapan (1 menit)

```bash
# Clone atau prepare repository
cd bot-trade

# Pastikan semua file ada
ls -la Dockerfile docker-compose.yml dokploy.yml
```

## 📤 Step 2: Push ke Git (1 menit)

```bash
# Initialize Git (jika belum)
git init
git add .
git commit -m "Ready for Dokploy deployment"

# Push ke GitHub/GitLab
git remote add origin https://github.com/yourusername/bot-trade.git
git push -u origin main
```

## 🎯 Step 3: Deploy di Dokploy (3 menit)

### A. Login & Create App

1. Go to https://dokploy.com
2. Login dengan GitHub/GitLab
3. Click **"New Application"**
4. Name: `trading-bot`

### B. Connect Repository

1. **Source**: GitHub/GitLab
2. **Repository**: Select `bot-trade`
3. **Branch**: `main`
4. **Build Method**: Dockerfile

### C. Set Environment Variables

Click **Environment** tab, add:

```env
# Required - Bitget API
BITGET_API_KEY=your_api_key
BITGET_API_SECRET=your_secret
BITGET_PASSWORD=your_password

# Optional - Trading Config
TRADING_PAIR=SOL/USDT:USDT
INITIAL_CAPITAL=100
LEVERAGE=5

# Optional - Telegram
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id

# Optional - Mode
RUN_MODE=all
```

⚠️ **Important**: Mark API keys as **"Secret"** (eye icon)

### D. Configure Port

1. **Container Port**: `5000`
2. **Enable Public Access**: ✅
3. **Protocol**: HTTP
4. **Custom Domain** (optional): `bot.yourdomain.com`

### E. Deploy!

1. Click **"Deploy"** button
2. Wait 2-3 minutes for build
3. ✅ Done!

## 🎉 Step 4: Access Dashboard

Your app is live at:

```
https://trading-bot-[random].dokploy.app
```

Or your custom domain:

```
https://bot.yourdomain.com
```

## ✅ Verify Deployment

Check these:

1. **Dashboard loads**

   - Open URL in browser
   - Should see dashboard UI

2. **API works**

   ```bash
   curl https://your-app.dokploy.app/api/status
   ```

3. **Bot is running**

   - Check Dokploy logs
   - Look for "Trading Bot initialized"

4. **Telegram works** (if configured)
   - Should receive startup notification

## 🔧 Post-Deployment

### View Logs

```
Dokploy Dashboard > Applications > trading-bot > Logs
```

### Monitor Resources

```
Dokploy Dashboard > Applications > trading-bot > Metrics
```

### Update Config

```bash
# Edit config locally
nano config/config.yaml

# Commit & push
git add config/config.yaml
git commit -m "Update config"
git push

# Dokploy auto-deploys!
```

### Restart App

```
Dokploy Dashboard > Applications > trading-bot > Restart
```

## 🐛 Quick Troubleshooting

### Build Failed?

```
Check: Dokploy > Logs > Build
Common: TA-Lib installation issue
Fix: Increase build resources (2GB RAM)
```

### Container Crashes?

```
Check: Dokploy > Logs > Runtime
Common: Missing environment variables
Fix: Add required env vars in dashboard
```

### Dashboard Not Loading?

```
Check: Port 5000 exposed?
Check: Health check passing?
Fix: Verify Dockerfile EXPOSE 5000
```

### No Trades Executing?

```
Check: Logs for "Trade not executed"
Common: Confidence threshold too high
Fix: Adjust in config.yaml
```

## 💡 Pro Tips

**Tip 1: Use Testnet First**

```env
# In environment variables
BITGET_API_KEY=testnet_key
BITGET_API_SECRET=testnet_secret
# Set testnet: true in config.yaml
```

**Tip 2: Dashboard Only Mode**

```env
RUN_MODE=dashboard
# Run bot separately on local/VPS
```

**Tip 3: Enable Auto-Deploy**

```
Dokploy > Settings > Auto Deploy: ON
Every push to main = auto deployment
```

**Tip 4: Set Resource Limits**

```
Dokploy > Resources
CPU: 1 core
Memory: 1GB
Storage: 2GB
```

**Tip 5: Add Custom Domain**

```
Dokploy > Domains > Add Domain
bot.yourdomain.com
Auto SSL: ON ✅
```

## 📊 Deployment Modes

### Mode 1: Dashboard Only (Recommended for Start)

```env
RUN_MODE=dashboard
```

- Bot runs locally
- Dashboard on Dokploy for 24/7 access
- Lower cost

### Mode 2: Bot + Dashboard (All-in-One)

```env
RUN_MODE=all
```

- Everything on Dokploy
- Easy management
- Requires persistent storage

### Mode 3: Separate Services (Production)

Use `docker-compose.yml`:

- Service 1: Dashboard (public)
- Service 2: Bot (private)
- Best scalability

## 🎯 Next Steps

After successful deployment:

1. ✅ Monitor dashboard for 24 hours
2. ✅ Check logs for any errors
3. ✅ Verify trades executing (dry-run)
4. ✅ Set up alerts (Telegram)
5. ✅ Test with small capital
6. ✅ Scale up gradually

## 📚 Documentation

- **Full Guide**: [DOKPLOY_DEPLOYMENT.md](DOKPLOY_DEPLOYMENT.md)
- **Dashboard**: [DASHBOARD.md](DASHBOARD.md)
- **Usage**: [USAGE_GUIDE.md](USAGE_GUIDE.md)
- **README**: [README.md](README.md)

## 🆘 Need Help?

Check logs first:

```bash
# Dokploy Dashboard
Applications > trading-bot > Logs

# Look for:
- "Trading Bot initialized" ✅
- "Error" or "Exception" ❌
- "Trade executed" ✅
```

Still stuck? Review:

1. Environment variables complete?
2. API credentials correct?
3. Port 5000 exposed?
4. Health check passing?

Happy Trading! 🚀📈
