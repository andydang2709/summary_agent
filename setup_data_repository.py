#!/usr/bin/env python3
"""
Script to set up the separate data repository structure.
This creates the necessary files and structure for the email-summary-data repository.
"""

import os
import json
from datetime import datetime

def create_data_repository_structure():
    """Create the structure for the data repository."""
    
    print("🚀 Setting up Email Summary Data Repository Structure")
    print("=" * 60)
    
    # Create data directory structure
    data_dir = "data_repository"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"✅ Created directory: {data_dir}")
    
    # Create logs subdirectory
    logs_dir = os.path.join(data_dir, "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print(f"✅ Created directory: {logs_dir}")
    
    # Create README for the data repository
    readme_content = """# Email Summary Data Repository

This repository contains the generated email summaries and reports from the Email Summary Agent.

## Structure

- `logs/` - Daily email summary reports (YYYYMMDD_email_summary_report.txt)
- `storytelling/` - Storytelling summaries for text-to-speech (YYYYMMDD_storytelling_summary.txt)
- `file_index.json` - Index of all available files with metadata
- `latest/` - Most recent summaries (today_email_summary_report.txt, executive_summary.txt)

## Files

### Daily Reports
- `20250817_email_summary_report.txt` - August 17, 2025 email summary
- `20250816_email_summary_report.txt` - August 16, 2025 email summary
- etc.

### Storytelling Summaries
- `20250817_storytelling_summary.txt` - August 17, 2025 storytelling summary
- `20250816_storytelling_summary.txt` - August 16, 2025 storytelling summary
- etc.

### Current Files
- `today_email_summary_report.txt` - Today's email summary
- `executive_summary.txt` - Today's storytelling summary

## Updates

This repository is automatically updated daily by GitHub Actions from the main Email Summary Agent repository.

## Usage

The main application fetches data from this repository via GitHub Pages URLs:
- `https://[username].github.io/email-summary-data/file_index.json`
- `https://[username].github.io/email-summary-data/logs/[filename]`
- `https://[username].github.io/email-summary-data/latest/[filename]`

## GitHub Pages

This repository is configured to serve files via GitHub Pages, making the data accessible to the main application.
"""
    
    readme_path = os.path.join(data_dir, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"✅ Created README: {readme_path}")
    
    # Create .gitignore for the data repository
    gitignore_content = """# Data Repository .gitignore

# Python cache files
__pycache__/
*.py[cod]
*$py.class

# Environment files
.env
*.env

# Credentials and tokens
*credentials*.json
*token*.pickle

# Temporary files
*.tmp
*.temp
*.log

# Keep all summary files
!*.txt
!*.json
!*.md
"""
    
    gitignore_path = os.path.join(data_dir, ".gitignore")
    with open(gitignore_path, 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    print(f"✅ Created .gitignore: {gitignore_path}")
    
    # Create GitHub Pages configuration
    pages_config = """# GitHub Pages Configuration

This repository is configured to serve files via GitHub Pages.

## Settings

1. Go to Settings > Pages
2. Source: Deploy from a branch
3. Branch: main
4. Folder: / (root)
5. Save

## CNAME (Optional)

If you have a custom domain, add it to Settings > Pages > Custom domain.
"""
    
    pages_path = os.path.join(data_dir, "GITHUB_PAGES_SETUP.md")
    with open(pages_path, 'w', encoding='utf-8') as f:
        f.write(pages_config)
    print(f"✅ Created GitHub Pages setup guide: {pages_path}")
    
    # Create sample file index structure
    sample_index = {
        "generated_at": datetime.now().isoformat(),
        "total_files": 0,
        "files": [],
        "repository_info": {
            "name": "email-summary-data",
            "description": "Email summary data repository",
            "github_pages_url": "https://[username].github.io/email-summary-data"
        }
    }
    
    index_path = os.path.join(data_dir, "file_index.json")
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(sample_index, f, indent=2, ensure_ascii=False)
    print(f"✅ Created sample file index: {index_path}")
    
    # Create setup instructions
    setup_instructions = """# Data Repository Setup Instructions

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
"""
    
    instructions_path = os.path.join(data_dir, "SETUP_INSTRUCTIONS.md")
    with open(instructions_path, 'w', encoding='utf-8') as f:
        f.write(setup_instructions)
    print(f"✅ Created setup instructions: {instructions_path}")
    
    print("\n" + "=" * 60)
    print("🎉 Data Repository Structure Created Successfully!")
    print("=" * 60)
    print(f"📁 Created in: {data_dir}/")
    print("\n📋 Next Steps:")
    print("1. Create a new GitHub repository called 'email-summary-data'")
    print("2. Copy the contents of the 'data_repository/' folder to it")
    print("3. Set up GitHub Pages on the new repository")
    print("4. Add the required secrets to your main repository")
    print("5. Test the workflow")
    
    return data_dir

if __name__ == "__main__":
    create_data_repository_structure()
