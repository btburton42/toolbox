#!/usr/bin/env python3
"""
macOS Auto-Logout Timer
Automatically logs out the current user after a specified duration.
"""

import argparse
import subprocess
import sys
import time
import os
from pathlib import Path
from typing import Optional
import json
import atexit


class MacTimer:
    """Handles automatic logout/sleep functionality for macOS."""
    
    def __init__(self, timeout_seconds: int, action: str = "logout", config_file: Optional[str] = None):
        """
        Initialize the timer.
        
        Args:
            timeout_seconds: Number of seconds before action
            action: Action to perform ('logout' or 'sleep')
            config_file: Optional path to configuration file
        """
        self.timeout_seconds = timeout_seconds
        self.action = action
        self.config_file = config_file
        self.start_time = None
        self.paused = False
        self.pause_time = None
    
    def start(self):
        """Start the timer and wait for logout."""
        self.start_time = time.time()
        hours = self.timeout_seconds // 3600
        minutes = (self.timeout_seconds % 3600) // 60
        seconds = self.timeout_seconds % 60
        
        time_str = ""
        if hours > 0:
            time_str += f"{hours}h "
        if minutes > 0:
            time_str += f"{minutes}m "
        time_str += f"{seconds}s"
        
        print(f"🔔 Auto-{self.action} timer started: {time_str}")
        print(f"⏱️  System will {self.action} in {self.timeout_seconds} seconds")
        print(f"⚠️  WARNING: This {self.action} cannot be cancelled!")
        
        time.sleep(self.timeout_seconds)
        if self.action == "logout":
            self.logout()
        elif self.action == "sleep":
            self.sleep()
    
    def logout(self):
        """Execute macOS force logout without user confirmation."""
        print(f"\n⏰ Time's up! Force logging out...")
        try:
            # Try force logout using AppleScript event code (no confirmation dialog)
            subprocess.run(
                ["osascript", "-e", 'tell app "loginwindow" to «event aevtrlgo»'],
                check=True
            )
        except subprocess.CalledProcessError:
            # Fallback: use launchctl to boot out the user session
            try:
                import pwd
                uid = pwd.getpwall()[0][2]  # Get current UID
                subprocess.run(
                    ["launchctl", "bootout", f"user/{os.getuid()}"],
                    check=True
                )
            except Exception:
                # Last resort: kill the login window process
                try:
                    subprocess.run(
                        ["killall", "loginwindow"],
                        check=False
                    )
                    time.sleep(1)
                except Exception as e:
                    print(f"Error: Could not force logout. {e}")
                    print("You may need to run with elevated privileges (sudo)")
                    sys.exit(1)
    
    def sleep(self):
        """Execute macOS system sleep."""
        print(f"\n⏰ Time's up! Putting system to sleep...")
        try:
            subprocess.run(["pmset", "sleepnow"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: Could not put system to sleep. {e}")
            print("You may need to run with elevated privileges (sudo)")
            sys.exit(1)
    
    def save_config(self):
        """Save current configuration to file."""
        if not self.config_file:
            return
        
        config = {
            "timeout_seconds": self.timeout_seconds,
            "action": self.action,
            "created_at": time.time()
        }
        
        try:
            Path(self.config_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"✅ Config saved to {self.config_file}")
        except IOError as e:
            print(f"Warning: Could not save config: {e}")
    
    @staticmethod
    def load_config(config_file: str) -> Optional[dict]:
        """
        Load configuration from file.
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            Config dict with timeout_seconds and action, or None if file doesn't exist
        """
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return {
                    "timeout_seconds": config.get("timeout_seconds"),
                    "action": config.get("action", "logout")
                }
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in config file {config_file}")
            return None


def parse_time_string(time_str: str) -> int:
    """
    Parse time string into seconds.
    
    Supports formats like:
    - "30s" for 30 seconds
    - "5m" for 5 minutes
    - "2h" for 2 hours
    - "1h30m" for 1 hour 30 minutes
    - "60" for 60 seconds (plain number)
    
    Args:
        time_str: Time string to parse
        
    Returns:
        Total seconds
    """
    time_str = time_str.lower().strip()
    
    # If it's just a number, treat it as seconds
    try:
        return int(time_str)
    except ValueError:
        pass
    
    total_seconds = 0
    current_num = ""
    
    for char in time_str:
        if char.isdigit():
            current_num += char
        elif char in ['h', 'm', 's']:
            if current_num:
                num = int(current_num)
                if char == 'h':
                    total_seconds += num * 3600
                elif char == 'm':
                    total_seconds += num * 60
                elif char == 's':
                    total_seconds += num
                current_num = ""
        elif char.isspace():
            continue
        else:
            print(f"Error: Invalid time format: {time_str}")
            sys.exit(1)
    
    if total_seconds == 0:
        print(f"Error: Could not parse time: {time_str}")
        sys.exit(1)
    
    return total_seconds


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automatically log out or sleep your macOS system after a specified time.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mac_timer.py 30s                    # Logout in 30 seconds
  python mac_timer.py 5m                     # Logout in 5 minutes
  python mac_timer.py 2h                     # Logout in 2 hours
  python mac_timer.py 1h30m                  # Logout in 1 hour 30 minutes
  python mac_timer.py 3600                   # Logout in 3600 seconds
  python mac_timer.py -a sleep 5m            # Sleep in 5 minutes
  python mac_timer.py -c config.json 5m      # Save config and logout in 5 minutes
        """
    )
    
    parser.add_argument(
        "duration",
        nargs="?",
        help="Time until action (e.g., '30s', '5m', '2h', '1h30m', or seconds as number)"
    )
    
    parser.add_argument(
        "-a", "--action",
        choices=["logout", "sleep"],
        default="logout",
        help="Action to perform when timer expires (default: logout)"
    )
    
    parser.add_argument(
        "-c", "--config",
        help="Path to configuration file to save/load settings"
    )
    
    parser.add_argument(
        "-l", "--load-config",
        action="store_true",
        help="Load timeout from config file (requires --config)"
    )
    
    parser.add_argument(
        "-b", "--background",
        action="store_true",
        help="Run in background and exit immediately"
    )
    args = parser.parse_args()
    
    # Determine timeout and action
    timeout_seconds = None
    action = args.action
    
    if args.load_config:
        if not args.config:
            print("Error: --config is required when using --load-config")
            sys.exit(1)
        config_data = MacTimer.load_config(args.config)
        if config_data is None:
            print(f"Error: Could not load config from {args.config}")
            sys.exit(1)
        timeout_seconds = config_data["timeout_seconds"]
        action = config_data["action"]
    elif args.duration:
        timeout_seconds = parse_time_string(args.duration)
    else:
        print("Error: Duration argument is required")
        parser.print_help()
        sys.exit(1)
    
    # Create and start timer
    timer = MacTimer(timeout_seconds, action, args.config)
    
    if args.config:
        timer.save_config()
    
    # Daemonize if background mode is requested
    if args.background:
        try:
            # Fork to background
            pid = os.fork()
            if pid > 0:
                # Parent process exits
                print(f"✅ Timer started in background (PID: {pid})")
                sys.exit(0)
        except OSError as e:
            print(f"Error: Could not fork to background: {e}")
            sys.exit(1)
        
        # Detach from terminal
        os.setsid()
        os.umask(0)
        
        # Redirect output to null
        with open(os.devnull, 'w') as devnull:
            os.dup2(devnull.fileno(), sys.stdout.fileno())
            os.dup2(devnull.fileno(), sys.stderr.fileno())
    
    timer.start()


if __name__ == "__main__":
    main()
