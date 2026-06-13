# morning — system design

The reference for *why* this is built the way it is. Read before changing architecture.

## Goal

A native iPhone alarm you can't dismiss until you solve a math problem, backed by an
accountability layer (streak, hit rate) you can review on a bigger screen.

## The unlock

iOS 26's **AlarmKit** lets a third-party app create a real system alarm that rings
through Silent mode and Focus, shows on Lock Screen / Dynamic Island, and survives
restarts. This is what makes the idea possible. Cost: the `com.apple.developer.alarmkit`
entitlement requires the paid ($99/yr) Apple Developer Program; a free Personal Team
can't use it. The Simulator runs AlarmKit without the entitlement (good for Phase 0).

## Principle that decides everything: offline-first, phone is the source of truth

The alarm must ring at 06:30 even if the server is down or wifi is off. So the network
is **never** in the critical path.

- The **phone owns the truth.** Schedules alarms locally (AlarmKit), records what
  happened, works 100% offline.
- The **backend is a sync target + analytics engine**, never required for the alarm to
  work. It can be down for a week and you only lose the dashboard, not the alarm or streak.

## Components

| Component | Tech | Role |
|---|---|---|
| `ios/` | SwiftUI + AlarmKit, iOS 26+ | Source of truth. Alarm, math gate, local event log. |
| `backend/` | Python FastAPI + DB | History archive + stats API. Lives on the Arch box later. |
| `dashboard/` | web (static) | Read-only big-screen view of streaks/trends. |
| `cli/` | Python (existing) | Original wake-up CLI. Its logic seeds the backend. |

## Data model: append-only event log

Do not store derived state ("streak = 7"). Store raw events; derive stats by folding.

```
Event {
  id:        UUID        # generated on the phone
  type:      TARGET_SET | ALARM_FIRED | CHALLENGE_SOLVED | CHECKED_IN
  timestamp: UTC + local offset
  payload:   { targetTime, actualWakeTime, intention, snoozeCount, ... }
}
```

- Streak, hit-rate, avg wake time are **computed**, never stored -> no field to desync.
- Events are immutable -> sync is trivial and idempotent (dedupe by `id`).
- The CLI's streak/hit logic is exactly this fold; it ports to the backend in Phase 2.

## Sync

- Phone POSTs events the server hasn't acked; keeps a `lastSynced` marker.
- Server dedupes by `id` (idempotent). Offline events queue and flush later.
- Only the phone writes events -> **no conflicts to resolve.**

## Failure modes (for an alarm app, this *is* the product)

| Breaks | Must happen |
|---|---|
| Server down at 06:30 | Alarm rings anyway (local schedule). Zero impact. |
| No network at check-in | Log locally, sync later. Never block a groggy user. |
| Phone reboots overnight | AlarmKit survives restarts. |
| App deleted / phone lost | Backend is the backup; reinstall re-pulls history. |
| Duplicate check-in | UUID idempotency drops it. |
| Timezone / DST | Store UTC + offset; define the "day" boundary in local time. |

## Auth

Single user. Phone holds a secret bearer token; backend checks it. No OAuth until/unless
multi-user. The event log already has a slot to grow a `userId` into.

## Scope discipline (what NOT to build)

One FastAPI service, one SQLite file (Postgres only if it grows), one static dashboard.
No microservices, queues, realtime, or container orchestration. This scales to thousands
of your own mornings on a Raspberry Pi.

## Build order — by risk, not by diagram

- **Phase 0** — validate the math-gate dismissal in AlarmKit (free, in the Simulator).
- **Phase 1** — SwiftUI + AlarmKit app: alarm + gate, data stored locally. Usable solo.
- **Phase 2** — FastAPI backend (ports the CLI logic) + DB; phone posts events.
- **Phase 3** — web dashboard reading the API.
