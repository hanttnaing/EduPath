function ScholarshipCard({
  scholarship,
  hostUniversityName,
}) {  // =========================
  // DATE FORMATTER
  // =========================
  const formatDate = (dateValue) => {
    if (!dateValue) {
      return null
    }

    const date = new Date(dateValue)

    if (Number.isNaN(date.getTime())) {
      return dateValue
    }

    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  // =========================
  // DEGREE LEVEL
  // =========================
  const rawDegreeLevels =
    scholarship.degree_levels ||
    scholarship.degree_level ||
    []

  const degreeLevels = Array.isArray(rawDegreeLevels)
    ? rawDegreeLevels.join(', ')
    : rawDegreeLevels || 'Not specified'

  // =========================
  // PROVIDER
  // =========================
  const provider =
    scholarship.provider ||
    scholarship.provider_name ||
    scholarship.scholarship_provider ||
    scholarship.scholarship_provider_name ||
    'Not specified'

    // =========================
    // HOST UNIVERSITY
    // =========================
    const hostUniversity =
    hostUniversityName ||
    scholarship.host_university_name ||
    scholarship.university_name ||
    ''

  // =========================
  // FUNDING
  // =========================
  const funding =
    scholarship.funding ||
    scholarship.funding_type ||
    scholarship.funding_status ||
    'Not specified'

  // =========================
  // STATUS
  // =========================
  const status =
    scholarship.status ||
    scholarship.scholarship_status ||
    scholarship.application_status ||
    'Not specified'

  const normalizedStatus = status
    .toString()
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '-')

  // =========================
  // APPLICATION CYCLE
  // =========================
  const applicationCycle =
    scholarship.application_cycle || ''

  // =========================
  // APPLICATION OPENING DATE
  // =========================
  const openingDate = formatDate(
    scholarship.application_opening_date ||
      scholarship.opening_date ||
      null
  )

  // =========================
  // APPLICATION DEADLINE
  // =========================
  const rawDeadline =
    scholarship.application_deadline ||
    scholarship.deadline ||
    scholarship.deadline_date ||
    null

  const formattedDeadline =
    formatDate(rawDeadline)

  let deadlineDisplay = formattedDeadline

  if (!deadlineDisplay) {
    if (normalizedStatus === 'upcoming') {
      deadlineDisplay = 'To be announced'
    } else {
      deadlineDisplay = 'Not available'
    }
  }

  // =========================
  // OFFICIAL LINK
  // =========================
  const scholarshipUrl =
    scholarship.official_url ||
    scholarship.official_website ||
    scholarship.source_url ||
    scholarship.scholarship_url ||
    scholarship.application_url ||
    scholarship.url ||
    ''

    // =========================
    // DATA QUALITY
    // =========================
    const dataQualityStatus =
    scholarship.data_quality_status || ''

    const freshnessStatus =
    scholarship.freshness_status || ''

    const lastVerifiedAt = formatDate(
    scholarship.last_verified_at || null
    )

    // =========================
    // ELIGIBILITY INFORMATION
    // =========================

    const ageLimit =
    scholarship.age_limit || ''

    const minimumGpa =
    scholarship.minimum_gpa

    const gpaScale =
    scholarship.gpa_scale

    const ieltsRequirement =
    scholarship.ielts_requirement || ''

    const eligibleNationalitiesRaw =
    scholarship.eligible_nationalities

    const eligibleNationalities = Array.isArray(
    eligibleNationalitiesRaw
    )
    ? eligibleNationalitiesRaw.join(', ')
    : eligibleNationalitiesRaw || ''

    const fieldsOfStudyRaw =
    scholarship.fields_of_study

    const fieldsOfStudy = Array.isArray(
    fieldsOfStudyRaw
    )
    ? fieldsOfStudyRaw.join(', ')
    : fieldsOfStudyRaw || ''

    const gpaDisplay =
    minimumGpa !== null &&
    minimumGpa !== undefined &&
    minimumGpa !== ''
        ? gpaScale
        ? `${minimumGpa} / ${gpaScale}`
        : `${minimumGpa}`
        : ''

    const hasEligibilityInfo =
    Boolean(ageLimit) ||
    Boolean(gpaDisplay) ||
    Boolean(ieltsRequirement) ||
    Boolean(eligibleNationalities) ||
    Boolean(fieldsOfStudy)
  return (
    <article className="scholarship-card">
      <div className="scholarship-card-top">
        <div className="scholarship-icon">
          🎓
        </div>

        <span
          className={`scholarship-status-badge status-${normalizedStatus}`}
        >
          {status}
        </span>
      </div>

      <h3 className="scholarship-card-title">
        {scholarship.scholarship_name ||
          scholarship.name ||
          'Unnamed Scholarship'}
      </h3>

      <p className="scholarship-provider">
        {provider}
      </p>

      <div className="scholarship-details">
        {hostUniversity && (
            <div className="scholarship-detail">
                <span className="scholarship-detail-label">
                Host University
                </span>

                <span className="scholarship-detail-value">
                {hostUniversity}
                </span>
            </div>
        )}
        <div className="scholarship-detail">
          <span className="scholarship-detail-label">
            Degree
          </span>

          <span className="scholarship-detail-value">
            {degreeLevels}
          </span>
        </div>

        <div className="scholarship-detail">
          <span className="scholarship-detail-label">
            Funding
          </span>

          <span className="scholarship-funding-badge">
            {funding}
          </span>
        </div>

        {applicationCycle && (
          <div className="scholarship-detail">
            <span className="scholarship-detail-label">
              Application Cycle
            </span>

            <span className="scholarship-detail-value">
              {applicationCycle}
            </span>
          </div>
        )}

        {openingDate && (
          <div className="scholarship-detail">
            <span className="scholarship-detail-label">
              Opens
            </span>

            <span className="scholarship-detail-value">
              {openingDate}
            </span>
          </div>
        )}

        <div className="scholarship-detail">
          <span className="scholarship-detail-label">
            Deadline
          </span>

          <span className="scholarship-detail-value">
            {deadlineDisplay}
          </span>
        </div>
      </div>

      {hasEligibilityInfo && (
        <div className="scholarship-eligibility">
            <h4 className="scholarship-eligibility-title">
            Eligibility
            </h4>

            {ageLimit && (
            <div className="eligibility-row">
                <span>Age Limit</span>
                <strong>{ageLimit}</strong>
            </div>
            )}

            {gpaDisplay && (
            <div className="eligibility-row">
                <span>Minimum GPA</span>
                <strong>{gpaDisplay}</strong>
            </div>
            )}

            {ieltsRequirement && (
            <div className="eligibility-row">
                <span>IELTS</span>
                <strong>{ieltsRequirement}</strong>
            </div>
            )}

            {eligibleNationalities && (
            <div className="eligibility-row">
                <span>Eligible Nationalities</span>
                <strong>
                {eligibleNationalities}
                </strong>
            </div>
            )}

            {fieldsOfStudy && (
            <div className="eligibility-row">
                <span>Fields of Study</span>
                <strong>{fieldsOfStudy}</strong>
            </div>
            )}
        </div>
        )}

        {(dataQualityStatus ||
            freshnessStatus ||
            lastVerifiedAt) && (
            <div className="scholarship-data-quality">
                <div className="scholarship-quality-badges">
                {dataQualityStatus && (
                    <span className="quality-badge verified-badge">
                    ✓ {dataQualityStatus}
                    </span>
                )}

                {freshnessStatus && (
                    <span className="quality-badge freshness-badge">
                    ● {freshnessStatus}
                    </span>
                )}
                </div>

                {lastVerifiedAt && (
                <p className="last-verified">
                    Last verified: {lastVerifiedAt}
                </p>
                )}
            </div>
        )}

        {scholarshipUrl ? (
            <a
            className="scholarship-link"
            href={scholarshipUrl}
            target="_blank"
            rel="noreferrer"
            >
            View Scholarship
            </a>
        ) : (
            <span className="scholarship-link-disabled">
            Official link unavailable
            </span>
        )}
    </article>
  )
}

export default ScholarshipCard