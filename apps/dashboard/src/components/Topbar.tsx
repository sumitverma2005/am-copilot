/* Topbar — spec §3.1: amber square + navy italic "AM" brand mark.
   Nav links: spec gap filled on Day 7 — spec §3.1 defines brand mark + user info
   but no nav links. Dashboard is unusable without navigation between 6 screens. */
import { NavLink } from 'react-router-dom'

const NAV_LINKS = [
  { to: '/', label: 'Calls', end: true },
  { to: '/queue/coaching', label: 'Coaching Queue' },
  { to: '/queue/compliance', label: 'Compliance' },
  { to: '/disagreements', label: 'Disagreements' },
]

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
      <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
        {/* Amber square brand mark */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
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

        {/* Nav links — spec gap filled on Day 7 */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          {NAV_LINKS.map(({ to, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              style={({ isActive }) => ({
                fontFamily: "'IBM Plex Sans', sans-serif",
                fontSize: '13px',
                fontWeight: isActive ? 600 : 400,
                color: isActive ? 'var(--teal-500)' : 'var(--faint)',
                textDecoration: 'none',
                padding: '6px 12px',
                borderRadius: 'var(--radius-sm)',
                background: isActive ? 'rgba(28,114,147,0.12)' : 'transparent',
                transition: 'all 0.15s',
              })}
            >
              {label}
            </NavLink>
          ))}
        </nav>
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
