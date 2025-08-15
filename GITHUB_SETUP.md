# 🚀 GitHub Actions Setup Guide

This guide will walk you through setting up your Email Summary Dashboard with GitHub Actions and GitHub Pages.

## 📋 Prerequisites

- GitHub account
- Gmail account with app password
- Google Gemini API key
- Git installed on your local machine

## 🔧 Step-by-Step Setup

### Step 1: Create GitHub Repository

1. **Go to GitHub** and click the "+" icon → "New repository"
2. **Name your repository** (e.g., `email-summary-dashboard`)
3. **Make it public** (required for GitHub Pages)
4. **Don't initialize** with README, .gitignore, or license
5. **Click "Create repository"**

### Step 2: Push Your Code

Run these commands in your project directory:

```bash
# Initialize git repository
git init

# Add all files
git add .

# Make initial commit
git commit -m "Initial commit: Email Summary Dashboard"

# Set main branch
git branch -M main

# Add remote origin (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git push -u origin main
```

### Step 3: Set Repository Secrets

1. **Go to your repository** → **Settings** → **Secrets and variables** → **Actions**
2. **Click "New repository secret"**
3. **Add these three secrets**:

   | Secret Name | Value |
   |-------------|-------|
   | `GMAIL_USERNAME` | Your Gmail address |
   | `GMAIL_PASSWORD` | Your Gmail app password |
   | `GEMINI_API_KEY` | Your Google Gemini API key |

4. **Click "Add secret"** for each one

### Step 4: Enable GitHub Pages

1. **Go to your repository** → **Settings** → **Pages**
2. **Source**: Select **"GitHub Actions"**
3. **Click "Configure"** if prompted
4. **Wait for deployment** (may take a few minutes)

### Step 5: Verify Workflows

1. **Go to your repository** → **Actions** tab
2. **You should see two workflows**:
   - **Daily Email Summary** - Runs your Python script daily
   - **Deploy to GitHub Pages** - Deploys your website

## 🧪 Testing Your Setup

### Test Manual Execution

1. **Go to Actions** → **Daily Email Summary**
2. **Click "Run workflow"** → **"Run workflow"**
3. **Watch the execution** in real-time
4. **Check for any errors** in the logs

### Expected Behavior

- ✅ **Workflow runs successfully**
- ✅ **Email summary script executes**
- ✅ **New summary files are generated**
- ✅ **Files are committed to repository**
- ✅ **GitHub Pages site updates**

## 📅 Schedule Configuration

### Current Schedule
- **Runs daily at 6:00 AM ET** (11:00 AM UTC)
- **Automatically triggered** by cron schedule
- **Can be manually triggered** anytime

### Change Schedule
Edit `.github/workflows/schedule-email-summary.yml`:

```yaml
schedule:
  - cron: '0 11 * * *'  # 6:00 AM ET daily
  # Format: minute hour day month day-of-week
  # Examples:
  # '0 9 * * *'     # 9:00 AM ET daily
  # '0 18 * * 1-5'  # 6:00 PM ET weekdays only
  # '0 12 * * 0'    # 12:00 PM ET Sundays only
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Workflow Not Running
- **Check Actions tab** for error messages
- **Verify repository secrets** are set correctly
- **Check cron syntax** in workflow file

#### 2. Authentication Errors
- **Verify Gmail credentials** are correct
- **Check Gmail app password** (not regular password)
- **Ensure Gemini API key** is valid

#### 3. Pages Not Updating
- **Check Pages deployment** in Actions
- **Verify workflow completed** successfully
- **Wait a few minutes** for deployment

#### 4. File Generation Issues
- **Check Python dependencies** in requirements.txt
- **Verify file paths** in main.py
- **Check workflow logs** for Python errors

### Debug Commands

Run locally to test:
```bash
# Test setup
python setup_github_actions.py

# Test email summary script
cd email_summary
python main.py

# Check file structure
ls -la .github/workflows/
ls -la email_summary/
```

## 📁 File Structure

After setup, your repository should look like:

```
email-summary-dashboard/
├── .github/
│   └── workflows/
│       ├── schedule-email-summary.yml  # Daily email processing
│       └── pages.yml                   # GitHub Pages deployment
├── email_summary/
│   ├── main.py                         # Main script
│   ├── requirements.txt                # Python dependencies
│   └── logs/                           # Generated summaries
├── index.html                          # Dashboard page
├── script.js                           # Frontend logic
├── styles.css                          # Styling
├── README.md                           # Project documentation
├── GITHUB_SETUP.md                     # This guide
└── .gitignore                          # Git ignore rules
```

## 🎯 What Happens Daily

1. **6:00 AM ET**: GitHub Actions triggers
2. **Script runs**: Fetches emails, generates summaries
3. **Files created**: New summary files in logs/ directory
4. **Repository updated**: New files committed automatically
5. **Pages deployed**: Website updates with new content
6. **Dashboard shows**: Latest summaries available

## 🔐 Security Notes

- **Repository secrets** are encrypted and secure
- **No credentials** are stored in code
- **Script runs** in isolated GitHub environment
- **Logs are private** to your repository

## 📞 Support

- **GitHub Issues**: Report bugs in your repository
- **Actions Logs**: Check workflow execution details
- **Local Testing**: Test changes locally before pushing

## 🎉 Success!

Once everything is working:
- ✅ **Your website** will be available at `https://YOUR_USERNAME.github.io/YOUR_REPO_NAME`
- ✅ **Email summaries** will be generated daily at 6:00 AM ET
- ✅ **Website updates** automatically with new content
- ✅ **No server maintenance** required

Your Email Summary Dashboard is now fully automated! 🚀
