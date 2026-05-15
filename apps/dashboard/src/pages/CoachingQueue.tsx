/* Screen 4 — Coaching queue. spec §3.4. */
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { DimScoreBadge, ScoreBadge } from '../components/ScoreBadge'
import { SkeletonTable } from '../components/Skeleton'
import type { CoachingQueueRow } from '../types'
import { DIMENSION_LABELS } from '../types'

function relativeDate(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const days = Math.floor(diff / 86_400_000)
  if (days === 0) return 'Today'
  if (days === 1) return 'Yesterday'
  return `${days}d ago`
}

const COL = '1fr 120px 110px 130px 110px 140px'

function TableHead() {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: COL,
        padding: '10px 16px',
        background: 'var(--surface-2)',
        borderBottom: '1px solid var(--border-strong)',
      }}
    >
      {['Agent', 'Call', 'Overall Score', 'Worst Dimension', 'In Queue Since', ''].map((h) => (
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
  )
}

export function CoachingQueue() {
  const navigate = useNavigate()
  const [rows, setRows] = useState<CoachingQueueRow[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState<string | null>(null)

  function load() {
    setLoading(true)
    api.queue
      .coaching()
      .then(setRows)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  async function handleCoach(callId: string) {
    setBusy(callId)
    try {
      await api.queue.markCoached(callId)
      load()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setBusy(null)
    }
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
          Coaching Queue
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
          Calls scoring below 70 — sorted lowest first.
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
            No calls in the coaching queue
          </div>
          <div
            style={{
              fontFamily: "'IBM Plex Sans', sans-serif",
              fontSize: '13px',
              color: 'var(--muted)',
            }}
          >
            All scored calls are at or above the 70-point threshold.
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
          <TableHead />
          {rows.map((row, i) => (
            <div
              key={`${row.call_id}-${i}`}
              style={{
                display: 'grid',
                gridTemplateColumns: COL,
                padding: '14px 16px',
                borderBottom: i < rows.length - 1 ? '1px solid var(--border)' : 'none',
                alignItems: 'center',
                opacity: row.coached_at ? 0.5 : 1,
              }}
            >
              <span
                style={{
                  fontFamily: "'IBM Plex Sans', sans-serif",
                  fontSize: '14px',
                  color: 'var(--text)',
                  fontWeight: 500,
                }}
              >
                {row.agent_id}
              </span>

              <button
                onClick={() => navigate(`/calls/${row.call_id}`)}
                style={{
                  background: 'none',
                  border: 'none',
                  padding: 0,
                  cursor: 'pointer',
                  textAlign: 'left',
                }}
              >
                <div
                  style={{
                    fontFamily: "'IBM Plex Mono', monospace",
                    fontSize: '12px',
                    color: 'var(--teal-500)',
                    textDecoration: 'underline',
                  }}
                >
                  {row.call_id}
                </div>
                <div
                  style={{
                    fontFamily: "'IBM Plex Sans', sans-serif",
                    fontSize: '11px',
                    color: 'var(--muted)',
                    marginTop: '2px',
                  }}
                >
                  {new Date(row.call_timestamp).toLocaleDateString()}
                </div>
              </button>

              <ScoreBadge score={row.overall_score} />

              <div>
                <div
                  style={{
                    fontFamily: "'IBM Plex Sans', sans-serif",
                    fontSize: '12px',
                    color: 'var(--text)',
                    marginBottom: '4px',
                  }}
                >
                  {row.worst_dimension ? (DIMENSION_LABELS[row.worst_dimension] ?? row.worst_dimension) : '—'}
                </div>
                {row.worst_dimension_score !== null && row.worst_dimension_score !== undefined && (
                  <DimScoreBadge score={row.worst_dimension_score} />
                )}
              </div>

              <span
                style={{
                  fontFamily: "'IBM Plex Sans', sans-serif",
                  fontSize: '13px',
                  color: 'var(--muted)',
                }}
              >
                {row.scored_at ? relativeDate(row.scored_at) : relativeDate(row.call_timestamp)}
              </span>

              <div>
                {row.coached_at ? (
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
                    Coached ✓
                  </span>
                ) : (
                  <button
                    onClick={() => handleCoach(row.call_id)}
                    disabled={busy === row.call_id}
                    style={{
                      fontFamily: "'IBM Plex Sans', sans-serif",
                      fontSize: '13px',
                      fontWeight: 500,
                      color: 'var(--white)',
                      background: 'var(--teal-500)',
                      border: 'none',
                      borderRadius: 'var(--radius-sm)',
                      padding: '6px 14px',
                      cursor: busy === row.call_id ? 'wait' : 'pointer',
                      opacity: busy === row.call_id ? 0.7 : 1,
                    }}
                  >
                    {busy === row.call_id ? 'Saving…' : 'Mark coached'}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
