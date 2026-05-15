/* Screen 6 — Disagreement log. spec §3.6. */
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { DimScoreBadge } from '../components/ScoreBadge'
import { SkeletonTable } from '../components/Skeleton'
import type { DisagreementRow } from '../types'
import { DIMENSION_LABELS } from '../types'

const COL = '100px 160px 90px 90px 60px 1fr 90px 100px'

function DeltaBadge({ delta }: { delta: number | null }) {
  if (delta === null) return <span style={{ color: 'var(--muted)', fontFamily: "'IBM Plex Mono'" }}>—</span>
  const sign = delta > 0 ? '+' : ''
  const color = delta > 0 ? '#065F46' : delta < 0 ? 'var(--red)' : 'var(--muted)'
  const bg = delta > 0 ? 'var(--green-soft)' : delta < 0 ? 'var(--red-soft)' : 'var(--surface-2)'
  return (
    <span
      style={{
        fontFamily: "'IBM Plex Mono', monospace",
        fontSize: '12px',
        fontWeight: 600,
        color,
        background: bg,
        padding: '2px 8px',
        borderRadius: 'var(--radius-sm)',
      }}
    >
      {sign}{delta}
    </span>
  )
}

export function DisagreementLog() {
  const [rows, setRows] = useState<DisagreementRow[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  function load() {
    setLoading(true)
    api.disagreements
      .list()
      .then(setRows)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  return (
    <div style={{ padding: '32px 24px', maxWidth: '1280px', margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h1
            style={{
              fontFamily: "'IBM Plex Sans', sans-serif",
              fontWeight: 600,
              fontSize: '20px',
              color: 'var(--ink)',
              margin: 0,
            }}
          >
            Disagreement Log
          </h1>
          <p style={{ fontFamily: "'IBM Plex Sans'", fontSize: '13px', color: 'var(--muted)', marginTop: '4px', marginBottom: 0 }}>
            Score overrides submitted by managers.
          </p>
        </div>

        {/* Export button — spec §3.6 */}
        <a
          href={api.disagreements.exportUrl()}
          download="disagreements.csv"
          style={{
            fontFamily: "'IBM Plex Sans', sans-serif",
            fontSize: '13px',
            fontWeight: 500,
            color: 'var(--teal-500)',
            border: '1px solid var(--teal-500)',
            borderRadius: 'var(--radius-sm)',
            padding: '8px 16px',
            textDecoration: 'none',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
          }}
        >
          ↓ Export CSV
        </a>
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
        <SkeletonTable rows={4} cols={8} />
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
          <div style={{ fontFamily: "'IBM Plex Sans'", fontSize: '15px', color: 'var(--ink)', marginBottom: '8px' }}>
            No overrides yet
          </div>
          <div style={{ fontFamily: "'IBM Plex Sans'", fontSize: '13px', color: 'var(--muted)' }}>
            Manager score overrides will appear here. Open a call and use the override section to submit one.
          </div>
        </div>
      ) : (
        <div
          style={{
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-md)',
            overflow: 'auto',
            background: 'var(--white)',
          }}
        >
          {/* Header */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: COL,
              padding: '10px 16px',
              background: 'var(--surface-2)',
              borderBottom: '1px solid var(--border-strong)',
              minWidth: '900px',
            }}
          >
            {['Call ID', 'Dimension', 'AI Score', 'Mgr Score', 'Delta', 'Comment', 'Manager', 'Date'].map((h) => (
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
              key={i}
              style={{
                display: 'grid',
                gridTemplateColumns: COL,
                padding: '14px 16px',
                borderBottom: i < rows.length - 1 ? '1px solid var(--border)' : 'none',
                alignItems: 'center',
                minWidth: '900px',
              }}
            >
              <Link
                to={`/calls/${row.call_id}`}
                style={{
                  fontFamily: "'IBM Plex Mono', monospace",
                  fontSize: '12px',
                  color: 'var(--teal-500)',
                  textDecoration: 'underline',
                }}
              >
                {row.call_id}
              </Link>

              <span style={{ fontFamily: "'IBM Plex Sans'", fontSize: '13px', color: 'var(--text)' }}>
                {DIMENSION_LABELS[row.dimension] ?? row.dimension}
              </span>

              <DimScoreBadge score={row.ai_score} />
              <DimScoreBadge score={row.manager_score} />
              <DeltaBadge delta={row.delta} />

              <span
                title={row.comment}
                style={{
                  fontFamily: "'IBM Plex Sans'", fontSize: '13px', color: 'var(--text)',
                  overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', paddingRight: '8px',
                }}
              >
                {row.comment}
              </span>

              <span style={{ fontFamily: "'IBM Plex Sans'", fontSize: '13px', color: 'var(--muted)' }}>
                {row.manager}
              </span>

              <span style={{ fontFamily: "'IBM Plex Mono'", fontSize: '11px', color: 'var(--muted)' }}>
                {new Date(row.date).toLocaleDateString()}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
