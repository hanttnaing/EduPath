import { useEffect, useState } from 'react'
import {
  authFetch,
  readApiError,
} from './api'
import './SavedPage.css'

const TAB_CONFIG = {
  programs: {
    label: 'Study Programmes',
    countKey: 'saved_program_count',
    dataKey: 'saved_programs',
  },
  scholarships: {
    label: 'Scholarships',
    countKey: 'saved_scholarship_count',
    dataKey: 'saved_scholarships',
  },
}

function getTitle(item, type) {
  if (type === 'universities') {
    return (
      item.university_name ||
      item.name ||
      item.university_id ||
      'Saved University'
    )
  }

  if (type === 'programs') {
    return (
      item.program_name ||
      item.name ||
      item.program_id ||
      'Saved Program'
    )
  }

  return (
    item.scholarship_name ||
    item.name ||
    item.scholarship_id ||
    'Saved Scholarship'
  )
}

function getSubtitle(item, type) {
  if (type === 'universities') {
    return (
      item.city ||
      item.country_name ||
      item.country ||
      ''
    )
  }

  if (type === 'programs') {
    return (
      item.university_name ||
      item.field_of_study ||
      item.field ||
      ''
    )
  }

  return (
    item.provider_name ||
    item.host_university_name ||
    item.funding_type ||
    ''
  )
}

function getMeta(item, type) {
  if (type === 'universities') {
    return [
      item.country_name || item.country,
      item.city,
    ]
      .filter(Boolean)
      .join(' / ')
  }

  if (type === 'programs') {
    return [
      item.degree_level,
      item.field_of_study || item.field,
      item.language,
    ]
      .filter(Boolean)
      .join(' / ')
  }

  return [
    item.country_name || item.country,
    item.funding_type,
    item.status,
  ]
    .filter(Boolean)
    .join(' / ')
}

function getItemId(item, type) {
  if (type === 'universities') {
    return item.university_id
  }

  if (type === 'programs') {
    return item.program_id
  }

  return item.scholarship_id
}

function getEndpointType(type) {
  if (type === 'universities') {
    return 'universities'
  }

  if (type === 'programs') {
    return 'programs'
  }

  return 'scholarships'
}

function SavedPage({
  onClose,
}) {
  const [activeTab, setActiveTab] =
    useState('programs')

  const [savedData, setSavedData] =
    useState(null)

  const [loading, setLoading] =
    useState(true)

  const [error, setError] =
    useState('')

  const [
    removingId,
    setRemovingId,
  ] = useState('')

  const loadSaved = async () => {
    setLoading(true)
    setError('')

    try {
      const response = await authFetch(
        '/api/me/saved'
      )

      if (!response.ok) {
        throw new Error(
          await readApiError(
            response,
            'Unable to load saved opportunities.'
          )
        )
      }

      const result =
        await response.json()

      setSavedData(result)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load saved opportunities.'
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSaved()
  }, [])

  const handleRemove = async (
    item,
    type
  ) => {
    const itemId =
      getItemId(item, type)

    if (!itemId) {
      setError(
        'Unable to identify this saved item.'
      )
      return
    }

    setRemovingId(itemId)
    setError('')

    try {
      const endpointType =
        getEndpointType(type)

      const response = await authFetch(
        `/api/me/saved/${endpointType}/${encodeURIComponent(
          itemId
        )}`,
        {
          method: 'DELETE',
        }
      )

      if (!response.ok) {
        throw new Error(
          await readApiError(
            response,
            'Unable to remove saved item.'
          )
        )
      }

      await loadSaved()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to remove saved item.'
      )
    } finally {
      setRemovingId('')
    }
  }

  const currentConfig =
    TAB_CONFIG[activeTab]

  const currentItems =
    savedData?.[
      currentConfig.dataKey
    ] || []

  return (
    <div className="saved-page-backdrop">
      <div className="saved-page">

        <div className="saved-sticky-close">
          <button
            type="button"
            onClick={onClose}
            aria-label="Close saved opportunities"
          >
            &times;
          </button>
        </div>

        <header className="saved-page-header">
          <p className="saved-eyebrow">
            YOUR COLLECTION
          </p>

          <h2>
            Saved Opportunities
          </h2>

          <p>
            Keep study programmes and scholarships
            you want to revisit.
          </p>
        </header>

        {loading && (
          <div className="saved-loading">
            Loading your saved opportunities...
          </div>
        )}

        {error && !loading && (
          <div className="saved-error">
            {error}
          </div>
        )}

        {!loading &&
          savedData && (
            <>
              <div className="saved-summary">
                <div>
                  <strong>
                    {
                      savedData.saved_program_count ??
                      0
                    }
                  </strong>
                  <span>
                    Study Programmes
                  </span>
                </div>

                <div>
                  <strong>
                    {
                      savedData.saved_scholarship_count ??
                      0
                    }
                  </strong>
                  <span>
                    Scholarships
                  </span>
                </div>
              </div>

              <div className="saved-tabs">
                {Object.entries(
                  TAB_CONFIG
                ).map(
                  ([
                    key,
                    config,
                  ]) => (
                    <button
                      key={key}
                      type="button"
                      className={
                        activeTab === key
                          ? 'active'
                          : ''
                      }
                      onClick={() =>
                        setActiveTab(key)
                      }
                    >
                      {config.label}
                      {' ('}
                      {
                        savedData[
                          config.countKey
                        ] ?? 0
                      }
                      {')'}
                    </button>
                  )
                )}
              </div>

              {currentItems.length === 0 ? (
                <section className="saved-empty">
                  <div className="saved-empty-icon">
                    S
                  </div>

                  <h3>
                    No saved{' '}
                    {
                      currentConfig.label
                        .toLowerCase()
                    }{' '}
                    yet
                  </h3>

                  <p>
                    Save opportunities while
                    exploring EduPath and they
                    will appear here.
                  </p>
                </section>
              ) : (
                <div className="saved-card-grid">
                  {currentItems.map(
                    (item) => {
                      const itemId =
                        getItemId(
                          item,
                          activeTab
                        )

                      return (
                        <article
                          className="saved-card"
                          key={itemId}
                        >
                          <div className="saved-card-type">
                            {
                              currentConfig.label
                            }
                          </div>

                          <h3>
                            {getTitle(
                              item,
                              activeTab
                            )}
                          </h3>

                          {getSubtitle(
                            item,
                            activeTab
                          ) && (
                            <p className="saved-card-subtitle">
                              {getSubtitle(
                                item,
                                activeTab
                              )}
                            </p>
                          )}

                          {getMeta(
                            item,
                            activeTab
                          ) && (
                            <p className="saved-card-meta">
                              {getMeta(
                                item,
                                activeTab
                              )}
                            </p>
                          )}

                          <button
                            type="button"
                            className="saved-remove-button"
                            disabled={
                              removingId ===
                              itemId
                            }
                            onClick={() =>
                              handleRemove(
                                item,
                                activeTab
                              )
                            }
                          >
                            {removingId ===
                            itemId
                              ? 'Removing...'
                              : 'Remove from Saved'}
                          </button>
                        </article>
                      )
                    }
                  )}
                </div>
              )}
            </>
          )}
      </div>
    </div>
  )
}

export default SavedPage
