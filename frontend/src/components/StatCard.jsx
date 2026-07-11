function StatCard({ label, value, hint, icon: Icon, tone = 'primary' }) {
  const iconClass =
    tone === 'accent'
      ? 'stat-card__icon stat-card__icon--accent'
      : tone === 'success'
        ? 'stat-card__icon stat-card__icon--success'
        : tone === 'warning'
          ? 'stat-card__icon stat-card__icon--warning'
          : 'stat-card__icon'

  return (
    <article className="stat-card">
      <div className="stat-card__top">
        <span className="stat-card__label">{label}</span>
        {Icon ? (
          <span className={iconClass} aria-hidden="true">
            <Icon />
          </span>
        ) : null}
      </div>
      <div className="stat-card__value">{value}</div>
      {hint ? <p className="stat-card__hint">{hint}</p> : null}
    </article>
  )
}

export default StatCard
