import { useState } from 'react'
import './Auth.css'

function RegisterPage({
  onRegister,
  onShowLogin,
}) {
  const [fullName, setFullName] =
    useState('')

  const [email, setEmail] =
    useState('')

  const [password, setPassword] =
    useState('')

  const [
    confirmPassword,
    setConfirmPassword,
  ] = useState('')

  const [submitting, setSubmitting] =
    useState(false)

  const [error, setError] =
    useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()

    setError('')

    if (password !== confirmPassword) {
      setError(
        'Passwords do not match.'
      )

      return
    }

    if (password.length < 8) {
      setError(
        'Password must contain at least 8 characters.'
      )

      return
    }

    setSubmitting(true)

    try {
      await onRegister({
        full_name: fullName.trim(),
        email: email.trim(),
        password,
      })
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to create account.'
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
            START YOUR PATH
          </p>

          <h1>
            Build your EduPath
            account.
          </h1>

          <p className="auth-brand-copy">
            Create your account first.
            Your academic profile and
            preferences will be completed
            separately.
          </p>

          <div className="auth-brand-points">
            <span>
              1. Create your account
            </span>

            <span>
              2. Complete your profile
            </span>

            <span>
              3. Receive recommendations
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
                CREATE ACCOUNT
              </p>

              <h2>Join EduPath</h2>

              <p>
                Start building your personalized
                education journey.
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
                <span>Full name</span>

                <input
                  type="text"
                  value={fullName}
                  onChange={(event) =>
                    setFullName(
                      event.target.value
                    )
                  }
                  placeholder="Your full name"
                  autoComplete="name"
                  minLength={2}
                  required
                />
              </label>

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
                  placeholder="At least 8 characters"
                  autoComplete="new-password"
                  minLength={8}
                  required
                />
              </label>

              <label>
                <span>Confirm password</span>

                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(event) =>
                    setConfirmPassword(
                      event.target.value
                    )
                  }
                  placeholder="Enter password again"
                  autoComplete="new-password"
                  required
                />
              </label>

              <button
                className="auth-primary-button"
                type="submit"
                disabled={submitting}
              >
                {submitting
                  ? 'Creating account...'
                  : 'Create Account'}
              </button>
            </form>

            <p className="auth-switch-text">
              Already have an account?{' '}

              <button
                type="button"
                className="auth-link-button"
                onClick={onShowLogin}
              >
                Sign in
              </button>
            </p>
          </div>
        </section>
      </div>
    </div>
  )
}

export default RegisterPage
