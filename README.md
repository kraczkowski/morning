# morning

A command-line tool that builds a consistent wake-up habit — set a target time,
get an iPhone reminder, and prove you're awake with a math challenge before your
streak counts.

Built as a learning project. Python 3, standard library only, macOS-native.

## Why

Alarms are easy to dismiss half-asleep. `morning` adds friction (a math problem
you must solve to check in) and accountability (a visible streak + hit rate), so
waking up on time becomes a game you don't want to lose.

## Requirements

- macOS (uses Reminders.app and notifications via `osascript`)
- Python 3 (no packages to install)
- iPhone optional — reminders sync from Mac via iCloud

## Setup

```bash
git clone https://github.com/kraczkowski/morning.git
cd morning

# add a shortcut so you can just type `morning`
echo "alias morning='python3 $(pwd)/morning.py'" >> ~/.zshrc
source ~/.zshrc
```

First run will ask macOS for Reminders access (System Settings → Privacy → Reminders).

## Usage

```bash
morning set 6:30                  # set tonight's wake target
morning set 6:30 go for a run     # target + an intention for tomorrow
morning checkin                   # log wake time, solve the challenge, see streak
morning stats                     # 14-day history, hit rate, average wake time
```

## How it works

- **Storage:** a single JSON file at `~/.morning_data.json` — no database, no cloud.
- **Hit detection:** checking in at or before your target counts as a hit.
- **Streak:** consecutive prior days with a hit; breaks on the first miss.
- **Anti-snooze:** check-in is gated behind a randomized arithmetic problem to make
  sure you're actually awake.

## Roadmap

- [ ] Frontend (web UI) instead of CLI-only
- [ ] Adjustable challenge difficulty (easier/harder math, configurable)
- [ ] Write daily check-ins to an Obsidian vault
- [ ] Scheduled evening reminder via `launchd`
- [ ] Weekly summary by email

## License

[MIT](LICENSE)
