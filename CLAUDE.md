# morning — wake up system

CLI tool for building a consistent wake-up habit.

## What it does
- `morning set HH:MM [intention]` — save tonight's wake target and tomorrow's focus
- `morning checkin` — log actual wake time, run anti-snooze math challenge, show streak
- `morning stats` — 14-day history, hit rate, average wake time

## Storage
Single JSON file: `~/.morning_data.json`

## Running
`morning` (alias in ~/.zshrc) → `python3 ~/dev/projects/morning/morning.py`

## Stack
Python 3, standard library only. No dependencies to install.

## Possible extensions
- Obsidian integration: write daily check-in to vault
- Evening reminder via launchd (scheduled macOS notification)
- Weekly email/Slack summary
