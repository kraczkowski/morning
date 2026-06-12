#!/usr/bin/env python3

import json
import sys
import os
import datetime
import argparse
import subprocess
import random
import re

DATA_FILE = os.path.expanduser("~/.morning_data.json")

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"target_time": None, "intention": None, "log": []}
    with open(DATA_FILE) as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def parse_time(time_str):
    time_str = time_str.strip()
    if re.match(r'^\d{1,2}$', time_str):
        return f"{int(time_str):02d}:00"
    if re.match(r'^\d{1,2}:\d{2}$', time_str):
        h, m = time_str.split(':')
        return f"{int(h):02d}:{m}"
    raise ValueError(f"Can't parse time: '{time_str}' — use HH:MM like 7:00 or 06:30")


def to_minutes(time_str):
    h, m = time_str.split(':')
    return int(h) * 60 + int(m)


def get_streak(log):
    today = datetime.date.today().isoformat()
    past = sorted(
        [e for e in log if e["date"] != today],
        key=lambda x: x["date"],
        reverse=True
    )
    streak = 0
    expected = datetime.date.today() - datetime.timedelta(days=1)
    for entry in past:
        entry_date = datetime.date.fromisoformat(entry["date"])
        if entry_date == expected and entry.get("hit"):
            streak += 1
            expected -= datetime.timedelta(days=1)
        else:
            break
    return streak


def anti_snooze_challenge():
    ops = [('+', lambda a, b: a + b), ('*', lambda a, b: a * b), ('-', lambda a, b: a - b)]
    op_sym, op_fn = random.choice(ops)
    if op_sym == '+':
        a, b = random.randint(10, 50), random.randint(10, 50)
    elif op_sym == '*':
        a, b = random.randint(2, 12), random.randint(2, 12)
    else:
        a, b = random.randint(20, 99), random.randint(1, 19)
    answer = op_fn(a, b)

    print(f"\n{YELLOW}{BOLD}Wake-up check: {a} {op_sym} {b} = ?{RESET}")
    attempts = 0
    while True:
        try:
            guess = input("> ").strip()
            if int(guess) == answer:
                print(f"{GREEN}Correct.{RESET}")
                return
            attempts += 1
            if attempts >= 3:
                print(f"{DIM}Answer: {answer}{RESET}")
                return
            print(f"{RED}Nope. Try again.{RESET}")
        except (ValueError, EOFError):
            print(f"{DIM}Answer: {answer}{RESET}")
            return
        except KeyboardInterrupt:
            print()
            return


def notify_mac(title, message):
    try:
        subprocess.run(
            ["osascript", "-e", f'display notification "{message}" with title "{title}"'],
            check=True, capture_output=True
        )
    except Exception:
        pass


def create_reminder(target_time, intention=None):
    h, m = target_time.split(':')
    label = f"⏰ Wake up — {intention}" if intention else "⏰ Wake up"
    label = label.replace('"', '\\"')

    now = datetime.datetime.now()
    alarm_dt = now.replace(hour=int(h), minute=int(m), second=0, microsecond=0)
    if alarm_dt <= now:
        alarm_dt += datetime.timedelta(days=1)

    extra_days = (alarm_dt.date() - datetime.date.today()).days
    script = f'''
tell application "Reminders"
    if not (exists list "morning") then
        make new list with properties {{name:"morning"}}
    end if
    tell list "morning"
        set alarmDate to current date
        set hours of alarmDate to {int(h)}
        set minutes of alarmDate to {int(m)}
        set seconds of alarmDate to 0
        if {extra_days} > 0 then
            set alarmDate to alarmDate + ({extra_days} * days)
        end if
        make new reminder with properties {{name:"{label}", remind me date:alarmDate, priority:1}}
    end tell
end tell
'''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return alarm_dt


def cmd_set(time_str, intention_parts):
    try:
        target = parse_time(time_str)
    except ValueError as e:
        print(f"{RED}{e}{RESET}")
        sys.exit(1)

    intention = " ".join(intention_parts) if intention_parts else None
    data = load_data()
    data["target_time"] = target
    data["intention"] = intention
    save_data(data)

    print(f"\n{BOLD}Target:{RESET} {GREEN}{target}{RESET}")
    if intention:
        print(f"{BOLD}Intention:{RESET} {CYAN}{intention}{RESET}")
    try:
        alarm_dt = create_reminder(target, intention)
        date_label = "today" if alarm_dt.date() == datetime.date.today() else "tomorrow"
        print(f"\n{GREEN}Reminder set{RESET} {DIM}({date_label} at {target} — syncs to iPhone via iCloud){RESET}")
    except Exception as e:
        print(f"\n{YELLOW}Could not create reminder:{RESET} {DIM}{e}{RESET}")
        print(f"{DIM}Make sure Reminders.app has access in System Settings → Privacy → Reminders{RESET}")

    print(f"{DIM}Run 'morning checkin' when you wake up.{RESET}\n")
    notify_mac("Morning System", f"Reminder set for {target}")


def cmd_checkin():
    now = datetime.datetime.now()
    today = now.date().isoformat()
    actual = now.strftime("%H:%M")

    data = load_data()

    existing = next((e for e in data["log"] if e["date"] == today), None)
    if existing:
        print(f"\n{YELLOW}Already checked in today at {existing['actual']}.{RESET}\n")
        return

    anti_snooze_challenge()

    target = data.get("target_time")
    intention = data.get("intention")
    hit = (to_minutes(actual) <= to_minutes(target)) if target else None

    data["log"].append({
        "date": today,
        "target": target,
        "actual": actual,
        "intention": intention,
        "hit": hit,
    })
    save_data(data)

    print()
    if target:
        diff = abs(to_minutes(actual) - to_minutes(target))
        if hit:
            print(f"{GREEN}{BOLD}On time.{RESET}  {actual} (target {target}, {diff}m early)")
        else:
            print(f"{RED}{BOLD}Late.{RESET}     {actual} (target {target}, {diff}m over)")
    else:
        print(f"{CYAN}Checked in at {actual}.{RESET}  {DIM}No target set — run 'morning set HH:MM' tonight.{RESET}")

    streak = get_streak(data["log"])
    if streak > 0:
        print(f"{YELLOW}{BOLD}Streak: {streak} day{'s' if streak != 1 else ''}{RESET}")
    else:
        print(f"{DIM}Streak: 0{RESET}")

    if intention:
        print(f"\n{BOLD}Today:{RESET} {CYAN}{intention}{RESET}")
    print()


def cmd_stats():
    data = load_data()
    log = sorted(data["log"], key=lambda x: x["date"], reverse=True)

    if not log:
        print(f"\n{DIM}No data yet. Run 'morning checkin' after waking up.{RESET}\n")
        return

    recent = log[:14]
    streak = get_streak(log)
    hit_count = sum(1 for e in log if e.get("hit"))

    print(f"\n{BOLD}Last {len(recent)} days:{RESET}\n")
    for e in recent:
        if e.get("hit") is True:
            marker = f"{GREEN}✓{RESET}"
        elif e.get("hit") is False:
            marker = f"{RED}✗{RESET}"
        else:
            marker = f"{DIM}·{RESET}"
        note = f"  {DIM}{e['intention'][:35]}{RESET}" if e.get("intention") else ""
        target_str = f" {DIM}/ {e['target']}{RESET}" if e.get("target") else ""
        print(f"  {DIM}{e['date']}{RESET}  {marker}  {e.get('actual','?')}{target_str}{note}")

    print()
    print(f"  {BOLD}Streak:{RESET}   {YELLOW}{streak} day{'s' if streak != 1 else ''}{RESET}")
    print(f"  {BOLD}Hit rate:{RESET} {GREEN}{hit_count}/{len(log)} ({int(hit_count/len(log)*100)}%){RESET}")

    times = [to_minutes(e["actual"]) for e in log if e.get("actual")]
    if times:
        avg = sum(times) // len(times)
        print(f"  {BOLD}Average:{RESET}  {CYAN}{avg // 60:02d}:{avg % 60:02d}{RESET}")
    print()


def main():
    parser = argparse.ArgumentParser(prog="morning", add_help=False)
    parser.add_argument("command", nargs="?", default="checkin")
    parser.add_argument("rest", nargs="*")
    args = parser.parse_args()

    if args.command in ("checkin", "c", "in"):
        cmd_checkin()
    elif args.command in ("set", "s"):
        if not args.rest:
            print(f"{RED}Usage: morning set HH:MM [intention]{RESET}")
            sys.exit(1)
        cmd_set(args.rest[0], args.rest[1:])
    elif args.command in ("stats", "st"):
        cmd_stats()
    elif args.command in ("help", "-h", "--help"):
        print(f"""
{BOLD}morning{RESET} — wake up system

  {CYAN}morning set 7:00{RESET}                     set tonight's target
  {CYAN}morning set 7:00 go for a run{RESET}        set target + intention
  {CYAN}morning checkin{RESET}                      log wake time, see streak
  {CYAN}morning stats{RESET}                        history and patterns

{DIM}Data: ~/.morning_data.json{RESET}
""")
    else:
        print(f"{RED}Unknown command: {args.command}{RESET}  {DIM}Try: morning help{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
