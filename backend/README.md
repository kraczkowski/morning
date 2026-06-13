# backend/

FastAPI + DB. History archive + stats API. See ../DESIGN.md.

## Status: Phase 2 — not started

Deliberately empty until the phone app (Phase 1) exists. Building the server before the
core would be infra-before-product. When we start: Python venv, FastAPI, pytest, ruff;
ports the streak/hit logic from ../cli/morning.py over the append-only event log.
