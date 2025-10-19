# Outlook Email Security Cleaner

Advanced email threat detection and cleaning tool for Microsoft Outlook with **AI-powered phishing detection**.

## 🔒 Security Features

- **Passive Analysis Only**: Never opens links or executes files
- **Multi-Layer Threat Detection**: Local pattern matching + external API verification + AI analysis
- **AI-Powered Detection**: Machine learning models for semantic phishing detection
- **Safe File Handling**: Files only read for hash calculation, never executed
- **SPF/DKIM/DMARC Validation**: Email authentication checks

## 📁 Project Structure

```
Mail/
├── main.py              # Entry point
├── config.py            # Configuration settings
├── api_checkers.py      # External API integrations (VirusTotal, URLScan, AbuseIPDB)
├── email_analyzer.py    # Email content analysis
├── outlook_cleaner.py   # Outlook integration and folder scanning
└── README.md           # This file
```

## 🚀 Installation

```powershell
pip install pywin32 requests
```

## 🔑 API Configuration (Optional)

Set environment variables for enhanced detection:

```powershell
$env:VIRUSTOTAL_API_KEY = "your_virustotal_api_key"
$env:URLSCAN_API_KEY = "your_urlscan_api_key"
$env:ABUSEIPDB_API_KEY = "your_abuseipdb_api_key"
```

### Get Free API Keys:
- **VirusTotal**: https://www.virustotal.com/gui/join-us
- **URLScan.io**: https://urlscan.io/about-api/
- **AbuseIPDB**: https://www.abuseipdb.com/register

## 📊 Usage

```powershell
cd Mail
python main.py
```

### Options CLI:

```powershell
# Mode interactif (par défaut)
python main.py

# Scan avec IA et APIs
python main.py --folder Inbox --use-ai --use-apis --report

# Mode non-interactif
python main.py --no-interactive --folder Inbox --report

# Dry-run (test sans modification)
python main.py --dry-run --threshold 60 --verbose

# Désactiver l'IA (utiliser seulement les règles)
python main.py --no-ai --folder Inbox

# Scan récursif avec IA
python main.py --recursive --use-ai --report
```

## 🛡️ Threat Detection

### Local Analysis:
- Dangerous file extensions (.exe, .bat, .scr, etc.)
- Double extensions (file.pdf.exe)
- Phishing keywords and urgency markers
- Spoofed sender domains
- Suspicious URLs (IP addresses, URL shorteners)
- HTML content analysis (hidden text, JavaScript, forms)
- Link text vs href mismatches
- Generic greetings and financial terms

### AI-Powered Detection:
- **Transformer Model**: DistilBERT-based phishing classification
- **Semantic Analysis**: Urgency, emotional manipulation, authority impersonation
- **Fallback Model**: TF-IDF + Random Forest for offline detection
- **Context Understanding**: Analyzes email content meaning, not just patterns

### External API Checks (if configured):
- **VirusTotal**: URL and file hash reputation (70+ engines)
- **URLScan.io**: Website behavior analysis from existing scans
- **AbuseIPDB**: IP address reputation and abuse reports

### Email Authentication:
- SPF validation
- DKIM signature verification
- DMARC policy checks

## 📈 Threat Scoring

Each email receives a threat score based on detected indicators:
- **Score < 50**: Safe
- **Score ≥ 50**: Dangerous (flagged for action)

**Score contributions:**
- Dangerous attachment: +50
- AI phishing detection (high confidence): +50
- VirusTotal malicious URL: up to +60
- Spoofed sender: +40
- SPF/DKIM failure: +30
- JavaScript in email: +40
- And many more...

## 📄 Output

- **Console**: Real-time scan progress and summary
- **mail_cleaner.log**: Detailed logs with timestamps
- **email_scan_report_*.json**: Comprehensive analysis reports (optional)

## 🧠 AI Models

### Primary Model (Online)
- **Model**: DistilBERT (distilbert-base-uncased)
- **Type**: Transformer-based text classification
- **Speed**: ~100-200ms per email on CPU
- **Accuracy**: High semantic understanding

### Fallback Model (Offline)
- **Model**: Random Forest + TF-IDF
- **Type**: Traditional machine learning
- **Speed**: ~10ms per email
- **Accuracy**: Good pattern matching

The tool automatically uses the best available model and falls back gracefully if AI libraries are not installed.

## ⚠️ Safety Notes

- The tool NEVER opens or visits suspicious URLs
- Files are NEVER executed, only hashed for lookup
- All external API checks are passive (query-only)
- AI models run locally on your machine (no data sent externally)
- Temporary files are immediately deleted after hash calculation
- Rate limiting prevents API quota exhaustion

## 🧪 Example Report Structure

```json
{
  "scan_date": "2025-10-15T14:30:00",
  "statistics": {
    "total": 150,
    "dangerous": 12,
    "moved": 12,
    "deleted": 0,
    "errors": 0
  },
  "dangerous_emails": [
    {
      "subject": "Urgent: Verify your account now!",
      "sender": "noreply@suspicious-domain.com",
      "received": "2025-10-15 10:23:45",
      "threat_score": 85,
      "threats": [
        "suspicious keywords: 3",
        "spoofed sender: paypal / noreply@suspicious-domain.com",
        "ai phishing: 0.92 confidence (transformer)",
        "vt url: 15/70 malicious",
        "urgency: 5"
      ]
    }
  ],
  "api_usage": {
    "virustotal": 8,
    "urlscan": 3,
    "abuseipdb": 2
  }
}
```

## 🤝 Contributing

Feel free to submit issues or pull requests for improvements.

## 📝 License

Educational use only. Use responsibly.
