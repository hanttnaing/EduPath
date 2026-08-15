import EduPathLogoMark from '../assets/edupath-logo-mark.png'
import { useState } from 'react'
import { authFetch, readApiError } from '../api'
import './ProfileSetupPage.css'

const INITIAL_FORM = {
  nationality: 'Myanmar',
  current_education_level: '',
  target_degree_level: '',
  preferred_major: '',
  gpa: '',
  gpa_scale: '',
  ielts_score: '',
  toefl_score: '',
  annual_budget: '',
  budget_currency: 'USD',
  preferred_countries: ['Japan'],
  scholarship_required: true,
  preferred_funding_type: 'Fully Funded',
  preferred_intake: '2027',
}

function toOptionalNumber(value) {
  const clean = String(value).trim()

  if (!clean) {
    return null
  }

  return Number(clean)
}

function ProfileSetupPage({
  account,
  onCompleted,
  onLogout,
}) {
  const [form, setForm] =
    useState(INITIAL_FORM)

  const [submitting, setSubmitting] =
    useState(false)

  const [error, setError] =
    useState('')

  const updateField = (
    field,
    value
  ) => {
    setForm((current) => ({
      ...current,
      [field]: value,
    }))
  }

  const handleSubmit = async (
    event
  ) => {
    event.preventDefault()

    setError('')
    setSubmitting(true)

    const payload = {
      nationality:
        form.nationality.trim(),

      current_education_level:
        form.current_education_level.trim(),

      target_degree_level:
        form.target_degree_level.trim(),

      preferred_major:
        form.preferred_major.trim(),

      gpa: toOptionalNumber(
        form.gpa
      ),

      gpa_scale: toOptionalNumber(
        form.gpa_scale
      ),

      ielts_score: toOptionalNumber(
        form.ielts_score
      ),

      toefl_score: toOptionalNumber(
        form.toefl_score
      ),

      annual_budget: toOptionalNumber(
        form.annual_budget
      ),

      budget_currency:
        form.annual_budget
          ? form.budget_currency.trim()
          : null,

      preferred_countries:
        form.preferred_countries,

      scholarship_required:
        form.scholarship_required,

      preferred_funding_type:
        form.scholarship_required
          ? form.preferred_funding_type.trim()
          : null,

      preferred_intake:
        form.preferred_intake.trim()
          || null,
    }

    try {
      const response = await authFetch(
        '/api/me/profile',
        {
          method: 'POST',
          headers: {
            'Content-Type':
              'application/json',
          },
          body: JSON.stringify(
            payload
          ),
        }
      )

      if (!response.ok) {
        throw new Error(
          await readApiError(
            response,
            'Unable to complete your profile.'
          )
        )
      }

      await response.json()

      await onCompleted()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to complete your profile.'
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="profile-setup-page">
      <div className="profile-setup-shell">

        <header className="profile-setup-header">
          <div>
            <img
        className="edupath-auth-logo-image"
        src={EduPathLogoMark}
        alt="EduPath logo"
      />

            <div>
              <strong>EduPath</strong>

              <p>
                Student profile setup
              </p>
            </div>
          </div>

          <button
            type="button"
            className="profile-setup-logout"
            onClick={onLogout}
          >
            Log out
          </button>
        </header>

        <div className="profile-setup-layout">

          <aside className="profile-setup-intro">
            <p className="profile-setup-eyebrow">
              STEP 2 OF 2
            </p>

            <h1>
              Tell us about your
              education goals.
            </h1>

            <p>
              Hi{' '}
              <strong>
                {account?.full_name}
              </strong>
              . We use this information
              to generate programs and
              scholarships that match
              your background.
            </p>

            <div className="profile-setup-progress">
              <div>
                <span>&#10003;</span>

                <div>
                  <strong>
                    Account created
                  </strong>

                  <p>
                    Your login is ready.
                  </p>
                </div>
              </div>

              <div className="active">
                <span>2</span>

                <div>
                  <strong>
                    Academic profile
                  </strong>

                  <p>
                    Add your goals and
                    preferences.
                  </p>
                </div>
              </div>
            </div>
          </aside>

          <section className="profile-setup-card">

            <div className="profile-setup-card-heading">
              <h2>
                Complete your profile
              </h2>

              <p>
                Required fields are marked
                with *.
              </p>
            </div>

            {error && (
              <div
                className="profile-setup-error"
                role="alert"
              >
                {error}
              </div>
            )}

            <form
              className="profile-setup-form"
              onSubmit={handleSubmit}
            >

              <div className="profile-setup-grid">

                <label>
                  <span>
                    Nationality *
                  </span>

                  <input
                    value={
                      form.nationality
                    }
                    onChange={(event) =>
                      updateField(
                        'nationality',
                        event.target.value
                      )
                    }
                    required
                  />
                </label>

                <label>
                  <span>
                    Current education *
                  </span>

                  <select
                    value={
                      form.current_education_level
                    }
                    onChange={(event) =>
                      updateField(
                        'current_education_level',
                        event.target.value
                      )
                    }
                    required
                  >
                    <option value="">
                      Select level
                    </option>

                    <option value="High School">
                      High School
                    </option>

                    <option value="Diploma">
                      Diploma
                    </option>

                    <option value="Bachelor's">
                      Bachelor's
                    </option>

                    <option value="Master's">
                      Master's
                    </option>
                  </select>
                </label>

                <label>
                  <span>
                    Target degree *
                  </span>

                  <select
                    value={
                      form.target_degree_level
                    }
                    onChange={(event) =>
                      updateField(
                        'target_degree_level',
                        event.target.value
                      )
                    }
                    required
                  >
                    <option value="">
                      Select degree
                    </option>

                    <option value="Bachelor">
                      Bachelor's
                    </option>

                    <option value="Master">
                      Master's
                    </option>

                    <option value="PhD">
                      PhD / Doctoral
                    </option>
                  </select>
                </label>

                <label>
                  <span>
                    Preferred major *
                  </span>

                  <input
                    value={
                      form.preferred_major
                    }
                    onChange={(event) =>
                      updateField(
                        'preferred_major',
                        event.target.value
                      )
                    }
                    placeholder="Computer Science"
                    required
                  />
                </label>

                <label>
                  <span>GPA</span>

                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={form.gpa}
                    onChange={(event) =>
                      updateField(
                        'gpa',
                        event.target.value
                      )
                    }
                    placeholder="3.5"
                  />
                </label>

                <label>
                  <span>GPA scale</span>

                  <input
                    type="number"
                    step="0.01"
                    min="0.1"
                    value={
                      form.gpa_scale
                    }
                    onChange={(event) =>
                      updateField(
                        'gpa_scale',
                        event.target.value
                      )
                    }
                    placeholder="4.0"
                  />
                </label>

                <label>
                  <span>
                    IELTS score
                  </span>

                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    max="9"
                    value={
                      form.ielts_score
                    }
                    onChange={(event) =>
                      updateField(
                        'ielts_score',
                        event.target.value
                      )
                    }
                    placeholder="6.5"
                  />
                </label>

                <label>
                  <span>
                    TOEFL score
                  </span>

                  <input
                    type="number"
                    min="0"
                    max="120"
                    value={
                      form.toefl_score
                    }
                    onChange={(event) =>
                      updateField(
                        'toefl_score',
                        event.target.value
                      )
                    }
                    placeholder="90"
                  />
                </label>

                <label>
                  <span>
                    Annual budget
                  </span>

                  <input
                    type="number"
                    min="0"
                    value={
                      form.annual_budget
                    }
                    onChange={(event) =>
                      updateField(
                        'annual_budget',
                        event.target.value
                      )
                    }
                    placeholder="18000"
                  />
                </label>

                <label>
                  <span>
                    Budget currency
                  </span>

                  <select
                    value={
                      form.budget_currency
                    }
                    onChange={(event) =>
                      updateField(
                        'budget_currency',
                        event.target.value
                      )
                    }
                  >
                    <option value="USD">
                      USD
                    </option>

                    <option value="JPY">
                      JPY
                    </option>

                    <option value="MMK">
                      MMK
                    </option>
                  </select>
                </label>

                <label>
                  <span>
                    Preferred country *
                  </span>

                  <select
                    value={
                      form.preferred_countries[0]
                    }
                    onChange={(event) =>
                      updateField(
                        'preferred_countries',
                        [
                          event.target.value
                        ]
                      )
                    }
                    required
                  >
                    <option value="Brunei">
                      Brunei
                    </option>

                    <option value="Cambodia">
                      Cambodia
                    </option>

                    <option value="China">
                      China
                    </option>

                    <option value="Hong Kong">
                      Hong Kong
                    </option>

                    <option value="Indonesia">
                      Indonesia
                    </option>

                    <option value="Japan">
                      Japan
                    </option>

                    <option value="Laos">
                      Laos
                    </option>

                    <option value="Macau">
                      Macau
                    </option>

                    <option value="Malaysia">
                      Malaysia
                    </option>

                    <option value="Mongolia">
                      Mongolia
                    </option>

                    <option value="Myanmar">
                      Myanmar
                    </option>

                    <option value="Philippines">
                      Philippines
                    </option>

                    <option value="Singapore">
                      Singapore
                    </option>

                    <option value="South Korea">
                      South Korea
                    </option>

                    <option value="Taiwan">
                      Taiwan
                    </option>

                    <option value="Thailand">
                      Thailand
                    </option>

                    <option value="Timor-Leste">
                      Timor-Leste
                    </option>

                    <option value="Vietnam">
                      Vietnam
                    </option>

                    </select>
                </label>

                <label>
                  <span>
                    Preferred intake
                  </span>

                  <input
                    value={
                      form.preferred_intake
                    }
                    onChange={(event) =>
                      updateField(
                        'preferred_intake',
                        event.target.value
                      )
                    }
                    placeholder="2027"
                  />
                </label>

              </div>

              <label className="profile-setup-checkbox">
                <input
                  type="checkbox"
                  checked={
                    form.scholarship_required
                  }
                  onChange={(event) =>
                    updateField(
                      'scholarship_required',
                      event.target.checked
                    )
                  }
                />

                <span>
                  I need scholarship
                  opportunities.
                </span>
              </label>

              {form.scholarship_required && (
                <label className="profile-setup-full">
                  <span>
                    Preferred funding type *
                  </span>

                  <select
                    value={
                      form.preferred_funding_type
                    }
                    onChange={(event) =>
                      updateField(
                        'preferred_funding_type',
                        event.target.value
                      )
                    }
                    required
                  >
                    <option value="Fully Funded">
                      Fully Funded
                    </option>

                    <option value="Partial Funding">
                      Partial Funding
                    </option>

                    <option value="Tuition Waiver">
                      Tuition Waiver
                    </option>
                  </select>
                </label>
              )}

              <button
                className="profile-setup-submit"
                type="submit"
                disabled={submitting}
              >
                {submitting
                  ? 'Saving profile...'
                  : 'Complete Profile'}
              </button>

            </form>
          </section>
        </div>
      </div>
    </div>
  )
}

export default ProfileSetupPage
