# ctm-integration

CTM API client, webhook normalizer, and transcript fetcher.

---

## Confirmed CTM data model (resolved D3)

CTM splits call data across **two endpoints**. The Day 2 open question is closed.

---

### Endpoint 1 — Call metadata

```
GET /api/v1/accounts/{account_id}/calls/{id}
```

Returns metadata only. **No transcript.** Confirmed fields:

| Field | Notes |
|---|---|
| `id`, `sid`, `account_id` | Identifiers |
| `duration`, `talk_time`, `ring_time`, `hold_time` | Timing (seconds) |
| `direction` | `"inbound"` or `"outbound"` |
| `caller_number`, `tracking_number`, `contact_number` | Phone numbers |
| `called_at`, `unix_time` | Call timestamp |
| `dial_status`, `call_status`, `status` | Status fields |
| `source` | CTM tracking source |
| `agent` | `{name, email, id}` object |
| `agent_id` | Agent identifier |
| `notes`, `tag_list` | Freeform metadata |
| `audio` | Recording URL — **NEVER fetch or store this** |
| `legs[]` | Call leg details |

---

### Endpoint 2 — Transcript

```
GET /api/v1/accounts/{account_id}/calls/{id}/transcription.json
```

Returns the transcript in three forms. Confirmed real response shape:

```json
{
  "callid": 12376,
  "versions": [48309386],
  "text": "Test User: How may I help you?\nTest Client: Thank you so much...",
  "sentiment": 2,
  "outline": [
    {
      "vendor": "g",
      "speaker": "Test User",
      "gender": "U",
      "text": "How may I help you?",
      "offset": 0,
      "channel": 2,
      "s": 0,
      "e": 2.5,
      "start_fmt": "00:00:00",
      "end_fmt": "00:00:02.50",
      "confidence": 0.817,
      "words": [["How", 0.91, 0, 0.1], "..."]
    }
  ]
}
```

---

## Normalizer rules (locked)

### Use `outline`, not `text`

The `text` field is a flat blob. The `outline` array is turn-by-turn diarized.
The normalizer reads `outline[]` exclusively.

### Speaker mapping — use `channel`, not `speaker`

The `speaker` field ("Test User", "Test Client") is generic and unreliable.
The `channel` number is reliable:

```python
# Confirmed channel mapping for this account
CHANNEL_TO_ROLE = {
    2: "agent",   # answered / inbound agent side
    1: "caller",  # caller side
}
```

**Phase B verification required:** Confirm this `channel→role` mapping holds on
real treatment-center call data before going live. It may vary by CTM account
configuration. This constant is intentionally isolated and easy to update.

### Fields to DROP in the normalizer

| Field | Reason |
|---|---|
| `audio` | Recording URL — never store |
| `words` | Word-level timing — not needed for scoring |
| `vendor` | Not needed |
| `gender` | Not needed |
| `text` (top-level blob) | Use `outline` instead |

### Fields to KEEP

| Field | Internal name | Notes |
|---|---|---|
| `outline[].channel` | mapped to `speaker` | Via `CHANNEL_TO_ROLE` |
| `outline[].text` | `text` | Turn text |
| `outline[].s` | `timestamp_seconds` | Start time in seconds |
| `outline[].confidence` | `confidence` | Optional — low confidence matters for scoring quality review |
| `sentiment` (top-level) | `ctm_sentiment` | Reference metadata only — scoring engine does NOT use this as input |

---

## Internal normalized format

All downstream services (scoring engine, compliance engine, evidence engine)
consume this format exclusively:

```python
{
    "call_id": str,
    "called_at": str,              # ISO-8601
    "duration": int,               # seconds
    "agent_id": str,
    "agent_name": str,
    "ctm_sentiment": int | None,   # CTM's score, reference only
    "transcript": [
        {
            "turn": int,           # sequential, 1-indexed
            "speaker": str,        # "agent" or "caller"
            "timestamp_seconds": float,
            "text": str,
            "confidence": float | None
        }
    ]
}
```

The synthetic transcripts (Phase A) are already in this format.
The scoring engine has no awareness of raw CTM format and must stay that way.
If CTM's format changes post-Phase A, only `normalizer.py` needs updating.

---

## CTM client interface

```python
class CTMClient:
    def get_call_metadata(self, call_id: str) -> dict: ...
    def get_call_transcript(self, call_id: str) -> dict: ...
```

Two methods — one per endpoint. The stub client (`CTM_MODE=stub`) simulates
both from the synthetic JSON files, splitting the bundled data to match the
real CTM contract exactly.

---

## Webhook events

| Event | Trigger | Action |
|---|---|---|
| `call_complete` | Call ends | Fetch metadata + transcript, normalize, enqueue |
| `transcript_ready` | Transcription done async | Re-fetch transcript if not present, re-enqueue |

Both events flow: fetch metadata → fetch transcript → normalize → push to SQS.
