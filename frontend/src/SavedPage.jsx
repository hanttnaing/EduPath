import { useEffect, useState } from 'react'
import {
  authFetch,
  readApiError,
} from './api'
import SavedOpportunityDetailModal from './SavedOpportunityDetailModal'
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
  if (type === 'programs') {
    return (
      item.program_name ||
      item.program_id ||
      'Saved Programme'
    )
  }

  return (
    item.scholarship_name ||
    item.scholarship_id ||
    'Saved Scholarship'
  )
}

function getItemId(item, type) {
  if (type === 'programs') {
    return item.program_id
  }

  return item.scholarship_id
}

function getEndpointType(type) {
  return type === 'programs'
    ? 'programs'
    : 'scholarships'
}

function getUniversityId(
  item,
  type
) {
  if (type === 'programs') {
    return item.university_id
  }

  return item.host_university_id
}

function getUniversityName(
  item,
  type,
  universitiesById
) {
  const universityId =
    getUniversityId(
      item,
      type
    )

  if (!universityId) {
    return ''
  }

  const university =
    universitiesById[
      universityId
    ]

  return (
    university?.university_name ||
    university?.official_name ||
    universityId
  )
}

function getCardSubtitle(
  item,
  type,
  universitiesById
) {
  if (type === 'programs') {
    return getUniversityName(
      item,
      type,
      universitiesById
    )
  }

  return (
    item.provider_name ||
    getUniversityName(
      item,
      type,
      universitiesById
    ) ||
    ''
  )
}

function getCardMeta(
  item,
  type,
  universitiesById
) {
  if (type === 'programs') {
    return [
      item.degree_level,
      item.field_of_study,
      item.language_of_instruction,
    ]
      .filter(Boolean)
      .join(' / ')
  }

  return [
    getUniversityName(
      item,
      type,
      universitiesById
    ),
    item.funding_type,
    item.scholarship_status,
  ]
    .filter(Boolean)
    .join(' / ')
}

function SavedPage({
  onClose,
}) {
  const [activeTab, setActiveTab] =
    useState('programs')

  const [savedData, setSavedData] =
    useState(null)

  const [
    universitiesById,
    setUniversitiesById,
  ] = useState({})

  const [
    selectedDetail,
    setSelectedDetail,
  ] = useState(null)

  const [loading, setLoading] =
    useState(true)

  const [error, setError] =
    useState('')

  const [
    removingId,
    setRemovingId,
  ] = useState('')

  // =========================
  // LOAD RELATED UNIVERSITIES
  // =========================
  const loadRelatedUniversities =
    async (savedResult) => {
      const universityIds = [
        ...(
          savedResult.saved_programs ||
          []
        ).map(
          (program) =>
            program.university_id
        ),

        ...(
          savedResult.saved_scholarships ||
          []
        ).map(
          (scholarship) =>
            scholarship.host_university_id
        ),
      ].filter(Boolean)

      const uniqueIds = [
        ...new Set(
          universityIds
        ),
      ]

      if (uniqueIds.length === 0) {
        setUniversitiesById({})
        return
      }

      const entries =
        await Promise.all(
          uniqueIds.map(
            async (universityId) => {
              try {
                const response =
                  await authFetch(
                    `/api/universities/${encodeURIComponent(
                      universityId
                    )}`
                  )

                if (!response.ok) {
                  return [
                    universityId,
                    null,
                  ]
                }

                const university =
                  await response.json()

                return [
                  universityId,
                  university,
                ]
              } catch {
                return [
                  universityId,
                  null,
                ]
              }
            }
          )
        )

      setUniversitiesById(
        Object.fromEntries(
          entries
        )
      )
    }

  // =========================
  // LOAD SAVED OPPORTUNITIES
  // =========================
  const loadSaved = async () => {
    setLoading(true)
    setError('')

    try {
      const response =
        await authFetch(
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

      await loadRelatedUniversities(
        result
      )
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

  // =========================
  // REMOVE SAVED ITEM
  // =========================
  const handleRemove = async (
    item,
    type
  ) => {
    const itemId =
      getItemId(
        item,
        type
      )

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

      const response =
        await authFetch(
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

      if (
        selectedDetail &&
        getItemId(
          selectedDetail.item,
          selectedDetail.type
        ) === itemId
      ) {
        setSelectedDetail(null)
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
    <>
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
              Keep study programmes and
              scholarships you want to revisit.
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
                        savedData
                          .saved_program_count ??
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
                        savedData
                          .saved_scholarship_count ??
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
                          setActiveTab(
                            key
                          )
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

                {currentItems.length ===
                0 ? (
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

                        const subtitle =
                          getCardSubtitle(
                            item,
                            activeTab,
                            universitiesById
                          )

                        const meta =
                          getCardMeta(
                            item,
                            activeTab,
                            universitiesById
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

                            {subtitle && (
                              <p className="saved-card-subtitle">
                                {subtitle}
                              </p>
                            )}

                            {meta && (
                              <p className="saved-card-meta">
                                {meta}
                              </p>
                            )}

                            <div className="saved-card-actions">
                              <button
                                type="button"
                                className="saved-view-button"
                                onClick={() =>
                                  setSelectedDetail(
                                    {
                                      item,
                                      type:
                                        activeTab,
                                    }
                                  )
                                }
                              >
                                View Details
                              </button>

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
                            </div>
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

      {selectedDetail && (
        <SavedOpportunityDetailModal
          item={
            selectedDetail.item
          }
          type={
            selectedDetail.type
          }
          universityName={
            getUniversityName(
              selectedDetail.item,
              selectedDetail.type,
              universitiesById
            )
          }
          onClose={() =>
            setSelectedDetail(
              null
            )
          }
          removing={
            removingId ===
            getItemId(
              selectedDetail.item,
              selectedDetail.type
            )
          }
          onRemove={() =>
            handleRemove(
              selectedDetail.item,
              selectedDetail.type
            )
          }
        />
      )}
    </>
  )
}

export default SavedPage
