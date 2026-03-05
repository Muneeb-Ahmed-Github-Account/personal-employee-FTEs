# 🚀 Using Qwen Code with AI Employee

## Quick Start

### Step 1: Start the Watcher

**Option A - Using the batch script (easiest):**
```bash
cd watchers
start-watcher.bat
```

**Option B - Manual:**
```bash
cd watchers
python filesystem_watcher.py --vault "../AI_Employee_Vault"
```

### Step 2: Drop a File

Copy any file to:
```
AI_Employee_Vault/Inbox/Drop/
```

Wait 30 seconds. An action file will be created in `Needs_Action/`.

### Step 3: Process with Qwen Code

```bash
cd AI_Employee_Vault
qwen "Process all files in ./Needs_Action folder"
```

---

## Qwen Code Commands

### Basic Processing
```bash
qwen "Read and process all files in ./Needs_Action"
```

### With Plan Creation
```bash
qwen "For each file in ./Needs_Action: 1) Create a Plan.md with steps, 2) Execute the plan, 3) Move to ./Done when complete"
```

### Ralph Wiggum Loop (Autonomous)
```bash
qwen "Process all files in ./Needs_Action and move them to ./Done when complete. Keep working until all files are processed. When done, output: <promise>TASK_COMPLETE</promise>"
```

---

## How It Works

```
1. You drop a file → Inbox/Drop/
2. Watcher detects it (within 30s)
3. Action file created → Needs_Action/
4. You run Qwen Code
5. Qwen processes and moves to Done/
```

---

## The `.qwen_prompt.md` File

The orchestrator automatically creates `.qwen_prompt.md` in the vault root when action files are detected. This file contains the current processing prompt for Qwen Code.

**Location:** `AI_Employee_Vault/.qwen_prompt.md`

**Contents:**
```markdown
You are the AI Employee. Process all files in the /Needs_Action folder.

For each file:
1. Read and understand the request
2. Create a Plan.md with steps to complete the task
3. Execute the plan using available tools
4. Move completed files to /Done folder
5. If approval is needed, create a file in /Pending_Approval

Begin processing now. When complete, output: <promise>TASK_COMPLETE</promise>
```

---

## Example Session

```bash
# Terminal 1: Start watcher
cd watchers
python filesystem_watcher.py --vault "../AI_Employee_Vault"

# Terminal 2: Drop a file and process
cd AI_Employee_Vault
copy C:\Users\YourName\Documents\invoice.pdf Inbox\Drop\

# Wait 30 seconds, then check
dir Needs_Action

# Process with Qwen
qwen "Process all files in ./Needs_Action"
```

---

## Troubleshooting

### Qwen not found
```bash
# Verify installation
qwen --version

# If not installed, install Qwen Code
npm install -g @anthropic/qwen-code  # or follow Qwen Code installation guide
```

### No action files created
- Check watcher is running (look for log output)
- Verify file was dropped in `Inbox/Drop/` (not just `Inbox/`)
- Check logs in `AI_Employee_Vault/Logs/`

### Qwen not processing
- Check `.qwen_prompt.md` exists in vault root
- Verify action files exist in `Needs_Action/`
- Try running Qwen interactively first: `qwen "Hello"`

---

## Tips

1. **Keep watcher running** - It's lightweight and monitors continuously
2. **Batch process** - Drop multiple files, then run Qwen once
3. **Check logs** - `AI_Employee_Vault/Logs/` has detailed logs
4. **Use Ralph Wiggum Loop** - For complex multi-step tasks

---

*AI Employee v0.1 (Bronze Tier)*
*Updated for Qwen Code*
