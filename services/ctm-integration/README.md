# ctm-integration

CTM API client, webhook normalizer, and transcript fetcher.

---

## D5 prerequisite — verify CTM transcript response shape

**Before writing `normalizer.py` on Day 5, confirm which of the three scenarios below
applies to CTM's `GET /api/v1/calls/{id}` response. The normalizer design is different
for each.**

### What to do on D5

Run this against the CTM sandbox before writing any normalizer code:

```bash
curl -H "Authorization: Bearer $CTM_API_KEY" \
  "https://api.calltrackingmetrics.com/api/v1/calls/{any_recent_call_id}" \
  | jq '.transcript // .transcription // .text // "no transcript field found"'
```

---

### Scenario A — Turn-by-turn diarized (best case)

CTM returns structured speaker turns with labels and timestamps:

```json
{
  "transcript": [
    { "speaker": "agent", "start_time": 0.0, "end_time": 4.2, "text": "Thank you for calling..." },
    { "speaker": "caller", "start_time": 4.5, "end_time": 12.1, "text": "Hi, I'm not sure..." }
  ]
}
```

**Normalizer work:** Straightforward field mapping. Rename `start_time` →
`timestamp_seconds`, add sequential `turn` numbers, map speaker labels.
`normalizer.py` stays simple (~30 lines).

---

### Scenario B — Raw text blob (worst case)

CTM returns an unsegmented string with no speaker labels or timestamps:

```json
{
  "transcription": "Thank you for calling... Hi, I'm not sure..."
}
```

**Normalizer work:** Requires a diarization pass before normalization. Options:
1. AWS Transcribe with speaker identification (adds cost and latency per call)
2. Simple heuristic segmentation by pause length (lossy, unreliable)
3. Third-party diarization API

This scenario pushes the D5 timeline and must be flagged to the client immediately
if encountered. Plan 2 additional days for diarization infrastructure.

---

### Scenario C — Mixed / semi-structured (most likely)

CTM returns speaker-labeled text but without per-turn timestamps:

```json
{
  "transcript": [
    { "type": "agent", "text": "Thank you for calling..." },
    { "type": "caller", "text": "Hi, I'm not sure..." }
  ]
}
```

**Normalizer work:** Moderate. Speaker labels map cleanly; timestamps must be
estimated from cumulative word count using average speaking rate (~130 wpm).
Evidence anchors will have approximate timestamps (±5 seconds), which is
acceptable for Phase A scoring but should be noted in the evaluation record.

---

### Why this matters for `normalizer.py`

The scoring engine, compliance engine, and evidence engine all consume the
**internal normalized format**:

```python
{
    "turn": int,           # sequential, 1-indexed
    "speaker": str,        # "agent" or "caller"
    "timestamp_seconds": int,
    "text": str
}
```

The normalizer's job is to produce this format regardless of what CTM returns.
The synthetic transcripts (Phase A) are already in this format — so the scoring
engine has no awareness of raw CTM format, and it must stay that way.

If CTM's format changes post-Phase A, only `normalizer.py` needs updating.
