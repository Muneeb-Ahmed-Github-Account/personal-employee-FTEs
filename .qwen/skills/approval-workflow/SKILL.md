---
name: approval-workflow
description: |
  Human-in-the-loop approval workflow for sensitive actions. Manages approval requests,
  tracks approvals/rejections, and ensures AI never takes sensitive actions without
  explicit human consent. Use for emails, payments, social posts, and file operations.
---

# Approval Workflow Skill

Human-in-the-loop approval for sensitive AI actions.

## Overview

The approval workflow ensures the AI Employee never takes sensitive actions without explicit human approval.

### Actions Requiring Approval

| Action Type | Always Requires Approval |
|-------------|-------------------------|
| Sending emails | ✅ Yes (all external comms) |
| WhatsApp messages | ✅ Yes (all external comms) |
| LinkedIn posts | ✅ Yes (all public content) |
| Payments | ✅ Yes (all financial) |
| File deletions | ✅ Yes (outside vault) |
| New payees | ✅ Yes (first-time recipients) |
| Contract commitments | ✅ Yes (all legal) |

## Approval File Format

```markdown
---
type: approval_request
action: send_email
to: client@example.com
subject: Invoice #123
created: 2026-03-02T10:30:00Z
expires: 2026-03-03T10:30:00Z
priority: normal
status: pending
---

# Approval Request

## Action Details

**Action Type:** Send Email
**To:** client@example.com
**Subject:** Invoice #123

## Content

```
Dear Client,

Please find attached invoice #123 for $1,500.

Payment is due within 15 days.

Best regards
```

## Attachments
- /Vault/Invoices/invoice_123.pdf

## Context
Client requested invoice via WhatsApp. Invoice generated and ready to send.

## Risk Assessment
- **Financial Impact:** None (sending invoice, not payment)
- **Reputation Risk:** Low (standard business communication)
- **Irreversible:** No (can send follow-up if needed)

---

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder.

## To Request Changes
Add a comment in this file and move back to `/Needs_Action`.

---
*Created: 2026-03-02T10:30:00Z*
*Expires: 2026-03-03T10:30:00Z*
```

## Folder Structure

```
AI_Employee_Vault/
├── Pending_Approval/     ← New approval requests go here
├── Approved/             ← Human moves here to approve
├── Rejected/             ← Human moves here to reject
├── Logs/
│   └── approvals.log     ← Audit trail
```

## Workflow

### Step 1: AI Creates Approval Request

```python
def create_approval_request(action_type: str, details: dict) -> Path:
    """Create approval request file"""
    timestamp = datetime.now().isoformat()
    expires = (datetime.now() + timedelta(days=1)).isoformat()
    
    content = f"""---
type: approval_request
action: {action_type}
created: {timestamp}
expires: {expires}
status: pending
---

# Approval Request

## Action Details
{format_details(details)}

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder.
"""
    
    filepath = pending_approval / f'APPROVAL_{action_type}_{timestamp}.md'
    filepath.write_text(content, encoding='utf-8')
    
    # Notify human
    notify_human(f"Approval required: {action_type}")
    
    return filepath
```

### Step 2: Human Reviews

Human receives notification and reviews:
- Action details
- Content to be sent
- Risk assessment
- Context

### Step 3: Human Decides

| Action | File Movement |
|--------|---------------|
| **Approve** | Move to `Approved/` |
| **Reject** | Move to `Rejected/` |
| **Request Changes** | Add comment, move to `Needs_Action/` |

### Step 4: AI Executes or Logs

```python
def process_approval_files():
    """Process approved and rejected files"""
    
    # Process approved
    for filepath in approved.glob('*.md'):
        action = parse_approval_file(filepath)
        if action['status'] == 'approved':
            execute_action(action)
            log_action(action, 'approved')
            shutil.move(filepath, done / filepath.name)
    
    # Process rejected
    for filepath in rejected.glob('*.md'):
        action = parse_approval_file(filepath)
        log_action(action, 'rejected')
        notify_human(f"Action rejected: {action['type']}")
        shutil.move(filepath, done / filepath.name)
```

## Approval Request Templates

### Email Approval

```markdown
---
type: approval_request
action: send_email
to: client@example.com
subject: Re: Project Inquiry
created: 2026-03-02T14:00:00Z
---

## Email to Send

**To:** client@example.com
**Subject:** Re: Project Inquiry

**Body:**
Hi,

Thank you for your interest in our services.

I'd be happy to discuss your project requirements.

Best regards

## Risk: Low
Standard business communication.
```

### Payment Approval

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Vendor LLC
created: 2026-03-02T14:00:00Z
---

## Payment Details

**Amount:** $500.00
**To:** Vendor LLC
**Bank:** XXXX1234
**Reference:** Invoice #789

## Invoice Attached
/Vault/Invoices/vendor_789.pdf

## Risk: Medium
Financial transaction. First payment to this vendor.
```

### Social Media Approval

```markdown
---
type: approval_request
action: linkedin_post
platform: LinkedIn
created: 2026-03-02T14:00:00Z
scheduled_for: 2026-03-02T18:00:00Z
---

## Post Content

🚀 Exciting announcement!

We've launched our new AI Employee Bronze Tier.

#AI #Automation

## Image
/Vault/Media/announcement.png

## Risk: Low
Public content, can be edited/deleted if needed.
```

## Notification Methods

### Email Notification

```
Subject: Approval Required: Send Email

An action requires your approval.

Action: Send Email
To: client@example.com
Created: 2026-03-02T14:00:00Z

Review in: AI_Employee_Vault/Pending_Approval/
```

### WhatsApp Notification

```
🔔 Approval Required

Action: Send Email
To: client@example.com

Please review in your AI Employee Vault.
```

### Dashboard Alert

```markdown
## ⏳ Awaiting Your Approval

| Action | To/For | Created | Status |
|--------|--------|---------|--------|
| Send Email | client@example.com | 2:00 PM | Pending |
| Payment | Vendor LLC ($500) | 1:30 PM | Pending |
```

## Audit Logging

```python
def log_action(action: dict, decision: str, decided_by: str = 'human'):
    """Log approval decision"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action_type': action['type'],
        'action_details': action,
        'decision': decision,
        'decided_by': decided_by,
        'file_path': str(action.get('filepath'))
    }
    
    # Append to audit log
    log_file = logs / 'approvals.log'
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
```

## Auto-Approval Rules (Optional)

For low-risk, repetitive actions:

```python
AUTO_APPROVE_RULES = {
    'send_email': {
        'to_known_contacts': True,  # Auto-approve if recipient in contacts
        'max_per_hour': 5,  # Rate limit
        'exclude_keywords': ['invoice', 'payment', 'contract']
    },
    'payment': {
        'recurring_same_amount': True,  # Auto-approve recurring bills
        'max_amount': 50,  # Auto-approve under $50
        'known_payees_only': True
    }
}
```

## Expiration Handling

```python
def check_expired_approvals():
    """Handle expired approval requests"""
    now = datetime.now()
    
    for filepath in pending_approval.glob('*.md'):
        content = filepath.read_text()
        expires = extract_expiry(content)
        
        if expires and datetime.fromisoformat(expires) < now:
            # Move to rejected with note
            add_note(filepath, "Expired - no response received")
            shutil.move(filepath, rejected / filepath.name)
            notify_human(f"Approval expired: {filepath.name}")
```

## Best Practices

1. **Clear context** - Explain why action is needed
2. **Risk assessment** - Help human understand implications
3. **Easy to review** - Format content clearly
4. **Expiration** - Set reasonable deadlines
5. **Audit trail** - Log all decisions
6. **Notifications** - Alert human promptly
7. **Easy to reject** - Make rejection as easy as approval

## Security Considerations

1. **Never bypass approval** for sensitive actions
2. **Verify file movement** - Check it was actually moved by human
3. **Log everything** - Complete audit trail
4. **Rate limit** - Don't spam approval requests
5. **Secure notifications** - Don't expose sensitive data

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Approval not processed | Check file was moved to Approved/ |
| Human not notified | Verify notification settings |
| File stuck in Pending | Check if human saw notification |
| Wrong action executed | Review approval file content |

---

*Approval Workflow Skill v0.1*
*For Silver Tier AI Employee*
