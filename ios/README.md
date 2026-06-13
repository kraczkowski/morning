# ios/

SwiftUI + AlarmKit app. iOS 26+. The source of truth (see ../DESIGN.md).

## Status: Phase 0 — validating the math gate

Before building the real app, prove the make-or-break unknown in the **Simulator** (free,
no entitlement needed): can alarm dismissal be blocked behind solving a math problem,
or is the system Stop button always one tap away?

The Xcode project is created in Xcode (Claude can't run Xcode). Claude writes Swift;
you build and report results.

## Phase 0 checklist

- [ ] Confirm Mac has Xcode 26+ and an iOS 26 Simulator.
- [ ] New SwiftUI app project here in `ios/`.
- [ ] Add `NSAlarmKitUsageDescription` to Info.plist.
- [ ] Schedule a near-future AlarmKit alarm.
- [ ] Attempt to gate dismissal behind a math challenge.
- [ ] Record the verdict in ../DESIGN.md (gate works / doesn't / partial).
