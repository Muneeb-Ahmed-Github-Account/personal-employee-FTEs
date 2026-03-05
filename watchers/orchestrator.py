"""
Orchestrator Module

Master process that manages watchers, triggers Qwen Code processing,
and coordinates the overall AI Employee system.
"""

import subprocess
import sys
import time
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class ProcessInfo:
    """Information about a managed process."""
    name: str
    command: List[str]
    process: Optional[subprocess.Popen] = None
    pid_file: Optional[Path] = None
    restart_count: int = 0
    last_restart: Optional[datetime] = None


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.

    Responsibilities:
    - Start and monitor watcher processes
    - Trigger Qwen Code processing when action files exist
    - Update dashboard with system status
    - Handle graceful shutdown
    """

    def __init__(self, vault_path: str, config: Optional[Dict] = None):
        """
        Initialize the orchestrator.

        Args:
            vault_path: Path to the Obsidian vault
            config: Optional configuration dictionary
        """
        self.vault_path = Path(vault_path)
        self.config = config or self._load_config()

        # Setup paths
        self.needs_action = self.vault_path / 'Needs_Action'
        self.in_progress = self.vault_path / 'In_Progress'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'

        # Ensure directories exist
        for dir_path in [self.needs_action, self.in_progress, self.done,
                         self.pending_approval, self.approved, self.logs]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self._setup_logging()

        # Process management
        self.processes: Dict[str, ProcessInfo] = {}
        self.running = False

        # Qwen Code settings
        self.qwen_check_interval = self.config.get('qwen_check_interval', 60)
        self.max_qwen_iterations = self.config.get('max_qwen_iterations', 5)

        self.logger.info(f"Orchestrator initialized for vault: {self.vault_path}")
    
    def _load_config(self) -> Dict:
        """Load configuration from file if exists."""
        config_path = Path(__file__).parent / 'orchestrator_config.json'
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        self.logger = logging.getLogger('Orchestrator')
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory
        self.logs.mkdir(parents=True, exist_ok=True)
        
        # File handler
        log_file = self.logs / f'orchestrator_{datetime.now().strftime("%Y%m%d")}.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def register_watcher(self, name: str, script_path: str, args: List[str]) -> None:
        """
        Register a watcher process.
        
        Args:
            name: Unique name for the watcher
            script_path: Path to the watcher script
            args: List of arguments for the script
        """
        command = [sys.executable, script_path] + args
        pid_file = self.logs / f'{name}.pid'
        
        self.processes[name] = ProcessInfo(
            name=name,
            command=command,
            pid_file=pid_file
        )
        self.logger.info(f"Registered watcher: {name}")
    
    def start_watcher(self, name: str) -> bool:
        """
        Start a registered watcher process.
        
        Args:
            name: Name of the watcher to start
            
        Returns:
            True if started successfully, False otherwise
        """
        if name not in self.processes:
            self.logger.error(f"Watcher not registered: {name}")
            return False
        
        proc_info = self.processes[name]
        
        try:
            # Start the process
            proc_info.process = subprocess.Popen(
                proc_info.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Save PID
            if proc_info.pid_file:
                proc_info.pid_file.write_text(str(proc_info.process.pid), encoding='utf-8')
            
            proc_info.restart_count += 1
            proc_info.last_restart = datetime.now()
            
            self.logger.info(f"Started watcher '{name}' with PID {proc_info.process.pid}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start watcher '{name}': {e}")
            return False
    
    def stop_watcher(self, name: str) -> bool:
        """
        Stop a running watcher process.
        
        Args:
            name: Name of the watcher to stop
            
        Returns:
            True if stopped successfully, False otherwise
        """
        if name not in self.processes:
            return False
        
        proc_info = self.processes[name]
        
        if proc_info.process:
            try:
                proc_info.process.terminate()
                proc_info.process.wait(timeout=5)
                self.logger.info(f"Stopped watcher: {name}")
                return True
            except subprocess.TimeoutExpired:
                proc_info.process.kill()
                self.logger.warning(f"Force killed watcher: {name}")
                return True
            except Exception as e:
                self.logger.error(f"Error stopping watcher '{name}': {e}")
                return False
        
        return False
    
    def check_action_files(self) -> int:
        """
        Check for action files that need processing.
        
        Returns:
            Number of action files waiting
        """
        if not self.needs_action.exists():
            return 0
        
        action_files = list(self.needs_action.glob('*.md'))
        return len(action_files)
    
    def trigger_qwen_processing(self) -> bool:
        """
        Trigger Qwen Code to process action files.
        
        Returns:
            True if processing was triggered, False otherwise
        """
        action_count = self.check_action_files()
        
        if action_count == 0:
            return False
        
        self.logger.info(f"Found {action_count} action files, triggering Qwen Code")
        
        # Create a processing prompt
        prompt = f"""
You are the AI Employee. Process all files in the /Needs_Action folder.

For each file:
1. Read and understand the request
2. Create a Plan.md with steps to complete the task
3. Execute the plan using available tools
4. Move completed files to /Done folder
5. If approval is needed, create a file in /Pending_Approval

Current action files: {action_count}

Begin processing now. When complete, output: <promise>TASK_COMPLETE</promise>
"""
        
        # Write prompt to a state file for Qwen to pick up
        state_file = self.vault_path / '.qwen_prompt.md'
        state_file.write_text(prompt, encoding='utf-8')
        
        # ALSO: Invoke Qwen Code directly using qwen_processor.py
        self.logger.info("Invoking Qwen Code processor...")
        watchers_dir = Path(__file__).parent
        qwen_processor = watchers_dir / 'qwen_processor.py'
        
        if qwen_processor.exists():
            try:
                # Run qwen_processor.py with --once flag
                cmd = [
                    sys.executable,
                    str(qwen_processor),
                    '--vault', str(self.vault_path),
                    '--once',
                    '--verbose'
                ]
                
                result = subprocess.run(
                    cmd,
                    cwd=str(self.vault_path),
                    capture_output=False,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                self.logger.info(f"Qwen processor exited with code: {result.returncode}")
                return result.returncode == 0
                
            except subprocess.TimeoutExpired:
                self.logger.error("Qwen processor timed out")
                return False
            except Exception as e:
                self.logger.error(f"Error invoking Qwen processor: {e}")
                # Fall back to just creating the prompt file
                self.logger.info("Created Qwen prompt file (manual invocation required)")
                return True
        else:
            self.logger.warning("qwen_processor.py not found, created prompt file only")
            return True
        
        self.logger.info("Created Qwen prompt file")
        return True
    
    def update_dashboard(self) -> None:
        """Update the dashboard with current system status."""
        if not self.dashboard.exists():
            return
        
        # Count files in each folder
        needs_action_count = len(list(self.needs_action.glob('*.md')))
        in_progress_count = len(list(self.in_progress.glob('*.md')))
        pending_approval_count = len(list(self.pending_approval.glob('*.md')))
        
        # Get watcher status
        watcher_status = []
        for name, proc_info in self.processes.items():
            if proc_info.process and proc_info.process.poll() is None:
                status = "🟢 Running"
            else:
                status = "⚪ Not Running"
            watcher_status.append(f"- **{name}**: {status}")

        # Read current dashboard with UTF-8 encoding
        content = self.dashboard.read_text(encoding='utf-8')
        
        # Update quick stats
        content = self._update_section(
            content, 
            "Quick Stats",
            f"""| Metric | Value | Status |
|--------|-------|--------|
| **Pending Actions** | {needs_action_count} | {"⚠️ Action needed" if needs_action_count > 0 else "✅ Clear"} |
| **In Progress** | {in_progress_count} | {"🔄 Processing" if in_progress_count > 0 else "✅ Clear"} |
| **Awaiting Approval** | {pending_approval_count} | {"⏳ Waiting" if pending_approval_count > 0 else "✅ Clear"} |
| **Completed Today** | - | - |
| **Completed This Week** | - | - |"""
        )
        
        # Update system status
        watcher_status_text = "\n".join(watcher_status) or "*No watchers registered*"
        content = self._update_section(
            content,
            "System Status",
            f"""| Component | Status | Last Check |
|-----------|--------|------------|
{watcher_status_text}

**Legend**: 🟢 Running | 🟡 Paused | 🔴 Error | ⚪ Not Running"""
        )
        
        # Update timestamp
        content = content.replace(
            "*Last generated:*",
            f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        )
        
        # Write updated dashboard with UTF-8 encoding
        self.dashboard.write_text(content, encoding='utf-8')

    def _update_section(self, content: str, section_header: str, new_content: str) -> str:
        """Update a section in the markdown content."""
        lines = content.split('\n')
        in_section = False
        new_lines = []
        
        for line in lines:
            if section_header in line and '##' in line:
                in_section = True
                new_lines.append(line)
                new_lines.append('')  # Empty line after header
                # Skip old content until next section or end
                continue
            
            if in_section:
                if line.startswith('##') and line.strip():
                    in_section = False
                    new_lines.append(new_content)
                    new_lines.append('')
                    new_lines.append(line)
                # Skip old section content
            else:
                new_lines.append(line)
        
        # If we ended while still in section, append new content at end
        if in_section:
            new_lines.append(new_content)
        
        return '\n'.join(new_lines)
    
    def run(self) -> None:
        """
        Main orchestrator run loop.
        """
        self.running = True
        self.logger.info("Starting orchestrator main loop")

        try:
            while self.running:
                # Update dashboard
                self.update_dashboard()

                # Check for action files and trigger Qwen if needed
                if self.check_action_files() > 0:
                    self.trigger_qwen_processing()

                # Check watcher health
                for name, proc_info in self.processes.items():
                    if proc_info.process and proc_info.process.poll() is not None:
                        self.logger.warning(f"Watcher '{name}' died, restarting...")
                        self.start_watcher(name)

                time.sleep(self.qwen_check_interval)

        except KeyboardInterrupt:
            self.logger.info("Orchestrator stopped by user")
            self.shutdown()
        except Exception as e:
            self.logger.critical(f"Orchestrator error: {e}", exc_info=True)
            self.shutdown()
            raise
    
    def shutdown(self) -> None:
        """Gracefully shutdown all processes."""
        self.logger.info("Shutting down orchestrator...")
        self.running = False
        
        # Stop all watchers
        for name in list(self.processes.keys()):
            self.stop_watcher(name)
        
        self.logger.info("Orchestrator shutdown complete")


def main():
    """Entry point for the orchestrator."""
    import argparse

    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument('--vault', type=str, required=True, help='Path to Obsidian vault')
    parser.add_argument('--config', type=str, default=None, help='Path to config file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    parser.add_argument('--auto-qwen', action='store_true', help='Auto-invoke Qwen Code when files detected')

    args = parser.parse_args()

    # Create orchestrator
    orchestrator = Orchestrator(vault_path=args.vault)

    # Register watchers
    watchers_dir = Path(__file__).parent

    # File System Watcher
    orchestrator.register_watcher(
        name='filesystem_watcher',
        script_path=str(watchers_dir / 'filesystem_watcher.py'),
        args=['--vault', args.vault, '--interval', '30']
    )

    # Qwen Code Processor (optional - for continuous auto-processing)
    if args.auto_qwen:
        orchestrator.register_watcher(
            name='qwen_processor',
            script_path=str(watchers_dir / 'qwen_processor.py'),
            args=['--vault', args.vault, '--interval', '60']
        )
        orchestrator.logger.info("Qwen Code auto-processor enabled")

    # Start all registered watchers
    for name in orchestrator.processes.keys():
        orchestrator.start_watcher(name)

    # Run main loop
    orchestrator.run()


if __name__ == '__main__':
    main()
