import { useEffect, useState } from 'react'
import { authFetch } from './api'
import './RecommendationModal.css'

function RecommendationModal({
  onClose,
}) {
  const [activeTab, setActiveTab] =
    useState('programs')

  const [
    recommendationsRequested,
    setRecommendationsRequested,
  ] = useState(false)

  const [programData, setProgramData] =
    useState(null)

  const [
    scholarshipData,
    setScholarshipData,
  ] = useState(null)

  const [loading, setLoading] =
    useState(false)

  const [error, setError] =
    useState('')

  // =========================
  // SAVED OPPORTUNITIES STATE
  // =========================
  const [
    savedUniversityIds,
    setSavedUniversityIds,
  ] = useState([])

  const [
    savedProgramIds,
    setSavedProgramIds,
  ] = useState([])


  const [
    savedScholarshipIds,
    setSavedScholarshipIds,
  ] = useState([])

  const [
    savingItem,
    setSavingItem,
  ] = useState('')

  // =========================
  // LOAD SAVED OPPORTUNITIES
  // =========================
  const loadSavedOpportunities =
    async () => {
      const response = await authFetch(
        '/api/me/saved'
      )

      if (!response.ok) {
        throw new Error(
          'Unable to load saved opportunities.'
        )
      }

      const data = await response.json()

      setSavedUniversityIds(
        Array.isArray(
          data.saved_universities
        )
          ? data.saved_universities
              .map(
                (item) =>
                  item.university_id
              )
              .filter(Boolean)
          : []
      )

      setSavedProgramIds(
        Array.isArray(
          data.saved_programs
        )
          ? data.saved_programs
              .map(
                (item) =>
                  item.program_id
              )
              .filter(Boolean)
          : []
      )

      setSavedScholarshipIds(
        Array.isArray(
          data.saved_scholarships
        )
          ? data.saved_scholarships
              .map(
                (item) =>
                  item.scholarship_id
              )
              .filter(Boolean)
          : []
      )
    }

  // =========================
  // LOAD RECOMMENDATIONS
  // =========================
  useEffect(() => {
    if (!recommendationsRequested) {
      return
    }

    const loadRecommendations =
      async () => {
        try {
          setLoading(true)
          setError('')

          const [
            programResponse,
            scholarshipResponse,
          ] = await Promise.all([
            authFetch(
              '/api/me/recommendations/programs?top_k=5'
            ),

            authFetch(
              '/api/me/recommendations/scholarships?top_k=5'
            ),
          ])

          if (!programResponse.ok) {
            const data =
              await programResponse.json()

            throw new Error(
              typeof data.detail ===
                'string'
                ? data.detail
                : 'Unable to load programme recommendations.'
            )
          }

          if (!scholarshipResponse.ok) {
            const data =
              await scholarshipResponse.json()

            throw new Error(
              typeof data.detail ===
                'string'
                ? data.detail
                : 'Unable to load scholarship recommendations.'
            )
          }

          const [
            programResult,
            scholarshipResult,
          ] = await Promise.all([
            programResponse.json(),
            scholarshipResponse.json(),
          ])

          setProgramData(programResult)

          setScholarshipData(
            scholarshipResult
          )

          await loadSavedOpportunities()

        } catch (err) {
          setError(
            err.message ||
              'Unable to generate recommendations.'
          )
        } finally {
          setLoading(false)
        }
      }

    loadRecommendations()
  }, [recommendationsRequested])

  // =========================
  // SCORE HELPERS
  // =========================
  const getScoreClass = (score) => {
    if (score >= 80) {
      return 'recommendation-score-high'
    }

    if (score >= 60) {
      return 'recommendation-score-medium'
    }

    return 'recommendation-score-low'
  }

  const formatScore = (score) => {
    const numericScore =
      Number(score)

    if (Number.isNaN(numericScore)) {
      return '0.00'
    }

    return numericScore.toFixed(2)
  }

  // =========================
  // SAVE / UNSAVE UNIVERSITY
  // =========================
  const toggleUniversitySave =
    async (universityId) => {
      if (!universityId) {
        return
      }

      const isSaved =
        savedUniversityIds.includes(
          universityId
        )

      const actionKey =
        `university-${universityId}`

      try {
        setSavingItem(actionKey)
        setError('')

        const response = await authFetch(
          `/api/me/saved/universities/${encodeURIComponent(
            universityId
          )}`,
          {
            method:
              isSaved
                ? 'DELETE'
                : 'POST',
          }
        )

        if (!response.ok) {
          let message =
            isSaved
              ? 'Unable to remove university.'
              : 'Unable to save university.'

          try {
            const data =
              await response.json()

            if (
              typeof data.detail ===
              'string'
            ) {
              message = data.detail
            }
          } catch {
            // Keep default message.
          }

          throw new Error(message)
        }

        await loadSavedOpportunities()
      } catch (err) {
        setError(
          err.message ||
            'Unable to update saved university.'
        )
      } finally {
        setSavingItem('')
      }
    }

  // =========================
  // SAVE / UNSAVE SCHOLARSHIP
  // =========================
  const toggleScholarshipSave =
    async (scholarshipId) => {
      if (!scholarshipId) {
        return
      }

      const isSaved =
        savedScholarshipIds.includes(
          scholarshipId
        )

      const actionKey =
        `scholarship-${scholarshipId}`

      try {
        setSavingItem(actionKey)
        setError('')

        const response = await authFetch(
          `/api/me/saved/scholarships/${encodeURIComponent(
            scholarshipId
          )}`,
          {
            method:
              isSaved
                ? 'DELETE'
                : 'POST',
          }
        )

        if (!response.ok) {
          let message =
            isSaved
              ? 'Unable to remove scholarship.'
              : 'Unable to save scholarship.'

          try {
            const data =
              await response.json()

            if (
              typeof data.detail ===
              'string'
            ) {
              message = data.detail
            }
          } catch {
            // Keep default message.
          }

          throw new Error(message)
        }

        await loadSavedOpportunities()
      } catch (err) {
        setError(
          err.message ||
            'Unable to update saved scholarship.'
        )
      } finally {
        setSavingItem('')
      }
    }

  // =========================
  // SAVE / UNSAVE PROGRAM
  // =========================
  const toggleProgramSave =
    async (programId) => {
      if (!programId) {
        return
      }

      const isSaved =
        savedProgramIds.includes(
          programId
        )

      const actionKey =
        `program-${programId}`

      try {
        setSavingItem(actionKey)
        setError('')

        const response = await authFetch(
          `/api/me/saved/programs/${encodeURIComponent(
            programId
          )}`,
          {
            method:
              isSaved
                ? 'DELETE'
                : 'POST',
          }
        )

        if (!response.ok) {
          let message =
            isSaved
              ? 'Unable to remove program.'
              : 'Unable to save program.'

          try {
            const data =
              await response.json()

            if (
              typeof data.detail ===
              'string'
            ) {
              message = data.detail
            }
          } catch {
            // Keep default message.
          }

          throw new Error(message)
        }

        await loadSavedOpportunities()
      } catch (err) {
        setError(
          err.message ||
            'Unable to update saved program.'
        )
      } finally {
        setSavingItem('')
      }
    }

  // =========================
  // PROGRAM CARD
  // =========================
  const renderProgram = (
    recommendation,
    index
  ) => (
    <article
      className="recommendation-card"
      key={recommendation.program_id}
    >
      <div className="recommendation-card-top">
        <div>
          <p className="recommendation-rank">
            #{index + 1} Recommended Programme
          </p>

          <h3>
            {recommendation.program_name}
          </h3>

          <p className="recommendation-university">
            {
              recommendation.university_name
            }
          </p>

          <p className="recommendation-location">
            {recommendation.country_name}
            {' • '}
            {recommendation.degree_level}
          </p>
        </div>

        <div
          className={`recommendation-score ${getScoreClass(
            recommendation.match_score
          )}`}
        >
          <strong>
            {formatScore(
              recommendation.match_score
            )}
          </strong>

          <span>/ 100</span>
        </div>
      </div>

      <div className="recommendation-meta-grid">
        <div>
          <span>Field</span>

          <strong>
            {recommendation.field_of_study ||
              'Not available'}
          </strong>
        </div>

        <div>
          <span>Language</span>

          <strong>
            {
              recommendation.language_of_instruction ||
              'Not available'
            }
          </strong>
        </div>

        <div>
          <span>Tuition</span>

          <strong>
            {recommendation.tuition_fee ??
              'N/A'}{' '}
            {
              recommendation.tuition_currency ||
              ''
            }
          </strong>
        </div>

        <div>
          <span>Known Status</span>

          <strong>
            {
              recommendation.known_eligibility_status ||
              'Requires checking'
            }
          </strong>
        </div>
      </div>

      <div className="recommendation-details-grid">
        <section className="recommendation-detail-box">
          <h4>Why Recommended</h4>

          <ul className="recommendation-reasons">
            {(
              recommendation.match_reasons ||
              recommendation.why_recommended ||
              []
            ).map((reason) => (
              <li key={reason}>
                {reason}
              </li>
            ))}
          </ul>
        </section>

        <section className="recommendation-detail-box">
          <h4>Requirement Gaps</h4>

          <ul className="recommendation-gaps">
            {(
              recommendation.requirement_gaps ||
              []
            ).map((gap) => (
              <li key={gap}>
                {gap}
              </li>
            ))}
          </ul>
        </section>
      </div>

      <section className="recommendation-breakdown">
        <h4>Match Score Breakdown</h4>

        <div className="recommendation-breakdown-grid">
          {Object.entries(
            recommendation.score_breakdown ||
              {}
          ).map(([key, value]) => (
            <div key={key}>
              <span>
                {key
                  .replaceAll('_', ' ')
                  .replace(/\b\w/g, (letter) =>
                    letter.toUpperCase()
                  )}
              </span>

              <strong>
                {Number(value).toFixed(2)}
              </strong>
            </div>
          ))}
        </div>
      </section>

      <div className="recommendation-card-actions">

        <button
          type="button"
          className={`recommendation-save-button ${
            savedProgramIds.includes(
              recommendation.program_id
            )
              ? 'saved'
              : ''
          }`}
          onClick={() =>
            toggleProgramSave(
              recommendation.program_id
            )
          }
          disabled={
            savingItem ===
            `program-${recommendation.program_id}`
          }
        >
          {savingItem ===
          `program-${recommendation.program_id}`
            ? 'Updating...'
            : savedProgramIds.includes(
                recommendation.program_id
              )
              ? 'Saved Programme'
              : 'Save Programme'}
        </button>

        {recommendation.program_url && (
          <a
            className="recommendation-link"
            href={
              recommendation.program_url
            }
            target="_blank"
            rel="noreferrer"
          >
            Visit Official Programme Page ↗
          </a>
        )}
      </div>

    </article>
  )

  // =========================
  // SCHOLARSHIP CARD
  // =========================
  const renderScholarship = (
    recommendation,
    index
  ) => (
    <article
      className="recommendation-card"
      key={
        recommendation.scholarship_id
      }
    >
      <div className="recommendation-card-top">
        <div>
          <p className="recommendation-rank">
            #{index + 1} Recommended Scholarship
          </p>

          <h3>
            {
              recommendation.scholarship_name
            }
          </h3>

          <p className="recommendation-university">
            {recommendation.provider_name}
          </p>

          <p className="recommendation-location">
            {recommendation.country_name}

            {recommendation.host_university_name
              ? ` • ${recommendation.host_university_name}`
              : ''}
          </p>
        </div>

        <div
          className={`recommendation-score ${getScoreClass(
            recommendation.match_score
          )}`}
        >
          <strong>
            {formatScore(
              recommendation.match_score
            )}
          </strong>

          <span>/ 100</span>
        </div>
      </div>

      <div className="recommendation-meta-grid">
        <div>
          <span>Funding</span>

          <strong>
            {recommendation.funding_type ||
              'Not available'}
          </strong>
        </div>

        <div>
          <span>Status</span>

          <strong>
            {
              recommendation.scholarship_status ||
              'Unknown'
            }
          </strong>
        </div>

        <div>
          <span>Deadline</span>

          <strong>
            {
              recommendation.application_deadline ||
              'Not available'
            }
          </strong>
        </div>

        <div>
          <span>Allowance</span>

          <strong>
            {recommendation.monthly_allowance
              ? `${recommendation.monthly_allowance} ${recommendation.allowance_currency || ''}`
              : 'Not available'}
          </strong>
        </div>
      </div>

      <div className="recommendation-details-grid">
        <section className="recommendation-detail-box">
          <h4>Why Recommended</h4>

          <ul className="recommendation-reasons">
            {(
              recommendation.match_reasons ||
              []
            ).map((reason) => (
              <li key={reason}>
                {reason}
              </li>
            ))}
          </ul>
        </section>

        <section className="recommendation-detail-box">
          <h4>Requirement Gaps</h4>

          <ul className="recommendation-gaps">
            {(
              recommendation.requirement_gaps ||
              []
            ).map((gap) => (
              <li key={gap}>
                {gap}
              </li>
            ))}
          </ul>
        </section>
      </div>

      <section className="recommendation-breakdown">
        <h4>Match Score Breakdown</h4>

        <div className="recommendation-breakdown-grid">
          {Object.entries(
            recommendation.score_breakdown ||
              {}
          ).map(([key, value]) => (
            <div key={key}>
              <span>
                {key
                  .replaceAll('_', ' ')
                  .replace(/\b\w/g, (letter) =>
                    letter.toUpperCase()
                  )}
              </span>

              <strong>
                {Number(value).toFixed(2)}
              </strong>
            </div>
          ))}
        </div>
      </section>

      <div className="recommendation-card-actions">
        <button
          type="button"
          className={`recommendation-save-button ${
            savedScholarshipIds.includes(
              recommendation.scholarship_id
            )
              ? 'saved'
              : ''
          }`}
          onClick={() =>
            toggleScholarshipSave(
              recommendation.scholarship_id
            )
          }
          disabled={
            savingItem ===
            `scholarship-${recommendation.scholarship_id}`
          }
        >
          {savingItem ===
          `scholarship-${recommendation.scholarship_id}`
            ? 'Saving...'
            : savedScholarshipIds.includes(
                recommendation.scholarship_id
              )
              ? '♥ Saved Scholarship'
              : '♡ Save Scholarship'}
        </button>

        {recommendation.official_website && (
          <a
            className="recommendation-link"
            href={
              recommendation.official_website
            }
            target="_blank"
            rel="noreferrer"
          >
            Visit Official Scholarship Page ↗
          </a>
        )}
      </div>
      
    </article>
  )

  return (
    <div className="recommendation-modal-backdrop">
      <div className="recommendation-modal">
        <div className="recommendation-sticky-close-row">
          <button
            type="button"
            className="recommendation-close-button"
            onClick={onClose}
            aria-label="Close recommendations"
          >
            &times;
          </button>
        </div>
        <header className="recommendation-modal-header">
          <div>
            <p className="recommendation-eyebrow">
              {recommendationsRequested
                ? 'PERSONALIZED RESULTS'
                : 'PERSONALIZED RECOMMENDATIONS'}
            </p>

            <h2>
              EduPath Recommendations
            </h2>

            <p>
              {recommendationsRequested
                ? 'Recommendations generated from your academic profile'
                : 'Discover programmes and scholarships matched to your goals'}
            </p>
          </div>
        </header>

        {!recommendationsRequested && (
          <section className="recommendation-start">
            <div className="recommendation-start-icon">
              EP
            </div>

            <p className="recommendation-start-label">
              PERSONALIZED FOR YOU
            </p>

            <h3>
              Find opportunities that
              match your goals.
            </h3>

            <p className="recommendation-start-description">
              EduPath analyses your academic
              profile and compares it with
              available programmes and
              scholarships to identify your
              strongest matches.
            </p>

            <div className="recommendation-start-features">
              <div>
                <span>&#10003;</span>
                <p>
                  <strong>
                    Degree and country
                  </strong>
                  <small>
                    Based on your study
                    destination and target level.
                  </small>
                </p>
              </div>

              <div>
                <span>&#10003;</span>
                <p>
                  <strong>
                    Major similarity
                  </strong>
                  <small>
                    Compares your preferred
                    field using content similarity.
                  </small>
                </p>
              </div>

              <div>
                <span>&#10003;</span>
                <p>
                  <strong>
                    Budget and intake
                  </strong>
                  <small>
                    Considers affordability
                    and preferred study intake.
                  </small>
                </p>
              </div>

              <div>
                <span>&#10003;</span>
                <p>
                  <strong>
                    Scholarship eligibility
                  </strong>
                  <small>
                    Checks funding, GPA and
                    English requirements.
                  </small>
                </p>
              </div>
            </div>

            <button
              type="button"
              className="recommendation-start-button"
              onClick={() => {
                setError('')
                setProgramData(null)
                setScholarshipData(null)
                setRecommendationsRequested(
                  true
                )
              }}
            >
              Get Personalized Recommendations
            </button>

            <p className="recommendation-start-note">
              Recommendations are generated
              from your current academic profile.
            </p>
          </section>
        )}

        {recommendationsRequested &&
          loading && (
          <div className="recommendation-loading">
            <div className="recommendation-spinner" />

            <p>
              Analysing your profile and
              generating recommendations...
            </p>
          </div>
        )}

        {error && !loading && (
          <div className="recommendation-error">
            {error}
          </div>
        )}

        {!loading &&
          !error &&
          programData &&
          scholarshipData && (
            <>
              <section className="recommendation-summary">
                <div>
                  <span>
                    Programme Candidates
                  </span>

                  <strong>
                    {
                      programData.total_program_candidates
                    }
                  </strong>
                </div>

                <div>
                  <span>
                    Eligible Programmes
                  </span>

                  <strong>
                    {
                      programData.eligible_candidates
                    }
                  </strong>
                </div>

                <div>
                  <span>
                    Scholarship Candidates
                  </span>

                  <strong>
                    {
                      scholarshipData.total_scholarship_candidates
                    }
                  </strong>
                </div>

                <div>
                  <span>
                    Eligible Scholarships
                  </span>

                  <strong>
                    {
                      scholarshipData.eligible_candidates
                    }
                  </strong>
                </div>
              </section>

              <div className="recommendation-tabs">
                <button
                  type="button"
                  className={
                    activeTab === 'programs'
                      ? 'active'
                      : ''
                  }
                  onClick={() =>
                    setActiveTab(
                      'programs'
                    )
                  }
                >
                  Recommended Programmes (
                  {
                    programData.returned_recommendations
                  }
                  )
                </button>

                <button
                  type="button"
                  className={
                    activeTab ===
                    'scholarships'
                      ? 'active'
                      : ''
                  }
                  onClick={() =>
                    setActiveTab(
                      'scholarships'
                    )
                  }
                >
                  Recommended Scholarships (
                  {
                    scholarshipData.returned_recommendations
                  }
                  )
                </button>
              </div>

              <section className="recommendation-algorithm">
                <strong>
                  Algorithm:
                </strong>{' '}

                {activeTab === 'programs'
                  ? programData.algorithm?.name
                  : scholarshipData.algorithm
                      ?.name}

                <span>
                  TF-IDF cosine similarity +
                  weighted scoring
                </span>
              </section>

              <div className="recommendation-list">
                {activeTab ===
                  'programs' &&
                  (
                    programData.recommendations ||
                    []
                  ).map(
                    renderProgram
                  )}

                {activeTab ===
                  'scholarships' &&
                  (
                    scholarshipData.recommendations ||
                    []
                  ).map(
                    renderScholarship
                  )}
              </div>
            </>
          )}
      </div>
    </div>
  )
}

export default RecommendationModal