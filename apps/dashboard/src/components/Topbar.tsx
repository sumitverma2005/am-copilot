/* Topbar — spec §3.1: amber square + navy italic "AM" brand mark */

export function Topbar() {
  return (
    <header
      style={{
        background: 'var(--navy-900)',
        borderBottom: '1px solid var(--navy-800)',
        padding: '0 24px',
        height: '56px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 40,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        {/* Amber square brand mark */}
        <div
          style={{
            width: '28px',
            height: '28px',
            background: 'var(--amber)',
            borderRadius: 'var(--radius-sm)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <span
            style={{
              fontFamily: "'Fraunces', serif",
              fontStyle: 'italic',
              fontWeight: 500,
              color: 'var(--navy-900)',
              fontSize: '14px',
              lineHeight: 1,
            }}
          >
            AM
          </span>
        </div>
        <div>
          <span
            style={{
              fontFamily: "'IBM Plex Sans', sans-serif",
              fontWeight: 600,
              color: 'var(--white)',
              fontSize: '15px',
            }}
          >
            AM Copilot
          </span>
          <span
            style={{
              fontFamily: "'IBM Plex Mono', monospace",
              fontSize: '11px',
              color: 'var(--teal-500)',
              marginLeft: '8px',
              letterSpacing: '0.05em',
            }}
          >
            Call Scoring · Phase A
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <span
          style={{
            fontFamily: "'IBM Plex Sans', sans-serif",
            fontSize: '13px',
            color: 'var(--faint)',
          }}
        >
          Alyssa Chen
        </span>
        <button
          style={{
            background: 'transparent',
            border: '1px solid var(--navy-700)',
            borderRadius: 'var(--radius-sm)',
            color: 'var(--faint)',
            fontFamily: "'IBM Plex Sans', sans-serif",
            fontSize: '12px',
            padding: '4px 10px',
            cursor: 'pointer',
          }}
        >
          Sign out
        </button>
      </div>
    </header>
  )
}
