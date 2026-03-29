---
name: gmail-watcher
description: |
  Gmail monitoring watcher. Reads emails from Gmail API, identifies important/unread messages,
  and creates action files in /Needs_Action for processing. Use when you need to monitor
  Gmail for new emails, especially from clients or with urgent keywords.
---

# Gmail Watcher Skill

Monitor Gmail and create action files for important emails.

## Prerequisites

### Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json`
6. Run authentication to get `token.json`

### Environment Variables

```bash
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REDIRECT_URI=http://localhost:8080
```

## Watcher Implementation

```python
# gmail_watcher.py
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from base_watcher import BaseWatcher
from datetime import datetime
import os

class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: str, credentials_path: str, check_interval: int = 120):
        super().__init__(vault_path, check_interval)
        self.credentials_path = credentials_path
        self.service = self._authenticate()
        self.keywords = ['urgent', 'invoice', 'payment', 'asap', 'important']
    
    def _authenticate(self):
        """Authenticate with Gmail API"""
        creds = Credentials.from_authorized_user_file(self.credentials_path)
        return build('gmail', 'v1', credentials=creds)
    
    def check_for_updates(self) -> list:
        """Check for new unread important emails"""
        results = self.service.users().messages().list(
            userId='me',
            q='is:unread -category:promotions -category:social',
            maxResults=10
        ).execute()
        
        messages = results.get('messages', [])
        new_emails = []
        
        for msg in messages:
            if msg['id'] not in self.processed_ids:
                email_data = self._fetch_email(msg['id'])
                if self._is_important(email_data):
                    new_emails.append(email_data)
                    self.processed_ids.add(msg['id'])
        
        return new_emails
    
    def _fetch_email(self, message_id: str) -> dict:
        """Fetch full email data"""
        message = self.service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        headers = {h['name']: h['value'] for h in message['payload']['headers']}
        
        # Get email body
        body = self._get_body(message['payload'])
        
        return {
            'id': message_id,
            'from': headers.get('From', 'Unknown'),
            'to': headers.get('To', ''),
            'subject': headers.get('Subject', 'No Subject'),
            'date': headers.get('Date', ''),
            'body': body,
            'snippet': message.get('snippet', '')
        }
    
    def _get_body(self, payload) -> str:
        """Extract email body"""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    import base64
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        elif 'body' in payload:
            import base64
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        return ''
    
    def _is_important(self, email: dict) -> bool:
        """Check if email is important based on keywords"""
        text = f"{email['subject']} {email['snippet']}".lower()
        return any(keyword in text for keyword in self.keywords)
    
    def create_action_file(self, email: dict) -> Path:
        """Create action file for email"""
        from_id = email['from'].replace('@', '_at_').replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        content = f"""---
type: email
from: {email['from']}
to: {email['to']}
subject: {email['subject']}
received: {datetime.now().isoformat()}
email_id: {email['id']}
priority: high
status: pending
---

# Email Received

## From
{email['from']}

## Subject
{email['subject']}

## Date
{email['date']}

## Content
{email['body']}

## Suggested Actions
- [ ] Read and understand the email
- [ ] Draft a reply
- [ ] Move to /Pending_Approval for review (if sending reply)
- [ ] Mark as read in Gmail after processing

## Reply Draft
*Draft your reply here*

---
*Created by GmailWatcher v0.1*
"""
        
        filepath = self.needs_action / f'EMAIL_{from_id}_{timestamp}.md'
        filepath.write_text(content, encoding='utf-8')
        return filepath
```

## Action File Format

```markdown
---
type: email
from: client@example.com
subject: Urgent: Invoice Needed
received: 2026-03-02T10:30:00
email_id: abc123
priority: high
status: pending
---

# Email Received

## From
client@example.com

## Subject
Urgent: Invoice Needed

## Content
Hi, can you send me the invoice for last month?

## Suggested Actions
- [ ] Read and understand the email
- [ ] Draft a reply
- [ ] Move to /Pending_Approval for review
```

## Processing Workflow

### 1. Watcher Detects Email

```
Gmail API → New unread email → Check keywords → Create action file
```

### 2. Qwen Code Processes

```bash
qwen "Process all files in ./Needs_Action"
```

### 3. Qwen Actions

1. Read email content
2. Understand the request
3. Draft a reply
4. Create approval request (if sending)
5. Mark email as read when done

## Integration with Approval Workflow

For email replies, always use approval workflow:

```markdown
---
type: approval_request
action: send_email
to: client@example.com
subject: Re: Invoice Request
created: 2026-03-02T10:35:00Z
---

## Email to Send

To: client@example.com
Subject: Re: Invoice Request

Hi,

I'll send the invoice shortly.

Best regards

## To Approve
Move to /Approved folder.

## To Reject
Move to /Rejected folder.
```

## Usage Example

### Start Gmail Watcher

```bash
python gmail_watcher.py --vault "../AI_Employee_Vault" --credentials "credentials.json"
```

### Process Emails with Qwen

```bash
cd AI_Employee_Vault
qwen "Process all email files in ./Needs_Action. Draft replies and create approval requests."
```

## Tips

1. **Filter promotions/social** - Don't waste time on newsletters
2. **Keyword matching** - Customize keywords for your needs
3. **Rate limiting** - Check every 2 minutes, not more frequently
4. **Token refresh** - Handle OAuth token expiration
5. **Error handling** - Continue on transient API errors

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication failed | Re-run OAuth flow, check credentials.json |
| No emails detected | Check Gmail query, verify labels |
| API quota exceeded | Reduce check frequency |
| Token expired | Refresh OAuth token |

---

*Gmail Watcher Skill v0.1*
*For Silver Tier AI Employee*
