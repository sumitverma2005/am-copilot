"""JSON-file state store for Phase A.

Persists queue actions (mark coached / mark reviewed) and score overrides.
Phase B: replace _read/_write with DB calls — public API is unchanged.
"""
from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_STATE_DIR = Path(__file__).parents[3] / "data" / "state"
_QUEUE_FILE = _STATE_DIR / "queue_state.json"
_OVERRIDES_FILE = _STATE_DIR / "overrides.json"
_lock = threading.Lock()


def _read(path: Path) -> Any:
    if not path.exists():
        return {} if path == _QUEUE_FILE else []
    return json.loads(path.read_text())


def _write(path: Path, data: Any) -> None:
    _STATE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


# ── Coaching queue ─────────────────────────────────────────────────────────────

def get_coached() -> dict:
    with _lock:
        return _read(_QUEUE_FILE).get("coached", {})


def mark_coached(call_id: str) -> None:
    with _lock:
        state = _read(_QUEUE_FILE)
        state.setdefault("coached", {})[call_id] = {
            "at": datetime.now(timezone.utc).isoformat(),
            "by": "demo",
        }
        _write(_QUEUE_FILE, state)


# ── Compliance queue ───────────────────────────────────────────────────────────

def get_reviewed() -> dict:
    with _lock:
        return _read(_QUEUE_FILE).get("reviewed", {})


def mark_reviewed(call_id: str, comment: str) -> None:
    with _lock:
        state = _read(_QUEUE_FILE)
        state.setdefault("reviewed", {})[call_id] = {
            "at": datetime.now(timezone.utc).isoformat(),
            "by": "demo",
            "comment": comment,
        }
        _write(_QUEUE_FILE, state)


# ── Coaching notes (per-call manager text) ────────────────────────────────────

def get_note(call_id: str) -> str | None:
    with _lock:
        return _read(_QUEUE_FILE).get("notes", {}).get(call_id)


def save_note(call_id: str, text: str) -> None:
    with _lock:
        state = _read(_QUEUE_FILE)
        state.setdefault("notes", {})[call_id] = text
        _write(_QUEUE_FILE, state)


# ── Overrides / disagreement log ───────────────────────────────────────────────

def get_overrides() -> list[dict]:
    with _lock:
        return _read(_OVERRIDES_FILE)


def add_override(override: dict) -> None:
    with _lock:
        overrides = _read(_OVERRIDES_FILE)
        overrides.append(override)
        _write(_OVERRIDES_FILE, overrides)
