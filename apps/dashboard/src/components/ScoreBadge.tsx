/* Colour thresholds verbatim from ui-ux-spec.md §1 "Score colour mapping":
   80–100 → green-soft / #065F46
   60–79  → amber-soft / #92400E
   0–59   → red-soft   / var(--red)
   N/A    → surface-2  / var(--muted)                                        */

interface Props {
  score: number | null
  size?: 'sm' | 'md'
}

function colours(score: number | null): { bg: string; fg: string } {
  if (score === null) return { bg: 'var(--surface-2)', fg: 'var(--muted)' }
  if (score >= 80) return { bg: 'var(--green-soft)', fg: '#065F46' }
  if (score >= 60) return { bg: 'var(--amber-soft)', fg: '#92400E' }
  return { bg: 'var(--red-soft)', fg: 'var(--red)' }
}

export function ScoreBadge({ score, size = 'md' }: Props) {
  const { bg, fg } = colours(score)
  const label = score === null ? 'N/A' : String(Math.round(score))
  const padding = size === 'sm' ? '2px 8px' : '4px 12px'
  const fontSize = size === 'sm' ? '12px' : '14px'

  return (
    <span
      style={{
        background: bg,
        color: fg,
        fontFamily: "'IBM Plex Mono', monospace",
        fontWeight: 500,
        fontSize,
        borderRadius: 'var(--radius-sm)',
        padding,
        display: 'inline-block',
        lineHeight: '1.4',
        whiteSpace: 'nowrap',
      }}
    >
      {label}
    </span>
  )
}

/* Dim-scale badge: raw_score 0–5, displayed as-is */
export function DimScoreBadge({ score }: { score: number | null }) {
  const scaled = score === null ? null : Math.round((score / 5) * 100)
  return <ScoreBadge score={scaled} size="sm" />
}
