# 🎯 COMPLETE BRONZE TIER GUIDE

## What's New: Automatic Qwen Code Processing!

The Bronze Tier is now **COMPLETE** with automatic Qwen Code processing. When you drop a file, the system:

1. ✅ Detects the file (File System Watcher)
2. ✅ Creates action file (in `Needs_Action/`)
3. ✅ **Auto-invokes Qwen Code** (Qwen Processor)
4. ✅ Qwen reads, plans, and executes
5. ✅ Moves completed task to `Done/`

---

## 🚀 Quick Start - Complete System

### Option 1: One-Click Start (Recommended)

```bash
cd watchers
start-all.bat
```

This starts:
- File System Watcher
- Qwen Code Auto-Processor

### Option 2: Orchestrator with Auto-Qwen

```bash
cd watchers
python orchestrator.py --vault "../AI_Employee_Vault" --auto-qwen
```

### Option 3: Separate Processes

**Terminal 1 - Watcher:**
```bash
cd watchers
python filesystem_watcher.py --vault "../AI_Employee_Vault"
```

**Terminal 2 - Qwen Processor:**
```bash
cd watchers
python qwen_processor.py --vault "../AI_Employee_Vault" --interval 60
```

---

## 📋 Complete Workflow Example

### Step 1: Start the System

```bash
cd watchers
python orchestrator.py --vault "../AI_Employee_Vault" --auto-qwen
```

**Expected output:**
```
00:00:00 - Orchestrator - INFO - Starting orchestrator main loop
00:00:00 - Orchestrator - INFO - Registered watcher: filesystem_watcher
00:00:00 - Orchestrator - INFO - Registered watcher: qwen_processor
00:00:00 - Orchestrator - INFO - Started watcher 'filesystem_watcher' with PID 12345
00:00:00 - Orchestrator - INFO - Qwen Code auto-processor enabled
```

### Step 2: Drop a File

Copy a file to:
```
AI_Employee_Vault/Inbox/Drop/test_document.txt
```

**Content of test file:**
```
Please summarize this document and tell me the key points.
```

### Step 3: Watch the Magic

**Terminal output:**
```
00:00:30 - FileSystemWatcher - INFO - Found new file: test_document.txt
00:00:30 - FileSystemWatcher - INFO - Created action file: FILE_DROP_test_document_20260301_120000.md
00:00:30 - Orchestrator - INFO - Found 1 action files, triggering Qwen Code
00:00:30 - Orchestrator - INFO - Invoking Qwen Code processor...
00:00:31 - QwenCodeProcessor - INFO - Found 1 action files, invoking Qwen Code
00:00:31 - QwenCodeProcessor - INFO - Created Qwen prompt file with 1 action files
```

### Step 4: Qwen Code Processes

Qwen Code will:
1. Read the action file
2. Read the dropped file
3. Create a Plan.md
4. Execute the plan (summarize document)
5. Update Dashboard.md
6. Move file to `Done/`

**Qwen output:**
```
I found 1 action file in ./Needs_Action

### FILE_DROP_test_document_20260301_120000.md
- Type: file_drop
- Original: test_document.txt

## Plan
1. [ ] Read the document content
2. [ ] Identify key points
3. [ ] Create summary
4. [ ] Update Dashboard.md
5. [ ] Move to Done/

Executing...

### Summary
The document contains...

<promise>TASK_COMPLETE</promise>
```

### Step 5: Verify Completion

**Check Done folder:**
```bash
dir AI_Employee_Vault\Done
```

**Expected:**
```
FILE_DROP_test_document_20260301_120000.md
```

**Check logs:**
```bash
type AI_Employee_Vault\Logs\qwen_processor_*.log
```

---

## 📁 File Structure

```
AI_Employee_Vault/
├── Inbox/
│   └── Drop/           ← Drop files here
├── Needs_Action/       ← Action files created here
├── In_Progress/        ← Files being processed
├── Done/               ← Completed tasks
├── Pending_Approval/   ← Awaiting your decision
├── Approved/           ← Approved actions
├── Plans/              ← Qwen's plans
├── Logs/               ← System logs
├── Dashboard.md        ← Real-time status
├── Company_Handbook.md ← Rules
└── Business_Goals.md   ← Objectives

watchers/
├── base_watcher.py         ← Base class
├── filesystem_watcher.py   ← File monitor
├── qwen_processor.py       ← Qwen auto-invoker
├── orchestrator.py         ← Master process
├── start-all.bat           ← One-click start
└── requirements.txt        ← Dependencies
```

---

## 🔧 Command Reference

### Start Commands

| Command | Purpose |
|---------|---------|
| `start-all.bat` | Start everything (Windows) |
| `python orchestrator.py --vault "../AI_Employee_Vault" --auto-qwen` | Orchestrator + auto Qwen |
| `python filesystem_watcher.py --vault "../AI_Employee_Vault"` | Just the watcher |
| `python qwen_processor.py --vault "../AI_Employee_Vault"` | Just Qwen processor |

### Qwen Code Commands

| Command | Purpose |
|---------|---------|
| `qwen "Process files in ./Needs_Action"` | Manual processing |
| `qwen "Process files... <promise>TASK_COMPLETE</promise>"` | With completion signal |

### Options

| Option | Description |
|--------|-------------|
| `--vault PATH` | Path to Obsidian vault |
| `--interval SECONDS` | Check interval (default: 30/60) |
| `--auto-qwen` | Enable auto Qwen invocation |
| `--verbose, -v` | Debug logging |
| `--once` | Process once and exit |

---

## ✅ Bronze Tier Checklist

- [x] Obsidian vault with Dashboard.md
- [x] Company_Handbook.md with rules
- [x] Business_Goals.md template
- [x] File System Watcher (working)
- [x] Qwen Processor (auto-invokes Qwen)
- [x] Orchestrator (coordinates everything)
- [x] Basic folder structure
- [x] Automatic Qwen Code integration
- [x] Ralph Wiggum loop pattern
- [x] Complete documentation

---

## 🆘 Troubleshooting

### "Qwen Code not found"

```bash
# Check installation
qwen --version

# Install if needed
npm install -g @anthropic/qwen-code
```

### "No action files processed"

1. Check watcher is running (look for log output)
2. Verify file was dropped in `Inbox/Drop/` (not just `Inbox/`)
3. Check logs: `Logs/qwen_processor_*.log`
4. Try manual processing: `qwen "Process files in ./Needs_Action"`

### "Qwen exits early"

1. Check `.qwen_prompt.md` for the prompt
2. Re-run with Ralph Wiggum loop:
   ```bash
   qwen "Keep working until all files in Needs_Action are moved to Done"
   ```

### "Files stuck in Needs_Action"

1. Check Qwen output for errors
2. Manually run: `qwen "Process remaining files in ./Needs_Action"`
3. Check file permissions on vault

---

## 📊 What Makes This Complete?

The original Bronze tier was **incomplete** because:
- ❌ Watcher created action files
- ❌ But nothing processed them automatically
- ❌ Required manual Qwen invocation

Now it's **complete** because:
- ✅ Watcher creates action files
- ✅ Orchestrator detects new files
- ✅ **Auto-invokes Qwen Code**
- ✅ Qwen processes files automatically
- ✅ Completed tasks archived in `Done/`

---

## 🎉 Success Indicators

You'll know it's working when:

1. ✅ Drop file → Action file appears within 30 seconds
2. ✅ Qwen Code automatically starts processing
3. ✅ You see Qwen output with plan and execution
4. ✅ File moves to `Done/` folder
5. ✅ Dashboard.md updated with activity
6. ✅ Logs show complete processing chain

---

## 📚 Additional Resources

- `USING_QWEN_CODE.md` - Detailed Qwen Code guide
- `.claude/QWEN.md` - Ralph Wiggum loop plugin
- `.qwen/skills/ai-employee-processor/SKILL.md` - Qwen skill definition
- `README.md` - Main documentation

---

*AI Employee v0.1 (Bronze Tier - COMPLETE)*
*Last Updated: March 1, 2026*
