function SkeletonBlock({ className = '', style }) {
  return <div className={`skeleton ${className}`.trim()} style={style} aria-hidden="true" />
}

function PageSkeleton({ cards = 4, showPanel = true, label = 'Loading content' }) {
  return (
    <div className="page-skeleton" role="status" aria-live="polite" aria-busy="true" aria-label={label}>
      <span className="visually-hidden">{label}</span>
      <SkeletonBlock className="skeleton--title" />
      <SkeletonBlock className="skeleton--text" />
      {cards > 0 ? (
        <div className="kpi-grid page-skeleton__cards">
          {Array.from({ length: cards }, (_, index) => (
            <SkeletonBlock key={index} className="skeleton--card" />
          ))}
        </div>
      ) : null}
      {showPanel ? <SkeletonBlock className="skeleton--panel" /> : null}
      {showPanel ? <SkeletonBlock className="skeleton--panel skeleton--panel-short" /> : null}
    </div>
  )
}

export { SkeletonBlock, PageSkeleton }
export default PageSkeleton
