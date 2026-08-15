import { useState } from 'react'
import './Auth.css'

function LoginPage({
  onLogin,
  onShowRegister,
  initialEmail = '',
}) {
  const [email, setEmail] =
    useState(initialEmail)

  const [password, setPassword] =
    useState('')

  const [submitting, setSubmitting] =
    useState(false)

  const [error, setError] =
    useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()

    setError('')
    setSubmitting(true)

    try {
      await onLogin({
        email: email.trim(),
        password,
      })
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to sign in.'
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-layout">
        <section className="auth-brand-panel">
          <div className="auth-brand-mark">
            EP
          </div>

          <p className="auth-eyebrow">
            EDUPATH
          </p>

          <h1>
            Find the education path
            that fits you.
          </h1>

          <p className="auth-brand-copy">
            Explore universities, programs,
            scholarships and personalized
            recommendations in one place.
          </p>

          <div className="auth-brand-points">
            <span>
              &#10003; Personalized recommendations
            </span>

            <span>
              &#10003; Scholarship discovery
            </span>

            <span>
              &#10003; Save opportunities for later
            </span>
          </div>
        </section>

        <section className="auth-form-panel">
          <div className="auth-form-card">
            <div className="auth-mobile-brand">
              <span className="auth-brand-mark small">
                EP
              </span>

              <strong>EduPath</strong>
            </div>

            <div className="auth-form-heading">
              <p className="auth-eyebrow">
                WELCOME BACK
              </p>

              <h2>Sign in to EduPath</h2>

              <p>
                Continue your education search
                and recommendations.
              </p>
            </div>

            {error && (
              <div
                className="auth-message error"
                role="alert"
              >
                {error}
              </div>
            )}

            <form
              className="auth-form"
              onSubmit={handleSubmit}
            >
              <label>
                <span>Email address</span>

                <input
                  type="email"
                  value={email}
                  onChange={(event) =>
                    setEmail(
                      event.target.value
                    )
                  }
                  placeholder="student@example.com"
                  autoComplete="email"
                  required
                />
              </label>

              <label>
                <span>Password</span>

                <input
                  type="password"
                  value={password}
                  onChange={(event) =>
                    setPassword(
                      event.target.value
                    )
                  }
                  placeholder="Enter your password"
                  autoComplete="current-password"
                  required
                />
              </label>

              <button
                className="auth-primary-button"
                type="submit"
                disabled={submitting}
              >
                {submitting
                  ? 'Signing in...'
                  : 'Sign In'}
              </button>
            </form>

            <p className="auth-switch-text">
              New to EduPath?{' '}

              <button
                type="button"
                className="auth-link-button"
                onClick={onShowRegister}
              >
                Create an account
              </button>
            </p>
          </div>
        </section>
      </div>
    </div>
  )
}

export default LoginPage
