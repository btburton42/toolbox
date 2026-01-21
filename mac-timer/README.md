# macOS Auto-Logout Timer

A Python application that automatically logs out your macOS user after a specified duration.

## Features

- ✅ Flexible time format support (seconds, minutes, hours)
- ✅ Configuration file support for saving settings
- ✅ Graceful interrupt handling (Ctrl+C to cancel)
- ✅ Cross-method logout handling
- ✅ Clear user feedback and status messages

## Installation

### Requirements

- macOS 10.13+
- Python 3.7+

### Setup

1. Clone or download the repository:
```bash
cd /Users/tylerburton/Repos/mac-timer
```

2. Make the script executable:
```bash
chmod +x mac_timer.py
```

## Usage

### Basic Examples

**Logout in 30 seconds:**
```bash
python3 mac_timer.py 30s
```

**Logout in 5 minutes:**
```bash
python3 mac_timer.py 5m
```

**Logout in 2 hours:**
```bash
python3 mac_timer.py 2h
```

**Logout in 1 hour 30 minutes:**
```bash
python3 mac_timer.py 1h30m
```

**Logout in 3600 seconds (plain number):**
```bash
python3 mac_timer.py 3600
```

### Configuration File

**Save configuration and start timer:**
```bash
python3 mac_timer.py -c ~/.mac-timer/config.json 5m
```

**Load and use saved configuration:**
```bash
python3 mac_timer.py -l -c ~/.mac-timer/config.json
```

## Time Format

The duration argument supports multiple formats:

- **Seconds**: `30s` or just `30`
- **Minutes**: `5m`
- **Hours**: `2h`
- **Combined**: `1h30m`, `2h15m30s`

## Important

⚠️ **Once started, the timer cannot be cancelled.** The system will force logout after the specified duration. Plan accordingly.

## Setup as Launch Agent (Optional)

To automatically start the timer at login, you can create a LaunchAgent:

1. Create the directory if it doesn't exist:
```bash
mkdir -p ~/Library/LaunchAgents
```

2. Create the plist file:
```bash
cat > ~/Library/LaunchAgents/com.local.mactimer.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.local.mactimer</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/tylerburton/Repos/mac-timer/mac_timer.py</string>
        <string>2h</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/mactimer.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/mactimer.err</string>
</dict>
</plist>
EOF
```

3. Load the agent:
```bash
launchctl load ~/Library/LaunchAgents/com.local.mactimer.plist
```

To unload:
```bash
launchctl unload ~/Library/LaunchAgents/com.local.mactimer.plist
```

## Security Considerations

- This application uses `osascript` to trigger logout, which requires user interaction/confirmation in some cases
- Alternative method using `loginwindow` may require elevated privileges
- The script can be interrupted at any time with Ctrl+C

## Troubleshooting

### "Could not trigger logout" error
- Try running with `sudo` if you have permission issues
- Ensure you're running on macOS 10.13 or later

### Timer doesn't work when screen is locked
- The app needs to be running in the foreground or background
- Consider using LaunchAgent for background execution

## License

MIT License
