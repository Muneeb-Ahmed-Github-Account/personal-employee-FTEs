---
name: plan-generator
description: |
  Automatic plan generator for AI Employee tasks. Creates structured Plan.md files with
  clear objectives, steps, and completion criteria. Enables multi-step task execution
  with progress tracking. Use for any complex task requiring multiple actions.
---

# Plan Generator Skill

Create structured plans for multi-step AI Employee tasks.

## Overview

The Plan Generator creates detailed `Plan.md` files that break down complex tasks into executable steps with clear completion criteria.

## Plan Format

```markdown
---
type: plan
task: Process invoice request
created: 2026-03-02T10:30:00Z
status: in_progress
priority: high
estimated_steps: 5
completed_steps: 0
---

# Plan: Process Invoice Request

## Objective
Generate and send invoice to client who requested via WhatsApp.

## Context
- Client: John Client
- Requested via: WhatsApp
- Amount: $1,500
- Service: Consulting (January 2026)

## Steps

| # | Step | Status | Notes |
|---|------|--------|-------|
| 1 | Read client request | ✅ Done | Understood requirement |
| 2 | Generate invoice PDF | ⬜ Pending | Use invoice template |
| 3 | Save to /Invoices/ | ⬜ Pending | Filename: invoice_123.pdf |
| 4 | Draft email to client | ⬜ Pending | Attach invoice |
| 5 | Create approval request | ⬜ Pending | For email send |
| 6 | Send after approval | ⬜ Pending | Wait for human |
| 7 | Log transaction | ⬜ Pending | Update accounting |
| 8 | Move to /Done | ⬜ Pending | Archive task |

## Dependencies
- Step 4 requires Step 2 complete
- Step 6 requires Step 5 approved

## Completion Criteria
- [ ] Invoice generated and saved
- [ ] Email sent to client
- [ ] Transaction logged
- [ ] All files archived in /Done

## Risks & Blockers
- None currently

---
*Last Updated: 2026-03-02T10:30:00Z*
```

## Plan Generation Workflow

### Step 1: Read Action File

```python
def read_action_file(filepath: Path) -> dict:
    """Parse action file YAML frontmatter"""
    content = filepath.read_text(encoding='utf-8')
    
    # Extract YAML frontmatter
    yaml_match = re.search(r'---\n(.+?)\n---', content, re.DOTALL)
    if yaml_match:
        metadata = yaml.safe_load(yaml_match.group(1))
        body = content.split('---', 2)[2]
        return {
            'metadata': metadata,
            'body': body,
            'filepath': filepath
        }
    return None
```

### Step 2: Analyze Task

```python
def analyze_task(action_file: dict) -> dict:
    """Analyze task and determine required steps"""
    task_type = action_file['metadata'].get('type', 'unknown')
    
    # Step templates by task type
    TEMPLATES = {
        'file_drop': [
            'Read file content',
            'Understand request',
            'Determine required action',
            'Execute action',
            'Update Dashboard',
            'Archive to /Done'
        ],
        'email': [
            'Read email content',
            'Understand sender request',
            'Draft reply',
            'Create approval request',
            'Send after approval',
            'Mark email as read',
            'Archive to /Done'
        ],
        'whatsapp_message': [
            'Read message content',
            'Identify urgency/keywords',
            'Draft response',
            'Create approval request',
            'Send after approval',
            'Mark as read',
            'Archive to /Done'
        ]
    }
    
    return {
        'type': task_type,
        'steps': TEMPLATES.get(task_type, ['Analyze task', 'Execute', 'Archive']),
        'priority': action_file['metadata'].get('priority', 'normal')
    }
```

### Step 3: Create Plan

```python
def create_plan(action_file: dict, analysis: dict) -> Path:
    """Create Plan.md file"""
    timestamp = datetime.now().isoformat()
    
    steps_table = '\n'.join([
        f"| {i+1} | {step} | ⬜ Pending | |"
        for i, step in enumerate(analysis['steps'])
    ])
    
    plan_content = f"""---
type: plan
task: {action_file['metadata'].get('type', 'Unknown Task')}
created: {timestamp}
status: pending
priority: {analysis['priority']}
estimated_steps: {len(analysis['steps'])}
completed_steps: 0
---

# Plan: {action_file['metadata'].get('subject', 'Process Action File')}

## Objective
{generate_objective(action_file)}

## Context
{generate_context(action_file)}

## Steps

| # | Step | Status | Notes |
|---|------|--------|-------|
{steps_table}

## Completion Criteria
{generate_completion_criteria(analysis['steps'])}

## Risks & Blockers
- None currently

---
*Created: {timestamp}*
"""
    
    # Save plan
    plan_name = f"PLAN_{action_file['filepath'].stem}.md"
    plan_path = vault / 'Plans' / plan_name
    plan_path.write_text(plan_content, encoding='utf-8')
    
    return plan_path
```

## Usage with Qwen Code

### Generate Plan

```bash
qwen "Read the action file in ./Needs_Action and create a detailed Plan.md with all required steps."
```

### Execute Plan

```bash
qwen "Execute the plan in ./Plans/PLAN_*.md. Update step status as you complete each one."
```

### Update Progress

```bash
qwen "Update the plan progress. Mark completed steps as done and note any blockers."
```

## Plan Templates by Task Type

### File Processing Plan

```markdown
---
type: plan
task: file_processing
created: 2026-03-02T10:00:00Z
status: pending
---

# Plan: Process Dropped File

## Objective
Process the file dropped into Inbox/Drop/ and take appropriate action.

## Steps

| # | Step | Status | Notes |
|---|------|--------|-------|
| 1 | Read file content | ⬜ Pending | |
| 2 | Identify file type | ⬜ Pending | PDF, TXT, DOCX, etc. |
| 3 | Extract key information | ⬜ Pending | |
| 4 | Determine required action | ⬜ Pending | |
| 5 | Execute action | ⬜ Pending | |
| 6 | Update Dashboard | ⬜ Pending | |
| 7 | Archive to /Done | ⬜ Pending | |

## Completion Criteria
- [ ] File processed
- [ ] Action taken
- [ ] Dashboard updated
- [ ] Archived in /Done
```

### Email Response Plan

```markdown
---
type: plan
task: email_response
created: 2026-03-02T10:00:00Z
status: pending
---

# Plan: Respond to Email

## Objective
Draft and send a professional response to the client email.

## Steps

| # | Step | Status | Notes |
|---|------|--------|-------|
| 1 | Read email carefully | ⬜ Pending | |
| 2 | Identify key questions | ⬜ Pending | |
| 3 | Gather needed information | ⬜ Pending | |
| 4 | Draft response | ⬜ Pending | Professional tone |
| 5 | Review for accuracy | ⬜ Pending | |
| 6 | Create approval request | ⬜ Pending | |
| 7 | Send after approval | ⬜ Pending | |
| 8 | Mark email as read | ⬜ Pending | |
| 9 | Archive to /Done | ⬜ Pending | |

## Completion Criteria
- [ ] Response drafted
- [ ] Approved by human
- [ ] Email sent
- [ ] Archived in /Done
```

### Social Media Plan

```markdown
---
type: plan
task: social_media_post
created: 2026-03-02T10:00:00Z
status: pending
---

# Plan: Create and Post LinkedIn Content

## Objective
Create engaging LinkedIn post about business update.

## Steps

| # | Step | Status | Notes |
|---|------|--------|-------|
| 1 | Understand topic | ⬜ Pending | |
| 2 | Research best practices | ⬜ Pending | |
| 3 | Draft post content | ⬜ Pending | Include hashtags |
| 4 | Select/create image | ⬜ Pending | |
| 5 | Review content | ⬜ Pending | Check tone |
| 6 | Create approval request | ⬜ Pending | |
| 7 | Schedule post | ⬜ Pending | Optimal time |
| 8 | Post after approval | ⬜ Pending | |
| 9 | Monitor engagement | ⬜ Pending | First 24 hours |

## Completion Criteria
- [ ] Content created
- [ ] Approved by human
- [ ] Posted to LinkedIn
- [ ] Engagement monitored
```

## Progress Tracking

### Update Step Status

```python
def update_step_status(plan_path: Path, step_number: int, status: str, notes: str = ''):
    """Update status of a specific step"""
    content = plan_path.read_text(encoding='utf-8')
    
    # Status icons
    icons = {
        'pending': '⬜',
        'in_progress': '🔄',
        'done': '✅',
        'blocked': '🚫'
    }
    
    # Update the specific row
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if f"| {step_number} |" in line:
            parts = line.split('|')
            parts[3] = f" {icons.get(status, '⬜')} {status} "
            if notes:
                parts[4] = f" {notes} "
            lines[i] = '|'.join(parts)
            break
    
    # Update completed count
    completed = content.count('✅ Done')
    content = re.sub(r'completed_steps: \d+', f'completed_steps: {completed}', content)
    
    plan_path.write_text(content, encoding='utf-8')
```

### Generate Progress Summary

```markdown
## Progress Summary

- **Total Steps:** 8
- **Completed:** 3 (37%)
- **In Progress:** 1
- **Pending:** 4
- **Blocked:** 0

**Current Step:** Draft response
**Estimated Completion:** 30 minutes
```

## Integration with Ralph Wiggum Loop

The Plan Generator works with the Ralph Wiggum persistence pattern:

1. **Create Plan** → Plan.md with steps
2. **Execute Steps** → Update status as you go
3. **Check Completion** → All steps done?
4. **If Not Done** → Continue working
5. **If Done** → Output `<promise>TASK_COMPLETE</promise>`

```bash
qwen "Execute all steps in the plan. Keep working until all steps are complete. Output <promise>TASK_COMPLETE</promise> when done."
```

## Best Practices

1. **Clear objectives** - One sentence describing goal
2. **Atomic steps** - Each step should be independently executable
3. **Dependencies noted** - Mark steps that depend on others
4. **Completion criteria** - Clear definition of "done"
5. **Progress tracking** - Update status as you work
6. **Blockers visible** - Note anything preventing progress

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Plan too vague | Break steps into smaller actions |
| Steps out of order | Add dependency notes |
| Progress not tracked | Update status after each step |
| Plan never completes | Add time estimates, set deadlines |

---

*Plan Generator Skill v0.1*
*For Silver Tier AI Employee*
