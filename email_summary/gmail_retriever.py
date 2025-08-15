#!/usr/bin/env python3
"""
Gmail API Email Retriever
Retrieves all emails from your Gmail account using the Gmail API.
"""

import os
import pickle
import base64
import email
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Token and credentials file paths
TOKEN_FILE = 'token.pickle'
CREDENTIALS_FILE = 'credentials.json'


class GmailRetriever:
    def __init__(self, credentials_file=None, token_file=None):
        self.service = None
        self.credentials_file = credentials_file or CREDENTIALS_FILE
        self.token_file = token_file or TOKEN_FILE
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Gmail API using OAuth2 with enhanced token management."""
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
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
            except Exception as e:
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
        except HttpError as error:
            print(f"❌ Error building Gmail service: {error}")
            raise
    
    def get_all_emails(self, max_results: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve all emails from Gmail.
        
        Args:
            max_results: Maximum number of emails to retrieve (None for all)
        
        Returns:
            List of email data dictionaries
        """
        if not self.service:
            raise RuntimeError("Gmail service not initialized. Please authenticate first.")
        
        try:
            # Get list of message IDs
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            print(f"📧 Found {len(messages)} emails. Retrieving details...")
            
            for i, message in enumerate(messages):
                print(f"Processing email {i+1}/{len(messages)}...", end='\r')
                
                # Get full message details
                msg = self.service.users().messages().get(
                    userId='me', 
                    id=message['id'],
                    format='full'
                ).execute()
                
                email_data = self._parse_email_message(msg)
                emails.append(email_data)
            
            print(f"\n✅ Successfully retrieved {len(emails)} emails")
            return emails
            
        except HttpError as error:
            print(f"❌ Error retrieving emails: {error}")
            raise

    def get_todays_emails(self, max_results: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve only today's emails from Gmail.
        
        Args:
            max_results: Maximum number of emails to retrieve (None for all today's emails)
        
        Returns:
            List of email data dictionaries for today's emails only
        """
        if not self.service:
            raise RuntimeError("Gmail service not initialized. Please authenticate first.")
        
        try:
            # Get today's date in YYYY/MM/DD format for Gmail search
            today = datetime.now().strftime("%Y/%m/%d")
            search_query = f"after:{today}"
            
            print(f"🔍 Searching for emails after {today}...")
            
            # Get list of message IDs for today
            results = self.service.users().messages().list(
                userId='me',
                q=search_query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            if not messages:
                print("📧 No emails found for today")
                return []
            
            print(f"📧 Found {len(messages)} emails for today. Retrieving details...")
            
            for i, message in enumerate(messages):
                print(f"Processing email {i+1}/{len(messages)}...", end='\r')
                
                # Get full message details
                msg = self.service.users().messages().get(
                    userId='me', 
                    id=message['id'],
                    format='full'
                ).execute()
                
                email_data = self._parse_email_message(msg)
                emails.append(email_data)
            
            print(f"\n✅ Successfully retrieved {len(emails)} emails for today")
            return emails
            
        except HttpError as error:
            print(f"❌ Error retrieving today's emails: {error}")
            raise
    
    def _parse_email_message(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Gmail message into structured data."""
        headers = msg['payload']['headers']
        
        # Extract common headers
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
        recipient = next((h['value'] for h in headers if h['name'] == 'To'), 'Unknown Recipient')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
        
        # Parse date
        try:
            parsed_date = email.utils.parsedate_to_datetime(date)
        except:
            parsed_date = None
        
        # Extract body content
        body = self._extract_body(msg['payload'])
        
        return {
            'id': msg['id'],
            'thread_id': msg['threadId'],
            'subject': subject,
            'sender': sender,
            'recipient': recipient,
            'date': date,
            'parsed_date': parsed_date,
            'snippet': msg.get('snippet', ''),
            'body': body,
            'labels': msg.get('labelIds', []),
            'internal_date': msg.get('internalDate'),
            'size_estimate': msg.get('sizeEstimate')
        }
    
    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """Extract email body content from payload."""
        if 'body' in payload and payload['body'].get('data'):
            try:
                return base64.urlsafe_b64decode(
                    payload['body']['data']
                ).decode('utf-8', errors='ignore')
            except:
                pass
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if part['body'].get('data'):
                        try:
                            return base64.urlsafe_b64decode(
                                part['body']['data']
                            ).decode('utf-8', errors='ignore')
                        except:
                            pass
        
        return "Body content not available"
    
    def search_emails(self, query: str, max_results: int = None) -> List[Dict[str, Any]]:
        """
        Search emails using Gmail search query.
        
        Args:
            query: Gmail search query (e.g., "from:example@gmail.com", "subject:important")
            max_results: Maximum number of results to return
        
        Returns:
            List of matching emails
        """
        if not self.service:
            raise RuntimeError("Gmail service not initialized. Please authenticate first.")
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            print(f"🔍 Found {len(messages)} emails matching query: '{query}'")
            
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', 
                    id=message['id'],
                    format='full'
                ).execute()
                
                email_data = self._parse_email_message(msg)
                emails.append(email_data)
            
            return emails
            
        except HttpError as error:
            print(f"❌ Error searching emails: {error}")
            raise
    
    def save_emails_to_file(self, emails: List[Dict[str, Any]], filename: str = None):
        """Save retrieved emails to a JSON file."""
        import json
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"emails_{timestamp}.json"
        
        # Convert datetime objects to strings for JSON serialization
        serializable_emails = []
        for email_data in emails:
            serializable_email = email_data.copy()
            if serializable_email['parsed_date']:
                serializable_email['parsed_date'] = serializable_email['parsed_date'].isoformat()
            serializable_emails.append(serializable_email)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable_emails, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Emails saved to {filename}")


class MultiAccountGmailRetriever:
    """Class to handle multiple Gmail accounts"""
    
    def __init__(self, account_configs):
        """
        Initialize with multiple account configurations.
        
        Args:
            account_configs: List of dicts with 'name', 'credentials_file', 'token_file' keys
        Example:
            account_configs = [
                {'name': 'personal', 'credentials_file': 'personal_credentials.json', 'token_file': 'personal_token.pickle'},
                {'name': 'work', 'credentials_file': 'work_credentials.json', 'token_file': 'work_token.pickle'}
            ]
        """
        self.accounts = {}
        self.account_configs = account_configs
        
        # Initialize each account
        for config in account_configs:
            try:
                print(f"\n🔐 Initializing account: {config['name']}")
                self.accounts[config['name']] = GmailRetriever(
                    credentials_file=config['credentials_file'],
                    token_file=config['token_file']
                )
                print(f"✅ Account '{config['name']}' initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize account '{config['name']}': {e}")
                self.accounts[config['name']] = None
    
    def get_todays_emails_from_all_accounts(self, max_results_per_account: int = 50):
        """Retrieve today's emails from all accounts."""
        all_emails = {}
        
        for account_name, gmail_retriever in self.accounts.items():
            if gmail_retriever is None:
                print(f"⚠️ Skipping account '{account_name}' due to initialization failure")
                continue
                
            try:
                print(f"\n📧 Retrieving emails from account: {account_name}")
                emails = gmail_retriever.get_todays_emails(max_results=max_results_per_account)
                all_emails[account_name] = emails
                print(f"✅ Retrieved {len(emails)} emails from {account_name}")
                
            except Exception as e:
                print(f"❌ Error retrieving emails from {account_name}: {e}")
                all_emails[account_name] = []
        
        return all_emails
    
    def save_all_emails_to_files(self, all_emails, base_filename: str = None):
        """Save emails from all accounts to separate files."""
        if not base_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"emails_{timestamp}"
        
        for account_name, emails in all_emails.items():
            if emails:
                filename = f"{base_filename}_{account_name}.json"
                # Create a temporary GmailRetriever instance just for saving
                temp_retriever = GmailRetriever()
                temp_retriever.save_emails_to_file(emails, filename)
        
        print(f"💾 All emails saved with base filename: {base_filename}")
    
    def get_account_summary(self, all_emails):
        """Get a summary of emails from all accounts."""
        print(f"\n📊 Multi-Account Email Summary")
        print("=" * 50)
        
        total_emails = 0
        for account_name, emails in all_emails.items():
            count = len(emails)
            total_emails += count
            print(f"{account_name}: {count} emails")
        
        print(f"Total: {total_emails} emails across all accounts")
        return total_emails


def main():
    """Main function to retrieve today's emails from multiple Gmail accounts."""
    try:
        # Configure your account (professional only)
        account_configs = [
            {
                'name': 'professional', 
                'credentials_file': 'professional_credentials.json',
                'token_file': 'professional_token.pickle'
            }
        ]
        
        print("🔍 Initializing multi-account Gmail retriever...")
        
        # Initialize multi-account retriever
        multi_retriever = MultiAccountGmailRetriever(account_configs)
        
        # Get today's emails from all accounts
        print("\n📥 Retrieving today's emails from all accounts...")
        all_emails = multi_retriever.get_todays_emails_from_all_accounts(max_results_per_account=50)
        
        # Get emails from professional account only
        professional_emails = all_emails.get('professional', [])
        
        # Save professional account emails to file
        print("\n💾 Saving professional account emails to file...")
        # Use the existing authenticated service from the professional account
        professional_retriever = multi_retriever.accounts['professional']
        if professional_retriever and professional_retriever.service:
            # Save using the existing service
            import json
            with open("todays_emails_professional.json", 'w', encoding='utf-8') as f:
                json.dump(professional_emails, f, indent=2, default=str)
            print("✅ Emails saved successfully")
        else:
            print("❌ Could not save emails - no authenticated service available")
        
        # Display summary
        print("\n📊 Professional Account Summary:")
        if professional_emails:
            print(f"  Professional: {len(professional_emails)} emails")
            
            # Show first few emails
            for i, email_data in enumerate(professional_emails[:3]):
                print(f"    {i+1}. {email_data['subject'][:60]}...")
        else:
            print(f"  Professional: 0 emails")
        
        total_emails = len(professional_emails)
        print(f"\n🎯 Total emails retrieved today: {total_emails}")
        print(f"📁 Professional emails saved to: todays_emails_professional.json")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure you have:")
        print("1. Downloaded spam_credentials.json and professional_credentials.json from Google Cloud Console")
        print("2. Placed them in the same directory as this script")
        print("3. Installed required packages: pip install -r requirements.txt")
        print("4. Run the script to authenticate each account (browser will open for OAuth)")


if __name__ == '__main__':
    main()
