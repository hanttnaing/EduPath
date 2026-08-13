function UniversityCard({ university }) {
  return (
    <article className="university-card">
      <div className="university-card-header">
        <span className="university-icon">🎓</span>

        <div>
          <h3>{university.university_name}</h3>
          <p className="university-location">
            📍 {university.city}
          </p>
        </div>
      </div>

      {university.university_type && (
        <p>Type: {university.university_type}</p>
      )}

      {university.scholarship_available !== null &&
        university.scholarship_available !== undefined && (
          <p>
            Scholarship:{' '}
            {university.scholarship_available
              ? 'Available'
              : 'Not available'}
          </p>
        )}

      {university.official_website && (
        <a
          className="website-button"
          href={university.official_website}
          target="_blank"
          rel="noreferrer"
        >
          Visit Official Website
        </a>
      )}
    </article>
  )
}

export default UniversityCard