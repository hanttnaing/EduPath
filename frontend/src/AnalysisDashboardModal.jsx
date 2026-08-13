import { useEffect } from 'react'

function AnalysisDashboardModal({
  onClose,
}) {
  // =========================
  // ESC KEY CLOSE SUPPORT
  // =========================
  useEffect(() => {
    const handleKeyDown = (
      event
    ) => {
      if (
        event.key === 'Escape'
      ) {
        onClose()
      }
    }

    window.addEventListener(
      'keydown',
      handleKeyDown
    )

    // Prevent the main page from
    // scrolling behind the dashboard.
    const previousOverflow =
      document.body.style.overflow

    document.body.style.overflow =
      'hidden'

    return () => {
      window.removeEventListener(
        'keydown',
        handleKeyDown
      )

      document.body.style.overflow =
        previousOverflow
    }
  }, [onClose])

  return (
    <div className="analysis-modal-overlay">
      <div className="analysis-modal-container">

        {/* =========================
            DASHBOARD TOP BAR
        ========================== */}

        <header className="analysis-modal-header">
          <div className="analysis-modal-brand">
            <div className="analysis-modal-logo">
              E
            </div>

            <div>
              <h2>
                EduPath Analysis Dashboard
              </h2>

              <p>
                Data Analysis Layer
              </p>
            </div>
          </div>

          <div className="analysis-modal-actions">
            <span className="analysis-modal-status">
              <span className="analysis-modal-status-dot" />

              Analysis
            </span>

            <button
              className="analysis-modal-close-button"
              type="button"
              onClick={onClose}
            >
              ← Back to EduPath
            </button>
          </div>
        </header>

        {/* =========================
            DASHBOARD IFRAME
        ========================== */}

        <div className="analysis-modal-content">
          <iframe
            className="analysis-dashboard-frame"
            src="/analysis.html"
            title="EduPath Analysis Dashboard"
          />
        </div>
      </div>
    </div>
  )
}

export default AnalysisDashboardModal