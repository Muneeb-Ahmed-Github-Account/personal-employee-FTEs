"""
Email MCP Server - Sends Emails via Gmail API

Silver Tier Requirement: "One working MCP server for external action (e.g., sending emails)"

Automatically:
1. Monitors Approved/ folder for email approval requests
2. Sends emails via Gmail API
3. Marks emails as read in Gmail
4. Moves files to Done/

Uses existing credentials.json for OAuth 2.0 authentication.
"""

import sys
import time
import base64
import json
import re
import shutil
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Gmail API Scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]


class EmailMCPServer:
    def __init__(self, vault_path: str, credentials_path: str, check_interval: int = 30):
        self.vault_path = Path(vault_path)
        self.credentials_path = Path(credentials_path)
        self.check_interval = check_interval
        
        # Folders
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        self.token_path = self.vault_path / '.gmail_token.json'
        
        # Ensure folders exist
        for folder in [self.approved, self.done, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Track processed files
        self.processed_files = set()
        
        # Gmail service
        self.service = None
        
        print("="*70)
        print("Email MCP Server - Sends Emails via Gmail API")
        print("="*70)
        print(f"Credentials: {self.credentials_path}")
        print(f"Monitoring: {self.approved}")
        print(f"Check interval: {check_interval} seconds")
        print("Silver Tier Requirement: One working MCP server")
        print("Press Ctrl+C to stop")
        print("="*70)
    
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
                print("GMAIL MCP SERVER AUTHENTICATION")
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
                
            except Exception as e:
                print(f"ERROR: OAuth authentication failed: {e}")
                return False
        
        # Build Gmail service
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            print("Gmail MCP Server connected successfully!")
            return True
        except Exception as e:
            print(f"ERROR: Could not build Gmail service: {e}")
            return False
    
    def get_approved_emails(self):
        """Get approved email actions from Approved/ folder"""
        approved_emails = []
        
        for file in self.approved.glob('*.md'):
            # Skip if already processed
            if file.name in self.processed_files:
                continue
            
            try:
                content = file.read_text(encoding='utf-8')
                
                # Check if this is an email action (Gmail Watcher format)
                is_email_action = (
                    'type: email' in content and
                    '## Reply Draft' in content
                ) or (
                    'type: approval_request' in content and
                    ('action: send_email' in content or 'action: email_reply' in content)
                ) or (
                    'type: email' in content and
                    'Suggested Actions' in content and
                    'Send after approval' in content
                )
                
                if is_email_action:
                    approved_emails.append({'file': file, 'content': content})
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Found approved email: {file.name}")
                    
            except Exception as e:
                print(f"Error reading {file.name}: {e}")
        
        return approved_emails
    
    def extract_email_details(self, content: str):
        """Extract email details from approval file"""
        details = {
            'to': '',
            'subject': '',
            'body': '',
            'attachments': []
        }
        
        # Extract 'from' email (for reply, this becomes 'to')
        from_match = re.search(r'from:\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
        if from_match:
            # Extract email address from "Name <email@domain.com>"
            email_match = re.search(r'<([^>]+)>', from_match.group(1))
            if email_match:
                details['to'] = email_match.group(1)
            else:
                details['to'] = from_match.group(1).strip()
        
        # Extract subject
        subject_match = re.search(r'subject:\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
        if subject_match:
            details['subject'] = subject_match.group(1).strip()
        
        # Extract body from Reply Draft section
        if '**Reply Draft:**' in content:
            # Get everything after **Reply Draft:**
            parts = content.split('**Reply Draft:**')
            if len(parts) > 1:
                body_section = parts[1]
                # Split by lines to handle the format properly
                lines = body_section.split('\n')
                message_lines = []
                in_message = False
                
                for line in lines:
                    line_stripped = line.strip()
                    
                    # Skip the first --- separator
                    if not in_message and line_stripped == '---':
                        in_message = True
                        continue
                    
                    # If we haven't hit the separator yet, skip empty lines
                    if not in_message and not line_stripped:
                        continue
                    
                    # Start collecting message after separator or non-empty line
                    if not in_message:
                        in_message = True
                    
                    # Stop at next section markers
                    if line_stripped.startswith('## To Approve') or line_stripped.startswith('## Original'):
                        break
                    
                    # Skip trailing ---
                    if line_stripped == '---' and message_lines:
                        break
                    
                    # Add non-empty lines or preserve spacing in message
                    message_lines.append(line)
                
                # Clean up: remove leading/trailing empty lines
                while message_lines and not message_lines[0].strip():
                    message_lines.pop(0)
                while message_lines and not message_lines[-1].strip():
                    message_lines.pop()
                
                details['body'] = '\n'.join(message_lines).strip()
        elif '## Reply Draft' in content:
            body_section = content.split('## Reply Draft')[1]
            if '##' in body_section:
                body_section = body_section.split('##')[0]
            details['body'] = body_section.strip()
        
        # Debug output
        if not details['body']:
            print(f"  WARNING: No body extracted. Content preview: {content[:200]}")
        
        return details
    
    def send_email(self, to: str, subject: str, body: str, attachments: list = None):
        """Send email via Gmail API"""
        try:
            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['from'] = 'me'
            message['subject'] = subject
            
            # Attach body
            message.attach(MIMEText(body, 'plain'))
            
            # Attach files if provided
            if attachments:
                for file_path in attachments:
                    try:
                        with open(file_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename={Path(file_path).name}'
                            )
                            message.attach(part)
                    except Exception as e:
                        print(f"Warning: Could not attach {file_path}: {e}")
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send email
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"Email sent successfully! Message ID: {sent_message['id']}")
            return True, sent_message['id']
            
        except HttpError as error:
            print(f"Gmail API error: {error}")
            return False, None
        except Exception as e:
            print(f"Error sending email: {e}")
            return False, None
    
    def mark_email_as_read(self, email_id: str):
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
    
    def process_approved_email(self, email_data):
        """Process a single approved email"""
        file = email_data['file']
        content = email_data['content']
        
        print(f"\nProcessing approved email: {file.name}")
        
        # Extract email details
        details = self.extract_email_details(content)
        
        if not details['to']:
            print("No recipient found, skipping")
            return False
        
        if not details['subject']:
            details['subject'] = 'No Subject'
        
        if not details['body']:
            print("No body found, skipping")
            return False
        
        print(f"To: {details['to']}")
        print(f"Subject: {details['subject']}")
        
        # Send email
        success, message_id = self.send_email(
            to=details['to'],
            subject=details['subject'],
            body=details['body'],
            attachments=details.get('attachments')
        )
        
        if success:
            # Mark original email as read if email_id is in content
            email_id_match = re.search(r'email_id:\s*(\S+)', content)
            if email_id_match:
                self.mark_email_as_read(email_id_match.group(1))
            
            # Move to Done
            done_path = self.done / file.name
            shutil.move(str(file), str(done_path))
            print(f"Moved to Done: {file.name}")
            
            # Log action
            self.log_action(file.name, details['to'], details['subject'], 'success')
            
            return True
        else:
            print("Failed to send email")
            self.log_action(file.name, details['to'], details['subject'], 'failed')
            return False
    
    def log_action(self, filename: str, to: str, subject: str, status: str):
        """Log email action to log file"""
        log_file = self.logs / f'email_mcp_{datetime.now().strftime("%Y%m%d")}.log'
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'file': filename,
            'to': to,
            'subject': subject,
            'status': status
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def run(self):
        """Main run loop"""
        # Authenticate first
        if not self.authenticate():
            print("Authentication failed. Exiting.")
            return
        
        print("\n" + "="*70)
        print("Email MCP Server is now monitoring Approved/ folder...")
        print(f"Checking every {self.check_interval} seconds")
        print("="*70)
        
        try:
            while True:
                # Get approved emails
                approved_emails = self.get_approved_emails()
                
                # Process each approved email
                for email_data in approved_emails:
                    success = self.process_approved_email(email_data)
                    if success:
                        self.processed_files.add(email_data['file'].name)
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\nStopped by user")
        except Exception as e:
            print(f"Fatal error: {e}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Email MCP Server')
    parser.add_argument('--vault', type=str, required=True, help='Path to Obsidian vault')
    parser.add_argument('--credentials', type=str, default='credentials.json', help='Path to Gmail credentials.json')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds')
    args = parser.parse_args()
    
    server = EmailMCPServer(
        vault_path=args.vault,
        credentials_path=args.credentials,
        check_interval=args.interval
    )
    server.run()


if __name__ == '__main__':
    main()
