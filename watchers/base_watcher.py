"""
Base Watcher Module

Abstract base class for all watcher scripts in the AI Employee system.
All watchers inherit from this class to ensure consistent behavior.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher scripts.
    
    Watchers monitor external data sources (Gmail, WhatsApp, filesystems, etc.)
    and create action files in the Obsidian vault's /Needs_Action folder.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.check_interval = check_interval
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        
        # Track processed items to avoid duplicates
        self.processed_ids: set = set()
        
        # State file for persistence across restarts
        self.state_file = self.vault_path / f'.state_{self.__class__.__name__.lower()}.json'
        self._load_state()
    
    def _load_state(self) -> None:
        """Load processed IDs from state file for persistence."""
        import json
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.processed_ids = set(state.get('processed_ids', []))
                    self.logger.info(f"Loaded {len(self.processed_ids)} processed IDs from state")
            except Exception as e:
                self.logger.warning(f"Could not load state file: {e}")
    
    def _save_state(self) -> None:
        """Save processed IDs to state file."""
        import json
        try:
            # Only keep last 1000 IDs to prevent unbounded growth
            ids_list = list(self.processed_ids)[-1000:]
            with open(self.state_file, 'w') as f:
                json.dump({'processed_ids': ids_list}, f)
        except Exception as e:
            self.logger.error(f"Could not save state file: {e}")
    
    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check the data source for new items.
        
        Returns:
            List of new items to process
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create a markdown action file in /Needs_Action folder.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to created file, or None if failed
        """
        pass
    
    def run(self) -> None:
        """
        Main run loop for the watcher.
        Continuously monitors for new items and creates action files.
        """
        self.logger.info(f"Starting {self.__class__.__name__}")
        self.logger.info(f"Vault path: {self.vault_path}")
        self.logger.info(f"Check interval: {self.check_interval}s")
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    for item in items:
                        filepath = self.create_action_file(item)
                        if filepath:
                            self.logger.info(f"Created action file: {filepath.name}")
                    
                    # Save state after each check
                    self._save_state()
                    
                except Exception as e:
                    self.logger.error(f"Error processing items: {e}", exc_info=True)
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info(f"{self.__class__.__name__} stopped by user")
            self._save_state()
        except Exception as e:
            self.logger.critical(f"Fatal error: {e}", exc_info=True)
            raise
