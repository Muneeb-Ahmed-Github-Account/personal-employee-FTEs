# Qwen Code Plugin - Ralph Wiggum Loop

**Purpose:** Keep Qwen Code working autonomously until all action files are processed.

---

## Installation

Copy this file to your AI Employee vault:
```
AI_Employee_Vault/.claude/QWEN.md
```

---

## Usage

### Start a Ralph Wiggum Loop

```bash
cd AI_Employee_Vault
qwen "Process all files in ./Needs_Action, move to ./Done when complete. Keep working until all files are processed."
```

### With Completion Promise

```bash
qwen "Process all files in ./Needs_Action. When complete, output: <promise>TASK_COMPLETE</promise>"
```

---

## How It Works

1. **Orchestrator detects** action files in `Needs_Action/`
2. **Creates prompt** in `.qwen_prompt.md`
3. **Qwen Code processes** each file:
   - Reads action file
   - Creates `Plan.md`
   - Executes steps
   - Moves to `Done/`
4. **Completion check:**
   - If files remain in `Needs_Action/` → Continue working
   - If all files in `Done/` → Output `<promise>TASK_COMPLETE</promise>`

---

## Completion Strategies

### Strategy 1: Promise-Based (Simple)

Qwen outputs when done:
```
<promise>TASK_COMPLETE</promise>
```

### Strategy 2: File Movement (Advanced)

Stop hook detects when task file moves to `/Done`:
- More reliable
- Completion is natural part of workflow
- Orchestrator creates state file programmatically

---

## State File Format

The orchestrator creates `.qwen_prompt.md`:

```markdown
---
created: 2026-03-01T12:00:00Z
action_count: 3
status: pending
---

# AI Employee Task - Process Action Files

**Files to Process:** 3

## Instructions

Process all files in /Needs_Action folder.

### For Each File:
1. READ the action file
2. CREATE Plan.md with steps
3. EXECUTE each step
4. MOVE to /Done when complete

### Completion Signal:
When ALL files processed, output:
<promise>TASK_COMPLETE</promise>
```

---

## Error Recovery

### If Qwen Exits Early

1. Check `Needs_Action/` for remaining files
2. Re-run: `qwen "Continue processing remaining files"`
3. Check logs in `Logs/` for errors

### If File Stuck In Progress

1. Move file back to `Needs_Action/`
2. Re-run Qwen Code
3. Check `Plan.md` for what went wrong

---

## Integration with Orchestrator

The orchestrator (`orchestrator.py`) automatically:
1. Monitors `Needs_Action/` folder
2. Creates `.qwen_prompt.md` when files detected
3. Invokes `qwen_processor.py` to run Qwen Code
4. Logs all activity to `Logs/`

### Run with Auto-Qwen

```bash
python orchestrator.py --vault "../AI_Employee_Vault" --auto-qwen
```

This starts:
- File System Watcher (monitors drop folder)
- Qwen Processor (auto-invokes Qwen when files detected)

---

## Example Session

```
$ qwen "Process all files in ./Needs_Action"

I found 2 action files in ./Needs_Action:
1. FILE_DROP_invoice_20260301.md
2. FILE_DROP_notes_20260301.md

### Processing FILE_DROP_invoice_20260301.md

**Plan:**
1. [ ] Read invoice PDF
2. [ ] Extract amount, date, vendor
3. [ ] Log to Accounting/
4. [ ] Update Dashboard.md
5. [ ] Move to Done/

Executing step 1...
Executing step 2...
...
✓ Completed: FILE_DROP_invoice_20260301.md

### Processing FILE_DROP_notes_20260301.md

...
✓ Completed: FILE_DROP_notes_20260301.md

<promise>TASK_COMPLETE</promise>
```

---

## Tips

1. **Run in background** - Use `&` or terminal multiplexer
2. **Check logs** - `Logs/qwen_processor_*.log` has details
3. **Monitor dashboard** - `Dashboard.md` shows progress
4. **Set timeouts** - Long tasks may need `--timeout` flag

---

*AI Employee v0.1 (Bronze Tier)*
*Ralph Wiggum Loop Plugin for Qwen Code*
