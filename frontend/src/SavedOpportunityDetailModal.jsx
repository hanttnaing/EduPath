import './SavedOpportunityDetailModal.css'

function displayValue(
  value,
  fallback = 'Not available'
) {
  if (
    value === null ||
    value === undefined ||
    value === ''
  ) {
    return fallback
  }

  return value
}

function formatDate(value) {
  if (!value) {
    return 'Not available'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return date.toLocaleDateString(
    undefined,
    {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    }
  )
}

function formatMoney(
  amount,
  currency
) {
  if (
    amount === null ||
    amount === undefined
  ) {
    return 'Not available'
  }

  return `${Number(
    amount
  ).toLocaleString()} ${
    currency || ''
  }`.trim()
}

function DetailItem({
  label,
  value,
}) {
  return (
    <div className="saved-detail-item">
      <span>{label}</span>

      <strong>
        {displayValue(value)}
      </strong>
    </div>
  )
}

function SavedOpportunityDetailModal({
  item,
  type,
  universityName,
  onClose,
  onRemove,
  removing = false,
}) {
  if (!item) {
    return null
  }

  const isProgram =
    type === 'programs'

  const isScholarship =
    type === 'scholarships'

  const title = isProgram
    ? item.program_name
    : item.scholarship_name

  const subtitle = isProgram
    ? universityName
    : item.provider_name

  return (
    <div className="saved-detail-backdrop">
      <div className="saved-detail-modal">

        <div className="saved-detail-sticky-close">
          <button
            type="button"
            onClick={onClose}
            aria-label="Close details"
          >
            &times;
          </button>
        </div>

        <header className="saved-detail-header">
          <p>
            {isProgram
              ? 'STUDY PROGRAMME'
              : 'SCHOLARSHIP'}
          </p>

          <h2>
            {title}
          </h2>

          {subtitle && (
            <h3>
              {subtitle}
            </h3>
          )}
        </header>

        {isProgram && (
          <>
            <section className="saved-detail-section">
              <h4>
                Academic Information
              </h4>

              <div className="saved-detail-grid">
                <DetailItem
                  label="Degree"
                  value={
                    item.degree_level
                  }
                />

                <DetailItem
                  label="Field"
                  value={
                    item.field_of_study
                  }
                />

                <DetailItem
                  label="Duration"
                  value={
                    item.duration_years
                      ? `${item.duration_years} years`
                      : null
                  }
                />

                <DetailItem
                  label="Study Mode"
                  value={
                    item.study_mode
                  }
                />

                <DetailItem
                  label="Language"
                  value={
                    item.language_of_instruction
                  }
                />

                <DetailItem
                  label="University"
                  value={
                    universityName
                  }
                />
              </div>
            </section>

            <section className="saved-detail-section">
              <h4>
                Tuition Information
              </h4>

              <div className="saved-detail-grid">
                <DetailItem
                  label="Tuition"
                  value={formatMoney(
                    item.tuition_fee,
                    item.tuition_currency
                  )}
                />

                <DetailItem
                  label="Tuition Period"
                  value={
                    item.tuition_period
                  }
                />

                <DetailItem
                  label="Academic Year"
                  value={
                    item.tuition_academic_year
                  }
                />

                <DetailItem
                  label="Last Verified"
                  value={formatDate(
                    item.tuition_last_verified_at
                  )}
                />
              </div>

              {item.tuition_note && (
                <div className="saved-detail-note">
                  <strong>
                    Tuition Note
                  </strong>

                  <p>
                    {item.tuition_note}
                  </p>
                </div>
              )}

              {item.tuition_student_scope && (
                <div className="saved-detail-note">
                  <strong>
                    Tuition Scope
                  </strong>

                  <p>
                    {
                      item.tuition_student_scope
                    }
                  </p>
                </div>
              )}
            </section>

            <section className="saved-detail-section">
              <h4>
                Admission Requirements
              </h4>

              <div className="saved-detail-grid">
                <DetailItem
                  label="Minimum GPA"
                  value={
                    item.minimum_gpa
                  }
                />

                <DetailItem
                  label="GPA Scale"
                  value={
                    item.gpa_scale
                  }
                />

                <DetailItem
                  label="IELTS"
                  value={
                    item.ielts_requirement
                  }
                />

                <DetailItem
                  label="TOEFL"
                  value={
                    item.toefl_requirement
                  }
                />

                <DetailItem
                  label="Intake"
                  value={
                    item.intake
                  }
                />

                <DetailItem
                  label="Application Deadline"
                  value={formatDate(
                    item.application_deadline
                  )}
                />
              </div>
            </section>
          </>
        )}

        {isScholarship && (
          <>
            <section className="saved-detail-section">
              <h4>
                Scholarship Overview
              </h4>

              <div className="saved-detail-grid">
                <DetailItem
                  label="Provider"
                  value={
                    item.provider_name
                  }
                />

                <DetailItem
                  label="Provider Type"
                  value={
                    item.provider_type
                  }
                />

                <DetailItem
                  label="Funding"
                  value={
                    item.funding_type
                  }
                />

                <DetailItem
                  label="Status"
                  value={
                    item.scholarship_status
                  }
                />

                <DetailItem
                  label="Application Cycle"
                  value={
                    item.application_cycle
                  }
                />

                <DetailItem
                  label="Host University"
                  value={
                    universityName
                  }
                />
              </div>
            </section>

            <section className="saved-detail-section">
              <h4>
                Supported Study
              </h4>

              <div className="saved-detail-list-box">
                <strong>
                  Degree Levels
                </strong>

                <p>
                  {Array.isArray(
                    item.degree_levels
                  ) &&
                  item.degree_levels.length
                    ? item.degree_levels.join(
                        ', '
                      )
                    : 'Not available'}
                </p>
              </div>

              <div className="saved-detail-list-box">
                <strong>
                  Fields of Study
                </strong>

                <p>
                  {Array.isArray(
                    item.fields_of_study
                  ) &&
                  item.fields_of_study.length
                    ? item.fields_of_study.join(
                        ', '
                      )
                    : 'Not available'}
                </p>
              </div>
            </section>

            <section className="saved-detail-section">
              <h4>
                Eligibility & Application
              </h4>

              <div className="saved-detail-grid">
                <DetailItem
                  label="Minimum GPA"
                  value={
                    item.minimum_gpa
                  }
                />

                <DetailItem
                  label="IELTS"
                  value={
                    item.ielts_requirement
                  }
                />

                <DetailItem
                  label="TOEFL"
                  value={
                    item.toefl_requirement
                  }
                />

                <DetailItem
                  label="Age Limit"
                  value={
                    item.age_limit
                  }
                />

                <DetailItem
                  label="Opening Date"
                  value={formatDate(
                    item.application_opening_date
                  )}
                />

                <DetailItem
                  label="Deadline"
                  value={formatDate(
                    item.application_deadline
                  )}
                />
              </div>
            </section>

            <section className="saved-detail-section">
              <h4>
                Financial Support
              </h4>

              <div className="saved-detail-grid">
                <DetailItem
                  label="Monthly Allowance"
                  value={formatMoney(
                    item.monthly_allowance,
                    item.allowance_currency
                  )}
                />

                <DetailItem
                  label="Tuition Coverage"
                  value={
                    item.tuition_coverage
                  }
                />

                <DetailItem
                  label="Travel Support"
                  value={
                    item.travel_allowance
                  }
                />

                <DetailItem
                  label="Accommodation"
                  value={
                    item.accommodation_support
                  }
                />

                <DetailItem
                  label="Health Insurance"
                  value={
                    item.health_insurance
                  }
                />
              </div>
            </section>

            {Array.isArray(
              item.required_documents
            ) &&
              item.required_documents
                .length > 0 && (
                <section className="saved-detail-section">
                  <h4>
                    Required Documents
                  </h4>

                  <ul className="saved-detail-documents">
                    {item.required_documents.map(
                      (document) => (
                        <li key={document}>
                          {document}
                        </li>
                      )
                    )}
                  </ul>
                </section>
              )}
          </>
        )}

        <div className="saved-detail-actions">
          {isProgram &&
            item.program_url && (
              <a
                href={item.program_url}
                target="_blank"
                rel="noreferrer"
              >
                Official Programme Page
              </a>
            )}

          {isProgram &&
            item.tuition_source_url && (
              <a
                href={
                  item.tuition_source_url
                }
                target="_blank"
                rel="noreferrer"
                className="secondary"
              >
                Tuition Source
              </a>
            )}

          {isScholarship &&
            item.official_website && (
              <a
                href={
                  item.official_website
                }
                target="_blank"
                rel="noreferrer"
              >
                Official Scholarship Page
              </a>
            )}

          {isScholarship &&
            item.source_url && (
              <a
                href={item.source_url}
                target="_blank"
                rel="noreferrer"
                className="secondary"
              >
                Application Source
              </a>
            )}

          <button
            type="button"
            className="saved-detail-remove"
            disabled={removing}
            onClick={onRemove}
          >
            {removing
              ? 'Removing...'
              : 'Remove from Saved'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default SavedOpportunityDetailModal
