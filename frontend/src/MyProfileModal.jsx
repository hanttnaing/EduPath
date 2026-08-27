import { useEffect, useState } from 'react'
import {
  authFetch,
  readApiError,
} from './api'
import './MyProfileModal.css'

const TARGET_DEGREE_OPTIONS = [
  {
    value: 'Diploma',
    label: 'Diploma',
  },
  {
    value: 'Bachelor',
    label: "Bachelor's",
  },
  {
    value: 'Master',
    label: "Master's",
  },
  {
    value: 'PhD',
    label: 'PhD / Doctoral',
  },
]

const EAST_SOUTHEAST_ASIA_DESTINATIONS = [
  'Brunei',
  'Cambodia',
  'China',
  'Hong Kong',
  'Indonesia',
  'Japan',
  'Laos',
  'Macau',
  'Malaysia',
  'Mongolia',
  'Myanmar',
  'Philippines',
  'Singapore',
  'South Korea',
  'Taiwan',
  'Thailand',
  'Timor-Leste',
  'Vietnam',
]

function normalizeTargetDegree(value) {
  const clean = String(
    value || ''
  )
    .trim()
    .toLowerCase()

  if (clean === 'diploma') {
    return 'Diploma'
  }

  if (
    clean === 'bachelor' ||
    clean === "bachelor's" ||
    clean === 'bachelors'
  ) {
    return 'Bachelor'
  }

  if (
    clean === 'master' ||
    clean === "master's" ||
    clean === 'masters'
  ) {
    return 'Master'
  }

  if (
    clean === 'phd' ||
    clean === 'doctoral' ||
    clean === 'doctorate'
  ) {
    return 'PhD'
  }

  return value || ''
}


const EMPTY_PROFILE = {
  nationality: '',
  current_education_level: '',
  target_degree_level: '',
  preferred_major: '',
  gpa: '',
  gpa_scale: '',
  ielts_score: '',
  toefl_score: '',
  annual_budget: '',
  budget_currency: 'USD',
  preferred_countries: [],
  scholarship_required: false,
  preferred_funding_type: '',
  preferred_intake: '',
}

function toFormProfile(profile) {
  return {
    ...EMPTY_PROFILE,
    ...profile,
    target_degree_level:
      normalizeTargetDegree(
        profile?.target_degree_level
      ),
    gpa: profile?.gpa ?? '',
    gpa_scale: profile?.gpa_scale ?? '',
    ielts_score: profile?.ielts_score ?? '',
    toefl_score: profile?.toefl_score ?? '',
    annual_budget:
      profile?.annual_budget ?? '',
    preferred_countries:
      Array.isArray(
        profile?.preferred_countries
      )
        ? profile.preferred_countries
        : [],
  }
}

function optionalNumber(value) {
  const clean = String(value).trim()

  if (!clean) {
    return null
  }

  return Number(clean)
}

function MyProfileModal({
  account,
  onClose,
  displayMode = 'modal',
}) {
  const isPageMode =
    displayMode === 'page'
  const [profile, setProfile] =
    useState(EMPTY_PROFILE)

  const [loading, setLoading] =
    useState(true)

  const [saving, setSaving] =
    useState(false)

  const [editing, setEditing] =
    useState(false)

  const [error, setError] =
    useState('')

  const [message, setMessage] =
    useState('')

  const loadProfile = async () => {
    setLoading(true)
    setError('')

    try {
      const response = await authFetch(
        '/api/me/profile'
      )

      if (!response.ok) {
        throw new Error(
          await readApiError(
            response,
            'Unable to load your profile.'
          )
        )
      }

      const data = await response.json()

      setProfile(
        toFormProfile(data)
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load your profile.'
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProfile()
  }, [])

  const updateField = (
    field,
    value
  ) => {
    setProfile((current) => ({
      ...current,
      [field]: value,
    }))
  }

  const handleSave = async () => {
    setSaving(true)
    setError('')
    setMessage('')

    const payload = {
      nationality:
        profile.nationality.trim(),

      current_education_level:
        profile.current_education_level.trim(),

      target_degree_level:
        profile.target_degree_level.trim(),

      preferred_major:
        profile.preferred_major.trim(),

      gpa: optionalNumber(
        profile.gpa
      ),

      gpa_scale: optionalNumber(
        profile.gpa_scale
      ),

      ielts_score: optionalNumber(
        profile.ielts_score
      ),

      toefl_score: optionalNumber(
        profile.toefl_score
      ),

      annual_budget: optionalNumber(
        profile.annual_budget
      ),

      budget_currency:
        profile.annual_budget
          ? profile.budget_currency.trim()
          : null,

      preferred_countries:
        profile.preferred_countries,

      scholarship_required:
        Boolean(
          profile.scholarship_required
        ),

      preferred_funding_type:
        profile.scholarship_required
          ? (
              profile.preferred_funding_type
                ?.trim() || null
            )
          : null,

      preferred_intake:
        profile.preferred_intake
          ?.trim() || null,
    }

    try {
      const response = await authFetch(
        '/api/me/profile',
        {
          method: 'PATCH',
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
            'Unable to update your profile.'
          )
        )
      }

      const result =
        await response.json()

      setProfile(
        toFormProfile(
          result.profile
        )
      )

      setEditing(false)

      setMessage(
        'Profile updated successfully.'
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to update your profile.'
      )
    } finally {
      setSaving(false)
    }
  }

  return (
    <div
      className={
        isPageMode
          ? 'my-profile-page-container'
          : 'my-profile-overlay'
      }
      role={
        isPageMode
          ? undefined
          : 'dialog'
      }
      aria-modal={
        isPageMode
          ? undefined
          : 'true'
      }
    >
      <div
        className={
          isPageMode
            ? 'my-profile-modal my-profile-page'
            : 'my-profile-modal'
        }
      >

        <header className="my-profile-header">
          <div>
            <p className="my-profile-eyebrow">
              MY ACCOUNT
            </p>

            <h2>My Profile</h2>

            <p>
              Manage your academic
              information and preferences.
            </p>
          </div>
          {!isPageMode && (

          <button
            type="button"
            className="my-profile-close"
            onClick={onClose}
            aria-label="Close profile"
          >
            ×
          </button>
          )}
        </header>

        <section className="my-profile-account">
          <div className="my-profile-avatar">
            {(
              account?.full_name?.[0] ||
              account?.email?.[0] ||
              'S'
            ).toUpperCase()}
          </div>

          <div>
            <strong>
              {account?.full_name}
            </strong>

            <p>{account?.email}</p>
          </div>

          <span className="my-profile-role">
            {account?.role || 'student'}
          </span>
        </section>

        {error && (
          <div
            className="my-profile-message error"
            role="alert"
          >
            {error}
          </div>
        )}

        {message && (
          <div className="my-profile-message success">
            {message}
          </div>
        )}

        {loading ? (
          <div className="my-profile-loading">
            Loading your profile...
          </div>
        ) : (
          <>
            <div className="my-profile-toolbar">
              <h3>
                Academic Profile
              </h3>

              {!editing ? (
                <button
                  type="button"
                  className="my-profile-edit-button"
                  onClick={() => {
                    setEditing(true)
                    setMessage('')
                  }}
                >
                  Edit Profile
                </button>
              ) : (
                <button
                  type="button"
                  className="my-profile-cancel-button"
                  onClick={() => {
                    setEditing(false)
                    setMessage('')
                    loadProfile()
                  }}
                >
                  Cancel
                </button>
              )}
            </div>

            <div className="my-profile-grid">

              <label>
                <span>Nationality</span>
                <input
                  value={
                    profile.nationality
                  }
                  disabled={!editing}
                  onChange={(event) =>
                    updateField(
                      'nationality',
                      event.target.value
                    )
                  }
                />
              </label>

              <label>
                <span>
                  Current education
                </span>
                <input
                  value={
                    profile.current_education_level
                  }
                  disabled={!editing}
                  onChange={(event) =>
                    updateField(
                      'current_education_level',
                      event.target.value
                    )
                  }
                />
              </label>

              <label>
                <span>Target degree</span>

                <select
                  value={
                    profile.target_degree_level
                  }
                  disabled={!editing}
                  onChange={(event) =>
                    updateField(
                      'target_degree_level',
                      event.target.value
                    )
                  }
                >
                  <option value="">
                    Select target degree
                  </option>

                  {TARGET_DEGREE_OPTIONS.map(
                    (option) => (
                      <option
                        key={option.value}
                        value={option.value}
                      >
                        {option.label}
                      </option>
                    )
                  )}
                </select>
              </label>

              <label>
                <span>Preferred major</span>
                <input
                  value={
                    profile.preferred_major
                  }
                  disabled={!editing}
                  onChange={(event) =>
                    updateField(
                      'preferred_major',
                      event.target.value
                    )
                  }
                />
              </label>

              <label>
                <span>GPA</span>
                <input
                  type="number"
                  step="0.01"
                  value={profile.gpa}
                  disabled={!editing}
                  onChange={(event) =>
                    updateField(
                      'gpa',
                      event.target.value
                    )
                  }
                />
              </label>

              <label>
                <span>GPA scale</span>
                <input
                  type="number"
                  step="0.01"
                  value={
                    profile.gpa_scale
                  }
                  disabled={!editing}
                  onChange={(event) =>
                    updateField(
                      'gpa_scale',
                      event.target.value
                    )
                  }
                />
              </label>

              <label>
                <span>IELTS</span>
                <input
                  type="number"
                  step="0.5"
                  value={
                    profile.ielts_score
                  }
                  disabled={!editing}
                  onChange={(event) =>
                    updateField(
                      'ielts_score',
                      event.target.value
                    )
                  }
                />
              </label>

              <label>
                <span>TOEFL</span>
                <input
                  type="number"
                  value={
                    profile.toefl_score
                  }
                  disabled={!editing}
                  onChange={(event) =>
                    updateField(
                      'toefl_score',
                      event.target.value
                    )
                  }
                />
              </label>

              <label>
                <span>Annual budget</span>
                <input
                  type="number"
                  value={
                    profile.annual_budget
                  }
                  disabled={!editing}
                  onChange={(event) =>
                    updateField(
                      'annual_budget',
                      event.target.value
                    )
                  }
                />
              </label>

              <label>
                <span>Currency</span>
                <select
                  value={
                    profile.budget_currency
                  }
                  disabled={!editing}
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
                  Preferred country
                </span>

                <select
                  value={
                    profile
                      .preferred_countries?.[0]
                    || ''
                  }
                  disabled={!editing}
                  onChange={(event) =>
                    updateField(
                      'preferred_countries',
                      event.target.value
                        ? [event.target.value]
                        : []
                    )
                  }
                >
                  <option value="">
                    Select preferred country
                  </option>

                  {EAST_SOUTHEAST_ASIA_DESTINATIONS.map(
                    (country) => (
                      <option
                        key={country}
                        value={country}
                      >
                        {country}
                      </option>
                    )
                  )}
                </select>
              </label>

              <label>
                <span>
                  Preferred intake
                </span>
                <input
                  value={
                    profile.preferred_intake
                  }
                  disabled={!editing}
                  onChange={(event) =>
                    updateField(
                      'preferred_intake',
                      event.target.value
                    )
                  }
                />
              </label>

            </div>

            <label className="my-profile-scholarship">
              <input
                type="checkbox"
                checked={
                  profile.scholarship_required
                }
                disabled={!editing}
                onChange={(event) =>
                  updateField(
                    'scholarship_required',
                    event.target.checked
                  )
                }
              />

              <span>
                Scholarship required
              </span>
            </label>

            {profile.scholarship_required && (
              <label className="my-profile-funding">
                <span>
                  Preferred funding type
                </span>

                <select
                  value={
                    profile.preferred_funding_type
                  }
                  disabled={!editing}
                  onChange={(event) =>
                    updateField(
                      'preferred_funding_type',
                      event.target.value
                    )
                  }
                >
                  <option value="">
                    Select funding
                  </option>

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

            {editing && (
              <button
                type="button"
                className="my-profile-save-button"
                onClick={handleSave}
                disabled={saving}
              >
                {saving
                  ? 'Saving...'
                  : 'Save Changes'}
              </button>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default MyProfileModal
