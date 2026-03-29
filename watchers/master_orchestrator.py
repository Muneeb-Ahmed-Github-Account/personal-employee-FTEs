"""
MASTER ORCHESTRATOR - Auto File Movement

Automatically moves files:
1. Inbox -> Needs_Action (within 2 seconds)
2. Needs_Action -> Pending_Approval (after Qwen processes, within 2 seconds)

DOES NOT open browser - LinkedIn Auto-Post handles that when file is in Approved/
"""

import sys
import time
import shutil
from pathlib import Path
from datetime import datetime


def move_files(source_folder, dest_folder, check_condition=None):
    """Generic file mover function"""
    moved = 0
    source = Path(source_folder)
    dest = Path(dest_folder)
    
    for file in source.iterdir():
        if file.is_file() and file.suffix == '.md':
            # Skip if already processed
            if file.name.startswith('.'):
                continue
            
            # Check condition if provided
            if check_condition:
                try:
                    content = file.read_text(encoding='utf-8')
                    if not check_condition(content):
                        continue
                except:
                    continue
            
            try:
                shutil.move(str(file), str(dest / file.name))
                print(f"[{datetime.now().strftime('%H:%M:%S')}] MOVED: {file.name}")
                moved += 1
            except Exception as e:
                print(f"Error moving {file.name}: {e}")
    
    return moved


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Master Orchestrator')
    parser.add_argument('--vault', type=str, required=True, help='Path to Obsidian vault')
    args = parser.parse_args()
    
    vault = Path(args.vault)
    
    # Ensure folders exist
    inbox = vault / 'Inbox'
    needs_action = vault / 'Needs_Action'
    pending_approval = vault / 'Pending_Approval'
    approved = vault / 'Approved'
    done = vault / 'Done'
    
    for folder in [inbox, needs_action, pending_approval, approved, done]:
        folder.mkdir(parents=True, exist_ok=True)
    
    print("="*70)
    print("MASTER ORCHESTRATOR - Auto File Movement")
    print("="*70)
    print("Workflow: Inbox -> Needs_Action -> Pending_Approval -> Approved -> Done")
    print("Browser opens ONLY when you move file to Approved/")
    print("Press Ctrl+C to stop")
    print("="*70)
    
    try:
        while True:
            # Step 1: Move ALL files from Inbox to Needs_Action
            moved = move_files(inbox, needs_action)
            if moved > 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Moved {moved} file(s) from Inbox to Needs_Action")
            
            # Step 2: Move files from Needs_Action to Pending_Approval
            # Only move if Qwen has processed them (contains approval markers)
            def is_approval_file(content):
                markers = [
                    'To Approve',
                    'Move this file to',
                    'type: approval_request',
                    'type: linkedin_post',
                    '## LinkedIn Post',
                    '## Post Content',
                    '## To Approve'
                ]
                return any(marker in content for marker in markers)
            
            moved = move_files(needs_action, pending_approval, is_approval_file)
            if moved > 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Moved {moved} file(s) from Needs_Action to Pending_Approval")
            
            # Step 3: Log approved files (LinkedIn Auto-Post handles posting)
            approved_count = len(list(approved.glob('*.md')))
            if approved_count > 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {approved_count} file(s) in Approved/ - LinkedIn Auto-Post will open browser")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nStopped by user")


if __name__ == '__main__':
    main()
