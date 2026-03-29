"""
Gmail Watcher - Monitors Gmail for Important Emails

Automatically:
1. Checks Gmail every 2 minutes (120 seconds)
2. Filters unread, important emails (excludes promotions/social)
3. Detects keywords: urgent, asap, invoice, payment, etc.
4. Creates action files in Needs_Action/ folder
5. Master Orchestrator auto-moves to Pending_Approval

Uses existing credentials.json for OAuth 2.0 authentication.
"""

import sys
import time
import base64
import json
import shutil
from pathlib import Path
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Gmail API Scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

# Keywords to identify important emails
IMPORTANT_KEYWORDS = [
    'urgent', 'asap', 'invoice', 'payment', 'important',
    'client', 'customer', 'order', 'purchase', 'buy',
    'help', 'question', 'reply', 'response', 'meeting',
    'deadline', 'today', 'tomorrow', 'immediately'
]

# Priority keywords
CRITICAL_KEYWORDS = ['urgent', 'asap', 'emergency', 'immediately', 'critical']
HIGH_KEYWORDS = ['invoice', 'payment', 'deadline', 'today', 'tomorrow']


class GmailWatcher:
    def __init__(self, vault_path: str, credentials_path: str, check_interval: int = 120):
        self.vault_path = Path(vault_path)
        self.credentials_path = Path(credentials_path)
        self.check_interval = check_interval
        
        # Folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logs = self.vault_path / 'Logs'
        self.token_path = self.vault_path / '.gmail_token.json'
        
        # Ensure folders exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)
        
        # Track processed email IDs to avoid duplicates
        self.processed_ids = set()
        self.state_file = self.vault_path / '.state_gmailwatcher.json'
        self._load_state()
        
        # Gmail service
        self.service = None
        
        print("="*70)
        print("Gmail Watcher - Monitors Gmail for Important Emails")
        print("="*70)
        print(f"Credentials: {self.credentials_path}")
        print(f"Check interval: {check_interval} seconds")
        print(f"Action files: {self.needs_action}")
        print("Press Ctrl+C to stop")
        print("="*70)
    
    def _load_state(self):
        """Load processed email IDs from state file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.processed_ids = set(state.get('processed_ids', []))
                    # Keep only last 1000 IDs to prevent unbounded growth
                    self.processed_ids = set(list(self.processed_ids)[-1000:])
                    print(f"Loaded {len(self.processed_ids)} processed email IDs from state")
            except Exception as e:
                print(f"Warning: Could not load state file: {e}")
    
    def _save_state(self):
        """Save processed email IDs to state file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({'processed_ids': list(self.processed_ids)}, f)
        except Exception as e:
            print(f"Warning: Could not save state file: {e}")
    
    def authenticate(self):
        """Authenticate with Gmail API using OAuth 2.0"""
        creds = None
        
        # Load existing token if available
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
                print("Loaded existing Gmail token")
            except Exception as e:
                print(f"Warning: Could not load token: {e}")
        
        # Refresh token if expired
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("Refreshed Gmail token")
            except Exception as e:
                print(f"Warning: Token refresh failed: {e}")
                creds = None
        
        # Run OAuth flow if no valid credentials
        if not creds or not creds.valid:
            try:
                print("\n" + "="*70)
                print("GMAIL AUTHENTICATION REQUIRED")
                print("="*70)
                print("Opening browser for Gmail authentication...")
                print("Please log in and grant permissions.")
                print("This is a ONE-TIME setup.")
                print("="*70)
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=8080, open_browser=True)
                
                # Save token for future use
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
                print(f"\nGmail token saved to: {self.token_path}")
                print("Next time, no authentication needed!")
                
            except Exception as e:
                print(f"ERROR: OAuth authentication failed: {e}")
                return False
        
        # Build Gmail service
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            print("Gmail API connected successfully!")
            return True
        except Exception as e:
            print(f"ERROR: Could not build Gmail service: {e}")
            return False
    
    def check_for_emails(self):
        """Check for new important emails"""
        if not self.service:
            print("Gmail service not connected")
            return []
        
        try:
            # Search for unread emails (exclude promotions and social)
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread -category:promotions -category:social',
                maxResults=20
            ).execute()
            
            messages = results.get('messages', [])
            new_emails = []
            
            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    email_data = self._fetch_email(msg['id'])
                    
                    # Check if email is important
                    if self._is_important(email_data):
                        new_emails.append(email_data)
                        self.processed_ids.add(msg['id'])
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Found important email: {email_data['subject']}")
            
            # Save state
            self._save_state()
            
            return new_emails
            
        except HttpError as error:
            print(f"Gmail API error: {error}")
            return []
        except Exception as e:
            print(f"Error checking Gmail: {e}")
            return []
    
    def _fetch_email(self, message_id: str):
        """Fetch full email data"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
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
                'snippet': message.get('snippet', ''),
                'thread_id': message.get('threadId', '')
            }
            
        except Exception as e:
            print(f"Error fetching email {message_id}: {e}")
            return {
                'id': message_id,
                'from': 'Unknown',
                'subject': 'Error fetching email',
                'body': str(e),
                'snippet': '',
                'date': '',
                'to': '',
                'thread_id': ''
            }
    
    def _get_body(self, payload):
        """Extract email body from payload"""
        try:
            if 'parts' in payload:
                # Multipart message
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                        return self._decode_body(part['body']['data'])
                    elif part['mimeType'] == 'text/html' and 'data' in part['body']:
                        return self._decode_body(part['body']['data'])
            
            # Simple message
            if 'body' in payload and 'data' in payload['body']:
                return self._decode_body(payload['body']['data'])
            
            return ''
            
        except Exception as e:
            print(f"Error extracting body: {e}")
            return ''
    
    def _decode_body(self, data: str):
        """Decode base64url encoded body"""
        try:
            # Add padding if needed
            padding = 4 - len(data) % 4
            if padding != 4:
                data += '=' * padding
            return base64.urlsafe_b64decode(data).decode('utf-8')
        except Exception as e:
            return f'[Error decoding body: {e}]'
    
    def _is_important(self, email):
        """Check if email is important based on keywords and sender"""
        # Check subject and snippet for keywords
        text = f"{email['subject']} {email['snippet']}".lower()
        
        # Check for critical/high priority keywords
        for keyword in CRITICAL_KEYWORDS:
            if keyword in text:
                email['priority'] = 'critical'
                return True
        
        for keyword in HIGH_KEYWORDS:
            if keyword in text:
                email['priority'] = 'high'
                return True
        
        # Check for other important keywords
        for keyword in IMPORTANT_KEYWORDS:
            if keyword in text:
                email['priority'] = 'normal'
                return True
        
        # Check if from important domains (customize as needed)
        from_email = email['from'].lower()
        important_domains = ['client', 'company', 'business', 'support']
        for domain in important_domains:
            if domain in from_email:
                email['priority'] = 'normal'
                return True
        
        email['priority'] = 'low'
        return False
    
    def create_action_file(self, email):
        """Create a markdown action file for the email"""
        try:
            # Create safe filename from email ID
            safe_id = email['id'][:16]
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Extract sender name and make it Windows-safe
            from_name = email['from']
            # Remove ALL invalid Windows filename characters: < > : " / \ | ? *
            for char in '<>:"/\\|?*':
                from_name = from_name.replace(char, '_')
            # Replace @ and spaces
            from_name = from_name.replace('@', '_at_').replace(' ', '_').replace('.', '_')
            # Limit length
            if len(from_name) > 30:
                from_name = from_name[:30]
            
            action_filename = f'EMAIL_{from_name}_{timestamp}.md'
            action_filepath = self.needs_action / action_filename
            
            priority = email.get('priority', 'normal')
            
            content = f"""---
type: email
from: {email['from']}
to: {email['to']}
subject: {email['subject']}
received: {datetime.now().isoformat()}
email_id: {email['id']}
thread_id: {email['thread_id']}
priority: {priority}
status: pending
---

# Email Received

## From
{email['from']}

## To
{email['to']}

## Subject
{email['subject']}

## Date
{email['date']}

## Content

{email['body']}

---

## Suggested Actions

- [ ] Read and understand the email
- [ ] Determine required response
- [ ] Draft a reply
- [ ] Create approval request (move to /Pending_Approval)
- [ ] Send after approval
- [ ] Mark as read in Gmail
- [ ] Archive to /Done

## Reply Draft

*Draft your reply here*

---
*Created by GmailWatcher v0.1*
*Priority: {priority}*
"""
            
            action_filepath.write_text(content, encoding='utf-8')
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Created action file: {action_filename}")
            
            return action_filepath
            
        except Exception as e:
            print(f"Failed to create action file: {e}")
            return None
    
    def mark_as_read(self, email_id):
        """Mark an email as read in Gmail"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            print(f"Marked email {email_id} as read")
            return True
        except Exception as e:
            print(f"Error marking email as read: {e}")
            return False
    
    def run(self):
        """Main run loop"""
        # Authenticate first
        if not self.authenticate():
            print("Authentication failed. Exiting.")
            return
        
        print("\n" + "="*70)
        print("Gmail Watcher is now monitoring your Gmail...")
        print(f"Checking every {self.check_interval} seconds")
        print("="*70)
        
        try:
            while True:
                # Check for new emails
                emails = self.check_for_emails()
                
                # Create action files for each email
                for email in emails:
                    self.create_action_file(email)
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\nStopped by user")
            self._save_state()
        except Exception as e:
            print(f"Fatal error: {e}")
            self._save_state()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Gmail Watcher')
    parser.add_argument('--vault', type=str, required=True, help='Path to Obsidian vault')
    parser.add_argument('--credentials', type=str, default='credentials.json', help='Path to Gmail credentials.json')
    parser.add_argument('--interval', type=int, default=120, help='Check interval in seconds')
    args = parser.parse_args()
    
    watcher = GmailWatcher(
        vault_path=args.vault,
        credentials_path=args.credentials,
        check_interval=args.interval
    )
    watcher.run()


if __name__ == '__main__':
    main()
