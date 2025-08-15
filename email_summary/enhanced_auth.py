#!/usr/bin/env python3
"""
Enhanced authentication system for Gmail API.
This script provides better token management and automated authentication options.
"""

import os
import pickle
import json
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class EnhancedGmailAuth:
    """Enhanced Gmail authentication with better token management."""
    
    def __init__(self, credentials_file, token_file):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        
    def authenticate(self, force_refresh=False):
        """Authenticate with Gmail API using enhanced token management."""
        creds = None
        
        # Load existing token if available and not forcing refresh
        if not force_refresh and os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
                print(f"📂 Loaded existing token from {self.token_file}")
            except Exception as e:
                print(f"⚠️ Error loading token: {e}")
                creds = None
        
        # Check if credentials are valid
        if creds and creds.valid:
            print("✅ Using existing valid credentials")
        elif creds and creds.expired and creds.refresh_token:
            try:
                print("🔄 Refreshing expired credentials...")
                creds.refresh(Request())
                print("✅ Credentials refreshed successfully")
            except RefreshError as e:
                print(f"❌ Error refreshing credentials: {e}")
                creds = None
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if not os.path.exists(self.credentials_file):
                raise FileNotFoundError(
                    f"Credentials file '{self.credentials_file}' not found. "
                    "Please download it from Google Cloud Console."
                )
            
            print("🔐 Starting OAuth2 authentication flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, SCOPES)
            
            # Use a higher port to avoid conflicts
            creds = flow.run_local_server(port=0, open_browser=True)
            print("✅ OAuth2 authentication completed")
            
            # Save credentials for next run
            try:
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
                print(f"💾 Credentials saved to {self.token_file}")
            except Exception as e:
                print(f"⚠️ Warning: Could not save credentials: {e}")
        
        # Build the Gmail service
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            print(f"✅ Successfully authenticated with Gmail API using {self.credentials_file}")
            return True
        except HttpError as error:
            print(f"❌ Error building Gmail service: {error}")
            raise
    
    def check_token_status(self):
        """Check the status of the current token."""
        if not os.path.exists(self.token_file):
            return "No token file found"
        
        try:
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
            
            if creds.valid:
                expiry = creds.expiry
                if expiry:
                    time_until_expiry = expiry - datetime.utcnow().replace(tzinfo=expiry.tzinfo)
                    if time_until_expiry > timedelta(days=1):
                        return f"Valid until {expiry.strftime('%Y-%m-%d %H:%M:%S')} ({time_until_expiry.days} days remaining)"
                    elif time_until_expiry > timedelta(hours=1):
                        return f"Valid until {expiry.strftime('%Y-%m-%d %H:%M:%S')} ({time_until_expiry.seconds//3600} hours remaining)"
                    else:
                        return f"Expires soon: {expiry.strftime('%Y-%m-%d %H:%M:%S')}"
                else:
                    return "Valid (no expiry set)"
            elif creds.expired and creds.refresh_token:
                return "Expired but refreshable"
            else:
                return "Expired and not refreshable"
                
        except Exception as e:
            return f"Error reading token: {e}"
    
    def test_connection(self):
        """Test the Gmail API connection."""
        if not self.service:
            return False, "Service not initialized"
        
        try:
            # Try to get user profile to test connection
            profile = self.service.users().getProfile(userId='me').execute()
            email = profile.get('emailAddress', 'Unknown')
            return True, f"Connected as {email}"
        except HttpError as error:
            return False, f"Connection failed: {error}"
    
    def get_service(self):
        """Get the Gmail service instance."""
        return self.service

def setup_automated_auth():
    """Set up automated authentication for multiple accounts."""
    print("🔧 SETTING UP AUTOMATED AUTHENTICATION")
    print("=" * 50)
    
    # Check existing tokens (professional account only)
    accounts = [
        ('professional', 'professional_credentials.json', 'professional_token.pickle')
    ]
    
    for account_name, cred_file, token_file in accounts:
        print(f"\n📋 Account: {account_name}")
        print(f"   Credentials: {cred_file}")
        print(f"   Token: {token_file}")
        
        if os.path.exists(cred_file) and os.path.exists(token_file):
            auth = EnhancedGmailAuth(cred_file, token_file)
            status = auth.check_token_status()
            print(f"   Status: {status}")
            
            # Test connection
            success, message = auth.test_connection()
            if success:
                print(f"   ✅ Connection: {message}")
            else:
                print(f"   ❌ Connection: {message}")
                print(f"   🔄 Re-authenticating...")
                try:
                    auth.authenticate()
                    success, message = auth.test_connection()
                    if success:
                        print(f"   ✅ Re-authenticated: {message}")
                    else:
                        print(f"   ❌ Re-authentication failed: {message}")
                except Exception as e:
                    print(f"   ❌ Authentication error: {e}")
        else:
            print(f"   ❌ Missing files")
    
    print(f"\n🎯 To run without authentication popups:")
    print(f"   1. Run this script once to authenticate all accounts")
    print(f"   2. Tokens will be saved and reused automatically")
    print(f"   3. Run main.py - it will use existing tokens")

if __name__ == "__main__":
    setup_automated_auth()
