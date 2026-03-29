---
name: whatsapp-watcher
description: |
  WhatsApp Web monitoring watcher. Uses Playwright to monitor WhatsApp Web for new messages,
  identifies urgent messages based on keywords, and creates action files in /Needs_Action.
  Use when you need to monitor WhatsApp for client messages, urgent requests, or business inquiries.
---

# WhatsApp Watcher Skill

Monitor WhatsApp Web and create action files for urgent messages.

## Prerequisites

### Playwright Installation

```bash
npm install -g @playwright/mcp
playwright install chromium
```

### WhatsApp Web Session

- Keep WhatsApp Web session authenticated
- Store session data in persistent context
- Handle QR code re-authentication

## Watcher Implementation

```python
# whatsapp_watcher.py
from playwright.sync_api import sync_playwright
from base_watcher import BaseWatcher
from pathlib import Path
from datetime import datetime
import time

class WhatsAppWatcher(BaseWatcher):
    def __init__(self, vault_path: str, session_path: str, check_interval: int = 60):
        super().__init__(vault_path, check_interval)
        self.session_path = Path(session_path)
        self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'emergency', 'price', 'order']
        self.browser = None
        self.page = None
    
    def _init_browser(self):
        """Initialize browser with persistent session"""
        if self.browser is None:
            playwright = sync_playwright().start()
            self.browser = playwright.chromium.launch_persistent_context(
                self.session_path,
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            self.page = self.browser.pages[0]
    
    def check_for_updates(self) -> list:
        """Check for new urgent WhatsApp messages"""
        self._init_browser()
        
        try:
            # Navigate to WhatsApp Web
            self.page.goto('https://web.whatsapp.com', wait_until='networkidle')
            
            # Wait for chat list
            self.page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
            
            # Find unread messages
            unread_chats = self.page.query_selector_all(
                '[aria-label*="unread"], [data-testid="unread-mark"]'
            )
            
            urgent_messages = []
            
            for chat in unread_chats:
                # Extract chat info
                chat_text = chat.inner_text()
                chat_name = chat.query_selector('[data-testid="chat-cell-title"]')
                name = chat_name.inner_text() if chat_name else 'Unknown'
                
                # Check for urgent keywords
                if any(keyword in chat_text.lower() for keyword in self.keywords):
                    # Get last message
                    last_msg = chat.query_selector('[data-testid="chat-cell-subtitle"]')
                    message_text = last_msg.inner_text() if last_msg else ''
                    
                    urgent_messages.append({
                        'from': name,
                        'text': message_text,
                        'full_text': chat_text,
                        'timestamp': datetime.now(),
                        'chat_element': chat
                    })
            
            return urgent_messages
            
        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {e}")
            return []
    
    def create_action_file(self, message: dict) -> Path:
        """Create action file for WhatsApp message"""
        from_name = message['from'].replace(' ', '_').replace('@', '')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        content = f"""---
type: whatsapp_message
from: {message['from']}
received: {message['timestamp'].isoformat()}
priority: urgent
status: pending
---

# WhatsApp Message Received

## From
{message['from']}

## Message
{message['text']}

## Full Context
{message['full_text']}

## Detected Keywords
{', '.join([k for k in ['urgent', 'asap', 'invoice', 'payment', 'help', 'emergency', 'price', 'order'] if k in message['full_text'].lower()])}

## Suggested Actions
- [ ] Read and understand the message
- [ ] Draft a reply
- [ ] Move to /Pending_Approval for review
- [ ] Mark as read in WhatsApp after processing

## Reply Draft
*Draft your reply here*

---
*Created by WhatsAppWatcher v0.1*
"""
        
        filepath = self.needs_action / f'WHATSAPP_{from_name}_{timestamp}.md'
        filepath.write_text(content, encoding='utf-8')
        return filepath
    
    def close(self):
        """Close browser"""
        if self.browser:
            self.browser.close()
            self.browser = None
```

## Action File Format

```markdown
---
type: whatsapp_message
from: John Client
received: 2026-03-02T15:30:00
priority: urgent
status: pending
---

# WhatsApp Message Received

## From
John Client

## Message
Hi, I need the invoice urgently!

## Detected Keywords
urgent, invoice

## Suggested Actions
- [ ] Read and understand the message
- [ ] Draft a reply
- [ ] Move to /Pending_Approval for review
```

## Processing Workflow

### 1. Watcher Monitors

```
WhatsApp Web → Check unread messages → Keyword match → Create action file
```

### 2. Keywords Detected

| Keyword | Priority | Auto-Action |
|---------|----------|-------------|
| urgent, asap | High | Create action file |
| invoice, payment | High | Create action + notify |
| help, emergency | Critical | Immediate notification |
| price, order | Medium | Create action file |

### 3. Qwen Code Processes

```bash
qwen "Process all WhatsApp files in ./Needs_Action. Draft professional replies."
```

## Usage Example

### Start WhatsApp Watcher

```bash
python whatsapp_watcher.py --vault "../AI_Employee_Vault" --session "./whatsapp_session"
```

### First Time Setup

1. Run the watcher
2. Scan QR code with WhatsApp mobile app
3. Session saved for future use

### Process Messages

```bash
cd AI_Employee_Vault
qwen "Process all WhatsApp messages. Draft polite, professional replies."
```

## Reply Templates

### For Invoice Requests

```
Hi [Name],

Thank you for reaching out. I'll prepare and send the invoice right away.

Best regards
```

### For Price Inquiries

```
Hi [Name],

Thanks for your interest! Let me get you the pricing information.

Best regards
```

### For Urgent Requests

```
Hi [Name],

I received your urgent message. I'm on it and will get back to you shortly.

Best regards
```

## Integration with Approval Workflow

Always use approval before sending:

```markdown
---
type: approval_request
action: send_whatsapp
to: John Client
message: |
  Hi John, I'll send the invoice right away.
created: 2026-03-02T15:35:00Z
---

## Reply to Send

**To:** John Client
**Message:** Hi John, I'll send the invoice right away.

## To Approve
Move to /Approved folder.

## To Reject
Move to /Rejected folder.
```

## Tips

1. **Persistent session** - Keep session data to avoid re-scanning QR
2. **Headless mode** - Run in background
3. **Rate limiting** - Check every 60 seconds, not more
4. **Keyword customization** - Adjust for your business
5. **Error recovery** - Reconnect if WhatsApp Web disconnects

## Troubleshooting

| Issue | Solution |
|-------|----------|
| QR code every time | Check session_path is writable |
| No messages detected | Verify WhatsApp Web is loaded |
| Session expired | Re-scan QR code |
| Browser crashes | Restart with fresh session |

## Security Notes

- Keep session file secure
- Never share session data
- Log out when not in use
- Monitor for unusual activity

---

*WhatsApp Watcher Skill v0.1*
*For Silver Tier AI Employee*
