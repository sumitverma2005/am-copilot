/* Screen 5 — Compliance queue. spec §3.5. */
import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { SkeletonTable } from '../components/Skeleton'
import type { ComplianceQueueRow } from '../types'

function fmtTimestamp(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${String(s).padStart(2, '0')}`
}

const FLAG_LABELS: Record<string, string> = {
  DIAG_CLAIM: 'Diagnostic Claim',
  OUTCOME_GUARANTEE: 'Outcome Guarantee',
  CLINICAL_SCOPE: 'Clinical Scope',
}

const FLAG_COLOR: Record<string, string> = {
  DIAG_CLAIM: '#92400E',
  OUTCOME_GUARANTEE: '#7C3AED',
  CLINICAL_SCOPE: 'var(--red)',
}

function ReviewModal({
  callId,
  onClose,
  onSave,
}: {
  callId: string
  onClose: () => void
  onSave: (comment: string) => Promise<void>
}) {
  const [comment, setComment] = useState('')
  const [saving, setSaving] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const areaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => areaRef.current?.focus(), [])

  async function handleSubmit() {
    if (!comment.trim()) { setErr('Comment is required.'); return }
    setSaving(true)
    try {
      await onSave(comment.trim())
      onClose()
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : 'Error saving')
      setSaving(false)
    }
  }

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.45)',
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        style={{
          background: 'var(--white)',
          borderRadius: 'var(--radius-lg)',
          width: '480px',
          maxWidth: '90vw',
          padding: '24px',
          boxShadow: '0 20px 60px rgba(0,0,0,0.25)',
        }}
      >
        <div
          style={{
            fontFamily: "'IBM Plex Sans', sans-serif",
            fontWeight: 600,
            fontSize: '16px',
            color: 'var(--ink)',
            marginBottom: '8px',
          }}
        >
          Mark as reviewed
        </div>
        <div
          style={{
            fontFamily: "'IBM Plex Sans', sans-serif",
            fontSize: '13px',
            color: 'var(--muted)',
            marginBottom: '16px',
          }}
        >
          {callId} — add a review comment before closing this flag.
        </div>

        <textarea
          ref={areaRef}
          value={comment}
          onChange={(e) => { setComment(e.target.value); setErr(null) }}
          placeholder="Describe the action taken or context…"
          rows={4}
          style={{
            width: '100%',
            fontFamily: "'IBM Plex Sans', sans-serif",
            fontSize: '14px',
            color: 'var(--ink)',
            border: err ? '1px solid var(--red)' : '1px solid var(--border-strong)',
            borderRadius: 'var(--radius-md)',
            padding: '10px 12px',
            resize: 'vertical',
            outline: 'none',
            boxSizing: 'border-box',
            background: 'var(--surface)',
          }}
        />
        {err && (
          <div style={{ fontFamily: "'IBM Plex Sans'", fontSize: '12px', color: 'var(--red)', marginTop: '4px' }}>
            {err}
          </div>
        )}

        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '16px' }}>
          <button
            onClick={onClose}
            style={{
              fontFamily: "'IBM Plex Sans', sans-serif",
              fontSize: '13px',
              background: 'transparent',
              border: '1px solid var(--border-strong)',
              borderRadius: 'var(--radius-sm)',
              padding: '8px 16px',
              cursor: 'pointer',
              color: 'var(--text)',
            }}
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={saving}
            style={{
              fontFamily: "'IBM Plex Sans', sans-serif",
              fontSize: '13px',
              fontWeight: 500,
              background: 'var(--teal-500)',
              border: 'none',
              borderRadius: 'var(--radius-sm)',
              padding: '8px 16px',
              cursor: saving ? 'wait' : 'pointer',
              color: 'var(--white)',
              opacity: saving ? 0.7 : 1,
            }}
          >
            {saving ? 'Saving…' : 'Save review'}
          </button>
        </div>
      </div>
    </div>
  )
}

const COL = '120px 140px 140px 1fr 80px 140px'

export function ComplianceQueue() {
  const navigate = useNavigate()
  const [rows, setRows] = useState<ComplianceQueueRow[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [reviewTarget, setReviewTarget] = useState<string | null>(null)

  function load() {
    setLoading(true)
    api.queue
      .compliance()
      .then(setRows)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  async function handleReview(callId: string, comment: string) {
    await api.queue.markReviewed(callId, comment)
    load()
  }

  return (
    <div style={{ padding: '32px 24px', maxWidth: '1280px', margin: '0 auto' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1
          style={{
            fontFamily: "'IBM Plex Sans', sans-serif",
            fontWeight: 600,
            fontSize: '20px',
            color: 'var(--ink)',
            margin: 0,
          }}
        >
          Compliance Queue
        </h1>
        <p
          style={{
            fontFamily: "'IBM Plex Sans', sans-serif",
            fontSize: '13px',
            color: 'var(--muted)',
            marginTop: '4px',
            marginBottom: 0,
          }}
        >
          Calls with compliance flags — most recent first.
        </p>
      </div>

      {error && (
        <div
          style={{
            background: 'var(--red-soft)',
            border: '1px solid var(--red)',
            borderRadius: 'var(--radius-md)',
            padding: '12px 16px',
            marginBottom: '20px',
            color: 'var(--red)',
            fontFamily: "'IBM Plex Sans', sans-serif",
            fontSize: '14px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          {error}
          <button
            onClick={() => { setError(null); load() }}
            style={{ background: 'none', border: 'none', color: 'var(--red)', cursor: 'pointer', fontFamily: "'IBM Plex Sans'" }}
          >
            Retry
          </button>
        </div>
      )}

      {loading ? (
        <SkeletonTable rows={4} cols={6} />
      ) : rows.length === 0 ? (
        <div
          style={{
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-md)',
            padding: '48px 24px',
            textAlign: 'center',
            background: 'var(--white)',
          }}
        >
          <div
            style={{
              fontFamily: "'IBM Plex Sans', sans-serif",
              fontSize: '15px',
              color: 'var(--ink)',
              marginBottom: '8px',
            }}
          >
            No compliance flags
          </div>
          <div style={{ fontFamily: "'IBM Plex Sans'", fontSize: '13px', color: 'var(--muted)' }}>
            All scored calls passed compliance checks.
          </div>
        </div>
      ) : (
        <div
          style={{
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-md)',
            overflow: 'hidden',
            background: 'var(--white)',
          }}
        >
          {/* Table header */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: COL,
              padding: '10px 16px',
              background: 'var(--surface-2)',
              borderBottom: '1px solid var(--border-strong)',
            }}
          >
            {['Agent', 'Call', 'Flag Type', 'Flagged Phrase', 'Timestamp', ''].map((h) => (
              <span
                key={h}
                style={{
                  fontFamily: "'IBM Plex Mono', monospace",
                  fontSize: '10px',
                  color: 'var(--muted)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.06em',
                }}
              >
                {h}
              </span>
            ))}
          </div>

          {rows.map((row, i) => (
            <div
              key={`${row.call_id}-${row.turn_number}`}
              style={{
                display: 'grid',
                gridTemplateColumns: COL,
                padding: '14px 16px',
                borderBottom: i < rows.length - 1 ? '1px solid var(--border)' : 'none',
                alignItems: 'center',
                opacity: row.reviewed_at ? 0.5 : 1,
              }}
            >
              <span style={{ fontFamily: "'IBM Plex Sans'", fontSize: '14px', color: 'var(--text)', fontWeight: 500 }}>
                {row.agent_id}
              </span>

              <button
                onClick={() => navigate(`/calls/${row.call_id}`)}
                style={{ background: 'none', border: 'none', padding: 0, cursor: 'pointer', textAlign: 'left' }}
              >
                <div style={{ fontFamily: "'IBM Plex Mono'", fontSize: '12px', color: 'var(--teal-500)', textDecoration: 'underline' }}>
                  {row.call_id}
                </div>
                <div style={{ fontFamily: "'IBM Plex Sans'", fontSize: '11px', color: 'var(--muted)', marginTop: '2px' }}>
                  {new Date(row.call_timestamp).toLocaleDateString()}
                </div>
              </button>

              <span
                style={{
                  fontFamily: "'IBM Plex Mono', monospace",
                  fontSize: '11px',
                  color: FLAG_COLOR[row.flag_code] ?? 'var(--red)',
                  background: 'var(--red-soft)',
                  padding: '3px 8px',
                  borderRadius: 'var(--radius-sm)',
                  display: 'inline-block',
                }}
              >
                {FLAG_LABELS[row.flag_code] ?? row.flag_code}
              </span>

              <span
                title={row.matched_phrase}
                style={{
                  fontFamily: "'IBM Plex Sans', sans-serif",
                  fontSize: '13px',
                  color: 'var(--text)',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  paddingRight: '8px',
                }}
              >
                "{row.matched_phrase}"
              </span>

              <span
                style={{
                  fontFamily: "'IBM Plex Mono', monospace",
                  fontSize: '13px',
                  color: 'var(--muted)',
                }}
              >
                {fmtTimestamp(row.timestamp_seconds)}
              </span>

              <div>
                {row.reviewed_at ? (
                  <span
                    style={{
                      fontFamily: "'IBM Plex Mono', monospace",
                      fontSize: '11px',
                      color: '#065F46',
                      background: 'var(--green-soft)',
                      padding: '3px 8px',
                      borderRadius: 'var(--radius-sm)',
                    }}
                  >
                    Reviewed ✓
                  </span>
                ) : (
                  <button
                    onClick={() => setReviewTarget(row.call_id)}
                    style={{
                      fontFamily: "'IBM Plex Sans', sans-serif",
                      fontSize: '13px',
                      fontWeight: 500,
                      color: 'var(--white)',
                      background: 'var(--red)',
                      border: 'none',
                      borderRadius: 'var(--radius-sm)',
                      padding: '6px 14px',
                      cursor: 'pointer',
                    }}
                  >
                    Mark reviewed
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {reviewTarget && (
        <ReviewModal
          callId={reviewTarget}
          onClose={() => setReviewTarget(null)}
          onSave={(comment) => handleReview(reviewTarget, comment)}
        />
      )}
    </div>
  )
}
