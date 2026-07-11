function ChartCard({ title, subtitle, children, empty, actions = null, className = '' }) {
  return (
    <section className={`chart-card${className ? ` ${className}` : ''}`}>
      <header className="chart-card__header">
        <div className="chart-card__titles">
          {title ? <h3 className="chart-card__title">{title}</h3> : null}
          {subtitle ? <p className="chart-card__subtitle">{subtitle}</p> : null}
        </div>
        {actions ? <div className="chart-card__actions">{actions}</div> : null}
      </header>
      <div className="chart-card__body">
        {empty ? <p className="chart-card__empty">{empty}</p> : children}
      </div>
    </section>
  )
}

export default ChartCard
