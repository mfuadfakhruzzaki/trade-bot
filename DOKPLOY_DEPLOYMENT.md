# 🚀 Deployment Guide - Dokploy

Complete guide untuk deploy Trading Bot di Dokploy (Docker-based PaaS platform).

## 📋 Prerequisites

- Akun Dokploy ([dokploy.com](https://dokploy.com))
- Git repository (GitHub/GitLab/Bitbucket)
- Bitget API credentials
- Telegram bot (optional)

## 🎯 Quick Deployment (5 menit)

### 1. Push ke Git Repository

```bash
# Initialize git (jika belum)
cd /home/zacht/projects/bot-trade
git init
git add .
git commit -m "Initial commit - Trading Bot"

# Push ke GitHub
git remote add origin https://github.com/yourusername/bot-trade.git
git branch -M main
git push -u origin main
```

### 2. Setup di Dokploy Dashboard

1. **Login ke Dokploy**

   - Buka https://dokploy.com
   - Login dengan akun Anda

2. **Create New Application**

   - Click "New Application"
   - Pilih "Docker" sebagai deployment type
   - Nama: `trading-bot`

3. **Connect Repository**

   - Connect GitHub/GitLab
   - Pilih repository `bot-trade`
   - Branch: `main`

4. **Configure Build**

   - Build Method: `Dockerfile`
   - Dockerfile Path: `./Dockerfile`
   - Auto-deploy: ✅ Enabled

5. **Set Environment Variables**

   Required variables:

   ```env
   BITGET_API_KEY=your_api_key_here
   BITGET_API_SECRET=your_secret_here
   BITGET_PASSWORD=your_password_here
   ```

   Optional variables:

   ```env
   TRADING_PAIR=SOL/USDT:USDT
   INITIAL_CAPITAL=100
   LEVERAGE=5
   TELEGRAM_BOT_TOKEN=your_token
   TELEGRAM_CHAT_ID=your_chat_id
   MODEL_TYPE=xgboost
   RUN_MODE=all
   ```

6. **Configure Port**

   - Container Port: `5000`
   - Public Port: `5000` (atau pilih lain)
   - Protocol: `HTTP`

7. **Set Health Check**

   - Path: `/api/status`
   - Port: `5000`
   - Interval: `30s`

8. **Configure Resources** (optional)

   - CPU: 0.5 - 1.0 cores
   - Memory: 512MB - 1GB
   - Storage: 2GB (untuk logs & data)

9. **Deploy!**
   - Click "Deploy"
   - Wait 3-5 minutes for build & deployment

### 3. Access Dashboard

```
Your app URL: https://trading-bot-xxxx.dokploy.app
or
Your custom domain: https://bot.yourdomain.com
```

## 🔧 Deployment Modes

### Mode 1: Dashboard Only (Default)

Deploy dashboard saja untuk monitoring:

```env
RUN_MODE=dashboard
```

Bot dijalankan terpisah (di local atau VPS lain), dashboard hanya untuk visualisasi data.

### Mode 2: Bot + Dashboard

Deploy bot dan dashboard dalam satu container:

```env
RUN_MODE=all
```

⚠️ **Note**: Memerlukan persistent storage untuk model & data!

### Mode 3: Bot Only

Deploy bot saja tanpa dashboard:

```env
RUN_MODE=bot
```

Dashboard dijalankan terpisah atau tidak digunakan.

## 📦 Multi-Container Setup (Recommended)

Untuk production, pisahkan bot dan dashboard menggunakan `docker-compose.yml`:

### Setup di Dokploy:

1. **Create Application 1: Dashboard**

   - Name: `trading-dashboard`
   - Service: `dashboard` (from docker-compose.yml)
   - Port: 5000
   - Public URL: ✅ Enabled

2. **Create Application 2: Bot**
   - Name: `trading-bot`
   - Service: `trading-bot` (from docker-compose.yml)
   - No public port needed
   - Depends on: `trading-dashboard`

### Benefits:

- ✅ Separate scaling
- ✅ Independent restarts
- ✅ Better resource management
- ✅ Easier debugging

## 💾 Persistent Storage

### Configure Volumes in Dokploy:

1. **Logs Volume**

   ```
   Volume Name: trading-logs
   Mount Path: /app/logs
   Size: 1GB
   ```

2. **Data Volume**

   ```
   Volume Name: trading-data
   Mount Path: /app/data
   Size: 500MB
   ```

3. **Model Volume**

   ```
   Volume Name: trading-model
   Mount Path: /app/model
   Size: 500MB
   ```

4. **Dashboard Data**
   ```
   Volume Name: dashboard-data
   Mount Path: /app/monitoring/dashboard_data.json
   Type: File
   ```

## 🔒 Security Best Practices

### 1. Environment Variables

**NEVER** commit `.env` ke git! Use Dokploy's secret management:

```bash
# In Dokploy Dashboard > Environment Variables
# Mark as "Secret" ✅
BITGET_API_KEY=***
BITGET_API_SECRET=***
BITGET_PASSWORD=***
```

### 2. API Access

Restrict dashboard access:

```python
# Update monitoring/dashboard.py
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

users = {
    "admin": "your_secure_password"
}

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return users[username] == password
    return False

@app.route('/')
@auth.login_required
def dashboard():
    return render_template('dashboard.html')
```

Then add to requirements.txt:

```
Flask-HTTPAuth>=4.8.0
```

### 3. Custom Domain + SSL

In Dokploy:

- Go to Domains
- Add: `bot.yourdomain.com`
- SSL: Auto (Let's Encrypt) ✅
- Force HTTPS: ✅

### 4. Firewall Rules

Only allow necessary ports:

- `5000` - Dashboard (via SSL)
- Block all other ports

## 📊 Monitoring in Production

### Dokploy Built-in Monitoring

1. **Logs**

   ```
   Dokploy Dashboard > Logs
   - Real-time container logs
   - Download & search
   ```

2. **Metrics**

   ```
   Dokploy Dashboard > Metrics
   - CPU usage
   - Memory usage
   - Network traffic
   ```

3. **Alerts** (if available)
   ```
   Set alerts for:
   - Container crashes
   - High CPU/memory
   - Health check failures
   ```

### External Monitoring

Add monitoring tools:

```python
# Add to requirements.txt
sentry-sdk>=1.40.0

# In main.py
import sentry_sdk

sentry_sdk.init(
    dsn="your_sentry_dsn",
    traces_sample_rate=1.0,
)
```

## 🔄 CI/CD Setup

### Auto-Deploy on Git Push

Dokploy automatically deploys when you push to main branch:

```bash
git add .
git commit -m "Update strategy"
git push origin main

# Dokploy will:
# 1. Detect push
# 2. Build new image
# 3. Run tests (if configured)
# 4. Deploy with zero-downtime
```

### Manual Deploy

```bash
# In Dokploy Dashboard
Applications > trading-bot > Deploy
```

### Rollback

```bash
# In Dokploy Dashboard
Applications > trading-bot > Deployments
Select previous version > Rollback
```

## 🧪 Testing Before Production

### 1. Test Locally with Docker

```bash
# Build image
docker build -t trading-bot .

# Run dashboard only
docker run -p 5000:5000 \
  -e RUN_MODE=dashboard \
  trading-bot

# Test
curl http://localhost:5000/api/status
```

### 2. Test with Docker Compose

```bash
# Create .env file
cp .env.example .env
nano .env  # Fill in credentials

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Dry-Run Test

```bash
# Add to docker-compose.yml environment
- DRY_RUN=true

# Deploy and verify no real trades
```

## 💰 Cost Estimation

### Dokploy Pricing (example):

**Hobby Plan** ($5-10/month):

- 512MB RAM
- 0.5 CPU
- 2GB Storage
- ✅ Good for testing

**Starter Plan** ($15-25/month):

- 1GB RAM
- 1 CPU
- 5GB Storage
- ✅ Good for small trading

**Pro Plan** ($50+/month):

- 2GB+ RAM
- 2+ CPU
- 10GB+ Storage
- ✅ Good for serious trading

### Cost Optimization:

1. **Use testnet** during development
2. **Dashboard-only mode** (bot on cheaper VPS)
3. **Scheduled scaling** (scale down during low volume)
4. **Log rotation** (prevent storage bloat)

## 🐛 Troubleshooting

### Issue 1: Build Fails

```bash
# Check build logs in Dokploy
# Common issues:
- TA-Lib installation failed
- Out of memory during build
- Missing dependencies

# Solution: Increase build resources
Settings > Resources > Build
CPU: 2 cores
Memory: 2GB
```

### Issue 2: Container Crashes

```bash
# Check container logs
Dokploy > Logs

# Common causes:
- Missing environment variables
- API credentials invalid
- Out of memory
- Model file not found

# Solution: Check environment & volumes
```

### Issue 3: Health Check Failing

```bash
# Test health check endpoint
curl https://your-app.dokploy.app/api/status

# If fails:
- Check if dashboard started
- Verify port 5000 is correct
- Check firewall rules
```

### Issue 4: Dashboard Shows Old Data

```bash
# Check if volume is mounted
Dokploy > Volumes > Verify mount path

# Check if bot is updating data
Dokploy > Logs > Search "dashboard"
```

## 🚀 Production Checklist

Before going live:

- [ ] Tested on testnet in Dokploy
- [ ] All environment variables set (as secrets)
- [ ] Persistent volumes configured
- [ ] Health checks working
- [ ] Custom domain configured (optional)
- [ ] SSL/HTTPS enabled
- [ ] Authentication added to dashboard
- [ ] Telegram notifications working
- [ ] Backup strategy in place
- [ ] Monitoring/alerts configured
- [ ] Emergency stop procedure documented
- [ ] Resource limits appropriate
- [ ] Logs rotating properly
- [ ] Cost estimate within budget

## 📚 Additional Resources

- **Dokploy Docs**: https://docs.dokploy.com
- **Docker Best Practices**: https://docs.docker.com/develop/dev-best-practices/
- **Flask Production**: https://flask.palletsprojects.com/en/latest/deploying/
- **Security Guide**: https://cheatsheetseries.owasp.org/

## 💬 Support

Issues with deployment? Check:

1. Dokploy Dashboard > Logs
2. Container health: `docker ps`
3. Environment variables: Correct & complete?
4. Volumes: Mounted correctly?
5. Network: Bot can reach Bitget API?

Happy Trading on Dokploy! 🚀📈
