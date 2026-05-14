/* Evidence modal — spec §3.3 */
import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { EvidenceAnchorRow, EvidenceResponse } from '../types'
import { DIMENSION_LABELS } from '../types'
import { DimScoreBadge } from './ScoreBadge'

interface Props {
  callId: string
  dimension: string
  onClose: () => void
}

function fmtTimestamp(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${String(s).padStart(2, '0')}`
}

function SnippetCard({ anchor }: { anchor: EvidenceAnchorRow }) {
  return (
    <div
      style={{
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-md)',
        padding: '14px 16px',
        marginBottom: '10px',
      }}
    >
      <div
        style={{
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: '11px',
          color: 'var(--muted)',
          textTransform: 'uppercase',
          letterSpacing: '0.06em',
          marginBottom: '8px',
        }}
      >
        {anchor.speaker.toUpperCase()} · {fmtTimestamp(anchor.timestamp_seconds)} · Turn {anchor.turn_number}
      </div>
      <p
        style={{
          fontFamily: "'IBM Plex Sans', sans-serif",
          fontSize: '14px',
          color: 'var(--text)',
          lineHeight: '1.6',
          margin: 0,
          borderLeft: '3px solid var(--amber)',
          paddingLeft: '12px',
        }}
      >
        "{anchor.text_snippet}"
      </p>
    </div>
  )
}

export function EvidenceModal({ callId, dimension, onClose }: Props) {
  const [data, setData] = useState<EvidenceResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    api.calls
      .evidence(callId, dimension)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [callId, dimension])

  const label = DIMENSION_LABELS[dimension] ?? dimension

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(10,31,61,0.5)',
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
      }}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        style={{
          background: 'var(--white)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-md)',
          width: '100%',
          maxWidth: '640px',
          maxHeight: '80vh',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: '20px 24px 16px',
            borderBottom: '1px solid var(--border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '12px',
            position: 'sticky',
            top: 0,
            background: 'var(--white)',
            zIndex: 1,
          }}
        >
          <div>
            <div
              style={{
                fontFamily: "'IBM Plex Mono', monospace",
                fontSize: '10px',
                color: 'var(--teal-500)',
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                marginBottom: '4px',
              }}
            >
              TRANSCRIPT EVIDENCE
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span
                style={{
                  fontFamily: "'Fraunces', serif",
                  fontWeight: 500,
                  fontSize: '18px',
                  color: 'var(--ink)',
                }}
              >
                {label}
              </span>
              {data?.dim_score && <DimScoreBadge score={data.dim_score.raw_score} />}
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--muted)',
              fontSize: '16px',
              width: '32px',
              height: '32px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: '20px 24px' }}>
          {loading && (
            <p style={{ color: 'var(--muted)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
              Loading evidence…
            </p>
          )}
          {error && (
            <p style={{ color: 'var(--red)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
              {error}
            </p>
          )}
          {data && !loading && (
            <>
              {/* Evidence snippets */}
              <div
                style={{
                  fontFamily: "'IBM Plex Mono', monospace",
                  fontSize: '11px',
                  color: 'var(--muted)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.06em',
                  marginBottom: '12px',
                }}
              >
                TRANSCRIPT EVIDENCE — {data.anchors.length} of {data.anchors.length} snippets
              </div>
              {data.anchors.map((a, i) => (
                <SnippetCard key={i} anchor={a} />
              ))}

              {/* Coaching note */}
              {data.dim_score?.coaching_note && (
                <div style={{ marginTop: '20px' }}>
                  <div
                    style={{
                      fontFamily: "'IBM Plex Mono', monospace",
                      fontSize: '11px',
                      color: 'var(--muted)',
                      textTransform: 'uppercase',
                      letterSpacing: '0.06em',
                      marginBottom: '10px',
                    }}
                  >
                    COACHING NOTE
                  </div>
                  <p
                    style={{
                      fontFamily: "'IBM Plex Sans', sans-serif",
                      fontSize: '14px',
                      color: 'var(--text)',
                      lineHeight: '1.6',
                      margin: 0,
                    }}
                  >
                    {data.dim_score.coaching_note}
                  </p>
                </div>
              )}

              {/* AI rationale */}
              {data.dim_score?.ai_rationale && (
                <div style={{ marginTop: '20px' }}>
                  <div
                    style={{
                      fontFamily: "'IBM Plex Mono', monospace",
                      fontSize: '11px',
                      color: 'var(--muted)',
                      textTransform: 'uppercase',
                      letterSpacing: '0.06em',
                      marginBottom: '10px',
                    }}
                  >
                    AI RATIONALE
                  </div>
                  <p
                    style={{
                      fontFamily: "'IBM Plex Sans', sans-serif",
                      fontSize: '13px',
                      color: 'var(--muted)',
                      lineHeight: '1.6',
                      margin: 0,
                    }}
                  >
                    {data.dim_score.ai_rationale}
                  </p>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div
          style={{
            padding: '14px 24px',
            borderTop: '1px solid var(--border)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <span
            style={{
              fontFamily: "'IBM Plex Mono', monospace",
              fontSize: '11px',
              color: 'var(--faint)',
            }}
          >
            Sources: CTM transcript · rubric-v1 · prompt-v1
          </span>
          <button
            onClick={onClose}
            style={{
              background: 'var(--navy-900)',
              color: 'var(--white)',
              border: 'none',
              borderRadius: 'var(--radius-sm)',
              fontFamily: "'IBM Plex Sans', sans-serif",
              fontSize: '13px',
              fontWeight: 500,
              padding: '7px 16px',
              cursor: 'pointer',
            }}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
