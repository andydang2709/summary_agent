"""
Configuration file for Gmail API Email Retriever
Customize these settings according to your needs.
"""

# Gmail API Configuration
GMAIL_API_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly'
]

# File paths
TOKEN_FILE = 'token.pickle'
CREDENTIALS_FILE = 'credentials.json'

# Default settings
DEFAULT_MAX_RESULTS = 100
DEFAULT_SEARCH_LIMIT = 50

# Rate limiting (in seconds between requests)
REQUEST_DELAY = 0.1  # 100ms between requests

# Email export settings
DEFAULT_EXPORT_FORMAT = 'json'
EXPORT_DIRECTORY = 'exports'

# Search query templates
SEARCH_TEMPLATES = {
    'recent': 'after:{date}',
    'from_sender': 'from:{email}',
    'with_attachment': 'has:attachment',
    'unread': 'is:unread',
    'important': 'is:important',
    'starred': 'is:starred',
    'work': 'label:work',
    'personal': 'label:personal'
}

# Email parsing options
PARSE_OPTIONS = {
    'include_body': True,
    'include_headers': True,
    'include_labels': True,
    'max_body_length': 10000,  # Maximum body length to parse
    'preferred_mime_type': 'text/plain'  # Preferred body format
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file': 'gmail_retriever.log'
}
