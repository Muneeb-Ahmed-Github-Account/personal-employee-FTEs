---
name: email-mcp-server
description: |
  Email MCP Server for sending emails via Gmail API. Provides tools for composing, drafting,
  and sending emails. Use when the AI Employee needs to send email replies, invoices, or
  business communications. Always requires human approval before sending.
---

# Email MCP Server Skill

Send emails via Gmail API with human-in-the-loop approval.

## Prerequisites

### Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Gmail API
3. Create OAuth 2.0 credentials
4. Download credentials

### MCP Server Installation

```bash
npm install -g @modelcontextprotocol/server-gmail
```

### Configuration

```json
// ~/.config/claude-code/mcp.json
{
  "servers": [
    {
      "name": "email",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-gmail"],
      "env": {
        "GMAIL_CLIENT_ID": "your_client_id",
        "GMAIL_CLIENT_SECRET": "your_client_secret",
        "GMAIL_REDIRECT_URI": "http://localhost:8080"
      }
    }
  ]
}
```

## MCP Tools

### send_email

Send an email to a recipient.

```json
{
  "to": "recipient@example.com",
  "subject": "Email Subject",
  "body": "Email body text",
  "cc": ["cc@example.com"],
  "bcc": ["bcc@example.com"],
  "attachments": ["/path/to/file.pdf"]
}
```

### draft_email

Create a draft email (doesn't send).

```json
{
  "to": "recipient@example.com",
  "subject": "Email Subject",
  "body": "Email body text"
}
```

### list_emails

List recent emails.

```json
{
  "query": "is:unread",
  "maxResults": 10
}
```

### read_email

Read a specific email.

```json
{
  "email_id": "message_id"
}
```

## Usage with Qwen Code

### Step 1: Create Email Draft

```bash
qwen "Draft a reply to the invoice request email. Be professional and friendly."
```

### Step 2: Create Approval Request

```markdown
---
type: approval_request
action: send_email
to: client@example.com
subject: Re: Invoice Request
created: 2026-03-02T10:35:00Z
status: pending
---

## Email to Send

**To:** client@example.com
**Subject:** Re: Invoice Request

**Body:**
Hi,

Thank you for your email. I'm preparing the invoice and will send it shortly.

Best regards

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

### Step 3: Send After Approval

When file is moved to `/Approved/`:

```bash
# MCP call to send email
npx -y @modelcontextprotocol/server-gmail send_email \
  --to "client@example.com" \
  --subject "Re: Invoice Request" \
  --body "Hi, Thank you for your email..."
```

## Python Implementation

```python
# email_mcp.py
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

class EmailMCPServer:
    def __init__(self, credentials_path: str, token_path: str):
        self.creds = Credentials.from_authorized_user_file(token_path)
        self.service = build('gmail', 'v1', credentials=self.creds)
    
    def send_email(self, to: str, subject: str, body: str, 
                   cc: list = None, attachments: list = None) -> dict:
        """Send an email"""
        try:
            message = self._create_message(to, subject, body, cc, attachments)
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            return {
                'success': True,
                'message_id': sent_message['id'],
                'thread_id': sent_message['thread_id']
            }
        except HttpError as error:
            return {
                'success': False,
                'error': str(error)
            }
    
    def _create_message(self, to: str, subject: str, body: str,
                        cc: list = None, attachments: list = None):
        """Create MIME message"""
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = 'me'
        message['subject'] = subject
        
        if cc:
            message['cc'] = ', '.join(cc)
        
        message.attach(MIMEText(body, 'plain'))
        
        if attachments:
            for file_path in attachments:
                self._attach_file(message, file_path)
        
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    
    def _attach_file(self, message: MIMEMultipart, file_path: str):
        """Attach a file to the message"""
        with open(file_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename={os.path.basename(file_path)}'
        )
        message.attach(part)
    
    def draft_email(self, to: str, subject: str, body: str) -> dict:
        """Create a draft email"""
        try:
            message = self._create_message(to, subject, body)
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': message}
            ).execute()
            
            return {
                'success': True,
                'draft_id': draft['id']
            }
        except HttpError as error:
            return {
                'success': False,
                'error': str(error)
            }
    
    def list_emails(self, query: str = '', max_results: int = 10) -> list:
        """List emails matching query"""
        results = self.service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()
        
        return results.get('messages', [])
    
    def read_email(self, email_id: str) -> dict:
        """Read a specific email"""
        message = self.service.users().messages().get(
            userId='me',
            id=email_id,
            format='full'
        ).execute()
        
        headers = {h['name']: h['value'] for h in message['payload']['headers']}
        
        return {
            'id': message['id'],
            'from': headers.get('From', ''),
            'to': headers.get('To', ''),
            'subject': headers.get('Subject', ''),
            'date': headers.get('Date', ''),
            'body': self._get_body(message['payload']),
            'snippet': message.get('snippet', '')
        }
    
    def _get_body(self, payload) -> str:
        """Extract email body"""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        elif 'body' in payload:
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        return ''
    
    def mark_as_read(self, email_id: str) -> bool:
        """Mark email as read"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except HttpError:
            return False
```

## Integration with Approval Workflow

### 1. Qwen Creates Approval Request

```markdown
---
type: approval_request
action: send_email
to: client@example.com
subject: Invoice #123
amount: 1500.00
created: 2026-03-02T10:35:00Z
---

## Email Details

**To:** client@example.com
**Subject:** Invoice #123
**Attachment:** /Vault/Invoices/invoice_123.pdf

**Body:**
Dear Client,

Please find attached invoice #123 for $1,500.

Payment is due within 15 days.

Best regards

## To Approve
Move to /Approved folder.
```

### 2. Human Reviews and Approves

Move file from `Pending_Approval/` to `Approved/`

### 3. Orchestrator Sends Email

```python
# When file appears in Approved/
email_server.send_email(
    to='client@example.com',
    subject='Invoice #123',
    body='Dear Client...',
    attachments=['/Vault/Invoices/invoice_123.pdf']
)
```

### 4. Log and Archive

```python
# Log the action
log_entry = {
    'timestamp': datetime.now().isoformat(),
    'action': 'send_email',
    'to': 'client@example.com',
    'subject': 'Invoice #123',
    'status': 'success',
    'approved_by': 'human'
}

# Move to Done
shutil.move('Approved/email_approval.md', 'Done/')
```

## Email Templates

### Invoice Email

```
Subject: Invoice #{invoice_number}

Dear {client_name},

Please find attached invoice #{invoice_number} for ${amount}.

Payment Details:
- Amount: ${amount}
- Due Date: {due_date}
- Payment Method: {bank_details}

If you have any questions, please don't hesitate to reach out.

Best regards
```

### Reply to Inquiry

```
Subject: Re: {original_subject}

Hi {name},

Thank you for reaching out.

{response_body}

Best regards
```

### Follow-up

```
Subject: Following up on {topic}

Hi {name},

Just following up on my previous email regarding {topic}.

Please let me know if you need any additional information.

Best regards
```

## Security Best Practices

1. **Always require approval** before sending
2. **Log all sent emails** for audit trail
3. **Verify recipient** before sending
4. **Don't send to unknown contacts** without review
5. **Rate limit** - max 10 emails per hour
6. **Dry-run mode** for testing

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication failed | Re-run OAuth flow |
| Email not sent | Check approval file in Approved/ |
| Attachment missing | Verify file path exists |
| Rate limit exceeded | Wait and retry |

---

*Email MCP Server Skill v0.1*
*For Silver Tier AI Employee*
