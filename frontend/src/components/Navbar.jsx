import { FiMenu } from 'react-icons/fi'

function Navbar({ title, subtitle, onMenuClick }) {
  return (
    <header className="navbar">
      <div className="navbar__left">
        <button
          type="button"
          className="navbar__menu-btn"
          onClick={onMenuClick}
          aria-label="Open navigation menu"
        >
          <FiMenu size={20} aria-hidden="true" />
        </button>
        <div className="navbar__titles">
          <h1 className="navbar__title">{title}</h1>
          {subtitle ? <p className="navbar__subtitle">{subtitle}</p> : null}
        </div>
      </div>

      <div className="navbar__right">
        <span className="navbar__badge" title="API status will be wired in a later phase">
          <span className="navbar__badge-dot" aria-hidden="true" />
          API idle
        </span>
      </div>
    </header>
  )
}

export default Navbar
