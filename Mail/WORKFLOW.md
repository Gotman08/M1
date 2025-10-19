# Email Processing Workflow

## Progressive Security System

This tool implements a **progressive security model** with two scanning stages:

### Stage 1: Inbox Scan
- **Source**: Inbox folder
- **Action**: Dangerous emails → Moved to **Junk folder**
- **Purpose**: First-level filtering of suspicious emails

### Stage 2: Junk Scan  
- **Source**: Junk folder
- **Action**: Dangerous emails → Moved to **Deleted Items (Bin)**
- **Purpose**: Second-level verification of already flagged emails

## Why This Approach?

### 1. Double Verification
Emails must be flagged as dangerous **twice** before going to Bin:
- Once in Inbox (moves to Junk)
- Again in Junk (moves to Bin)

This reduces false positives impacting important emails.

### 2. User Review Opportunity
Users can review emails in Junk folder before final deletion.

### 3. Cache System
The tool remembers analyzed emails (stored in `analyzed_emails.json`):
- **Skip re-analysis**: Already analyzed emails are skipped
- **Independent tracking**: Separate from Outlook's read/unread status
- **Performance**: Faster subsequent scans

## Workflow Example

```
Initial State:
  Inbox: [Email A, Email B, Email C]
  Junk:  [Email X, Email Y]
  Bin:   []

After "Scan Inbox + Junk" (Option 2):
  
  Step 1 - Inbox Analysis:
    - Email A: Safe (score: 20) → Stays in Inbox
    - Email B: Dangerous (score: 85) → Moved to Junk
    - Email C: Safe (score: 15) → Stays in Inbox
  
  Step 2 - Junk Analysis:
    - Email X: Dangerous (score: 120) → Moved to Bin
    - Email Y: Safe (score: 30) → Stays in Junk
    - Email B: Just moved, not analyzed yet (cached skip)

Final State:
  Inbox: [Email A, Email C]
  Junk:  [Email B, Email Y]
  Bin:   [Email X]
```

## Cache Behavior

### First Scan
All emails are analyzed and results cached:
```json
{
  "entry_id_123": {
    "analyzed_at": "2025-10-15T10:30:00",
    "subject": "Amazon Order Confirmation",
    "threat_score": 65,
    "action": "moved_to_junk"
  }
}
```

### Second Scan (same emails)
Cached emails are skipped:
```
Total: 50 emails
Cached (skipped): 45 emails
New analyzed: 5 emails
```

### Cache Management

**View cache stats** (Option 6):
```
Total analyzed: 150
Dangerous: 23
Safe: 127
Moved to Junk: 18
Moved to Bin: 5
```

**Clear cache** (Option 7):
- Resets all tracked emails
- Next scan will re-analyze everything
- Use when you want fresh analysis

**Auto-cleanup**:
Cache entries older than 30 days are automatically removed.

## Command Line Usage

### Scan with progressive logic
```powershell
# Interactive mode (recommended)
python main.py
# Select option 2: "scan inbox + junk"

# Non-interactive mode
python main.py --no-interactive --folder Inbox --report
python main.py --no-interactive --folder "Junk E-mail" --report
```

### Disable cache (re-analyze all)
```powershell
python main.py --no-cache
```

### Clear cache before scan
```powershell
python main.py --clear-cache
```

## SafeLinks Protection

The tool automatically excludes Outlook's own protection system:
- `*.safelinks.protection.outlook.com` domains are trusted
- No false positives from Microsoft's URL rewriting
- Legitimate emails with SafeLinks are not flagged

## Trusted Domains

These domains are excluded from suspicious checks:
- `safelinks.protection.outlook.com` (all regions)
- `aka.ms` (Microsoft short links)
- `google.com`, `microsoft.com`, `apple.com`
- `github.com`, `stackoverflow.com`

You can add more in `config.py` → `TRUSTED_DOMAINS` list.
