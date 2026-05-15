/* Screen 2 — Call detail. spec §3.2. Includes radar chart (screen 3 spec §3.2 right col). */
import { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from 'recharts'
import { api } from '../api/client'
import { EvidenceModal } from '../components/EvidenceModal'
import { DimScoreBadge, ScoreBadge } from '../components/ScoreBadge'
import type { DimensionScoreRow, ScoreResult } from '../types'
import { DIMENSION_LABELS } from '../types'

const SCORE_OPTIONS = ['N/A', '0', '1', '2', '3', '4', '5']

function OverrideSection({ callId, dims }: { callId: string; dims: DimensionScoreRow[] }) {
  const [dimension, setDimension] = useState('')
  const [aiScore, setAiScore] = useState<string>('')
  const [managerScore, setManagerScore] = useState<string>('')
  const [comment, setComment] = useState('')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [err, setErr] = useState<string | null>(null)

  function parseScore(v: string): number | null {
    if (v === 'N/A' || v === '') return null
    return parseFloat(v)
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!dimension) { setErr('Select a dimension.'); return }
    if (!comment.trim()) { setErr('Comment is required.'); return }
    const selectedDim = dims.find((d) => d.dimension === dimension)
    setSaving(true)
    setErr(null)
    try {
      await api.calls.override(callId, {
        dimension,
        ai_score: aiScore !== '' ? parseScore(aiScore) : (selectedDim?.raw_score ?? null),
        manager_score: parseScore(managerScore),
        comment: comment.trim(),
      })
      setSaved(true)
      setDimension('')
      setAiScore('')
      setManagerScore('')
      setComment('')
      setTimeout(() => setSaved(false), 3000)
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : 'Error submitting override')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div
      style={{
        background: 'var(--white)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-md)',
        padding: '20px',
        marginBottom: '24px',
      }}
    >
      <div
        style={{
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: '10px',
          color: 'var(--muted)',
          textTransform: 'uppercase',
          letterSpacing: '0.06em',
          marginBottom: '14px',
        }}
      >
        SCORE OVERRIDE — Disagreement Log
      </div>

      {saved && (
        <div
          style={{
            background: 'var(--green-soft)',
            color: '#065F46',
            fontFamily: "'IBM Plex Sans'",
            fontSize: '13px',
            padding: '8px 12px',
            borderRadius: 'var(--radius-sm)',
            marginBottom: '12px',
          }}
        >
          Override saved — visible in the Disagreement Log.
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
          <div>
            <label style={labelStyle}>Dimension</label>
            <select
              value={dimension}
              onChange={(e) => { setDimension(e.target.value); setErr(null) }}
              style={selectStyle}
            >
              <option value="">Select…</option>
              {dims.filter((d) => !d.is_na).map((d) => (
                <option key={d.dimension} value={d.dimension}>
                  {DIMENSION_LABELS[d.dimension] ?? d.dimension}
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            <div>
              <label style={labelStyle}>AI Score</label>
              <select value={aiScore} onChange={(e) => setAiScore(e.target.value)} style={selectStyle}>
                <option value="">Auto</option>
                {SCORE_OPTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label style={labelStyle}>Manager Score</label>
              <select
                value={managerScore}
                onChange={(e) => { setManagerScore(e.target.value); setErr(null) }}
                style={selectStyle}
              >
                <option value="">Select…</option>
                {SCORE_OPTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          </div>
        </div>

        <div style={{ marginBottom: '12px' }}>
          <label style={labelStyle}>Comment (required)</label>
          <textarea
            value={comment}
            onChange={(e) => { setComment(e.target.value); setErr(null) }}
            placeholder="Explain the reason for the override…"
            rows={3}
            style={{
              ...selectStyle,
              resize: 'vertical',
              height: 'auto',
              fontFamily: "'IBM Plex Sans', sans-serif",
            }}
          />
        </div>

        {err && (
          <div style={{ fontFamily: "'IBM Plex Sans'", fontSize: '12px', color: 'var(--red)', marginBottom: '10px' }}>
            {err}
          </div>
        )}

        <button
          type="submit"
          disabled={saving}
          style={{
            fontFamily: "'IBM Plex Sans', sans-serif",
            fontSize: '13px',
            fontWeight: 500,
            background: 'var(--teal-500)',
            border: 'none',
            borderRadius: 'var(--radius-sm)',
            padding: '8px 18px',
            color: 'var(--white)',
            cursor: saving ? 'wait' : 'pointer',
            opacity: saving ? 0.7 : 1,
          }}
        >
          {saving ? 'Saving…' : 'Submit override'}
        </button>
      </form>
    </div>
  )
}

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontFamily: "'IBM Plex Mono', monospace",
  fontSize: '10px',
  color: 'var(--muted)',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  marginBottom: '6px',
}

const selectStyle: React.CSSProperties = {
  width: '100%',
  fontFamily: "'IBM Plex Sans', sans-serif",
  fontSize: '13px',
  color: 'var(--ink)',
  background: 'var(--surface)',
  border: '1px solid var(--border-strong)',
  borderRadius: 'var(--radius-sm)',
  padding: '8px 10px',
  outline: 'none',
  boxSizing: 'border-box',
}

function CoachingNotesSection({ callId }: { callId: string }) {
  const [text, setText] = useState('')
  const [loaded, setLoaded] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const prevRef = useRef('')

  useEffect(() => {
    api.calls.getNote(callId).then(({ text: t }) => {
      setText(t)
      prevRef.current = t
      setLoaded(true)
    }).catch(() => setLoaded(true))
  }, [callId])

  async function handleSave() {
    if (text === prevRef.current) return
    setSaving(true)
    setErr(null)
    try {
      await api.calls.saveNote(callId, text)
      prevRef.current = text
      setSaved(true)
      setTimeout(() => setSaved(false), 2500)
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : 'Error saving')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div
      style={{
        background: 'var(--white)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-md)',
        padding: '20px',
        marginBottom: '24px',
      }}
    >
      <div
        style={{
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: '10px',
          color: 'var(--muted)',
          textTransform: 'uppercase',
          letterSpacing: '0.06em',
          marginBottom: '14px',
        }}
      >
        COACHING NOTES
      </div>
      <textarea
        value={loaded ? text : ''}
        onChange={(e) => { setText(e.target.value); setSaved(false) }}
        placeholder={loaded ? 'Add coaching notes for this call…' : 'Loading…'}
        disabled={!loaded}
        rows={4}
        style={{
          width: '100%',
          fontFamily: "'IBM Plex Sans', sans-serif",
          fontSize: '14px',
          color: 'var(--ink)',
          background: 'var(--surface)',
          border: '1px solid var(--border-strong)',
          borderRadius: 'var(--radius-sm)',
          padding: '10px 12px',
          resize: 'vertical',
          outline: 'none',
          boxSizing: 'border-box',
          marginBottom: '12px',
        }}
      />
      {err && (
        <div style={{ fontFamily: "'IBM Plex Sans'", fontSize: '12px', color: 'var(--red)', marginBottom: '8px' }}>{err}</div>
      )}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button
          onClick={handleSave}
          disabled={saving || !loaded}
          style={{
            fontFamily: "'IBM Plex Sans', sans-serif",
            fontSize: '13px',
            fontWeight: 500,
            background: 'var(--teal-500)',
            border: 'none',
            borderRadius: 'var(--radius-sm)',
            padding: '8px 18px',
            color: 'var(--white)',
            cursor: saving ? 'wait' : 'pointer',
            opacity: saving ? 0.7 : 1,
          }}
        >
          {saving ? 'Saving…' : 'Save notes'}
        </button>
        {saved && (
          <span style={{ fontFamily: "'IBM Plex Sans'", fontSize: '13px', color: '#065F46' }}>Saved ✓</span>
        )}
      </div>
    </div>
  )
}

function fmtDuration(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}m ${String(s).padStart(2, '0')}s`
}

function fmtDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function AgentAvatar({ agentId }: { agentId: string }) {
  const initials = agentId.replace(/[^A-Z0-9]/gi, '').slice(0, 2).toUpperCase()
  return (
    <div
      style={{
        width: '40px',
        height: '40px',
        borderRadius: '50%',
        background: 'linear-gradient(135deg, var(--amber), var(--amber-soft))',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: "'IBM Plex Sans', sans-serif",
        fontWeight: 600,
        fontSize: '14px',
        color: 'var(--navy-900)',
        flexShrink: 0,
      }}
    >
      {initials}
    </div>
  )
}

function KpiStrip({ result }: { result: ScoreResult }) {
  const { evaluation, dimension_scores, compliance_flags } = result
  const naCount = dimension_scores.filter((d) => d.is_na).length
  const items = [
    { label: 'OVERALL SCORE', value: <ScoreBadge score={evaluation.overall_score} /> },
    {
      label: 'CONFIDENCE',
      value: (
        <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontWeight: 500 }}>
          {Math.round(evaluation.confidence_overall * 100)}%
        </span>
      ),
    },
    {
      label: 'N/A DIMENSIONS',
      value: (
        <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontWeight: 500 }}>
          {naCount}
        </span>
      ),
    },
    {
      label: 'COMPLIANCE FLAGS',
      value: (
        <span
          style={{
            fontFamily: "'IBM Plex Mono', monospace",
            fontWeight: 500,
            color: compliance_flags.length > 0 ? 'var(--red)' : '#065F46',
          }}
        >
          {compliance_flags.length}
        </span>
      ),
    },
  ]

  return (
    <div
      style={{
        display: 'flex',
        gap: '0',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-md)',
        overflow: 'hidden',
        marginBottom: '24px',
      }}
    >
      {items.map((item, i) => (
        <div
          key={item.label}
          style={{
            flex: 1,
            padding: '16px',
            borderRight: i < items.length - 1 ? '1px solid var(--border)' : 'none',
            background: 'var(--white)',
          }}
        >
          <div
            style={{
              fontFamily: "'IBM Plex Mono', monospace",
              fontSize: '10px',
              color: 'var(--muted)',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              marginBottom: '6px',
            }}
          >
            {item.label}
          </div>
          <div style={{ fontSize: '20px', color: 'var(--ink)' }}>{item.value}</div>
        </div>
      ))}
    </div>
  )
}

function DimensionTable({
  dims,
  onDimClick,
}: {
  dims: DimensionScoreRow[]
  onDimClick: (dim: string) => void
}) {
  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-md)',
        overflow: 'hidden',
        background: 'var(--white)',
        marginBottom: '24px',
      }}
    >
      <div
        style={{
          background: 'var(--surface-2)',
          borderBottom: '1px solid var(--border-strong)',
          display: 'grid',
          gridTemplateColumns: '1fr 80px 60px 80px 80px',
          padding: '10px 16px',
        }}
      >
        {['Dimension', 'Score', 'Weight', 'Confidence', ''].map((h) => (
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
      {dims.map((dim, i) => (
        <div
          key={dim.dimension}
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 80px 60px 80px 80px',
            padding: '12px 16px',
            borderBottom: i < dims.length - 1 ? '1px solid var(--border)' : 'none',
            alignItems: 'center',
            cursor: 'pointer',
            transition: 'background 0.1s',
          }}
          onMouseEnter={(e) =>
            ((e.currentTarget as HTMLElement).style.background = 'var(--surface)')
          }
          onMouseLeave={(e) =>
            ((e.currentTarget as HTMLElement).style.background = 'transparent')
          }
          onClick={() => onDimClick(dim.dimension)}
        >
          <span
            style={{
              fontFamily: "'IBM Plex Sans', sans-serif",
              fontSize: '14px',
              color: 'var(--text)',
            }}
          >
            {DIMENSION_LABELS[dim.dimension] ?? dim.dimension}
          </span>
          <span>
            <DimScoreBadge score={dim.raw_score} />
          </span>
          <span
            style={{
              fontFamily: "'IBM Plex Mono', monospace",
              fontSize: '12px',
              color: 'var(--muted)',
            }}
          >
            ×{dim.weight}
          </span>
          <span
            style={{
              fontFamily: "'IBM Plex Mono', monospace",
              fontSize: '12px',
              color: 'var(--muted)',
            }}
          >
            {dim.confidence !== null ? `${Math.round((dim.confidence ?? 0) * 100)}%` : '—'}
          </span>
          <span
            style={{
              fontFamily: "'IBM Plex Sans', sans-serif",
              fontSize: '12px',
              color: 'var(--teal-500)',
              textDecoration: 'underline',
              cursor: 'pointer',
            }}
          >
            Evidence →
          </span>
        </div>
      ))}
    </div>
  )
}

function ScoreRadar({ dims }: { dims: DimensionScoreRow[] }) {
  const data = dims.map((d) => ({
    dimension: DIMENSION_LABELS[d.dimension]?.split(' ')[0] ?? d.dimension,
    score: d.is_na ? 0 : (d.raw_score ?? 0),
    fullMark: 5,
  }))

  return (
    <div
      style={{
        background: 'var(--white)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-md)',
        padding: '16px',
        marginBottom: '20px',
      }}
    >
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
        SCORE RADAR
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
          <PolarGrid stroke="var(--border)" />
          <PolarAngleAxis
            dataKey="dimension"
            tick={{ fontSize: 11, fontFamily: 'IBM Plex Sans', fill: 'var(--muted)' }}
          />
          <PolarRadiusAxis domain={[0, 5]} tick={false} axisLine={false} />
          <Radar
            name="Score"
            dataKey="score"
            stroke="#1C7293"
            fill="#1C7293"
            fillOpacity={0.2}
            strokeWidth={2}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}

export function CallDetail() {
  const { callId } = useParams<{ callId: string }>()
  const navigate = useNavigate()
  const [result, setResult] = useState<ScoreResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeDim, setActiveDim] = useState<string | null>(null)

  useEffect(() => {
    if (!callId) return
    api.calls
      .get(callId)
      .then(setResult)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [callId])

  if (loading)
    return (
      <div style={{ padding: '40px 24px', color: 'var(--muted)', fontFamily: "'IBM Plex Sans'" }}>
        Loading…
      </div>
    )
  if (error)
    return (
      <div style={{ padding: '40px 24px', color: 'var(--red)', fontFamily: "'IBM Plex Sans'" }}>
        {error}
      </div>
    )
  if (!result) return null

  const { evaluation, dimension_scores, compliance_flags } = result

  return (
    <div style={{ padding: '32px 24px', maxWidth: '1280px', margin: '0 auto' }}>
      {/* Back */}
      <button
        onClick={() => navigate('/')}
        style={{
          background: 'transparent',
          border: 'none',
          fontFamily: "'IBM Plex Sans', sans-serif",
          fontSize: '13px',
          color: 'var(--teal-500)',
          cursor: 'pointer',
          padding: '0 0 20px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
        }}
      >
        ← All calls
      </button>

      {/* Compliance banner */}
      {compliance_flags.length > 0 && (
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
            fontWeight: 500,
          }}
        >
          ⚠ {compliance_flags.length} compliance flag{compliance_flags.length !== 1 ? 's' : ''} on
          this call — review required.
        </div>
      )}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr',
          gap: '24px',
        }}
        className="lg-two-col"
      >
        {/* Left column */}
        <div>
          {/* Call header */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '14px',
              marginBottom: '20px',
              background: 'var(--white)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)',
              padding: '16px',
            }}
          >
            <AgentAvatar agentId={evaluation.agent_id} />
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                <span
                  style={{
                    fontFamily: "'IBM Plex Sans', sans-serif",
                    fontWeight: 600,
                    fontSize: '15px',
                    color: 'var(--ink)',
                  }}
                >
                  {evaluation.agent_id}
                </span>
                <span
                  style={{
                    fontFamily: "'IBM Plex Mono', monospace",
                    fontSize: '12px',
                    color: 'var(--muted)',
                  }}
                >
                  {evaluation.call_id}
                </span>
                {evaluation.scenario_type && (
                  <span
                    style={{
                      fontFamily: "'IBM Plex Mono', monospace",
                      fontSize: '11px',
                      background: 'var(--surface-2)',
                      border: '1px solid var(--border)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '2px 8px',
                      color: 'var(--muted)',
                      textTransform: 'capitalize',
                    }}
                  >
                    {evaluation.scenario_type.replace(/_/g, ' ')}
                  </span>
                )}
              </div>
              <div
                style={{
                  fontFamily: "'IBM Plex Sans', sans-serif",
                  fontSize: '13px',
                  color: 'var(--muted)',
                  marginTop: '4px',
                }}
              >
                {fmtDate(evaluation.call_timestamp)} · {fmtDuration(evaluation.duration_seconds)}
              </div>
            </div>
          </div>

          {/* Manager summary */}
          <div
            style={{
              background: 'var(--white)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)',
              padding: '20px',
              marginBottom: '24px',
            }}
          >
            <div
              style={{
                fontFamily: "'IBM Plex Mono', monospace",
                fontSize: '10px',
                color: 'var(--muted)',
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
                marginBottom: '10px',
              }}
            >
              MANAGER SUMMARY
            </div>
            <p
              style={{
                fontFamily: "'Fraunces', serif",
                fontStyle: 'italic',
                fontWeight: 300,
                fontSize: '16px',
                color: 'var(--ink)',
                lineHeight: '1.7',
                margin: 0,
              }}
            >
              {evaluation.manager_summary}
            </p>
          </div>

          {/* KPI strip */}
          <KpiStrip result={result} />

          {/* Dimension breakdown */}
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
            DIMENSION BREAKDOWN — click any row to see evidence
          </div>
          <DimensionTable dims={dimension_scores} onDimClick={setActiveDim} />

          {/* Override section — spec §3.2 */}
          <OverrideSection callId={callId!} dims={dimension_scores} />

          {/* Coaching notes section — spec §3.2 */}
          <CoachingNotesSection callId={callId!} />
        </div>

        {/* Right column — radar chart */}
        <div>
          <ScoreRadar dims={dimension_scores} />
          <div
            style={{
              background: 'var(--white)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)',
              padding: '16px',
            }}
          >
            <div
              style={{
                fontFamily: "'IBM Plex Mono', monospace",
                fontSize: '10px',
                color: 'var(--muted)',
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
                marginBottom: '10px',
              }}
            >
              EVALUATION METADATA
            </div>
            {[
              ['Rubric', evaluation.rubric_version],
              ['Prompt', evaluation.prompt_version],
              ['Model', evaluation.model_id.split(':')[0]],
              ['Scored at', new Date(evaluation.scored_at).toLocaleString()],
            ].map(([label, value]) => (
              <div
                key={label}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  padding: '6px 0',
                  borderBottom: '1px solid var(--border)',
                }}
              >
                <span
                  style={{
                    fontFamily: "'IBM Plex Sans', sans-serif",
                    fontSize: '13px',
                    color: 'var(--muted)',
                  }}
                >
                  {label}
                </span>
                <span
                  style={{
                    fontFamily: "'IBM Plex Mono', monospace",
                    fontSize: '12px',
                    color: 'var(--text)',
                  }}
                >
                  {value}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Evidence modal */}
      {activeDim && callId && (
        <EvidenceModal
          callId={callId}
          dimension={activeDim}
          onClose={() => setActiveDim(null)}
        />
      )}
    </div>
  )
}
