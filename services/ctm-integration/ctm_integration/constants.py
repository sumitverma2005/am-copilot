"""Shared constants for CTM integration.

CHANNEL_TO_ROLE is the single source of truth for the channel→speaker mapping
observed in CTM's transcription.json outline[] array.

PHASE B VERIFICATION REQUIRED: Confirm this mapping holds on real treatment-center
call data before going live. CTM channel assignments may vary by account configuration.
This constant is intentionally isolated here so both the stub client and the
normalizer stay in sync and the mapping can be updated in one place.
"""

CHANNEL_TO_ROLE: dict[int, str] = {
    2: "agent",   # channel 2 = agent side (confirmed from real CTM example)
    1: "caller",  # channel 1 = caller side (confirmed from real CTM example)
}
