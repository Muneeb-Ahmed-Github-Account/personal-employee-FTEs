---
name: ai-employee-processor
description: |
  AI Employee action file processor. Reads action files from /Needs_Action,
  creates plans, executes tasks, and moves completed files to /Done.
  Use when processing files created by the File System Watcher or other watchers.
---

# AI Employee Processor Skill

This skill enables Qwen Code to process action files in the AI Employee vault.

## Core Workflow

### 1. Read Action Files

```bash
# List all action files
ls Needs_Action/*.md

# Read each action file
cat Needs_Action/FILE_DROP_*.md
```

### 2. Parse YAML Frontmatter

Each action file has metadata:

```yaml
---
type: file_drop
original_name: document.pdf
size: 1048576
status: pending
priority: normal
---
```

### 3. Create Plan.md

For each action file, create a plan:

```markdown
# Plan for FILE_DROP_document_20260301.md

## Objective
Process the dropped file: document.pdf

## Steps
- [ ] Read the file content
- [ ] Determine required action
- [ ] Execute the action
- [ ] Update Dashboard.md
- [ ] Move to Done/
```

### 4. Execute Actions

Based on the action type:

| Type | Action |
|------|--------|
| `file_drop` | Read file, summarize, categorize |
| `email` | Draft reply, flag for approval |
| `approval_request` | Wait for human decision |
| `task` | Execute task steps |

### 5. Move to Done

After completion:

```bash
mv Needs_Action/FILE_DROP_*.md Done/
```

## File Operations

### Read Action File
```bash
cat Needs_Action/*.md
```

### Read Dropped File
```bash
# For text files
cat Inbox/filename.txt

# For PDFs (if tools available)
pdftotext Inbox/filename.pdf -

# For images (describe)
# Use vision capabilities if available
```

### Update Dashboard
```bash
# Read current dashboard
cat Dashboard.md

# Update with new activity (append to Recent Activity section)
```

### Move Files
```bash
# Completed task
mv Needs_Action/file.md Done/

# Needs approval
mv Needs_Action/file.md Pending_Approval/

# Approved by human
mv Approved/file.md Needs_Action/  # Then process
```

## Completion Signal

When ALL action files are processed:

```
<promise>TASK_COMPLETE</promise>
```

## Error Handling

### If File Not Found
```markdown
**Error:** File not found: Inbox/filename.pdf

**Action:** Check if file exists, log error, move to Done with error note.
```

### If Action Unclear
```markdown
**Error:** Unable to determine required action

**Action:** Create approval request with suggestions, move to Pending_Approval.
```

### If Tool Unavailable
```markdown
**Error:** Required tool not available: PDF reader

**Action:** Note limitation, suggest manual review, move to Done with note.
```

## Example Session

```
I found 1 action file in ./Needs_Action

### FILE_DROP_invoice_20260301.md
- Type: file_drop
- Original: invoice_january.pdf
- Size: 256 KB

## Plan
1. [ ] Read invoice PDF
2. [ ] Extract: amount, date, vendor
3. [ ] Log to Accounting/
4. [ ] Update Dashboard.md
5. [ ] Move to Done/

Executing step 1...
```

## Quick Commands

| Task | Command |
|------|---------|
| List pending | `ls Needs_Action/` |
| Read action file | `cat Needs_Action/*.md` |
| Read dropped file | `cat Inbox/filename` |
| Create plan | `echo "# Plan..." > Needs_Action/Plan.md` |
| Complete task | `mv Needs_Action/file.md Done/` |
| Request approval | `mv file.md Pending_Approval/` |

## Integration Points

### With Watchers
- Watchers create action files in `Needs_Action/`
- This skill processes them
- Moves completed to `Done/`

### With Orchestrator
- Orchestrator monitors `Needs_Action/`
- Triggers this skill when files appear
- Logs processing status

### With Dashboard
- Update `Dashboard.md` after each action
- Track completion counts
- Log any errors

---

*AI Employee Processor Skill v0.1*
*For use with Qwen Code*
