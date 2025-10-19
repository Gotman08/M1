"""
Configuration settings for Email Security Cleaner.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# region API Keys
VIRUSTOTAL_API_KEY = os.getenv('VIRUSTOTAL_API_KEY', '')
URLSCAN_API_KEY = os.getenv('URLSCAN_API_KEY', '')
ABUSEIPDB_API_KEY = os.getenv('ABUSEIPDB_API_KEY', '')
# endregion

# region Threat Detection
DANGEROUS_EXTENSIONS = [
    '.exe', '.bat', '.cmd', '.com', '.scr', '.vbs', '.js', 
    '.jar', '.msi', '.reg', '.ps1', '.pif', '.app', '.apk',
    '.hta', '.wsf', '.lnk', '.dll', '.sys', '.ocx'
]

SUSPICIOUS_KEYWORDS = [
    'urgent', 'verify account', 'suspended', 'click here', 
    'confirm identity', 'prize', 'lottery', 'inheritance',
    'bitcoin', 'crypto', 'investment opportunity', 'act now',
    'limited time', 'password reset', 'unusual activity',
    'security alert', 'account locked', 'refund', 'tax return',
    'package delivery', 'wire transfer', 'social security'
]

DANGEROUS_DOMAINS = [
    'bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly', 'is.gd'
]

# Trusted domains - exclude from suspicious checks
TRUSTED_DOMAINS = [
    'safelinks.protection.outlook.com',  # Outlook SafeLinks
    'eur01.safelinks.protection.outlook.com',
    'nor01.safelinks.protection.outlook.com',
    'nam01.safelinks.protection.outlook.com',
    'apc01.safelinks.protection.outlook.com',
    'aka.ms',  # Microsoft short links
    'google.com', 'microsoft.com', 'apple.com',
    'github.com', 'stackoverflow.com'
]

OFFICIAL_BRANDS = [
    'paypal', 'bank', 'amazon', 'microsoft', 'google', 
    'apple', 'facebook', 'netflix', 'ebay', 'fedex', 'dhl'
]

LOOKALIKE_PATTERNS = [
    r'pay[p4]a[l1]', r'amaz[o0]n', r'micr[o0]s[o0]ft', 
    r'g[o0][o0]g[l1]e', r'app[l1]e', r'netf[l1]ix'
]

CREDENTIAL_PATTERNS = [
    r'password', r'username', r'credit\s*card', r'ssn', 
    r'social\s*security', r'pin\s*code', r'cvv', r'bank\s*account'
]

GENERIC_GREETINGS = [
    'dear customer', 'dear user', 'dear member', 'hello user'
]

FINANCIAL_TERMS = [
    'wire transfer', '$', '€', '£', 'bitcoin', 'wallet', 'payment', 'invoice'
]
# endregion

# region Scoring Thresholds
DEFAULT_THREAT_THRESHOLD = 50
VIRUSTOTAL_DETECTION_THRESHOLD = 10  # % of engines
URL_DETECTION_THRESHOLD = 5  # % of engines
# endregion

# region API Rate Limits
API_RATE_LIMITS = {
    'virustotal': {'calls': 0, 'max_per_minute': 4, 'last_reset': 0},
    'urlscan': {'calls': 0, 'max_per_minute': 10, 'last_reset': 0},
    'abuseipdb': {'calls': 0, 'max_per_day': 1000, 'last_reset': 0}
}
# endregion

# region Network Settings
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds
MAX_URLS_PER_EMAIL = 10
# endregion

# region Logging
LOG_FILE = 'mail_cleaner.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5
# endregion

# region Outlook Filters
OUTLOOK_MESSAGE_CLASS = 'IPM.Note'
# endregion

# region AI Detection
USE_AI_DETECTION = True
AI_MODEL_NAME = None  # Use default (distilbert-base-uncased)
AI_CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence for phishing prediction
# endregion
