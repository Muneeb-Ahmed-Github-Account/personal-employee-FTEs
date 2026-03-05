# AI Employee - Bronze Tier Implementation

> *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

This repository contains a **Bronze Tier** implementation of the Personal AI Employee (Digital FTE) system. It provides the foundational layer for an autonomous agent that proactively manages personal and business affairs using **Qwen Code** and **Obsidian**.

## 🏆 Bronze Tier Deliverables

✅ **Completed:**
- [x] Obsidian vault with `Dashboard.md` and `Company_Handbook.md`
- [x] File System Watcher script (monitors drop folder for new files)
- [x] Qwen Code integration (reads/writes to vault)
- [x] Basic folder structure: `/Inbox`, `/Needs_Action`, `/Done`, `/Pending_Approval`, `/Approved`
- [x] Base watcher abstract class for future extensions

## 📁 Project Structure

```
personal-employee-FTEs/
├── AI_Employee_Vault/          # Obsidian vault
│   ├── Inbox/                  # Raw incoming items
│   │   └── Drop/              # File drop folder (watched)
│   ├── Needs_Action/          # Items requiring attention
│   ├── In_Progress/           # Items being processed
│   ├── Done/                  # Completed tasks archive
│   ├── Pending_Approval/      # Awaiting human decision
│   ├── Approved/              # Approved actions
│   ├── Rejected/              # Rejected actions
│   ├── Plans/                 # Claude's task plans
│   ├── Briefings/             # CEO briefings
│   ├── Logs/                  # System logs
│   ├── Dashboard.md           # Main dashboard
│   ├── Company_Handbook.md    # Rules of engagement
│   └── Business_Goals.md      # Q1 2026 objectives
├── watchers/                   # Python watcher scripts
│   ├── base_watcher.py        # Abstract base class
│   ├── filesystem_watcher.py  # File system monitor
│   ├── orchestrator.py        # Master process
│   └── requirements.txt       # Python dependencies
├── Personal AI Employee Hackathon 0_...md  # Main blueprint
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| [Python](https://www.python.org/downloads/) | 3.13+ | Watcher scripts |
| [Obsidian](https://obsidian.md/download) | v1.10.6+ | Knowledge base |
| [Qwen Code](https://github.com/QwenLM/qwen-code) | Installed | Reasoning engine |

### Installation

1. **Clone the repository:**
   ```bash
   cd personal-employee-FTEs
   ```

2. **Install Python dependencies:**
   ```bash
   cd watchers
   pip install -r requirements.txt
   ```

3. **Open the vault in Obsidian:**
   - Launch Obsidian
   - Click "Open folder as vault"
   - Select `AI_Employee_Vault` folder

### Running the Complete System (Recommended)

**Option 1: Using the start script (Windows):**
```bash
cd watchers
start-all.bat
```

**Option 2: Using orchestrator with auto-qwen:**
```bash
cd watchers
python orchestrator.py --vault "../AI_Employee_Vault" --auto-qwen
```

**Option 3: Manual - Start watcher and Qwen processor separately:**
```bash
# Terminal 1: Start watcher
python filesystem_watcher.py --vault "../AI_Employee_Vault"

# Terminal 2: Start Qwen processor (continuous)
python qwen_processor.py --vault "../AI_Employee_Vault" --interval 60
```

### Running Just the File Watcher

The File System Watcher monitors a drop folder for new files and creates action files in Obsidian.

**Start the watcher:**
```bash
cd watchers
python filesystem_watcher.py --vault "../AI_Employee_Vault" --interval 30
```

**Options:**
- `--vault PATH`: Path to Obsidian vault (required)
- `--drop-folder PATH`: Custom drop folder (default: vault/Inbox/Drop)
- `--interval SECONDS`: Check interval (default: 30)
- `--verbose, -v`: Enable debug logging

**Example with custom drop folder:**
```bash
python filesystem_watcher.py --vault "../AI_Employee_Vault" --drop-folder "C:/Users/YourName/Drop" --interval 60
```

### Running the Orchestrator

The orchestrator manages watchers and triggers Claude Code processing.

```bash
cd watchers
python orchestrator.py --vault "../AI_Employee_Vault"
```

### Testing the Complete System

**1. Start the complete system:**
```bash
cd watchers
python orchestrator.py --vault "../AI_Employee_Vault" --auto-qwen
```

**2. Drop a file** into the monitored folder:
```
AI_Employee_Vault/Inbox/Drop/test_document.txt
```

**3. Watch the magic happen:**
- Watcher detects the file (within 30 seconds)
- Action file created in `Needs_Action/`
- Qwen Code automatically invoked
- Qwen reads the action file and creates a plan
- Qwen executes the plan
- File moved to `Done/` when complete

**4. Check the results:**
```bash
# Check action files were processed
dir AI_Employee_Vault\Done

# Check logs
type AI_Employee_Vault\Logs\qwen_processor_*.log
```

**5. Open Obsidian** to see:
- Dashboard updated with activity
- Completed task in `Done/` folder
- Any plans created in `Plans/` folder

## 📖 How It Works

### Watcher Architecture

```
┌─────────────────┐
│  Drop Folder    │
│  (Inbox/Drop)   │
└────────┬────────┘
         │ File added
         ▼
┌─────────────────┐
│ FileSystemWatcher│
│  (Python script)│
└────────┬────────┘
         │ Creates action file
         ▼
┌─────────────────┐
│ Needs_Action/   │
│ (*.md files)    │
└────────┬────────┘
         │ Orchestrator detects
         ▼
┌─────────────────┐
│ Qwen Processor  │
│ (Auto-invokes   │
│  Qwen Code)     │
└────────┬────────┘
         │ Qwen Code processes
         ▼
┌─────────────────┐
│ Plan.md +       │
│ Actions taken   │
└────────┬────────┘
         │ Complete
         ▼
┌─────────────────┐
│ Done/           │
│ (Archived)      │
└─────────────────┘
```

### Action File Format

When a file is dropped, the watcher creates a markdown file with YAML frontmatter:

```markdown
---
type: file_drop
original_name: document.pdf
size: 1048576
size_human: 1.00 MB
received: 2026-02-27T10:30:00
status: pending
priority: normal
---

# File Drop for Processing

## File Information
- **Original Name**: document.pdf
- **Size**: 1.00 MB
- **Received**: 2026-02-27 10:30:00

## Suggested Actions
- [ ] Review file contents
- [ ] Determine required action
- [ ] Process and move to /Done
```

### Qwen Code Integration

The system now **automatically invokes Qwen Code** when action files are detected.

**Automatic Processing (with --auto-qwen flag):**
```bash
cd watchers
python orchestrator.py --vault "../AI_Employee_Vault" --auto-qwen
```

**Manual Processing (if not using auto mode):**
```bash
cd AI_Employee_Vault
qwen "Process all files in ./Needs_Action folder. Create Plan.md for each task and execute."
```

**Ralph Wiggum Loop** (for autonomous multi-step tasks):
```bash
qwen "Process all files in ./Needs_Action, move to ./Done when complete. Keep working until done. When finished, output: <promise>TASK_COMPLETE</promise>"
```

### Qwen Processor Script

The `qwen_processor.py` script:
- Monitors `Needs_Action/` for action files
- Automatically invokes Qwen Code when files detected
- Uses Ralph Wiggum loop pattern for multi-step tasks
- Logs all activity to `Logs/qwen_processor_*.log`

**Run standalone:**
```bash
python qwen_processor.py --vault "../AI_Employee_Vault" --interval 60
```

## 🎯 Usage Workflow

### 1. File Drop Workflow (Automatic Processing)

1. Drop any file into `AI_Employee_Vault/Inbox/Drop/`
2. Watcher detects the file within 30 seconds
3. Action file created in `Needs_Action/`
4. **Orchestrator auto-invokes Qwen Code**
5. Qwen reads, plans, and executes
6. Completed task moved to `Done/`

### 2. File Drop Workflow (Manual Processing)

1. Drop any file into `AI_Employee_Vault/Inbox/Drop/`
2. Watcher detects the file within 30 seconds
3. Action file created in `Needs_Action/`
4. **You run:** `qwen "Process files in ./Needs_Action"`
5. Qwen reads, plans, and executes
6. Completed task moved to `Done/`

### 2. Approval Workflow

For sensitive actions, Qwen creates an approval request:

```markdown
---
type: approval_request
action: file_operation
created: 2026-02-27T10:30:00Z
status: pending
---

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

**Human reviews and moves file** → Qwen executes approved action.

### 3. Dashboard Updates

The `Dashboard.md` provides real-time visibility:
- Pending actions count
- System status (watchers running/stopped)
- Recent completions
- Financial overview (when integrated)

## 📋 Configuration

### Watcher Configuration

Edit `filesystem_watcher.py` to customize:

```python
# Check interval (seconds)
check_interval = 30

# Drop folder location
self.drop_folder = self.inbox / 'Drop'

# File types to ignore
ignored_extensions = ['.tmp', '.swp']
```

### Company Handbook Rules

Update `Company_Handbook.md` to set your rules:
- Payment thresholds
- Communication guidelines
- Task prioritization
- Approval requirements

## 🔧 Troubleshooting

### Watcher not detecting files

1. Check the watcher is running: Look for log output
2. Verify drop folder path: `AI_Employee_Vault/Inbox/Drop/`
3. Check file permissions on the vault folder
4. Try reducing interval: `--interval 10`

### Action files not creating

1. Check `Needs_Action/` folder exists
2. Verify write permissions
3. Check logs in `AI_Employee_Vault/Logs/`

### Qwen Code not processing

1. Ensure Qwen Code is installed: `qwen --version`
2. Navigate to vault folder before running
3. Check for `.md` files in `Needs_Action/`
4. Check the `.qwen_prompt.md` file for the pending prompt

## 📈 Next Steps (Silver Tier)

To advance to **Silver Tier**, add:

1. **Gmail Watcher** - Monitor Gmail for important emails
2. **WhatsApp Watcher** - Monitor WhatsApp for urgent messages
3. **MCP Server** - Send emails via Gmail API
4. **Approval Workflow** - Human-in-the-loop for sensitive actions
5. **Scheduled Tasks** - Cron/Task Scheduler integration

## 🛡️ Security Notes

- **Never commit** `.env` files with credentials
- Keep vault backed up (use Git or cloud sync)
- Review all automated actions regularly
- Start with dry-run mode for new watchers

## 📚 Resources

- **Main Blueprint:** `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Obsidian Help:** https://help.obsidian.md
- **Qwen Code:** https://github.com/QwenLM/qwen-code
- **Wednesday Meetings:** Zoom ID 871 8870 7642, Wednesdays 10:00 PM PKT

## 🏅 Achievement Status

**Bronze Tier: COMPLETE ✅**

| Requirement | Status |
|-------------|--------|
| Obsidian vault with Dashboard.md | ✅ |
| Company_Handbook.md | ✅ |
| One working Watcher (File System) | ✅ |
| Claude Code reading/writing to vault | ✅ |
| Basic folder structure | ✅ |

---

*AI Employee v0.1 (Bronze Tier)*
*Built for Personal AI Employee Hackathon 0*
