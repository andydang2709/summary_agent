#!/usr/bin/env python3
"""
Setup script for GitHub Actions and GitHub Pages deployment.
This script helps verify your configuration and provides setup instructions.
"""

import os
import sys
from pathlib import Path

def check_files():
    """Check if all required files exist."""
    print("🔍 Checking required files...")
    
    required_files = [
        '.github/workflows/schedule-email-summary.yml',
        '.github/workflows/pages.yml',
        'email_summary/main.py',
        'email_summary/requirements.txt',
        'index.html',
        'script.js',
        'styles.css'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def check_environment_variables():
    """Check if required environment variables are set."""
    print("\n🔐 Checking environment variables...")
    
    required_vars = [
        'GMAIL_USERNAME',
        'GMAIL_PASSWORD', 
        'GEMINI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is not set")
            missing_vars.append(var)
    
    return len(missing_vars) == 0

def generate_setup_instructions():
    """Generate setup instructions for GitHub."""
    print("\n📋 GitHub Setup Instructions:")
    print("=" * 50)
    
    print("\n1. 🚀 Push to GitHub:")
    print("   git init")
    print("   git add .")
    print("   git commit -m 'Initial commit'")
    print("   git branch -M main")
    print("   git remote add origin <your-repo-url>")
    print("   git push -u origin main")
    
    print("\n2. 🔑 Set Repository Secrets:")
    print("   Go to: Settings → Secrets and variables → Actions")
    print("   Add these secrets:")
    print("   - GMAIL_USERNAME: your-email@gmail.com")
    print("   - GMAIL_PASSWORD: your-app-password")
    print("   - GEMINI_API_KEY: your-gemini-api-key")
    
    print("\n3. 🌐 Enable GitHub Pages:")
    print("   Go to: Settings → Pages")
    print("   Source: GitHub Actions")
    print("   Click 'Configure' if prompted")
    
    print("\n4. ✅ Verify Workflows:")
    print("   Go to: Actions tab")
    print("   You should see two workflows:")
    print("   - Daily Email Summary")
    print("   - Deploy to GitHub Pages")
    
    print("\n5. 🧪 Test Manual Trigger:")
    print("   Go to: Actions → Daily Email Summary")
    print("   Click 'Run workflow' → 'Run workflow'")
    print("   This will test your setup immediately")

def main():
    """Main setup function."""
    print("🚀 GitHub Actions Setup for Email Summary Dashboard")
    print("=" * 60)
    
    # Check files
    files_ok = check_files()
    
    # Check environment variables
    env_ok = check_environment_variables()
    
    # Generate instructions
    generate_setup_instructions()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Setup Summary:")
    print(f"   Files: {'✅ Ready' if files_ok else '❌ Issues found'}")
    print(f"   Environment: {'✅ Ready' if env_ok else '❌ Issues found'}")
    
    if files_ok and env_ok:
        print("\n🎉 Your project is ready for GitHub Actions!")
        print("   Follow the setup instructions above to deploy.")
    else:
        print("\n⚠️  Please fix the issues above before proceeding.")
        print("   Missing files or environment variables will cause failures.")

if __name__ == "__main__":
    main()
