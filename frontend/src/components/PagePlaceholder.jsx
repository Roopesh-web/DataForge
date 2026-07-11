function PagePlaceholder({ title, description }) {
  return (
    <div className="page">
      <header className="page__header">
        <span className="page__eyebrow">Coming soon</span>
        <h2 className="page__heading">{title}</h2>
        <p className="page__description">{description}</p>
      </header>

      <div className="page-placeholder">
        <h3 className="page-placeholder__title">{title}</h3>
        <p className="page-placeholder__text">
          This page is reserved for a later phase. Navigation is wired; features are
          not implemented yet.
        </p>
      </div>
    </div>
  )
}

export default PagePlaceholder
