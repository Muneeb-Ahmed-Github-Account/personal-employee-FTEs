# Personal AI Employee (Digital FTE) Project

## Project Overview

This repository contains a blueprint and implementation framework for building a **Personal AI Employee** (also called a **Digital FTE** - Full-Time Equivalent). It's a local-first, agent-driven automation system where an AI agent powered by **Claude Code** and **Obsidian** proactively manages personal and business affairs 24/7.

**Tagline:** *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

### Core Architecture

The system follows a **Perception → Reasoning → Action** architecture:

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Perception (Watchers)** | Python Sentinel Scripts | Monitor Gmail, WhatsApp, filesystems, bank transactions |
| **Reasoning (Brain)** | Claude Code | Multi-step reasoning, planning, decision-making |
| **Memory/GUI** | Obsidian (Markdown) | Dashboard, knowledge base, state management |
| **Action (Hands)** | MCP Servers | External system integration (email, browser, payments) |

### Key Concepts

- **Digital FTE:** An AI agent priced and managed like a human employee (works 168 hours/week vs human's 40 hours)
- **Watchers:** Lightweight Python scripts that monitor inputs and create action files in `/Needs_Action`
- **Ralph Wiggum Loop:** A persistence pattern that keeps Claude working until tasks are complete
- **Human-in-the-Loop:** Sensitive actions require approval via file movement (`/Pending_Approval` → `/Approved`)

## Directory Structure

```
personal-employee-FTEs/
├── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md  # Main blueprint document
├── skills-lock.json          # Qwen skill dependencies
├── .qwen/
│   └── skills/
│       └── browsing-with-playwright/  # Browser automation skill
│           ├── SKILL.md              # Skill documentation
│           ├── scripts/
│           │   ├── mcp-client.py     # MCP client for browser control
│           │   ├── start-server.sh   # Start Playwright MCP server
│           │   ├── stop-server.sh    # Stop Playwright MCP server
│           │   └── verify.py         # Server verification script
│           └── references/
│               └── playwright-tools.md
└── .gitattributes
```

## Key Files

| File | Description |
|------|-------------|
| `Personal AI Employee Hackathon 0_...md` | Comprehensive 1200+ line blueprint with architecture, templates, and implementation guides |
| `.qwen/skills/browsing-with-playwright/SKILL.md` | Browser automation via Playwright MCP - navigation, forms, screenshots, data extraction |
| `skills-lock.json` | Tracks installed Qwen skills and their versions |

## Building and Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| [Claude Code](https://claude.com/product/claude-code) | Active subscription | Primary reasoning engine |
| [Obsidian](https://obsidian.md/download) | v1.10.6+ | Knowledge base & dashboard |
| [Python](https://www.python.org/downloads/) | 3.13+ | Watcher scripts & orchestration |
| [Node.js](https://nodejs.org) | v24+ LTS | MCP servers & automation |
| [GitHub Desktop](https://desktop.github.com/download/) | Latest | Version control |

**Hardware:** Minimum 8GB RAM, 4-core CPU, 20GB free disk. Recommended: 16GB RAM, 8-core CPU, SSD.

### Setup Steps

1. **Create Obsidian Vault:**
   ```
   /Vault/
   ├── Inbox/
   ├── Needs_Action/
   ├── In_Progress/
   ├── Done/
   ├── Pending_Approval/
   ├── Approved/
   ├── Rejected/
   ├── Dashboard.md
   └── Company_Handbook.md
   ```

2. **Start Playwright MCP Server:**
   ```bash
   bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh
   ```

3. **Verify Server:**
   ```bash
   python .qwen/skills/browsing-with-playwright/scripts/verify.py
   ```

4. **Stop Server (when done):**
   ```bash
   bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
   ```

### Watcher Pattern

All watchers follow this base structure:

```python
# base_watcher.py
from abc import ABC, abstractmethod
from pathlib import Path
import time

class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        
    @abstractmethod
    def check_for_updates(self) -> list:
        '''Return list of new items to process'''
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        '''Create .md file in Needs_Action folder'''
        pass
    
    def run(self):
        while True:
            items = self.check_for_updates()
            for item in items:
                self.create_action_file(item)
            time.sleep(self.check_interval)
```

### Ralph Wiggum Loop (Persistence)

Keep Claude working autonomously until task completion:

```bash
# Start a Ralph loop
/ralph-loop "Process all files in /Needs_Action, move to /Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

**Completion Strategies:**
1. **Promise-based:** Claude outputs `<promise>TASK_COMPLETE</promise>`
2. **File movement:** Stop hook detects when task file moves to `/Done`

## Development Conventions

### Coding Style
- Python watchers use type hints and abstract base classes
- All action files use YAML frontmatter with consistent schemas
- Markdown files follow Obsidian-compatible formatting

### Testing Practices
- Verify MCP servers before browser operations
- Use `verify.py` script to check server health
- Watchers should log errors gracefully and continue running

### Human-in-the-Loop Pattern

For sensitive actions (payments, sending messages), Claude writes an approval request:

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
created: 2026-01-07T10:30:00Z
status: pending
---

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

### Achievement Tiers

| Tier | Time | Deliverables |
|------|------|--------------|
| **Bronze** | 8-12 hrs | Obsidian vault, 1 watcher, basic Claude integration |
| **Silver** | 20-30 hrs | 2+ watchers, Plan.md generation, 1 MCP server, approval workflow |
| **Gold** | 40+ hrs | Full integration, Odoo accounting, multiple MCPs, weekly audit |
| **Platinum** | 60+ hrs | Cloud deployment, domain specialization, A2A sync, production-ready |

## Usage

### Typical Workflow

1. **Watcher detects input** (new email, WhatsApp message, bank transaction)
2. **Creates action file** in `/Needs_Action/` with metadata
3. **Claude reads** the folder and creates `Plan.md` with steps
4. **Claude executes** via MCP servers (drafts reply, schedules post)
5. **Approval required?** → Write to `/Pending_Approval/` and wait
6. **User approves** → Move file to `/Approved/`
7. **Claude completes** action and moves task to `/Done/`

### Monday Morning CEO Briefing

The autonomous audit feature generates weekly reports:

```markdown
# Monday Morning CEO Briefing

## Revenue
- **This Week**: $2,450
- **MTD**: $4,500 (45% of $10,000 target)

## Bottlenecks
| Task | Expected | Actual | Delay |
|------|----------|--------|-------|
| Client B proposal | 2 days | 5 days | +3 days |

## Proactive Suggestions
- **Notion**: No team activity in 45 days. Cost: $15/month.
  - [ACTION] Cancel subscription? Move to /Pending_Approval
```

## Resources

- **Main Blueprint:** `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Playwright Tools:** `.qwen/skills/browsing-with-playwright/references/playwright-tools.md`
- **Zoom Meetings:** Wednesdays 10:00 PM PKT (First meeting: Jan 7, 2026)
  - Meeting ID: 871 8870 7642, Passcode: 744832
- **YouTube:** https://www.youtube.com/@panaversity
