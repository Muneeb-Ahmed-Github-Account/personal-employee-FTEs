"""
File System Watcher Module

Monitors a drop folder for new files and creates action files in the Obsidian vault.
This is the simplest watcher to set up and perfect for Bronze tier.
"""

import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

from base_watcher import BaseWatcher


class FileDropItem:
    """Represents a file dropped for processing."""
    
    def __init__(self, source_path: Path, content_hash: str):
        self.source_path = source_path
        self.content_hash = content_hash
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'source_path': str(self.source_path),
            'content_hash': self.content_hash,
            'timestamp': self.timestamp.isoformat()
        }


class FileSystemWatcher(BaseWatcher):
    """
    Watches a drop folder for new files.
    
    When a file is added, it creates an action file in /Needs_Action
    with metadata about the dropped file.
    """
    
    def __init__(self, vault_path: str, drop_folder: Optional[str] = None, check_interval: int = 30):
        """
        Initialize the file system watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            drop_folder: Path to the drop folder (default: vault/Inbox/Drop)
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)
        
        # Set up drop folder
        if drop_folder:
            self.drop_folder = Path(drop_folder)
        else:
            self.drop_folder = self.inbox / 'Drop'
        
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Drop folder: {self.drop_folder}")
    
    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file for deduplication."""
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def check_for_updates(self) -> List[FileDropItem]:
        """
        Check drop folder for new files.
        
        Returns:
            List of new FileDropItem objects
        """
        new_items = []
        
        if not self.drop_folder.exists():
            return new_items
        
        # Get all files in drop folder (not directories)
        for file_path in self.drop_folder.iterdir():
            if file_path.is_file() and not file_path.name.startswith('.'):
                content_hash = self._calculate_hash(file_path)
                unique_id = f"{file_path.name}_{content_hash}"
                
                if unique_id not in self.processed_ids:
                    item = FileDropItem(file_path, content_hash)
                    new_items.append(item)
                    self.processed_ids.add(unique_id)
                    self.logger.info(f"Found new file: {file_path.name}")
        
        return new_items
    
    def create_action_file(self, item: FileDropItem) -> Optional[Path]:
        """
        Create a markdown action file for the dropped file.
        
        Args:
            item: The FileDropItem to create an action file for
            
        Returns:
            Path to created file, or None if failed
        """
        try:
            # Copy file to vault for safekeeping
            dest_path = self.inbox / item.source_path.name
            shutil.copy2(item.source_path, dest_path)
            
            # Get file info
            file_size = item.source_path.stat().st_size
            file_mtime = datetime.fromtimestamp(item.source_path.stat().st_mtime)
            
            # Create action file content
            content = f"""---
type: file_drop
original_name: {item.source_path.name}
size: {file_size}
size_human: {self._human_readable_size(file_size)}
received: {datetime.now().isoformat()}
original_modified: {file_mtime.isoformat()}
content_hash: {item.content_hash}
status: pending
priority: normal
---

# File Drop for Processing

## File Information
- **Original Name**: {item.source_path.name}
- **Size**: {self._human_readable_size(file_size)}
- **Received**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Original Modified**: {file_mtime.strftime('%Y-%m-%d %H:%M:%S')}

## File Location
- **Copied to**: `{dest_path}`
- **Content Hash**: `{item.content_hash}`

## Suggested Actions
- [ ] Review file contents
- [ ] Determine required action
- [ ] Process and move to /Done
- [ ] Delete original from drop folder

## Notes
*Add any notes about processing this file here*

---
*Created by FileSystemWatcher v0.1*
"""
            
            # Generate unique filename
            safe_name = item.source_path.stem.replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            action_filename = f"FILE_DROP_{safe_name}_{timestamp}.md"
            action_filepath = self.needs_action / action_filename
            
            # Write action file
            action_filepath.write_text(content, encoding='utf-8')
            
            self.logger.info(f"Created action file: {action_filename}")
            return action_filepath
            
        except Exception as e:
            self.logger.error(f"Failed to create action file: {e}", exc_info=True)
            return None
    
    def _human_readable_size(self, size_bytes: int) -> str:
        """Convert bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"


def main():
    """Entry point for running the file system watcher."""
    import argparse
    import sys
    import logging

    parser = argparse.ArgumentParser(description='File System Watcher for AI Employee')
    parser.add_argument('--vault', type=str, required=True, help='Path to Obsidian vault')
    parser.add_argument('--drop-folder', type=str, default=None, help='Path to drop folder')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(Path(args.vault) / 'Logs' / 'filesystem_watcher.log')
        ]
    )
    
    # Create and run watcher
    watcher = FileSystemWatcher(
        vault_path=args.vault,
        drop_folder=args.drop_folder,
        check_interval=args.interval
    )
    watcher.run()


if __name__ == '__main__':
    main()
