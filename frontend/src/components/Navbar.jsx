import { FiMenu } from 'react-icons/fi'

function Navbar({ title, subtitle, onMenuClick, menuOpen = false }) {
  return (
    <header className="navbar">
      <div className="navbar__left">
        <button
          type="button"
          className="navbar__menu-btn"
          onClick={onMenuClick}
          aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
          aria-expanded={menuOpen}
          aria-controls="app-sidebar"
        >
          <FiMenu size={20} aria-hidden="true" />
        </button>
        <div className="navbar__titles">
          <h1 className="navbar__title">{title}</h1>
          {subtitle ? <p className="navbar__subtitle">{subtitle}</p> : null}
        </div>
      </div>
    </header>
  )
}

export default Navbar
