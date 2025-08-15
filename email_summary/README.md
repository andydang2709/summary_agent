# Gmail API Email Retriever

A Python application that allows you to retrieve all emails from your Gmail account using the Gmail API.

## Features

- 🔐 OAuth2 authentication with Gmail API
- 📧 Retrieve all emails from your Gmail account
- 🔍 Search emails using Gmail search queries
- 💾 Save emails to JSON files
- 📊 Extract email metadata (subject, sender, date, body, etc.)
- 🔄 Automatic token refresh

## Prerequisites

- Python 3.7 or higher
- A Google account with Gmail
- Google Cloud Console access

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click on it and press "Enable"

### 3. Create OAuth 2.0 Credentials

1. In Google Cloud Console, go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop application" as the application type
4. Give it a name (e.g., "Gmail Email Retriever")
5. Click "Create"
6. Download the JSON file and rename it to `credentials.json`
7. Place `credentials.json` in the same directory as the script

### 4. Configure Gmail API Scopes

The application uses the following scope:
- `https://www.googleapis.com/auth/gmail.readonly` - Read-only access to Gmail

This scope allows the application to:
- Read your emails
- Search through emails
- Access email metadata and content
- **Cannot** send, delete, or modify emails

### 5. Multiple Gmail Accounts Setup

To use multiple Gmail accounts, you need to:

1. **Create separate Google Cloud projects** for each account
2. **Enable Gmail API** in each project
3. **Create OAuth 2.0 credentials** for each project
4. **Download and rename** credential files:
   - `personal_credentials.json` (for personal account)
   - `work_credentials.json` (for work account)
   - `business_credentials.json` (for business account)
5. **Configure OAuth consent screen** for each project
6. **Add test users** or publish to production

**Important**: Each account needs its own Google Cloud project and credentials file.

## Usage

### Basic Usage

Run the script to retrieve today's emails (limited to 100 for demo):

```bash
python gmail_retriever.py
```

### Programmatic Usage

```python
from gmail_retriever import GmailRetriever

# Initialize the retriever
gmail = GmailRetriever()

# Get today's emails (limit to 1000)
emails = gmail.get_todays_emails(max_results=1000)

# Get all emails (limit to 1000)
all_emails = gmail.get_all_emails(max_results=1000)

# Search for specific emails
important_emails = gmail.search_emails("subject:important", max_results=50)

# Save emails to file
gmail.save_emails_to_file(emails, "my_emails.json")
```

### Multiple Gmail Accounts

To use multiple Gmail accounts, use the `MultiAccountGmailRetriever` class:

```python
from gmail_retriever import MultiAccountGmailRetriever

# Configure multiple accounts
account_configs = [
    {
        'name': 'personal',
        'credentials_file': 'personal_credentials.json',
        'token_file': 'personal_token.pickle'
    },
    {
        'name': 'work',
        'credentials_file': 'work_credentials.json',
        'token_file': 'work_token.pickle'
    }
]

# Initialize multi-account retriever
multi_gmail = MultiAccountGmailRetriever(account_configs)

# Get today's emails from all accounts
all_emails = multi_gmail.get_todays_emails_from_all_accounts()

# Save emails to separate files
multi_gmail.save_all_emails_to_files(all_emails, "todays_emails")
```

Run the multi-account example:
```bash
python multi_account_example.py
```

### Email Search Queries

You can use Gmail search operators:

- `from:example@gmail.com` - Emails from specific sender
- `to:example@gmail.com` - Emails to specific recipient
- `subject:important` - Emails with "important" in subject
- `has:attachment` - Emails with attachments
- `after:2024/01/01` - Emails after specific date
- `before:2024/12/31` - Emails before specific date
- `label:work` - Emails with specific label

## Output Format

Each email is returned as a dictionary with the following structure:

```json
{
  "id": "email_id",
  "thread_id": "thread_id",
  "subject": "Email Subject",
  "sender": "sender@example.com",
  "recipient": "recipient@example.com",
  "date": "Wed, 15 Jan 2024 10:30:00 +0000",
  "parsed_date": "2024-01-15T10:30:00+00:00",
  "snippet": "Email preview text...",
  "body": "Full email body content",
  "labels": ["INBOX", "UNREAD"],
  "internal_date": "1705312200000",
  "size_estimate": 1234
}
```

## Security Notes

- The application only requests read-only access to your Gmail
- Credentials are stored locally in `token.pickle`
- Never share your `credentials.json` or `token.pickle` files
- The application runs locally and doesn't send data to external servers

## Troubleshooting

### Common Issues

1. **"Credentials file not found"**
   - Make sure `credentials.json` is in the same directory as the script
   - Verify the file was downloaded from Google Cloud Console

2. **"Invalid credentials"**
   - Delete `token.pickle` and re-authenticate
   - Check if your Google Cloud project has Gmail API enabled

3. **"Quota exceeded"**
   - Gmail API has daily quotas
   - Consider implementing rate limiting for large email retrievals

4. **"Permission denied"**
   - Ensure you're using the correct Google account
   - Check if the OAuth consent screen is properly configured

### Rate Limiting

Gmail API has quotas:
- 1 billion queries per day per user
- 250 queries per second per user
- 1,000 queries per 100 seconds per user

For large email retrievals, consider implementing delays between requests.

## File Structure

```
summary_agent/
├── gmail_retriever.py      # Main script
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── credentials.json       # OAuth2 credentials (you need to add this)
└── token.pickle          # Authentication token (created after first run)
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.
