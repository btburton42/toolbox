#!/usr/bin/env python3
"""
Installation and setup script for macOS Auto-Logout Timer.
"""

import os
import sys
import subprocess
from pathlib import Path


def setup_executable():
    """Make the main script executable."""
    script_path = Path(__file__).parent / "mac_timer.py"
    if script_path.exists():
        os.chmod(script_path, 0o755)
        print(f"✅ Made {script_path.name} executable")


def create_symlink():
    """Create a symlink in /usr/local/bin for easy access."""
    source = Path(__file__).parent / "mac_timer.py"
    link = Path("/usr/local/bin/mac-timer")
    
    try:
        if link.exists() or link.is_symlink():
            link.unlink()
        link.symlink_to(source)
        print(f"✅ Created symlink: {link} -> {source}")
        print(f"   You can now run: mac-timer 5m")
    except PermissionError:
        print(f"⚠️  Could not create /usr/local/bin symlink (requires sudo)")
        print(f"   Alternative: run as 'python3 /path/to/mac_timer.py'")
    except Exception as e:
        print(f"⚠️  Could not create symlink: {e}")


def main():
    """Run setup."""
    print("🚀 Setting up macOS Auto-Logout Timer...\n")
    
    setup_executable()
    create_symlink()
    
    print("\n✨ Setup complete!")
    print("\nQuick start:")
    print("  python3 mac_timer.py 5m    # Logout in 5 minutes")
    print("  python3 mac_timer.py 2h    # Logout in 2 hours")
    print("\nFor more info, see README.md")


if __name__ == "__main__":
    main()
