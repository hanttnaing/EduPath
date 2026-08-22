import { useState } from 'react'
import API_BASE_URL from './api'
import './UserProfileModal.css'

const INITIAL_FORM = {
  user_id: '',
  nationality: 'Myanmar',
  current_education_level: '',
  target_degree_level: '',
  preferred_major: '',
  gpa: '',
  gpa_scale: '4.0',
  ielts_score: '',
  toefl_score: '',
  annual_budget: '',
  budget_currency: 'USD',
  preferred_countries: ['Japan'],
  scholarship_required: true,
  preferred_funding_type: '',
  preferred_intake: '',
}

function UserProfileModal({
  onClose,
  onGetRecommendations,
}) {

  const [profileId, setProfileId] =
    useState('user_validation_153')

  const [profileForm, setProfileForm] =
    useState(INITIAL_FORM)

  const [loading, setLoading] =
    useState(false)

  const [message, setMessage] =
    useState('')

  const [error, setError] =
    useState('')

  // =========================
  // SAVED OPPORTUNITIES STATE
  // =========================
  const [
    savedOpportunities,
    setSavedOpportunities,
  ] = useState({
    saved_university_count: 0,
    saved_scholarship_count: 0,
    saved_universities: [],
    saved_scholarships: [],
  })

  const [
    savedLoading,
    setSavedLoading,
  ] = useState(false)

  const [
    savedError,
    setSavedError,
  ] = useState('')


  // =========================
  // RECOMMENDATION HISTORY STATE
  // =========================
  const [
    recommendationHistory,
    setRecommendationHistory,
  ] = useState([])

  const [
    historyLoading,
    setHistoryLoading,
  ] = useState(false)

  const [
    historyError,
    setHistoryError,
  ] = useState('')

  // =========================
  // LOAD SAVED OPPORTUNITIES
  // =========================
  const loadSavedOpportunities =
    async (userId) => {
      const cleanUserId =
        String(userId || '').trim()

      if (!cleanUserId) {
        setSavedOpportunities({
          saved_university_count: 0,
          saved_scholarship_count: 0,
          saved_universities: [],
          saved_scholarships: [],
        })

        return
      }

      try {
        setSavedLoading(true)
        setSavedError('')

        const response = await fetch(
          `${API_BASE_URL}/api/user-profiles/${encodeURIComponent(
            cleanUserId
          )}/saved-opportunities`
        )

        const data =
          await response.json()

        if (!response.ok) {
          throw new Error(
            typeof data.detail ===
              'string'
              ? data.detail
              : 'Unable to load saved opportunities.'
          )
        }

        setSavedOpportunities({
          saved_university_count:
            Number(
              data.saved_university_count
            ) || 0,

          saved_scholarship_count:
            Number(
              data.saved_scholarship_count
            ) || 0,

          saved_universities:
            Array.isArray(
              data.saved_universities
            )
              ? data.saved_universities
              : [],

          saved_scholarships:
            Array.isArray(
              data.saved_scholarships
            )
              ? data.saved_scholarships
              : [],
        })
      } catch (err) {
        setSavedError(
          err.message ||
            'Unable to load saved opportunities.'
        )
      } finally {
        setSavedLoading(false)
      }
    }

  // =========================
  // LOAD RECOMMENDATION HISTORY
  // =========================
  const loadRecommendationHistory =
    async (userId) => {
      const cleanUserId =
        String(userId || '').trim()

      if (!cleanUserId) {
        setRecommendationHistory([])
        return
      }

      try {
        setHistoryLoading(true)
        setHistoryError('')

        const response = await fetch(
          `${API_BASE_URL}/api/user-profiles/${encodeURIComponent(
            cleanUserId
          )}/recommendation-history`
        )

        const data =
          await response.json()

        if (!response.ok) {
          throw new Error(
            typeof data.detail === 'string'
              ? data.detail
              : 'Unable to load recommendation history.'
          )
        }

        setRecommendationHistory(
          Array.isArray(
            data.recommendation_history
          )
            ? data.recommendation_history
            : []
        )
      } catch (err) {
        setHistoryError(
          err.message ||
            'Unable to load recommendation history.'
        )
      } finally {
        setHistoryLoading(false)
      }
    }

  // =========================
  // REMOVE SAVED UNIVERSITY
  // =========================
  const removeSavedUniversity =
    async (universityId) => {
      const userId =
        profileForm.user_id.trim()

      if (!userId || !universityId) {
        return
      }

      try {
        setSavedLoading(true)
        setSavedError('')

        const response = await fetch(
          `${API_BASE_URL}/api/user-profiles/${encodeURIComponent(
            userId
          )}/saved-universities/${encodeURIComponent(
            universityId
          )}`,
          {
            method: 'DELETE',
          }
        )

        const data =
          await response.json()

        if (!response.ok) {
          throw new Error(
            typeof data.detail === 'string'
              ? data.detail
              : 'Unable to remove saved university.'
          )
        }

        await loadSavedOpportunities(
          userId
        )
      } catch (err) {
        setSavedError(
          err.message ||
            'Unable to remove saved university.'
        )
      } finally {
        setSavedLoading(false)
      }
    }


  // =========================
  // REMOVE SAVED SCHOLARSHIP
  // =========================
  const removeSavedScholarship =
    async (scholarshipId) => {
      const userId =
        profileForm.user_id.trim()

      if (!userId || !scholarshipId) {
        return
      }

      try {
        setSavedLoading(true)
        setSavedError('')

        const response = await fetch(
          `${API_BASE_URL}/api/user-profiles/${encodeURIComponent(
            userId
          )}/saved-scholarships/${encodeURIComponent(
            scholarshipId
          )}`,
          {
            method: 'DELETE',
          }
        )

        const data =
          await response.json()

        if (!response.ok) {
          throw new Error(
            typeof data.detail === 'string'
              ? data.detail
              : 'Unable to remove saved scholarship.'
          )
        }

        await loadSavedOpportunities(
          userId
        )
      } catch (err) {
        setSavedError(
          err.message ||
            'Unable to remove saved scholarship.'
        )
      } finally {
        setSavedLoading(false)
      }
    }
  
  // =========================
  // FORM CHANGE HANDLER
  // =========================
  const handleChange = (event) => {
    const {
      name,
      value,
      type,
      checked,
    } = event.target

    setProfileForm((previous) => ({
      ...previous,
      [name]:
        type === 'checkbox'
          ? checked
          : value,
    }))
  }

  // =========================
  // NUMBER CONVERSION
  // =========================
  const numberOrNull = (value) => {
    if (
      value === '' ||
      value === null ||
      value === undefined
    ) {
      return null
    }

    const number = Number(value)

    return Number.isNaN(number)
      ? null
      : number
  }

  // =========================
  // BUILD CREATE PAYLOAD
  // =========================
  const buildCreatePayload = () => ({
    user_id: profileForm.user_id.trim(),

    nationality:
      profileForm.nationality.trim(),

    current_education_level:
      profileForm.current_education_level,

    target_degree_level:
      profileForm.target_degree_level,

    preferred_major:
      profileForm.preferred_major.trim(),

    gpa:
      numberOrNull(profileForm.gpa),

    gpa_scale:
      numberOrNull(profileForm.gpa_scale),

    ielts_score:
      numberOrNull(
        profileForm.ielts_score
      ),

    toefl_score:
      numberOrNull(
        profileForm.toefl_score
      ),

    annual_budget:
      numberOrNull(
        profileForm.annual_budget
      ),

    budget_currency:
      profileForm.budget_currency ||
      null,

    preferred_countries:
      profileForm.preferred_countries,

    scholarship_required:
      profileForm.scholarship_required,

    preferred_funding_type:
      profileForm.preferred_funding_type ||
      null,

    preferred_intake:
      profileForm.preferred_intake.trim() ||
      null,
  })

  // =========================
  // VALIDATION
  // =========================
  const validateCreateForm = () => {
    if (
      profileForm.user_id.trim().length < 3
    ) {
      return 'User ID must contain at least 3 characters.'
    }

    if (
      profileForm.nationality.trim().length < 2
    ) {
      return 'Please enter your nationality.'
    }

    if (
      !profileForm.current_education_level
    ) {
      return 'Please select your current education level.'
    }

    if (
      !profileForm.target_degree_level
    ) {
      return 'Please select your target degree level.'
    }

    if (
      profileForm.preferred_major.trim()
        .length < 2
    ) {
      return 'Please enter your preferred major.'
    }

    if (
      profileForm.preferred_countries
        .length === 0
    ) {
      return 'Please select at least one preferred country.'
    }

    const ielts =
      numberOrNull(
        profileForm.ielts_score
      )

    if (
      ielts !== null &&
      (ielts < 0 || ielts > 9)
    ) {
      return 'IELTS score must be between 0 and 9.'
    }

    const toefl =
      numberOrNull(
        profileForm.toefl_score
      )

    if (
      toefl !== null &&
      (toefl < 0 || toefl > 120)
    ) {
      return 'TOEFL score must be between 0 and 120.'
    }

    return ''
  }

  // =========================
  // CREATE PROFILE
  // =========================
  const createProfile = async () => {
    const validationError =
      validateCreateForm()

    if (validationError) {
      setError(validationError)
      setMessage('')
      return
    }

    try {
      setLoading(true)
      setError('')
      setMessage('')

      const payload =
        buildCreatePayload()

      const response = await fetch(
        `${API_BASE_URL}/api/user-profiles`,
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json',
          },

          body:
            JSON.stringify(payload),
        }
      )

      const data =
        await response.json()

      if (!response.ok) {
        throw new Error(
          typeof data.detail ===
            'string'
            ? data.detail
            : 'Unable to create profile.'
        )
      }

      setProfileId(
        profileForm.user_id.trim()
      )

      await loadSavedOpportunities(
        profileForm.user_id.trim()
      )

      await loadRecommendationHistory(
        profileForm.user_id.trim()
      )

      setMessage(
        `Profile "${profileForm.user_id.trim()}" created successfully.`
      )
    } catch (err) {
      setError(
        err.message ||
          'Unable to create profile.'
      )
    } finally {
      setLoading(false)
    }
  }

  // =========================
  // LOAD PROFILE
  // =========================
  const loadProfile = async () => {
    const userId =
      profileId.trim()

    if (!userId) {
      setError(
        'Please enter a User ID.'
      )

      setMessage('')
      return
    }

    try {
      setLoading(true)
      setError('')
      setMessage('')

      const response = await fetch(
        `${API_BASE_URL}/api/user-profiles/${encodeURIComponent(
          userId
        )}`
      )

      const data =
        await response.json()

      if (!response.ok) {
        throw new Error(
          typeof data.detail ===
            'string'
            ? data.detail
            : 'Unable to load profile.'
        )
      }

      // Supports either:
      // { ...profile fields }
      // or { profile: { ... } }
      const profile =
        data.profile ||
        data.user_profile ||
        data

      setProfileForm({
        user_id:
          profile.user_id || userId,

        nationality:
          profile.nationality || '',

        current_education_level:
          profile.current_education_level ||
          '',

        target_degree_level:
          profile.target_degree_level ||
          '',

        preferred_major:
          profile.preferred_major || '',

        gpa:
          profile.gpa === null ||
          profile.gpa === undefined
            ? ''
            : String(profile.gpa),

        gpa_scale:
          profile.gpa_scale === null ||
          profile.gpa_scale === undefined
            ? ''
            : String(
                profile.gpa_scale
              ),

        ielts_score:
          profile.ielts_score === null ||
          profile.ielts_score ===
            undefined
            ? ''
            : String(
                profile.ielts_score
              ),

        toefl_score:
          profile.toefl_score === null ||
          profile.toefl_score ===
            undefined
            ? ''
            : String(
                profile.toefl_score
              ),

        annual_budget:
          profile.annual_budget ===
            null ||
          profile.annual_budget ===
            undefined
            ? ''
            : String(
                profile.annual_budget
              ),

        budget_currency:
          profile.budget_currency ||
          'USD',

        preferred_countries:
          Array.isArray(
            profile.preferred_countries
          ) &&
          profile.preferred_countries
            .length > 0
            ? profile.preferred_countries
            : ['Japan'],

        scholarship_required:
          Boolean(
            profile.scholarship_required
          ),

        preferred_funding_type:
          profile.preferred_funding_type ||
          '',

        preferred_intake:
          profile.preferred_intake || '',
      })

      await loadSavedOpportunities(
        profile.user_id || userId
      )

      await loadRecommendationHistory(
        profile.user_id || userId
      )

      setMessage(
        `Profile "${userId}" loaded successfully.`
      )
    } catch (err) {
      setError(
        err.message ||
          'Unable to load profile.'
      )
    } finally {
      setLoading(false)
    }
  }

  // =========================
  // UPDATE PROFILE
  // =========================
  const updateProfile = async () => {
    const userId =
      profileForm.user_id.trim() ||
      profileId.trim()

    if (!userId) {
      setError(
        'Please load or enter a User ID first.'
      )

      setMessage('')
      return
    }

    const validationError =
      validateCreateForm()

    if (validationError) {
      setError(validationError)
      setMessage('')
      return
    }

    try {
      setLoading(true)
      setError('')
      setMessage('')

      const createPayload =
        buildCreatePayload()

      // user_id is NOT part of
      // UserProfileUpdate schema.
      const {
        user_id: ignoredUserId,
        ...updatePayload
      } = createPayload

      void ignoredUserId

      const response = await fetch(
        `${API_BASE_URL}/api/user-profiles/${encodeURIComponent(
          userId
        )}`,
        {
          method: 'PATCH',

          headers: {
            'Content-Type':
              'application/json',
          },

          body:
            JSON.stringify(
              updatePayload
            ),
        }
      )

      const data =
        await response.json()

      if (!response.ok) {
        throw new Error(
          typeof data.detail ===
            'string'
            ? data.detail
            : 'Unable to update profile.'
        )
      }

      setProfileId(userId)

      setMessage(
        `Profile "${userId}" updated successfully.`
      )
    } catch (err) {
      setError(
        err.message ||
          'Unable to update profile.'
      )
    } finally {
      setLoading(false)
    }
  }

  // =========================
  // DELETE PROFILE
  // =========================
  const deleteProfile = async () => {
    const userId =
      profileForm.user_id.trim() ||
      profileId.trim()

    if (!userId) {
      setError(
        'Please load a profile first.'
      )

      return
    }

    const confirmed =
      window.confirm(
        `Delete profile "${userId}"? This action cannot be undone.`
      )

    if (!confirmed) {
      return
    }

    try {
      setLoading(true)
      setError('')
      setMessage('')

      const response = await fetch(
        `${API_BASE_URL}/api/user-profiles/${encodeURIComponent(
          userId
        )}`,
        {
          method: 'DELETE',
        }
      )

      if (!response.ok) {
        let detail =
          'Unable to delete profile.'

        try {
          const data =
            await response.json()

          if (
            typeof data.detail ===
            'string'
          ) {
            detail = data.detail
          }
        } catch {
          // Keep default error.
        }

        throw new Error(detail)
      }

      setProfileForm(INITIAL_FORM)

      setProfileId('')

      setSavedOpportunities({
        saved_university_count: 0,
        saved_scholarship_count: 0,
        saved_universities: [],
        saved_scholarships: [],
      })

      setSavedError('')

      setRecommendationHistory([])
      setHistoryError('')

      setMessage(
        `Profile "${userId}" deleted successfully.`
      )
    } catch (err) {
      setError(
        err.message ||
          'Unable to delete profile.'
      )
    } finally {
      setLoading(false)
    }
  }

  // =========================
  // RESET FORM
  // =========================
  const resetForm = () => {
    setProfileForm(
      INITIAL_FORM
    )

    setSavedOpportunities({
      saved_university_count: 0,
      saved_scholarship_count: 0,
      saved_universities: [],
      saved_scholarships: [],
    })

    setSavedError('')

    setRecommendationHistory([])
    setHistoryError('')

    setMessage('')
    setError('')
  }

  // =========================
  // FORMAT HISTORY DATE
  // =========================
  const formatHistoryDate = (value) => {
    if (!value) {
      return 'Date unavailable'
    }

    const [datePart, timePart = ''] =
      String(value).split('T')

    const shortTime =
      timePart.slice(0, 5)

    return shortTime
      ? `${datePart} ${shortTime}`
      : datePart
  }

  // =========================
  // OPEN RECOMMENDATIONS
  // =========================
  const openRecommendations = () => {
    const userId =
      profileForm.user_id.trim()

    if (!userId) {
      setError(
        'Please load or create a profile before generating recommendations.'
      )

      setMessage('')
      return
    }

    setError('')
    setMessage('')

    if (
      typeof onGetRecommendations ===
      'function'
    ) {
      onGetRecommendations(userId)
    }
  }

  return (
    <div
      className="profile-modal-backdrop"
      role="presentation"
    >
      <div
        className="profile-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="profile-modal-title"
      >
        {/* HEADER */}
        <div className="profile-modal-header">
          <div>
            <p className="profile-modal-eyebrow">
              STUDENT PROFILE
            </p>

            <h2 id="profile-modal-title">
              My Profile
            </h2>

            <p className="profile-modal-subtitle">
              Manage your academic
              information and preferences
              for personalized EduPath
              recommendations.
            </p>
          </div>

          <button
            type="button"
            className="profile-modal-close"
            onClick={onClose}
            aria-label="Close My Profile"
          >
            ×
          </button>
        </div>

        {/* LOAD EXISTING PROFILE */}
        <section className="profile-load-section">
          <div className="profile-load-input">
            <label htmlFor="profile-id">
              Existing User ID
            </label>

            <input
              id="profile-id"
              type="text"
              value={profileId}
              onChange={(event) =>
                setProfileId(
                  event.target.value
                )
              }
              placeholder="e.g. user_validation_153"
            />
          </div>

          <button
            type="button"
            className="profile-load-button"
            onClick={loadProfile}
            disabled={loading}
          >
            Load Profile
          </button>
        </section>

        {/* STATUS MESSAGES */}
        {message && (
          <div className="profile-message profile-success">
            {message}
          </div>
        )}

        {error && (
          <div className="profile-message profile-error">
            {error}
          </div>
        )}

        {/* BASIC INFORMATION */}
        <section className="profile-form-section">
          <h3>Academic Profile</h3>

          <div className="profile-form-grid">
            <div className="profile-field">
              <label htmlFor="user-id">
                User ID *
              </label>

              <input
                id="user-id"
                type="text"
                name="user_id"
                value={
                  profileForm.user_id
                }
                onChange={handleChange}
                placeholder="e.g. crystal_001"
              />
            </div>

            <div className="profile-field">
              <label htmlFor="nationality">
                Nationality *
              </label>

              <input
                id="nationality"
                type="text"
                name="nationality"
                value={
                  profileForm.nationality
                }
                onChange={handleChange}
              />
            </div>

            <div className="profile-field">
              <label htmlFor="current-level">
                Current Education Level *
              </label>

              <select
                id="current-level"
                name="current_education_level"
                value={
                  profileForm.current_education_level
                }
                onChange={handleChange}
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

                <option value="PhD">
                  PhD
                </option>
              </select>
            </div>

            <div className="profile-field">
              <label htmlFor="target-level">
                Target Degree Level *
              </label>

              <select
                id="target-level"
                name="target_degree_level"
                value={
                  profileForm.target_degree_level
                }
                onChange={handleChange}
              >
                <option value="">
                  Select degree
                </option>

                <option value="Bachelor's">
                  Bachelor's
                </option>

                <option value="Master's">
                  Master's
                </option>

                <option value="PhD">
                  PhD
                </option>
              </select>
            </div>

            <div className="profile-field profile-field-wide">
              <label htmlFor="preferred-major">
                Preferred Major *
              </label>

              <input
                id="preferred-major"
                type="text"
                name="preferred_major"
                value={
                  profileForm.preferred_major
                }
                onChange={handleChange}
                placeholder="e.g. Computer Science"
              />
            </div>
          </div>
        </section>

        {/* ACADEMIC SCORES */}
        <section className="profile-form-section">
          <h3>Academic Scores</h3>

          <div className="profile-form-grid">
            <div className="profile-field">
              <label htmlFor="gpa">
                GPA
              </label>

              <input
                id="gpa"
                type="number"
                min="0"
                step="0.01"
                name="gpa"
                value={profileForm.gpa}
                onChange={handleChange}
                placeholder="3.40"
              />
            </div>

            <div className="profile-field">
              <label htmlFor="gpa-scale">
                GPA Scale
              </label>

              <input
                id="gpa-scale"
                type="number"
                min="0.1"
                step="0.1"
                name="gpa_scale"
                value={
                  profileForm.gpa_scale
                }
                onChange={handleChange}
                placeholder="4.0"
              />
            </div>

            <div className="profile-field">
              <label htmlFor="ielts">
                IELTS Score
              </label>

              <input
                id="ielts"
                type="number"
                min="0"
                max="9"
                step="0.5"
                name="ielts_score"
                value={
                  profileForm.ielts_score
                }
                onChange={handleChange}
                placeholder="6.5"
              />
            </div>

            <div className="profile-field">
              <label htmlFor="toefl">
                TOEFL Score
              </label>

              <input
                id="toefl"
                type="number"
                min="0"
                max="120"
                step="1"
                name="toefl_score"
                value={
                  profileForm.toefl_score
                }
                onChange={handleChange}
                placeholder="90"
              />
            </div>
          </div>
        </section>

        {/* STUDY PREFERENCES */}
        <section className="profile-form-section">
          <h3>Study Preferences</h3>

          <div className="profile-form-grid">
            <div className="profile-field">
              <label htmlFor="annual-budget">
                Annual Budget
              </label>

              <input
                id="annual-budget"
                type="number"
                min="0"
                step="1"
                name="annual_budget"
                value={
                  profileForm.annual_budget
                }
                onChange={handleChange}
                placeholder="15000"
              />
            </div>

            <div className="profile-field">
              <label htmlFor="budget-currency">
                Currency
              </label>

              <select
                id="budget-currency"
                name="budget_currency"
                value={
                  profileForm.budget_currency
                }
                onChange={handleChange}
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
            </div>

            <div className="profile-field">
              <label htmlFor="funding-type">
                Preferred Funding
              </label>

              <select
                id="funding-type"
                name="preferred_funding_type"
                value={
                  profileForm.preferred_funding_type
                }
                onChange={handleChange}
              >
                <option value="">
                  Any Funding
                </option>

                <option value="Fully Funded">
                  Fully Funded
                </option>

                <option value="Partially Funded">
                  Partially Funded
                </option>

                <option value="Self Funded">
                  Self Funded
                </option>
              </select>
            </div>

            <div className="profile-field">
              <label htmlFor="preferred-intake">
                Preferred Intake
              </label>

              <input
                id="preferred-intake"
                type="text"
                name="preferred_intake"
                value={
                  profileForm.preferred_intake
                }
                onChange={handleChange}
                placeholder="e.g. 2027"
              />
            </div>
          </div>

          <div className="profile-country-section">
            <p className="profile-country-label">
              Preferred Country *
            </p>

            <label className="profile-country-option">
              <input
                type="checkbox"
                checked={
                  profileForm.preferred_countries.includes(
                    'Japan'
                  )
                }
                onChange={() => {
                  setProfileForm(
                    (previous) => ({
                      ...previous,

                      preferred_countries:
                        previous.preferred_countries.includes(
                          'Japan'
                        )
                          ? []
                          : ['Japan'],
                    })
                  )
                }}
              />

              <span>Japan</span>
            </label>

            <p className="profile-country-note">
              EduPath MVP currently
              contains Japan data.
              Additional countries can be
              added later.
            </p>
          </div>

          <label className="profile-scholarship-option">
            <input
              type="checkbox"
              name="scholarship_required"
              checked={
                profileForm.scholarship_required
              }
              onChange={handleChange}
            />

            <span>
              I require scholarship support
            </span>
          </label>
        </section>

        {/* =========================
            SAVED OPPORTUNITIES
        ========================== */}

        <section className="profile-saved-section">
          <div className="profile-saved-header">
            <div>
              <p className="profile-saved-eyebrow">
                SAVED OPPORTUNITIES
              </p>

              <h3>
                My Saved Options
              </h3>

              <p>
                Review universities and
                scholarships that you saved
                from your recommendation
                results.
              </p>
            </div>

            <button
              type="button"
              className="profile-saved-refresh"
              disabled={
                savedLoading ||
                !profileForm.user_id.trim()
              }
              onClick={() =>
                loadSavedOpportunities(
                  profileForm.user_id
                )
              }
            >
              {savedLoading
                ? 'Loading...'
                : '↻ Refresh'}
            </button>
          </div>

          {savedError && (
            <div className="profile-saved-error">
              {savedError}
            </div>
          )}

          <div className="profile-saved-counts">
            <div>
              <span>
                Saved Universities
              </span>

              <strong>
                {
                  savedOpportunities.saved_university_count
                }
              </strong>
            </div>

            <div>
              <span>
                Saved Scholarships
              </span>

              <strong>
                {
                  savedOpportunities.saved_scholarship_count
                }
              </strong>
            </div>
          </div>

          <div className="profile-saved-columns">
            {/* SAVED UNIVERSITIES */}
            <div className="profile-saved-column">
              <h4>
                🎓 Universities
              </h4>

              {savedLoading && (
                <p className="profile-saved-empty">
                  Loading saved universities...
                </p>
              )}

              {!savedLoading &&
                savedOpportunities
                  .saved_universities
                  .length === 0 && (
                  <p className="profile-saved-empty">
                    No universities saved yet.
                  </p>
                )}

              {!savedLoading &&
                savedOpportunities
                  .saved_universities
                  .map((university) => (
                    <article
                      className="profile-saved-card"
                      key={
                        university.university_id
                      }
                    >
                      <div>
                        <h5>
                          {
                            university.university_name ||
                            university.university_id
                          }
                        </h5>

                        <p>
                          {university.city ||
                            'City unavailable'}

                          {university.country_id
                            ? ` • ${university.country_id}`
                            : ''}
                        </p>
                      </div>

                      <button
                        type="button"
                        className="profile-saved-remove"
                        disabled={
                          savedLoading
                        }
                        onClick={() =>
                          removeSavedUniversity(
                            university.university_id
                          )
                        }
                      >
                        Remove
                      </button>
                    </article>
                  ))}
            </div>

            {/* SAVED SCHOLARSHIPS */}
            <div className="profile-saved-column">
              <h4>
                🎓 Scholarships
              </h4>

              {savedLoading && (
                <p className="profile-saved-empty">
                  Loading saved scholarships...
                </p>
              )}

              {!savedLoading &&
                savedOpportunities
                  .saved_scholarships
                  .length === 0 && (
                  <p className="profile-saved-empty">
                    No scholarships saved yet.
                  </p>
                )}

              {!savedLoading &&
                savedOpportunities
                  .saved_scholarships
                  .map((scholarship) => (
                    <article
                      className="profile-saved-card"
                      key={
                        scholarship.scholarship_id
                      }
                    >
                      <div>
                        <h5>
                          {
                            scholarship.scholarship_name ||
                            scholarship.scholarship_id
                          }
                        </h5>

                        <p>
                          {scholarship.provider_name ||
                            'Provider unavailable'}

                          {scholarship.funding_type
                            ? ` • ${scholarship.funding_type}`
                            : ''}
                        </p>

                        {scholarship.application_deadline && (
                          <p className="profile-saved-deadline">
                            Deadline:{' '}
                            {String(
                              scholarship.application_deadline
                            ).slice(0, 10)}
                          </p>
                        )}
                      </div>

                      <button
                        type="button"
                        className="profile-saved-remove"
                        disabled={
                          savedLoading
                        }
                        onClick={() =>
                          removeSavedScholarship(
                            scholarship.scholarship_id
                          )
                        }
                      >
                        Remove
                      </button>
                    </article>
                  ))}
            </div>
          </div>
        </section>

        {/* =========================
            RECOMMENDATION HISTORY
        ========================== */}

        <section className="profile-history-section">
          <div className="profile-history-header">
            <div>
              <p className="profile-history-eyebrow">
                RECOMMENDATION HISTORY
              </p>

              <h3>
                Previous Recommendation Runs
              </h3>

              <p>
                Review when programme and
                scholarship recommendations
                were generated for this profile.
              </p>
            </div>

            <button
              type="button"
              className="profile-history-refresh"
              disabled={
                historyLoading ||
                !profileForm.user_id.trim()
              }
              onClick={() =>
                loadRecommendationHistory(
                  profileForm.user_id
                )
              }
            >
              {historyLoading
                ? 'Loading...'
                : '↻ Refresh'}
            </button>
          </div>

          <div className="profile-history-summary">
            <span>
              Total Recommendation Runs
            </span>

            <strong>
              {recommendationHistory.length}
            </strong>
          </div>

          {historyError && (
            <div className="profile-history-error">
              {historyError}
            </div>
          )}

          {historyLoading && (
            <div className="profile-history-empty">
              Loading recommendation history...
            </div>
          )}

          {!historyLoading &&
            recommendationHistory.length === 0 && (
              <div className="profile-history-empty">
                No recommendation history yet.
              </div>
            )}

          {!historyLoading &&
            recommendationHistory.length > 0 && (
              <div className="profile-history-list">
                {[
                  ...recommendationHistory,
                ]
                  .reverse()
                  .map((historyItem) => {
                    const isProgram =
                      historyItem
                        .recommendation_type ===
                      'program'

                    return (
                      <article
                        className="profile-history-card"
                        key={
                          historyItem.history_id
                        }
                      >
                        <div
                          className={`profile-history-type ${
                            isProgram
                              ? 'program'
                              : 'scholarship'
                          }`}
                        >
                          {isProgram
                            ? '🎓'
                            : '💰'}
                        </div>

                        <div className="profile-history-content">
                          <div className="profile-history-card-top">
                            <h4>
                              {isProgram
                                ? 'Programme Recommendations'
                                : 'Scholarship Recommendations'}
                            </h4>

                            <span
                              className={`profile-history-badge ${
                                isProgram
                                  ? 'program'
                                  : 'scholarship'
                              }`}
                            >
                              {isProgram
                                ? 'PROGRAM'
                                : 'SCHOLARSHIP'}
                            </span>
                          </div>

                          <p>
                            Generated:{' '}
                            <strong>
                              {formatHistoryDate(
                                historyItem.created_at
                              )}
                            </strong>
                          </p>

                          <div className="profile-history-meta">
                            <span>
                              Results
                              <strong>
                                {
                                  historyItem.result_count
                                }
                              </strong>
                            </span>

                            <span>
                              Saved Run
                              <strong>
                                ✓
                              </strong>
                            </span>
                          </div>
                        </div>
                      </article>
                    )
                  })}
              </div>
            )}
        </section>
        
        
        {/* PERSONALIZED RECOMMENDATIONS */}
        <section className="profile-recommendation-cta">
          <div>
            <p className="profile-recommendation-label">
              PERSONALIZED MATCHING
            </p>

            <h3>
              Ready to find your best options?
            </h3>

            <p>
              Use your saved academic profile to
              generate ranked programme and
              scholarship recommendations.
            </p>
          </div>

          <button
            type="button"
            className="profile-recommendation-button"
            onClick={openRecommendations}
            disabled={loading}
          >
            <span>✨</span>

            <span>
              Get My Recommendations
            </span>
          </button>
        </section>

        {/* ACTIONS */}
        <div className="profile-modal-actions">
          <button
            type="button"
            className="profile-reset-button"
            onClick={resetForm}
            disabled={loading}
          >
            Reset
          </button>

          <button
            type="button"
            className="profile-delete-button"
            onClick={deleteProfile}
            disabled={loading}
          >
            Delete Profile
          </button>

          <button
            type="button"
            className="profile-update-button"
            onClick={updateProfile}
            disabled={loading}
          >
            Update Profile
          </button>

          <button
            type="button"
            className="profile-create-button"
            onClick={createProfile}
            disabled={loading}
          >
            {loading
              ? 'Please wait...'
              : 'Create Profile'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default UserProfileModal