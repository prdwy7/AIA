# kiosk — channel-adapter-kiosk (S1)

> **Flutter app skeleton** — built in Phase 1 (MVP: touch + text + print, basic
> voice) → extended Phases 2, 4, 5 (camera, cross-correction UX, media sets).
> Full spec: `docs/02-modules.md` §S1.

## Purpose

The farmer-facing kiosk application.

## Responsibilities

- Voice capture (mic array → 16 kHz WAV).
- Touch guided flow (pickers, quick replies, confirmation gates).
- Text input (Telugu script + Latin keyboard).
- Camera capture with framing guidance.
- TTS playback.
- Print UI.
- Session lifecycle (start / timeout / reset).
- Offline queue visibility.

## Tech

Flutter 3.x (Linux target), kiosk mode (auto-start, no desktop escape). Plugins:
`camera`, `record` (audio), `esc_pos_printer`, `usb_serial`, `local_auth`
(operator PIN). All intelligence calls go to the **local core-api over
localhost**.

## Interfaces

core-api (localhost HTTP), thermal printer (USB/serial ESC/POS), device-agent
(health queries), hardware sensors (temperature, UPS).

## Dependencies

S4 (input-orchestrator), S5 (speech-service, TTS playback), S12
(prescription-service, print), S20 (device-agent).

## Scaling

One instance per device; no horizontal scaling — reliability engineering instead
(watchdog auto-restart, session resume, print idempotency).

## Key invariants

- **Every touch action is a typed `Input` node** with `modality=touch`,
  `confidence=1.0`.
- **No dead ends** — every screen offers "talk to an expert", "print what I
  have", "start over".
- **Do-not-repeat memory** enforced in the UI.
- Consent gate before any case begins (DPDP); pseudonymous `farmer_ref`, never a
  name.

## Layout

```
lib/
  main.dart                        # entrypoint → runApp(AiKioskApp)
  app.dart                         # HomeScreen: 5 modality buttons + consent gate
  core/session.dart                # Session.start() (consent-gated), reset()
  core/case_model.dart             # InputNode / CaseNode / CaseView mirrors
  widgets/no_dead_end_actions.dart # shared "talk to expert / print / start over"
  features/voice/                  # 🎤 voice capture screen
  features/touch/                  # 👆 crop picker (8 Kurnool crops)
  features/text/                   # ⌨️ text input screen
  features/picture/                # 📷 camera capture screen
  features/print/                  # 🖨️ print screen
```

## Run (dev)

```bash
cd kiosk
flutter pub get
flutter run -d linux    # kiosk target; or `make kiosk-build` for a release build
```
