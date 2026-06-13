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

## Where this is going

The CLI proves the idea: friction + accountability makes waking up a game. The
limit is that the Mac can't ring a real alarm on the phone — Reminders sync, but
alarms don't, and a reminder is easy to swipe away half-asleep.

iOS 26 changed this. Apple's **AlarmKit** lets a third-party app create a real
system alarm that rings through Silent mode and Focus, shows on the Lock Screen
and Dynamic Island, and survives restarts. That makes the real goal possible:

> A native iPhone alarm you can't dismiss until you solve the math, backed by an
> accountability layer you can review on a bigger screen.

### Roadmap (built in order of risk, not order of the diagram)

- [ ] **Phase 0 — validate the gate.** Prototype AlarmKit and confirm dismissal
      can be blocked behind the math challenge (the one make-or-break unknown).
- [ ] **Phase 1 — the phone app.** SwiftUI + AlarmKit alarm with the anti-snooze
      math gate. Streak/stats stored locally on the phone. Usable on day one, no
      server needed.
- [ ] **Phase 2 — the backend.** Port this tool's logic (streak math, hit
      detection, challenge generation) into a Python API + DB. The phone posts
      each check-in.
- [ ] **Phase 3 — the dashboard.** Web/Mac frontend reading the API for a clear
      view of streaks and hit rate over time — the big-screen stats view.

The CLI's logic isn't throwaway: it becomes the backend's brain in Phase 2.

### Carried over from the CLI era

- [ ] Adjustable challenge difficulty (easier/harder math, configurable)
- [ ] Write daily check-ins to an Obsidian vault

## License

[MIT](LICENSE)
