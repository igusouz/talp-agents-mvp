interface ErrorStateProps {
  title: string
  description: string
  actionLabel?: string
  onAction?: () => void
}

export function ErrorState({ title, description, actionLabel, onAction }: ErrorStateProps) {
  return (
    <section className="state-panel state-panel--error" role="alert" aria-live="polite">
      <h2 className="state-panel__title">{title}</h2>
      <p className="state-panel__description">{description}</p>
      {actionLabel && onAction ? (
        <button type="button" className="button button--primary" onClick={onAction}>
          {actionLabel}
        </button>
      ) : null}
    </section>
  )
}
