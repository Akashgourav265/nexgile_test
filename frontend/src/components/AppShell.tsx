import { useEffect, useState, type ReactNode } from 'react'
import type { AnalystStatus, Meta } from '../api/types'
import { dayLabel } from '../lib/format'
import { href } from '../lib/router'
import { SourceBadge } from './ui/Badges'
import { Icon, type IconName } from './ui/Icon'

export const NAV: { group: string; items: { page: string; label: string; icon: IconName }[] }[] = [
  {
    group: 'Analysis',
    items: [
      { page: 'overview', label: 'Executive overview', icon: 'overview' },
      { page: 'bridge', label: 'Revenue bridge', icon: 'bridge' },
    ],
  },
  {
    group: 'Initiatives',
    items: [
      { page: 'onboarding', label: 'Onboarding', icon: 'flask' },
      { page: 'pricing', label: 'European pricing', icon: 'tag' },
      { page: 'referrals', label: 'Referral programme', icon: 'share' },
    ],
  },
  {
    group: 'Diagnostics',
    items: [
      { page: 'retention', label: 'Retention & acquisition', icon: 'users' },
      { page: 'data-quality', label: 'Data quality', icon: 'shield' },
    ],
  },
  { group: 'Assistant', items: [{ page: 'analyst', label: 'AI Analyst', icon: 'sparkle' }] },
  {
    group: 'Deliverables',
    items: [
      { page: 'decisions', label: 'Decisions', icon: 'message' },
      { page: 'report', label: 'Report', icon: 'table' },
    ],
  },
]

type Theme = 'system' | 'light' | 'dark'
const THEME_KEY = 'revenue-review-theme'

function readTheme(): Theme {
  try {
    const t = localStorage.getItem(THEME_KEY)
    return t === 'light' || t === 'dark' ? t : 'system'
  } catch {
    return 'system'
  }
}

function useTheme() {
  const [theme, setTheme] = useState<Theme>(readTheme)
  useEffect(() => {
    const root = document.documentElement
    if (theme === 'system') root.removeAttribute('data-theme')
    else root.setAttribute('data-theme', theme)
    try {
      localStorage.setItem(THEME_KEY, theme)
    } catch {
      // storage unavailable (private mode); theme still applies for this session
    }
  }, [theme])
  const next: Record<Theme, Theme> = { system: 'light', light: 'dark', dark: 'system' }
  return { theme, cycle: () => setTheme((t) => next[t]) }
}

export function AppShell({
  page,
  meta,
  analyst,
  children,
}: {
  page: string
  meta: Meta | null
  analyst: AnalystStatus | null
  children: ReactNode
}) {
  const [navOpen, setNavOpen] = useState(false)
  const { theme, cycle } = useTheme()
  useEffect(() => setNavOpen(false), [page])
  const themeIcon: IconName = theme === 'light' ? 'sun' : theme === 'dark' ? 'moon' : 'monitor'
  const current = NAV.flatMap((g) => g.items).find((i) => i.page === page)

  return (
    <div className={`shell ${navOpen ? 'nav-open' : ''}`}>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <aside className="sidebar" aria-label="Primary">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">
            <Icon name="bridge" size={16} />
          </span>
          <div>
            <div className="brand-name">Revenue Review</div>
            <div className="brand-sub">Q2 → Q3 analysis</div>
          </div>
          <button type="button" className="icon-btn nav-close" onClick={() => setNavOpen(false)} aria-label="Close menu">
            <Icon name="close" />
          </button>
        </div>
        <nav>
          {NAV.map((g) => (
            <div key={g.group} className="nav-group">
              <div className="nav-group-label">{g.group}</div>
              {g.items.map((it) => (
                <a
                  key={it.page}
                  href={href(it.page)}
                  className={`nav-item ${page === it.page ? 'active' : ''}`}
                  aria-current={page === it.page ? 'page' : undefined}
                >
                  <Icon name={it.icon} size={17} />
                  {it.label}
                </a>
              ))}
            </div>
          ))}
        </nav>
        <div className="sidebar-foot">
          <div className="foot-row">
            <span className={`mode-dot ${analyst?.default_mode === 'external' ? 'ext' : ''}`} />
            Analyst: {analyst?.default_mode === 'external' ? 'external AI' : 'local engine'}
          </div>
          {meta && <div className="foot-row muted">Data as of {dayLabel(meta.as_of_date, true)}</div>}
        </div>
      </aside>
      <div className="scrim" onClick={() => setNavOpen(false)} aria-hidden="true" />

      <div className="main-col">
        <header className="topbar">
          <button type="button" className="icon-btn nav-open-btn" onClick={() => setNavOpen(true)} aria-label="Open menu">
            <Icon name="menu" />
          </button>
          <div className="topbar-title">{current?.label ?? 'Revenue Review'}</div>
          <div className="topbar-right">
            {meta && <SourceBadge isMock={meta.is_mock} />}
            <button
              type="button"
              className="icon-btn"
              onClick={cycle}
              aria-label={`Theme: ${theme}. Click to change.`}
              title={`Theme: ${theme}`}
            >
              <Icon name={themeIcon} />
            </button>
          </div>
        </header>
        {meta?.is_mock && (
          <div className="mock-banner" role="note">
            <Icon name="alert" size={16} />
            <span>
              <strong>Development build.</strong> Every figure in this app is synthetic mock data. Nothing here is a
              finding from the assignment.
            </span>
          </div>
        )}
        <main id="main" className="content" tabIndex={-1}>
          {children}
        </main>
      </div>
    </div>
  )
}
