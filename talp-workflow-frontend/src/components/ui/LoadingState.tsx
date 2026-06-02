export function LoadingState() {
  return (
    <div className="loading-state" aria-live="polite" aria-busy="true">
      <div className="loading-state__bar loading-state__bar--wide" />
      <div className="loading-state__bar" />
      <div className="loading-state__bar" />
    </div>
  );
}
