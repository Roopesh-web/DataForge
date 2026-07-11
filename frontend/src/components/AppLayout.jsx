import { useEffect, useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Navbar from './Navbar'
import Sidebar from './Sidebar'

const PAGE_META = {
  '/': {
    title: 'Dashboard',
    subtitle: 'Platform overview and key metrics',
  },
  '/upload': {
    title: 'Upload',
    subtitle: 'Ingest CSV, Excel, or JSON datasets',
  },
  '/overview': {
    title: 'Dataset Overview',
    subtitle: 'Schema, profiles, and missing values',
  },
  '/analytics': {
    title: 'Analytics',
    subtitle: 'Statistics, correlations, and outliers',
  },
  '/quality': {
    title: 'Data Quality',
    subtitle: 'Validation rules and quality scoring',
  },
  '/warehouse': {
    title: 'Warehouse',
    subtitle: 'Load datasets into PostgreSQL',
  },
  '/history': {
    title: 'History',
    subtitle: 'Uploads, activity, and warehouse loads',
  },
  '/settings': {
    title: 'Settings',
    subtitle: 'Platform information and runtime details',
  },
}

function AppLayout() {
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const meta = PAGE_META[location.pathname] ?? {
    title: 'DataForge',
    subtitle: 'Enterprise data engineering platform',
  }

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setSidebarOpen(false)
    }, 0)
    return () => window.clearTimeout(timer)
  }, [location.pathname])

  useEffect(() => {
    const onKeyDown = (event) => {
      if (event.key === 'Escape') setSidebarOpen(false)
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [])

  return (
    <div className="app-shell">
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <Sidebar open={sidebarOpen} onNavigate={() => setSidebarOpen(false)} />

      <button
        type="button"
        className={`app-overlay${sidebarOpen ? ' app-overlay--visible' : ''}`}
        aria-label="Close navigation menu"
        onClick={() => setSidebarOpen(false)}
      />

      <div className="app-main">
        <Navbar
          title={meta.title}
          subtitle={meta.subtitle}
          onMenuClick={() => setSidebarOpen((open) => !open)}
        />
        <main id="main-content" className="app-content" tabIndex={-1}>
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default AppLayout
