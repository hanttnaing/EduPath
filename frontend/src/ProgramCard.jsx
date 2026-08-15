function ProgramCard({
  program,
  universityName,
  isSaved = false,
  saving = false,
  onToggleSave,
}) {
  const hasTuition =
    program.tuition_fee !== null &&
    program.tuition_fee !== undefined

  return (
    <article className="program-card">
      <div className="program-card-header">
        <span
          className="program-icon"
          aria-hidden="true"
        >
           {'\u{1F4D8}'}
        </span>

        <div>
          <h3>
            {program.program_name}
          </h3>

          {universityName && (
            <p className="program-university">
              {universityName}
            </p>
          )}
        </div>
      </div>

      <div className="program-details">
        {program.degree_level && (
          <p>
            <strong>
              Degree:
            </strong>{' '}
            {program.degree_level}
          </p>
        )}

        {program.field_of_study && (
          <p>
            <strong>
              Field:
            </strong>{' '}
            {program.field_of_study}
          </p>
        )}

        {program.language_of_instruction && (
          <p>
            <strong>
              Language:
            </strong>{' '}
            {
              program.language_of_instruction
            }
          </p>
        )}

        {hasTuition && (
          <p>
            <strong>
              Annual Tuition:
            </strong>{' '}
            {Number(
              program.tuition_fee
            ).toLocaleString()}{' '}
            {
              program.tuition_currency ||
              'JPY'
            }
          </p>
        )}

        {program.tuition_academic_year && (
          <p>
            <strong>
              Academic Year:
            </strong>{' '}
            {
              program.tuition_academic_year
            }
          </p>
        )}
      </div>

      <div className="program-card-actions">
        {onToggleSave && (
          <button
            type="button"
            className={`program-save-button ${
              isSaved
                ? 'saved'
                : ''
            }`}
            disabled={saving}
            onClick={() =>
              onToggleSave(
                program.program_id
              )
            }
          >
            {saving
              ? 'Updating...'
              : isSaved
                ? 'Saved \u2713'
                : 'Save Programme'}
          </button>
        )}

        {program.program_url && (
          <a
            className="program-link"
            href={
              program.program_url
            }
            target="_blank"
            rel="noreferrer"
          >
            View Programme
          </a>
        )}
      </div>
    </article>
  )
}

export default ProgramCard
