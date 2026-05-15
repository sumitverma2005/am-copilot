/* Skeleton shimmer — spec §5 "skeleton shimmer on all data-dependent elements" */

const shimmerKeyframes = `
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
`

if (typeof document !== 'undefined' && !document.getElementById('shimmer-style')) {
  const style = document.createElement('style')
  style.id = 'shimmer-style'
  style.textContent = shimmerKeyframes
  document.head.appendChild(style)
}

export function Skeleton({
  width = '100%',
  height = '16px',
  borderRadius = 'var(--radius-sm)',
}: {
  width?: string | number
  height?: string | number
  borderRadius?: string
}) {
  return (
    <div
      style={{
        width,
        height,
        borderRadius,
        background: 'linear-gradient(90deg, var(--surface-2) 25%, var(--border) 50%, var(--surface-2) 75%)',
        backgroundSize: '200% 100%',
        animation: 'shimmer 1.4s ease-in-out infinite',
      }}
    />
  )
}

export function SkeletonRow({ cols = 4 }: { cols?: number }) {
  return (
    <div style={{ display: 'flex', gap: '16px', padding: '14px 16px', alignItems: 'center' }}>
      {Array.from({ length: cols }).map((_, i) => (
        <Skeleton key={i} width={`${100 / cols}%`} height="14px" />
      ))}
    </div>
  )
}

export function SkeletonTable({ rows = 4, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-md)',
        overflow: 'hidden',
        background: 'var(--white)',
      }}
    >
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} style={{ borderBottom: i < rows - 1 ? '1px solid var(--border)' : 'none' }}>
          <SkeletonRow cols={cols} />
        </div>
      ))}
    </div>
  )
}
