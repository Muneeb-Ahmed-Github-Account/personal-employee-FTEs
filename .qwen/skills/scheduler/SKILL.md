---
name: scheduler
description: |
  Task scheduler for recurring AI Employee operations. Supports cron-style scheduling,
  Windows Task Scheduler integration, and time-based triggers. Use for daily briefings,
  weekly audits, scheduled posts, and periodic task execution.
---

# Scheduler Skill

Schedule recurring tasks for the AI Employee.

## Overview

The Scheduler enables time-based execution of AI Employee tasks:
- Daily briefings (8 AM)
- Weekly audits (Sunday 8 PM)
- Scheduled social posts
- Periodic file cleanup
- Recurring reports

## Scheduling Methods

### Method 1: Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Daily briefing at 8 AM
0 8 * * * cd /path/to/vault && qwen "Generate daily briefing" >> /var/log/ai-employee.log

# Weekly audit every Sunday at 8 PM
0 20 * * 0 cd /path/to/vault && qwen "Generate weekly audit" >> /var/log/ai-employee.log

# Check for action files every 5 minutes
*/5 * * * * cd /path/to/watchers && python orchestrator.py --vault "../AI_Employee_Vault" --auto-qwen
```

### Method 2: Windows Task Scheduler

```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "qwen" -Argument "Generate daily briefing" -WorkingDirectory "C:\path\to\vault"
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
$principal = New-ScheduledTaskPrincipal -UserId "S-1-5-18" -LogonType ServiceAccount
Register-ScheduledTask -TaskName "AI_Employee_Daily_Briefing" -Action $action -Trigger $trigger -Principal $principal
```

### Method 3: Python Scheduler (Cross-Platform)

```python
# scheduler.py
import schedule
import time
from pathlib import Path
import subprocess

class AIScheduler:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.logs = self.vault_path / 'Logs'
    
    def daily_briefing(self):
        """Generate daily briefing at 8 AM"""
        print("Generating daily briefing...")
        result = subprocess.run(
            ['qwen', 'Generate daily briefing for yesterday\'s activities'],
            cwd=str(self.vault_path),
            capture_output=True,
            text=True
        )
        self._log('daily_briefing', result.returncode == 0)
    
    def weekly_audit(self):
        """Generate weekly audit on Sunday"""
        print("Generating weekly audit...")
        result = subprocess.run(
            ['qwen', 'Generate weekly business audit and CEO briefing'],
            cwd=str(self.vault_path),
            capture_output=True,
            text=True
        )
        self._log('weekly_audit', result.returncode == 0)
    
    def process_action_files(self):
        """Process any pending action files"""
        print("Processing action files...")
        result = subprocess.run(
            ['python', 'qwen_processor.py', '--vault', str(self.vault_path), '--once'],
            cwd=str(self.vault_path / 'watchers'),
            capture_output=True,
            text=True
        )
        self._log('process_action_files', result.returncode == 0)
    
    def _log(self, task: str, success: bool):
        """Log task execution"""
        timestamp = datetime.now().isoformat()
        log_file = self.logs / 'scheduler.log'
        with open(log_file, 'a') as f:
            f.write(f"{timestamp} - {task} - {'SUCCESS' if success else 'FAILED'}\n")
    
    def run(self):
        """Run scheduler"""
        # Daily briefing at 8 AM
        schedule.every().day.at("08:00").do(self.daily_briefing)
        
        # Weekly audit on Sunday at 8 PM
        schedule.every().sunday.at("20:00").do(self.weekly_audit)
        
        # Process action files every 5 minutes
        schedule.every(5).minutes.do(self.process_action_files)
        
        # Run scheduler
        print("Scheduler started. Press Ctrl+C to stop.")
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == '__main__':
    scheduler = AIScheduler("../AI_Employee_Vault")
    scheduler.run()
```

## Scheduled Task Templates

### Daily Briefing (8 AM)

```markdown
---
type: scheduled_task
name: daily_briefing
schedule: 0 8 * * *
description: Generate daily briefing of yesterday's activities
---

# Daily Briefing Task

## Prompt
```
Generate a daily briefing covering:
1. Tasks completed yesterday
2. Pending actions
3. Upcoming deadlines
4. Any blockers or concerns

Format as a concise report for review.
```

## Output Location
/Vault/Briefings/Daily_YYYY-MM-DD.md

## Distribution
- Update Dashboard.md
- Log to /Logs/daily_briefing.log
```

### Weekly Audit (Sunday 8 PM)

```markdown
---
type: scheduled_task
name: weekly_audit
schedule: 0 20 * * 0
description: Generate weekly business audit and CEO briefing
---

# Weekly Audit Task

## Prompt
```
Generate a comprehensive weekly audit including:

1. Revenue Summary
   - This week's earnings
   - Month-to-date progress
   - Trend analysis

2. Task Completion
   - Tasks completed this week
   - Average completion time
   - Bottlenecks identified

3. Financial Review
   - Income by category
   - Expenses
   - Subscription audit

4. Upcoming Deadlines
   - Next week's priorities
   - Critical dates

5. Proactive Suggestions
   - Cost optimization opportunities
   - Process improvements
   - Actions requiring approval

Format as CEO Briefing document.
```

## Output Location
/Vault/Briefings/CEO_Briefing_YYYY-MM-DD.md
```

### Social Media Schedule

```markdown
---
type: scheduled_task
name: linkedin_post
schedule: 0 18 * * 1,3,5
description: Post LinkedIn content Monday, Wednesday, Friday at 6 PM
---

# LinkedIn Posting Schedule

## Schedule
- Monday: Thought Leadership
- Wednesday: Business Update
- Friday: Engagement Post

## Process
1. Generate content based on type
2. Create approval request
3. If approved, post at scheduled time
4. Log engagement metrics

## Content Templates

### Thought Leadership (Monday)
```
💡 Lesson learned this week...

[Key insight]

What's your experience?

#Leadership #Professional
```

### Business Update (Wednesday)
```
🚀 Update from our team...

[What's new]

#Business #Innovation
```

### Engagement Post (Friday)
```
❓ Question for the weekend...

[Thought-provoking question]

Share your thoughts below!

#Community #Discussion
```
```

## Implementation

### Install Schedule Library

```bash
pip install schedule
```

### Create Scheduler Script

```python
# watchers/scheduler.py
import schedule
import time
import subprocess
from pathlib import Path
from datetime import datetime

class EmployeeScheduler:
    def __init__(self, vault_path: str):
        self.vault = Path(vault_path)
        self.watchers = self.vault.parent / 'watchers'
        
    def generate_daily_briefing(self):
        """Generate daily briefing"""
        subprocess.run(
            ['qwen', 'Generate daily briefing'],
            cwd=str(self.vault)
        )
    
    def generate_weekly_audit(self):
        """Generate weekly audit"""
        subprocess.run(
            ['qwen', 'Generate weekly audit and CEO briefing'],
            cwd=str(self.vault)
        )
    
    def run(self):
        # Schedule tasks
        schedule.every().day.at("08:00").do(self.generate_daily_briefing)
        schedule.every().sunday.at("20:00").do(self.generate_weekly_audit)
        
        # Run scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == '__main__':
    scheduler = EmployeeScheduler("../AI_Employee_Vault")
    scheduler.run()
```

### Run as Background Service

**Linux/Mac:**
```bash
# Start scheduler in background
nohup python scheduler.py > scheduler.log 2>&1 &

# Or use systemd
sudo systemctl enable ai-employee-scheduler
sudo systemctl start ai-employee-scheduler
```

**Windows:**
```powershell
# Create scheduled task for scheduler
$action = New-ScheduledTaskAction -Execute "python" -Argument "scheduler.py" -WorkingDirectory "C:\path\to\watchers"
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName "AI_Employee_Scheduler" -Action $action -Trigger $trigger -RunLevel Highest
```

## Cron Reference

```
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of week (0 - 6)
# │ │ │ │ │
# * * * * *  command to execute

# Examples:
0 8 * * *      # Daily at 8 AM
0 20 * * 0     # Sunday at 8 PM
*/5 * * * *    # Every 5 minutes
0 9 * * 1-5    # Weekdays at 9 AM
0 0 1 * *      # First of every month
```

## Task Execution Log

```markdown
# Scheduler Log

## Recent Executions

| Date/Time | Task | Status | Duration |
|-----------|------|--------|----------|
| 2026-03-02 08:00 | Daily Briefing | ✅ Success | 45s |
| 2026-03-01 20:00 | Weekly Audit | ✅ Success | 120s |
| 2026-03-01 08:00 | Daily Briefing | ✅ Success | 38s |

## Failed Executions

| Date/Time | Task | Error |
|-----------|------|-------|
| - | - | - |

## Next Scheduled Tasks

| Task | Scheduled Time |
|------|----------------|
| Daily Briefing | 2026-03-03 08:00 |
| Weekly Audit | 2026-03-09 20:00 |
```

## Best Practices

1. **Log everything** - Track execution success/failure
2. **Error handling** - Continue on transient failures
3. **Time zones** - Use local time for scheduling
4. **Overlap prevention** - Don't run if previous task still executing
5. **Notification** - Alert on repeated failures
6. **Review regularly** - Check logs weekly

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Task not running | Check cron/service is active |
| Wrong time | Verify timezone settings |
| Task overlaps | Add lock file mechanism |
| Missed execution | Check system was awake |

---

*Scheduler Skill v0.1*
*For Silver Tier AI Employee*
