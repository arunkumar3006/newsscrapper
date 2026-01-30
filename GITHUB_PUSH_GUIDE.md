# 🚀 GitHub Push & Deployment Guide

## Step 1: Initialize Git Repository

Open terminal in your project folder and run:

```bash
cd d:\newsscraper-main\newsscraper-main
git init
```

## Step 2: Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `news-intelligence-system` (or your choice)
3. Description: "News intelligence app that analyzes headlines to identify top agencies"
4. **Keep it Public** (for free Streamlit Cloud deployment)
5. **DO NOT** initialize with README (we already have one)
6. Click "Create repository"

## Step 3: Add Files to Git

```bash
git add .
git commit -m "Initial commit: News Intelligence System"
```

## Step 4: Connect to GitHub

Replace `YOUR_USERNAME` with your GitHub username:

```bash
git remote add origin https://github.com/YOUR_USERNAME/news-intelligence-system.git
git branch -M main
git push -u origin main
```

**If prompted for credentials:**
- Username: Your GitHub username
- Password: Use a Personal Access Token (not your password)

### How to create Personal Access Token:
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name: "News Intelligence Deploy"
4. Select scopes: `repo` (full control)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)
7. Use this token as your password

## Step 5: Verify Upload

Go to: `https://github.com/YOUR_USERNAME/news-intelligence-system`

You should see all your files!

---

## 🌐 Deploy to Streamlit Cloud (FREE)

### Step 1: Go to Streamlit Cloud

Visit: https://share.streamlit.io

### Step 2: Sign In

Click "Sign in with GitHub"

### Step 3: Deploy New App

1. Click "New app"
2. Repository: Select `news-intelligence-system`
3. Branch: `main`
4. Main file path: `app2.py`
5. Click "Deploy!"

### Step 4: Wait for Deployment

- Takes 2-5 minutes
- You'll see build logs
- Once done, you'll get a URL like: `https://your-app-name.streamlit.app`

### Step 5: Share Your App!

Your app is now live and accessible to anyone! 🎉

---

## 🔄 Update Your Deployed App

Whenever you make changes:

```bash
git add .
git commit -m "Description of changes"
git push origin main
```

Streamlit Cloud will **automatically redeploy** your app!

---

## 📋 Quick Command Reference

```bash
# Check status
git status

# Add all changes
git add .

# Commit changes
git commit -m "Your message"

# Push to GitHub
git push origin main

# Pull latest changes
git pull origin main

# View commit history
git log --oneline
```

---

## 🚨 Troubleshooting

### "git: command not found"
Install Git: https://git-scm.com/downloads

### "Permission denied"
Use Personal Access Token instead of password

### "Repository not found"
Check the repository URL is correct

### "Failed to push"
```bash
git pull origin main --rebase
git push origin main
```

---

## ✅ Success Checklist

- [ ] Git repository initialized
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] Streamlit Cloud account created
- [ ] App deployed to Streamlit Cloud
- [ ] App is live and accessible

---

## 🎯 Your App URLs

After deployment, you'll have:

- **GitHub Repo:** `https://github.com/YOUR_USERNAME/news-intelligence-system`
- **Live App:** `https://your-app-name.streamlit.app`

---

**Need help? Check the DEPLOYMENT_GUIDE.md for more options!** 🚀
