/* Screen 1 — Call list. spec §3.1 */
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { ScoreBadge } from '../components/ScoreBadge'
import type { CallSummary } from '../types'
import { DIMENSION_LABELS } from '../types'

const SCENARIO_COLOURS: Record<string, string> = {
  excellent: '#065F46',
  weak: 'var(--red)',
  family_caller: '#1C7293',
  urgency: '#92400E',
  objection_heavy: '#6B21A8',
}

function fmtDuration(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}m ${String(s).padStart(2, '0')}s`
}

function ScenarioBadge({ type }: { type: string | null }) {
  if (!type) return null
  const label = type.replace(/_/g, ' ')
  const color = SCENARIO_COLOURS[type] ?? 'var(--muted)'
  return (
    <span
      style={{
        fontFamily: "'IBM Plex Mono', monospace",
        fontSize: '11px',
        color,
        background: 'var(--surface-2)',
        border: `1px solid var(--border)`,
        borderRadius: 'var(--radius-sm)',
        padding: '2px 8px',
        textTransform: 'capitalize',
        whiteSpace: 'nowrap',
      }}
    >
      {label}
    </span>
  )
}

const FILTERS = ['All', 'Excellent', 'Family-caller', 'Urgency', 'Weak', 'Compliance-failure']

export function CallList() {
  const [calls, setCalls] = useState<CallSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState('All')
  const navigate = useNavigate()

  useEffect(() => {
    api.calls
      .list()
      .then(setCalls)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const filtered = calls.filter((c) => {
    if (filter === 'All') return true
    if (filter === 'Compliance-failure') return c.has_compliance_flags
    if (filter === 'Excellent') return c.scenario_type === 'excellent'
    if (filter === 'Family-caller') return c.scenario_type === 'family_caller'
    if (filter === 'Urgency') return c.scenario_type === 'urgency'
    if (filter === 'Weak') return c.scenario_type === 'weak'
    return true
  })

  const needAttention = calls.filter((c) => c.overall_score < 70).length
  const onTrack = calls.length - needAttention

  return (
    <div style={{ padding: '32px 24px', maxWidth: '1280px', margin: '0 auto' }}>
      {/* Page header */}
      <div style={{ marginBottom: '28px' }}>
        <div
          style={{
            fontFamily: "'IBM Plex Mono', monospace",
            fontSize: '11px',
            color: 'var(--teal-500)',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            marginBottom: '8px',
          }}
        >
          PHASE A TRIAL
        </div>
        <h1
          style={{
            fontFamily: "'Fraunces', serif",
            fontWeight: 500,
            fontSize: '36px',
            color: 'var(--ink)',
            margin: '0 0 6px',
            lineHeight: 1.2,
          }}
        >
          {calls.length} calls scored,{' '}
          <em style={{ fontStyle: 'italic', fontWeight: 300 }}>ready for review</em>
        </h1>
        {!loading && (
          <p
            style={{
              fontFamily: "'IBM Plex Sans', sans-serif",
              fontSize: '14px',
              color: 'var(--muted)',
              margin: 0,
            }}
          >
            {needAttention} need attention · {onTrack} on track
          </p>
        )}
      </div>

      {/* Filter chips */}
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '20px' }}>
        {FILTERS.map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{
              fontFamily: "'IBM Plex Sans', sans-serif",
              fontSize: '13px',
              fontWeight: filter === f ? 600 : 400,
              padding: '6px 14px',
              borderRadius: '999px',
              border: `1px solid ${filter === f ? 'var(--navy-700)' : 'var(--border)'}`,
              background: filter === f ? 'var(--navy-900)' : 'var(--white)',
              color: filter === f ? 'var(--white)' : 'var(--text)',
              cursor: 'pointer',
              transition: 'all 0.12s',
            }}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Table */}
      {loading && (
        <p style={{ color: 'var(--muted)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
          Loading calls…
        </p>
      )}
      {error && (
        <p style={{ color: 'var(--red)', fontFamily: "'IBM Plex Sans', sans-serif" }}>
          {error}
        </p>
      )}
      {!loading && !error && (
        <div
          style={{
            background: 'var(--white)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-lg)',
            boxShadow: 'var(--shadow-sm)',
            overflow: 'hidden',
          }}
        >
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr
                style={{
                  background: 'var(--surface-2)',
                  borderBottom: '1px solid var(--border-strong)',
                }}
              >
                {['Call ID', 'Scenario', 'Agent', 'Duration', 'Score', 'Worst Dimension', 'Status', 'Flags'].map(
                  (col) => (
                    <th
                      key={col}
                      style={{
                        fontFamily: "'IBM Plex Mono', monospace",
                        fontSize: '11px',
                        color: 'var(--muted)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.06em',
                        fontWeight: 500,
                        padding: '10px 16px',
                        textAlign: 'left',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {col}
                    </th>
                  )
                )}
              </tr>
            </thead>
            <tbody>
              {filtered.map((call, i) => (
                <tr
                  key={call.call_id}
                  onClick={() => navigate(`/calls/${call.call_id}`)}
                  style={{
                    borderBottom:
                      i < filtered.length - 1 ? '1px solid var(--border)' : 'none',
                    cursor: 'pointer',
                    transition: 'background 0.1s',
                  }}
                  onMouseEnter={(e) =>
                    ((e.currentTarget as HTMLElement).style.background = 'var(--surface)')
                  }
                  onMouseLeave={(e) =>
                    ((e.currentTarget as HTMLElement).style.background = 'transparent')
                  }
                >
                  <td style={{ padding: '14px 16px' }}>
                    <span
                      style={{
                        fontFamily: "'IBM Plex Mono', monospace",
                        fontSize: '13px',
                        color: 'var(--navy-700)',
                        fontWeight: 500,
                      }}
                    >
                      {call.call_id}
                    </span>
                  </td>
                  <td style={{ padding: '14px 16px' }}>
                    <ScenarioBadge type={call.scenario_type} />
                  </td>
                  <td
                    style={{
                      padding: '14px 16px',
                      fontFamily: "'IBM Plex Sans', sans-serif",
                      fontSize: '14px',
                      color: 'var(--text)',
                    }}
                  >
                    {call.agent_id}
                  </td>
                  <td
                    style={{
                      padding: '14px 16px',
                      fontFamily: "'IBM Plex Mono', monospace",
                      fontSize: '13px',
                      color: 'var(--muted)',
                    }}
                  >
                    {fmtDuration(call.duration_seconds)}
                  </td>
                  <td style={{ padding: '14px 16px' }}>
                    <ScoreBadge score={call.overall_score} size="sm" />
                  </td>
                  <td
                    style={{
                      padding: '14px 16px',
                      fontFamily: "'IBM Plex Sans', sans-serif",
                      fontSize: '13px',
                      color: 'var(--muted)',
                    }}
                  >
                    {call.worst_dimension
                      ? DIMENSION_LABELS[call.worst_dimension] ?? call.worst_dimension
                      : '—'}
                  </td>
                  <td style={{ padding: '14px 16px' }}>
                    <span
                      style={{
                        fontFamily: "'IBM Plex Sans', sans-serif",
                        fontSize: '12px',
                        color:
                          call.status === 'scored'
                            ? '#065F46'
                            : call.status === 'overridden'
                              ? '#92400E'
                              : 'var(--muted)',
                        background:
                          call.status === 'scored'
                            ? 'var(--green-soft)'
                            : call.status === 'overridden'
                              ? 'var(--amber-soft)'
                              : 'var(--surface-2)',
                        borderRadius: 'var(--radius-sm)',
                        padding: '2px 8px',
                        textTransform: 'capitalize',
                      }}
                    >
                      {call.status}
                    </span>
                  </td>
                  <td style={{ padding: '14px 16px', textAlign: 'center' }}>
                    {call.has_compliance_flags && (
                      <span
                        title="Compliance flag"
                        style={{ color: 'var(--red)', fontSize: '16px' }}
                      >
                        ⚠
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filtered.length === 0 && (
            <p
              style={{
                textAlign: 'center',
                color: 'var(--muted)',
                padding: '32px',
                fontFamily: "'IBM Plex Sans', sans-serif",
              }}
            >
              No calls match this filter.
            </p>
          )}
        </div>
      )}
    </div>
  )
}
