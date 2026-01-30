# Deployment Guide - News Intelligence System

## 🚀 Quick Deploy Options

### Option 1: Streamlit Cloud (Easiest - FREE)

**Best for:** Quick deployment, free hosting, automatic updates

1. **Push to GitHub** (see instructions below)

2. **Deploy to Streamlit Cloud:**
   - Go to: https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app"
   - Select your repository: `news-intelligence-system`
   - Main file: `app2.py`
   - Click "Deploy"
   - Your app will be live at: `https://your-app-name.streamlit.app`

**Pros:**
- ✅ Completely FREE
- ✅ Automatic HTTPS
- ✅ Auto-deploys on git push
- ✅ No configuration needed

**Cons:**
- ⚠️ Limited resources (1GB RAM)
- ⚠️ App sleeps after inactivity

---

### Option 2: Heroku (FREE Tier Available)

**Best for:** More control, custom domain

1. **Create Procfile:**
```bash
echo "web: streamlit run app2.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
```

2. **Deploy:**
```bash
# Install Heroku CLI first
heroku login
heroku create your-app-name
git push heroku main
heroku open
```

**Pros:**
- ✅ More resources than Streamlit Cloud
- ✅ Custom domains
- ✅ Better uptime

**Cons:**
- ⚠️ Requires credit card (even for free tier)
- ⚠️ More complex setup

---

### Option 3: Railway (FREE $5/month credit)

**Best for:** Modern deployment, good free tier

1. **Go to:** https://railway.app
2. **Connect GitHub repo**
3. **Set start command:** `streamlit run app2.py`
4. **Deploy**

**Pros:**
- ✅ $5 free credit/month
- ✅ Easy setup
- ✅ Good performance

**Cons:**
- ⚠️ Credit card required after free tier

---

### Option 4: Render (FREE)

**Best for:** Free tier with good resources

1. **Go to:** https://render.com
2. **New Web Service**
3. **Connect GitHub repo**
4. **Build command:** `pip install -r requirements.txt`
5. **Start command:** `streamlit run app2.py --server.port=$PORT --server.address=0.0.0.0`

**Pros:**
- ✅ FREE tier
- ✅ Better resources than Streamlit Cloud
- ✅ No credit card needed

**Cons:**
- ⚠️ Slower cold starts

---

## 📋 Pre-Deployment Checklist

Before deploying, make sure you have:

- ✅ `app2.py` - Main application file
- ✅ `requirements.txt` - All dependencies listed
- ✅ `.gitignore` - Excludes unnecessary files
- ✅ `README.md` - Project documentation
- ✅ Logo file (optional): `Mavericks logo.png`

---

## 🔧 Environment Configuration

### For Streamlit Cloud:

No configuration needed! Just deploy.

### For Heroku/Railway/Render:

Create `.streamlit/config.toml`:

```toml
[server]
headless = true
port = $PORT
enableCORS = false

[browser]
gatherUsageStats = false
```

---

## 🌐 Custom Domain Setup

### Streamlit Cloud:
- Not available on free tier

### Heroku:
```bash
heroku domains:add www.yourdomain.com
```

### Railway/Render:
- Configure in dashboard settings

---

## 📊 Monitoring & Logs

### Streamlit Cloud:
- View logs in dashboard
- Monitor app health

### Heroku:
```bash
heroku logs --tail
```

### Railway/Render:
- View logs in dashboard

---

## 🔄 Updating Your Deployed App

### All Platforms:

1. Make changes locally
2. Commit and push:
```bash
git add .
git commit -m "Update: description"
git push origin main
```

3. App auto-deploys (Streamlit Cloud, Railway, Render)
4. For Heroku: `git push heroku main`

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid Plans Start At |
|----------|-----------|---------------------|
| **Streamlit Cloud** | ✅ Unlimited (1GB RAM) | N/A |
| **Heroku** | ✅ Limited hours | $7/month |
| **Railway** | ✅ $5 credit/month | $5/month |
| **Render** | ✅ Unlimited | $7/month |

---

## 🎯 Recommended Deployment Path

**For Beginners:**
1. Start with **Streamlit Cloud** (easiest, free)
2. If you need more resources → **Render**
3. If you need custom domain → **Heroku** or **Railway**

**For Production:**
- Use **Railway** or **Render** for better reliability
- Set up monitoring and alerts
- Configure custom domain

---

## 🚨 Troubleshooting

### App won't start:
- Check `requirements.txt` has all dependencies
- Verify Python version compatibility
- Check logs for errors

### Slow performance:
- Upgrade to paid tier
- Optimize code (reduce API calls)
- Add caching

### App sleeps/shuts down:
- Normal for free tiers
- Upgrade to paid tier for 24/7 uptime
- Use uptime monitoring services

---

## 📞 Support

- **Streamlit Cloud:** https://docs.streamlit.io/streamlit-community-cloud
- **Heroku:** https://devcenter.heroku.com
- **Railway:** https://docs.railway.app
- **Render:** https://render.com/docs

---

**Ready to deploy? Start with Streamlit Cloud - it's the easiest!** 🚀
