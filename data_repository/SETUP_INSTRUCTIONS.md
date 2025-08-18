# Data Repository Setup Instructions

## 1. Create the Repository

1. Go to GitHub and create a new repository called `email-summary-data`
2. Make it public (required for GitHub Pages)
3. Don't initialize with README, .gitignore, or license

## 2. Set Up GitHub Pages

1. Go to your new repository
2. Go to Settings > Pages
3. Source: Deploy from a branch
4. Branch: main
5. Folder: / (root)
6. Click Save

## 3. Add Repository Secrets

In your MAIN repository (summary_agent), add these secrets:

1. Go to Settings > Secrets and variables > Actions
2. Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `DATA_REPO_TOKEN` | Personal access token with repo access |
| `DATA_REPO_OWNER` | Your GitHub username |

## 4. Generate Personal Access Token

1. Go to GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
2. Generate new token
3. Give it repo access
4. Copy the token and add it as `DATA_REPO_TOKEN`

## 5. Push This Structure

1. Clone your new data repository
2. Copy all files from the `data_repository/` folder
3. Commit and push

## 6. Test the Setup

1. Run the main workflow manually
2. Check if files are pushed to the data repository
3. Verify GitHub Pages is serving the files

## 7. Update Main Application

The main application will now fetch from:
- `https://[username].github.io/email-summary-data/file_index.json`
- `https://[username].github.io/email-summary-data/logs/[filename]`

## File Structure After Setup

```
email-summary-data/
├── README.md
├── .gitignore
├── file_index.json
├── logs/
│   ├── 20250817_email_summary_report.txt
│   ├── 20250817_storytelling_summary.txt
│   └── ...
├── latest/
│   ├── today_email_summary_report.txt
│   └── executive_summary.txt
└── GITHUB_PAGES_SETUP.md
```
