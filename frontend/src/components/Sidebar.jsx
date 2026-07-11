import { NavLink } from 'react-router-dom'
import {
  FiBarChart2,
  FiCheckCircle,
  FiClock,
  FiDatabase,
  FiHome,
  FiSettings,
  FiUploadCloud,
  FiLayers,
} from 'react-icons/fi'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: FiHome, end: true },
  { to: '/upload', label: 'Upload', icon: FiUploadCloud },
  { to: '/overview', label: 'Dataset Overview', icon: FiLayers },
  { to: '/analytics', label: 'Analytics', icon: FiBarChart2 },
  { to: '/quality', label: 'Data Quality', icon: FiCheckCircle },
  { to: '/warehouse', label: 'Warehouse', icon: FiDatabase },
  { to: '/history', label: 'History', icon: FiClock },
  { to: '/settings', label: 'Settings', icon: FiSettings },
]

function Sidebar({ open = false, onNavigate }) {
  return (
    <aside className={`sidebar${open ? ' sidebar--open' : ''}`} aria-label="Main navigation">
      <div className="sidebar__brand">
        <div className="sidebar__logo" aria-hidden="true">
          DF
        </div>
        <div className="sidebar__brand-text">
          <span className="sidebar__brand-name">DataForge</span>
          <span className="sidebar__brand-tag">Data Platform</span>
        </div>
      </div>

      <nav className="sidebar__nav">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `sidebar__link${isActive ? ' sidebar__link--active' : ''}`
            }
            onClick={onNavigate}
          >
            <Icon className="sidebar__link-icon" aria-hidden="true" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar__footer">
        DataForge v1.0
        <br />
        FastAPI · React · PostgreSQL
      </div>
    </aside>
  )
}

export default Sidebar
