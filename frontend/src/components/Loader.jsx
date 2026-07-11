function Loader({ label = 'Loading…', fullPage = false }) {
  return (
    <div
      className={`loader${fullPage ? ' loader--full' : ''}`}
      role="status"
      aria-live="polite"
      aria-busy="true"
    >
      <span className="loader__spinner" aria-hidden="true" />
      {label ? <p className="loader__label">{label}</p> : null}
    </div>
  )
}

export default Loader
