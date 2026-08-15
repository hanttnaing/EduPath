import { useEffect, useState } from 'react'
import API_BASE_URL, {
  authFetch,
  clearAccessToken,
  getAccessToken,
  readApiError,
  setAccessToken,
} from './api'
import LoginPage from './auth/LoginPage'
import RegisterPage from './auth/RegisterPage'
import ProfileSetupPage from './auth/ProfileSetupPage'
import UniversityCard from './UniversityCard'
import ProgramCard from './ProgramCard'
import ScholarshipCard from './ScholarshipCard'
import MyProfileModal from './MyProfileModal'
import RecommendationModal from './RecommendationModal'
import SavedPage from './SavedPage'
import './App.css'

// =========================
// COUNTRY NORMALIZATION HELPERS
// =========================
function getCountryId(country) {
  if (!country) return ''

  const rawValue =
    country.country_id ??
    country.id ??
    country.country_code ??
    country.code ??
    country.iso2 ??
    country.iso_code ??
    ''

  const value = String(rawValue).trim()

  if (!value) return ''

  if (value.toLowerCase().startsWith('country_')) {
    return value.toLowerCase()
  }

  if (/^[a-zA-Z]{2}$/.test(value)) {
    return `country_${value.toLowerCase()}`
  }

  return value
}

function getCountryLabel(country) {
  if (!country) return ''

  return (
    country.country_name ??
    country.name ??
    country.country ??
    country.display_name ??
    country.label ??
    getCountryId(country)
  )
}

function extractCountryItems(data) {
  if (Array.isArray(data)) {
    return data
  }

  if (Array.isArray(data?.items)) {
    return data.items
  }

  if (Array.isArray(data?.countries)) {
    return data.countries
  }

  if (Array.isArray(data?.results)) {
    return data.results
  }

  return []
}


const EXPLORE_PAGE_SIZE = 12

function getExploreTotalPages(items) {
  return Math.max(
    1,
    Math.ceil(
      items.length / EXPLORE_PAGE_SIZE
    )
  )
}

function getExploreSafePage(
  items,
  page
) {
  return Math.min(
    Math.max(page, 1),
    getExploreTotalPages(items)
  )
}

function getExplorePageItems(
  items,
  page
) {
  const safePage =
    getExploreSafePage(
      items,
      page
    )

  const start =
    (safePage - 1) *
    EXPLORE_PAGE_SIZE

  return items.slice(
    start,
    start + EXPLORE_PAGE_SIZE
  )
}

function getExplorePageStart(
  items,
  page
) {
  if (!items.length) {
    return 0
  }

  const safePage =
    getExploreSafePage(
      items,
      page
    )

  return (
    (safePage - 1) *
      EXPLORE_PAGE_SIZE +
    1
  )
}

function getExplorePageEnd(
  items,
  page
) {
  if (!items.length) {
    return 0
  }

  const safePage =
    getExploreSafePage(
      items,
      page
    )

  return Math.min(
    safePage *
      EXPLORE_PAGE_SIZE,
    items.length
  )
}

function ExplorePagination({
  items,
  page,
  onPageChange,
}) {
  const totalPages =
    getExploreTotalPages(items)

  const safePage =
    getExploreSafePage(
      items,
      page
    )

  if (
    items.length <=
    EXPLORE_PAGE_SIZE
  ) {
    return null
  }

  return (
    <nav
      className="explore-pagination"
      aria-label="Explore results pages"
    >
      <button
        type="button"
        className="explore-page-button explore-page-nav-button"
        disabled={safePage === 1}
        onClick={() =>
          onPageChange(
            safePage - 1
          )
        }
      >
        Previous
      </button>

      <div className="explore-page-numbers">
        {Array.from(
          {
            length: totalPages,
          },
          (_, index) =>
            index + 1
        ).map(
          (pageNumber) => (
            <button
              type="button"
              key={pageNumber}
              className={
                safePage ===
                pageNumber
                  ? 'explore-page-button active'
                  : 'explore-page-button'
              }
              aria-current={
                safePage ===
                pageNumber
                  ? 'page'
                  : undefined
              }
              onClick={() =>
                onPageChange(
                  pageNumber
                )
              }
            >
              {pageNumber}
            </button>
          )
        )}
      </div>

      <button
        type="button"
        className="explore-page-button explore-page-nav-button"
        disabled={
          safePage ===
          totalPages
        }
        onClick={() =>
          onPageChange(
            safePage + 1
          )
        }
      >
        Next
      </button>
    </nav>
  )
}

function App() {
  // =========================
  // AUTHENTICATION STATE
  // =========================
  const [
    authStatus,
    setAuthStatus,
  ] = useState('checking')

  const [
    authMode,
    setAuthMode,
  ] = useState('login')

  const [
    currentAccount,
    setCurrentAccount,
  ] = useState(null)

  // =========================
  // ANALYSIS DASHBOARD STATE
  // =========================
  const [
    showAnalysisDashboard,
    setShowAnalysisDashboard,
  ] = useState(false)

  // =========================
  // USER PROFILE MODAL STATE
  // =========================
  const [
    showUserProfile,
    setShowUserProfile,
  ] = useState(false)

  // =========================
  // RECOMMENDATION MODAL STATE
  // =========================
  const [
    showRecommendationModal,
    setShowRecommendationModal,
  ] = useState(false)

  // =========================
  // SAVED PROGRAMME STATE
  // =========================
  const [
    savedProgramIds,
    setSavedProgramIds,
  ] = useState([])

  const [
    savingProgramId,
    setSavingProgramId,
  ] = useState('')

  // =========================
  // SAVED SCHOLARSHIP STATE
  // =========================
  const [
    savedScholarshipIds,
    setSavedScholarshipIds,
  ] = useState([])

  const [
    savingScholarshipId,
    setSavingScholarshipId,
  ] = useState('')

  // =========================
  // SAVED OPPORTUNITIES STATE
  // =========================
  const [
    showSavedPage,
    setShowSavedPage,
  ] = useState(false)

  // =========================
  // MAIN NAVIGATION STATE
  // =========================
  const [
    activePage,
    setActivePage,
  ] = useState('home')

  const [
    showExploreMenu,
    setShowExploreMenu,
  ] = useState(false)

  const isExploreActive =
    [
      'universities',
      'programs',
      'scholarships',
    ].includes(activePage)




  // =========================
  // EXPLORE MENU KEYBOARD UX
  // =========================

  useEffect(() => {
    const handleExploreEscape =
      (event) => {
        if (
          event.key === 'Escape'
        ) {
          setShowExploreMenu(
            false
          )
        }
      }

    window.addEventListener(
      'keydown',
      handleExploreEscape
    )

    return () => {
      window.removeEventListener(
        'keydown',
        handleExploreEscape
      )
    }
  }, [])

  // =========================
  // NAVIGATION PAGE CHANGE UX
  // =========================

  useEffect(() => {
    setShowExploreMenu(false)

    window.scrollTo({
      top: 0,
      left: 0,
      behavior: 'smooth',
    })
  }, [activePage])


  // =========================
  // EXPLORE PAGINATION
  // =========================

  const [
    universityPage,
    setUniversityPage,
  ] = useState(1)

  const [
    programPage,
    setProgramPage,
  ] = useState(1)

  const [
    scholarshipPage,
    setScholarshipPage,
  ] = useState(1)


  // =========================
  // UNIVERSITY STATES
  // =========================
  const [universities, setUniversities] =
    useState([])

  const [loading, setLoading] =
    useState(true)

  const [error, setError] =
    useState('')

  const [
    totalUniversities,
    setTotalUniversities,
  ] = useState(0)

  const [
    searchTerm,
    setSearchTerm,
  ] = useState('')

  // =========================
  // COUNTRY STATES
  // =========================
  const [
    countries,
    setCountries,
  ] = useState([])

  const [
    selectedCountry,
    setSelectedCountry,
  ] = useState('country_jp')

  // =========================
  // PROGRAM STATES
  // =========================
  const [
    programs,
    setPrograms,
  ] = useState([])

  const [
    programLoading,
    setProgramLoading,
  ] = useState(true)

  const [
    programError,
    setProgramError,
  ] = useState('')

  const [
    programSearchTerm,
    setProgramSearchTerm,
  ] = useState('')

  // =========================
  // SCHOLARSHIP STATES
  // =========================
  const [
    scholarships,
    setScholarships,
  ] = useState([])

  const [
    totalScholarships,
    setTotalScholarships,
  ] = useState(0)

  const [
    scholarshipLoading,
    setScholarshipLoading,
  ] = useState(true)

  const [
    scholarshipError,
    setScholarshipError,
  ] = useState('')

  const [
    scholarshipSearchTerm,
    setScholarshipSearchTerm,
  ] = useState('')

  const [
    selectedDegree,
    setSelectedDegree,
  ] = useState('all')

  const [
    selectedFunding,
    setSelectedFunding,
  ] = useState('all')

  const [
    selectedStatus,
    setSelectedStatus,
  ] = useState('all')

  const [
    selectedField,
    setSelectedField,
  ] = useState('all')

  // =========================
  // EXPLORE PAGINATION RESET
  // =========================

  useEffect(() => {
    setUniversityPage(1)
  }, [
    searchTerm,
    selectedCountry,
  ])

  useEffect(() => {
    setProgramPage(1)
  }, [
    programSearchTerm,
    selectedCountry,
  ])

  useEffect(() => {
    setScholarshipPage(1)
  }, [
    scholarshipSearchTerm,
    selectedDegree,
    selectedFunding,
    selectedStatus,
    selectedField,
    selectedCountry,
  ])


  // =========================
  // LOAD SAVED PROGRAMMES
  // =========================
  useEffect(() => {
    let cancelled = false

    const loadSavedProgrammes =
      async () => {
        if (
          authStatus !==
          'authenticated'
        ) {
          if (!cancelled) {
            setSavedProgramIds([])
            setSavedScholarshipIds([])
          }

          return
        }

        try {
          const response =
            await authFetch(
              '/api/me/saved'
            )

          if (!response.ok) {
            return
          }

          const result =
            await response.json()

          if (!cancelled) {
            setSavedProgramIds(
              Array.isArray(
                result.saved_programs
              )
                ? result.saved_programs
                    .map(
                      (item) =>
                        item.program_id
                    )
                    .filter(Boolean)
                : []
            )

            setSavedScholarshipIds(
              Array.isArray(
                result.saved_scholarships
              )
                ? result.saved_scholarships
                    .map(
                      (item) =>
                        item.scholarship_id
                    )
                    .filter(Boolean)
                : []
            )
          }
        } catch {
          if (!cancelled) {
            setSavedProgramIds([])
            setSavedScholarshipIds([])
          }
        }
      }

    loadSavedProgrammes()

    return () => {
      cancelled = true
    }
  }, [authStatus])

  // =========================
  // SAVE / UNSAVE PROGRAMME
  // =========================
  const handleToggleProgramSave =
    async (programId) => {
      if (!programId) {
        return
      }

      const isSaved =
        savedProgramIds.includes(
          programId
        )

      try {
        setSavingProgramId(
          programId
        )

        const response =
          await authFetch(
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
          throw new Error(
            await readApiError(
              response,
              isSaved
                ? 'Unable to remove programme.'
                : 'Unable to save programme.'
            )
          )
        }

        setSavedProgramIds(
          (currentIds) =>
            isSaved
              ? currentIds.filter(
                  (id) =>
                    id !==
                    programId
                )
              : currentIds.includes(
                    programId
                  )
                ? currentIds
                : [
                    ...currentIds,
                    programId,
                  ]
        )
      } finally {
        setSavingProgramId('')
      }
    }

  // =========================
  // SAVE / UNSAVE SCHOLARSHIP
  // =========================
  const handleToggleScholarshipSave =
    async (scholarshipId) => {
      if (!scholarshipId) {
        return
      }

      const isSaved =
        savedScholarshipIds.includes(
          scholarshipId
        )

      try {
        setSavingScholarshipId(
          scholarshipId
        )

        const response =
          await authFetch(
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
          throw new Error(
            await readApiError(
              response,
              isSaved
                ? 'Unable to remove scholarship.'
                : 'Unable to save scholarship.'
            )
          )
        }

        setSavedScholarshipIds(
          (currentIds) =>
            isSaved
              ? currentIds.filter(
                  (id) =>
                    id !==
                    scholarshipId
                )
              : currentIds.includes(
                    scholarshipId
                  )
                ? currentIds
                : [
                    ...currentIds,
                    scholarshipId,
                  ]
        )
      } finally {
        setSavingScholarshipId('')
      }
    }

  // =========================
  // LOAD COUNTRIES
  // =========================
  // =========================
  // AUTHENTICATION
  // =========================
  useEffect(() => {
    let cancelled = false

    const restoreSession = async () => {
      const token = getAccessToken()

      if (!token) {
        if (!cancelled) {
          setCurrentAccount(null)
          setAuthStatus('guest')
        }

        return
      }

      try {
        const response = await authFetch(
          '/api/auth/me'
        )

        if (!response.ok) {
          clearAccessToken()

          if (!cancelled) {
            setCurrentAccount(null)
            setAuthStatus('guest')
          }

          return
        }

        const account =
          await response.json()

        if (!cancelled) {
          setCurrentAccount(account)
          setAuthStatus(
            'authenticated'
          )
        }
      } catch {
        if (!cancelled) {
          setCurrentAccount(null)
          setAuthStatus('guest')
        }
      }
    }

    restoreSession()

    return () => {
      cancelled = true
    }
  }, [])

  const handleLogin = async ({
    email,
    password,
  }) => {
    const response = await fetch(
      `${API_BASE_URL}/api/auth/login`,
      {
        method: 'POST',
        headers: {
          'Content-Type':
            'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
        }),
      }
    )

    if (!response.ok) {
      throw new Error(
        await readApiError(
          response,
          'Unable to sign in.'
        )
      )
    }

    const result = await response.json()

    setAccessToken(
      result.access_token
    )

    setCurrentAccount(
      result.user
    )

    setAuthStatus(
      'authenticated'
    )
  }

  const handleRegister = async ({
    full_name,
    email,
    password,
  }) => {
    const response = await fetch(
      `${API_BASE_URL}/api/auth/register`,
      {
        method: 'POST',
        headers: {
          'Content-Type':
            'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({
          full_name,
          email,
          password,
        }),
      }
    )

    if (!response.ok) {
      throw new Error(
        await readApiError(
          response,
          'Unable to create account.'
        )
      )
    }

    // Registration creates the account.
    // Immediately sign the student in.
    await handleLogin({
      email,
      password,
    })
  }

  const handleProfileCompleted = async () => {
    const response = await authFetch(
      '/api/auth/me'
    )

    if (!response.ok) {
      throw new Error(
        await readApiError(
          response,
          'Unable to refresh your account.'
        )
      )
    }

    const account = await response.json()

    setCurrentAccount(account)
    setAuthStatus('authenticated')
  }

  const handleLogout = () => {
    clearAccessToken()

    setCurrentAccount(null)
    setAuthMode('login')
    setAuthStatus('guest')
    setSavedProgramIds([])
    setSavedScholarshipIds([])

    setActivePage('home')
    setShowExploreMenu(false)

    setActivePage('home')
    setShowExploreMenu(false)

  }

  useEffect(() => {
    const handleAuthExpired = () => {
      clearAccessToken()

      setCurrentAccount(null)
      setAuthMode('login')
      setAuthStatus('guest')
      setSavedProgramIds([])
      setSavedScholarshipIds([])

      setActivePage('home')
      setShowExploreMenu(false)

    }

    window.addEventListener(
      'edupath-auth-expired',
      handleAuthExpired
    )

    return () => {
      window.removeEventListener(
        'edupath-auth-expired',
        handleAuthExpired
      )
    }
  }, [])

  useEffect(() => {
    fetch(
      `${API_BASE_URL}/api/countries?limit=100`
    )
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            'Failed to load countries'
          )
        }

        return response.json()
      })

      .then((data) => {
        const countryItems = extractCountryItems(data)

        setCountries(countryItems)

        setSelectedCountry((currentCountry) => {
          const currentSelectionExists =
            countryItems.some(
              (country) =>
                getCountryId(country) === currentCountry
            )

          if (currentSelectionExists) {
            return currentCountry
          }

          const japanCountry =
            countryItems.find(
              (country) =>
                getCountryId(country) === 'country_jp' ||
                String(getCountryLabel(country))
                  .trim()
                  .toLowerCase() === 'japan'
            )

          if (japanCountry) {
            return getCountryId(japanCountry)
          }

          if (countryItems.length > 0) {
            return getCountryId(countryItems[0])
          }

          return currentCountry
        })
      })

      .catch((error) => {
        console.error(
          'Countries error:',
          error
        )

        setCountries([])
      })
  }, [])

  // =========================
  // LOAD UNIVERSITIES
  // WHEN COUNTRY CHANGES
  // =========================
  useEffect(() => {
    if (!selectedCountry) {
      setUniversities([])
      setTotalUniversities(0)
      setLoading(false)
      setError('')
      return
    }

    setLoading(true)
    setError('')

    fetch(
      `${API_BASE_URL}/api/universities?country_id=${selectedCountry}&limit=100`
    )
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            'Failed to load universities'
          )
        }

        return response.json()
      })

      .then((data) => {
        const items =
          data.items || []

        setUniversities(
          items
        )

        setTotalUniversities(
          typeof data.total === 'number'
            ? data.total
            : items.length
        )

        setLoading(false)
      })

      .catch((error) => {
        console.error(
          'Universities error:',
          error
        )

        setUniversities([])
        setTotalUniversities(0)

        setError(
          error.message
        )

        setLoading(false)
      })
  }, [selectedCountry])

  // =========================
  // LOAD ALL PROGRAMS
  // =========================
  useEffect(() => {
    setProgramLoading(true)
    setProgramError('')

    fetch(
      `${API_BASE_URL}/api/programs?limit=100`
    )
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            'Failed to load programs'
          )
        }

        return response.json()
      })

      .then((data) => {
        setPrograms(
          data.items || []
        )

        setProgramLoading(false)
      })

      .catch((error) => {
        console.error(
          'Programs error:',
          error
        )

        setPrograms([])

        setProgramError(
          error.message
        )

        setProgramLoading(false)
      })
  }, [])

  // =========================
  // LOAD SCHOLARSHIPS
  // WHEN COUNTRY CHANGES
  // =========================
  useEffect(() => {
    if (!selectedCountry) {
      setScholarships([])
      setTotalScholarships(0)
      setScholarshipLoading(false)
      setScholarshipError('')
      return
    }

    setScholarshipLoading(true)
    setScholarshipError('')

    setScholarships([])
    setTotalScholarships(0)

    fetch(
      `${API_BASE_URL}/api/scholarships?country_id=${selectedCountry}&limit=100`
    )
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            'Failed to load scholarships'
          )
        }

        return response.json()
      })

      .then((data) => {
        const scholarshipItems =
          data.items || []

        setScholarships(
          scholarshipItems
        )

        setTotalScholarships(
          typeof data.total === 'number'
            ? data.total
            : scholarshipItems.length
        )

        setScholarshipLoading(false)
      })

      .catch((error) => {
        console.error(
          'Scholarships error:',
          error
        )

        setScholarships([])
        setTotalScholarships(0)

        setScholarshipError(
          error.message
        )

        setScholarshipLoading(false)
      })
  }, [selectedCountry])

  // =========================
  // UNIVERSITY SEARCH
  // =========================
  const filteredUniversities =
    universities.filter(
      (university) => {
        const searchValue =
          searchTerm
            .trim()
            .toLowerCase()

        const universityName =
          university
            .university_name
            ?.toLowerCase() || ''

        const city =
          university
            .city
            ?.toLowerCase() || ''

        return (
          universityName.includes(
            searchValue
          ) ||
          city.includes(
            searchValue
          )
        )
      }
    )

  // =========================
  // SELECTED COUNTRY NAME
  // =========================
  const selectedCountryRecord =
    countries.find(
      (country) =>
        getCountryId(country) ===
        selectedCountry
    )

  const selectedCountryName =
    selectedCountryRecord
      ? getCountryLabel(
          selectedCountryRecord
        )
      : selectedCountry
        ? selectedCountry
            .replace(/^country_/i, '')
            .toUpperCase()
        : 'Country'

  // =========================
  // UNIVERSITY IDS FOR
  // SELECTED COUNTRY
  // =========================
  const selectedUniversityIds =
    new Set(
      universities.map(
        (university) =>
          university.university_id
      )
    )

  // =========================
  // PROGRAMS FOR
  // SELECTED COUNTRY
  // =========================
  const selectedCountryPrograms =
    programs.filter(
      (program) =>
        selectedUniversityIds.has(
          program.university_id
        )
    )

  // =========================
  // PROGRAM SEARCH
  // =========================
  const filteredPrograms =
    selectedCountryPrograms.filter(
      (program) => {
        const searchValue =
          programSearchTerm
            .trim()
            .toLowerCase()

        const university =
          universities.find(
            (university) =>
              university.university_id ===
              program.university_id
          )

        const programName =
          program
            .program_name
            ?.toLowerCase() || ''

        const fieldOfStudy =
          program
            .field_of_study
            ?.toLowerCase() || ''

        const universityName =
          university
            ?.university_name
            ?.toLowerCase() || ''

        return (
          programName.includes(
            searchValue
          ) ||
          fieldOfStudy.includes(
            searchValue
          ) ||
          universityName.includes(
            searchValue
          )
        )
      }
    )

  // =========================
  // SCHOLARSHIP FILTER OPTIONS
  // =========================
  const scholarshipDegrees = [
    ...new Set(
      scholarships.flatMap(
        (scholarship) => {
          if (
            Array.isArray(
              scholarship.degree_levels
            )
          ) {
            return scholarship.degree_levels
          }

          if (
            scholarship.degree_levels
          ) {
            return [
              scholarship.degree_levels,
            ]
          }

          return []
        }
      )
    ),
  ].filter(Boolean)

  const scholarshipFundings = [
    ...new Set(
      scholarships
        .map(
          (scholarship) =>
            scholarship.funding ||
            scholarship.funding_type ||
            scholarship.funding_status ||
            ''
        )
        .filter(Boolean)
    ),
  ]

  const scholarshipStatuses = [
    ...new Set(
      scholarships
        .map(
          (scholarship) =>
            scholarship.status ||
            scholarship.scholarship_status ||
            scholarship.application_status ||
            ''
        )
        .filter(Boolean)
    ),
  ]

  const scholarshipFields = [
    ...new Set(
      scholarships.flatMap(
        (scholarship) => {
          const fields =
            scholarship.fields_of_study

          if (
            Array.isArray(fields)
          ) {
            return fields
          }

          if (fields) {
            return [fields]
          }

          return []
        }
      )
    ),
  ].filter(Boolean)

  // =========================
  // UNIVERSITY LOOKUP MAP
  // =========================
  const universityNameById =
    new Map(
      universities.map(
        (university) => [
          university.university_id,
          university.university_name,
        ]
      )
    )

  // =========================
  // SCHOLARSHIP SEARCH
  // + FILTERS
  // =========================
  const filteredScholarships =
    scholarships.filter(
      (scholarship) => {
        const searchValue =
          scholarshipSearchTerm
            .trim()
            .toLowerCase()

        // -------------------------
        // Degree
        // -------------------------
        const degreeLevels =
          Array.isArray(
            scholarship.degree_levels
          )
            ? scholarship.degree_levels
            : scholarship.degree_levels
              ? [
                  scholarship.degree_levels,
                ]
              : []

        const degreeText =
          degreeLevels
            .join(' ')
            .toLowerCase()

        // -------------------------
        // Field of Study
        // -------------------------
        const fieldLevels =
          Array.isArray(
            scholarship.fields_of_study
          )
            ? scholarship.fields_of_study
            : scholarship.fields_of_study
              ? [
                  scholarship.fields_of_study,
                ]
              : []

        const fieldText =
          fieldLevels
            .join(' ')
            .toLowerCase()

        // -------------------------
        // Scholarship Name
        // -------------------------
        const scholarshipName =
          (
            scholarship.scholarship_name ||
            scholarship.name ||
            ''
          ).toLowerCase()

        // -------------------------
        // Provider
        // -------------------------
        const provider =
          (
            scholarship.provider ||
            scholarship.provider_name ||
            scholarship.scholarship_provider ||
            scholarship.scholarship_provider_name ||
            ''
          ).toLowerCase()

        // -------------------------
        // Funding
        // -------------------------
        const funding =
          (
            scholarship.funding ||
            scholarship.funding_type ||
            scholarship.funding_status ||
            ''
          ).toLowerCase()

        // -------------------------
        // Status
        // -------------------------
        const status =
          (
            scholarship.status ||
            scholarship.scholarship_status ||
            scholarship.application_status ||
            ''
          ).toLowerCase()

        // -------------------------
        // Host University
        // -------------------------
        const hostUniversitySearchText =
          (
            universityNameById.get(
              scholarship.host_university_id
            ) ||
            scholarship.host_university_name ||
            scholarship.university_name ||
            ''
          ).toLowerCase()

        // =========================
        // SEARCH CONDITION
        // =========================
        const matchesSearch =
          scholarshipName.includes(
            searchValue
          ) ||
          provider.includes(
            searchValue
          ) ||
          degreeText.includes(
            searchValue
          ) ||
          fieldText.includes(
            searchValue
          ) ||
          funding.includes(
            searchValue
          ) ||
          status.includes(
            searchValue
          ) ||
          hostUniversitySearchText.includes(
            searchValue
          )

        // =========================
        // DEGREE CONDITION
        // =========================
        const matchesDegree =
          selectedDegree === 'all' ||
          degreeLevels.some(
            (degree) =>
              String(degree)
                .toLowerCase()
                .trim() ===
              selectedDegree
                .toLowerCase()
                .trim()
          )

        // =========================
        // FUNDING CONDITION
        // =========================
        const matchesFunding =
          selectedFunding === 'all' ||
          funding ===
            selectedFunding
              .toLowerCase()

        // =========================
        // STATUS CONDITION
        // =========================
        const matchesStatus =
          selectedStatus === 'all' ||
          status ===
            selectedStatus
              .toLowerCase()

        // =========================
        // FIELD CONDITION
        // =========================
        const matchesField =
          selectedField === 'all' ||
          fieldLevels.some(
            (field) =>
              String(field)
                .toLowerCase()
                .trim() ===
              selectedField
                .toLowerCase()
                .trim()
          )

        return (
          matchesSearch &&
          matchesDegree &&
          matchesFunding &&
          matchesStatus &&
          matchesField
        )
      }
    )

  // =========================
  // RESET COUNTRY-DEPENDENT
  // SEARCH/FILTER STATE
  // =========================
  const handleCountryChange = (
    event
  ) => {
    setSelectedCountry(
      event.target.value
    )

    setSearchTerm('')
    setProgramSearchTerm('')
    setScholarshipSearchTerm('')

    setSelectedDegree('all')
    setSelectedFunding('all')
    setSelectedStatus('all')
    setSelectedField('all')
  }

  // =========================
  // RESET SCHOLARSHIP FILTERS
  // =========================
  const resetScholarshipFilters =
    () => {
      setScholarshipSearchTerm('')
      setSelectedDegree('all')
      setSelectedFunding('all')
      setSelectedStatus('all')
      setSelectedField('all')
      setScholarshipPage(1)
    }

  // =========================
  // AUTHENTICATION UI
  // =========================
  if (authStatus === 'checking') {
    return (
      <div className="auth-session-loading">
        Checking your EduPath session...
      </div>
    )
  }

  if (authStatus !== 'authenticated') {
    if (authMode === 'register') {
      return (
        <RegisterPage
          onRegister={handleRegister}
          onShowLogin={() =>
            setAuthMode('login')
          }
        />
      )
    }

    return (
      <LoginPage
        onLogin={handleLogin}
        onShowRegister={() =>
          setAuthMode('register')
        }
      />
    )
  }

  // =========================
  // PROFILE COMPLETION GATE
  // =========================
  if (
    currentAccount &&
    currentAccount.profile_completed !== true
  ) {
    return (
      <ProfileSetupPage
        account={currentAccount}
        onCompleted={
          handleProfileCompleted
        }
        onLogout={handleLogout}
      />
    )
  }

  // =========================
  // MAIN APPLICATION UI
  // =========================
  return (
    <>
      {/* =========================
          MAIN NAVIGATION
      ========================== */}

      <nav className="edupath-navbar">
        <div className="edupath-navbar-inner">

          <button
            type="button"
              aria-haspopup="menu"
              aria-expanded={showExploreMenu}
            className={`edupath-brand ${isExploreActive ? 'active' : ''}`}
            onClick={() => {
              setActivePage('home')
              setShowExploreMenu(false)
            }}
          >
            <span className="edupath-brand-mark">
              EP
            </span>

            <span className="edupath-brand-name">
              EduPath
            </span>
          </button>

          <div className="edupath-nav-links">
            <button
              type="button"
              className={
                activePage === 'home'
                  ? 'edupath-nav-link active'
                  : 'edupath-nav-link'
              }
              onClick={() => {
                setActivePage('home')
                setShowExploreMenu(false)
              }}
            >
              Home
            </button>

            <div className="edupath-explore-wrapper">
              <button
                type="button"
                className={
                  [
                    'universities',
                    'programs',
                    'scholarships',
                  ].includes(activePage)
                    ? 'edupath-nav-link active'
                    : 'edupath-nav-link'
                }
                onClick={() =>
                  setShowExploreMenu(
                    (current) => !current
                  )
                }
              >
                Explore
                <span
                  className={`edupath-nav-chevron ${
                    showExploreMenu
                      ? 'open'
                      : ''
                  }`}
                  aria-hidden="true"
                />
              </button>

              {showExploreMenu && (
                <div className="edupath-explore-menu">
                  <button
                    type="button"
                    onClick={() => {
                      setActivePage(
                        'universities'
                      )
                      setShowExploreMenu(false)
                    }}
                  >
                    Universities
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setActivePage(
                        'programs'
                      )
                      setShowExploreMenu(false)
                    }}
                  >
                    Programmes
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setActivePage(
                        'scholarships'
                      )
                      setShowExploreMenu(false)
                    }}
                  >
                    Scholarships
                  </button>
                </div>
              )}
            </div>

            <button
              type="button"
              className={`edupath-nav-link ${
                activePage === 'recommendations'
                  ? 'active'
                  : ''
              }`}
              onClick={() => {
                setActivePage(
                  'recommendations'
                )
                setShowExploreMenu(false)
              }}
            >
              Recommendations
            </button>

            <button
              type="button"
              className={`edupath-nav-link ${
                activePage === 'saved'
                  ? 'active'
                  : ''
              }`}
              onClick={() => {
                setActivePage('saved')
                setShowExploreMenu(false)
              }}
            >
              Saved
            </button>
          </div>

          <div className="edupath-account-nav">

            <button
              type="button"
              className={`edupath-profile-nav ${
                activePage === 'profile'
                  ? 'active'
                  : ''
              }`}
              onClick={() => {
                setActivePage('profile')
                setShowExploreMenu(false)
              }}
            >
              <span
                className="edupath-profile-avatar"
                aria-hidden="true"
              >
                {'\u{1F464}'}
              </span>

              <span className="edupath-profile-copy">
                <strong>
                  {currentAccount?.full_name ||
                    'My Profile'}
                </strong>

                <small>
                  Profile
                </small>
              </span>
            </button>

            <button
              type="button"
              className="edupath-navbar-logout"
              onClick={handleLogout}
            >
              Log out
            </button>

          </div>

        </div>
      </nav>

      <main>
        {/* =========================
            HOME PAGE
        ========================== */}

        {activePage === 'home' && (
          <section className="edupath-home">

            <div className="edupath-home-hero">
              <p className="edupath-home-eyebrow">
                YOUR STUDY PATH STARTS HERE
              </p>

              <h1>
                Find the right study
                opportunity for you.
              </h1>

              <p className="edupath-home-description">
                Explore universities,
                programmes and scholarships,
                or generate personalised
                recommendations based on your
                academic profile.
              </p>

              <div className="edupath-home-actions">
                <button
                  type="button"
                  className="edupath-home-primary"
                  onClick={() =>
                    setActivePage(
                      'recommendations'
                    )
                  }
                >
                  Get Personalized Recommendations
                </button>

                <button
                  type="button"
                  className="edupath-home-secondary"
                  onClick={() =>
                    setActivePage(
                      'universities'
                    )
                  }
                >
                  Explore Opportunities
                </button>
              </div>
            </div>

            <div className="edupath-home-stats">
              <button
                type="button"
                className="edupath-home-stat-card"
                onClick={() =>
                  setActivePage(
                    'universities'
                  )
                }
              >
                <span className="home-stat-icon">
                  {'\u{1F393}'}
                </span>

                <strong>
                  {totalUniversities}
                </strong>

                <span>
                  Universities
                </span>

                <small>
                  Browse universities
                </small>
              </button>

              <button
                type="button"
                className="edupath-home-stat-card"
                onClick={() =>
                  setActivePage(
                    'programs'
                  )
                }
              >
                <span className="home-stat-icon">
                  {'\u{1F4D8}'}
                </span>

                <strong>
                  {
                    selectedCountryPrograms
                      .length
                  }
                </strong>

                <span>
                  Study Programmes
                </span>

                <small>
                  Compare study options
                </small>
              </button>

              <button
                type="button"
                className="edupath-home-stat-card"
                onClick={() =>
                  setActivePage(
                    'scholarships'
                  )
                }
              >
                <span className="home-stat-icon">
                  {'\u{1F3C5}'}
                </span>

                <strong>
                  {totalScholarships}
                </strong>

                <span>
                  Scholarships
                </span>

                <small>
                  Find funding opportunities
                </small>
              </button>
            </div>

            {/* =========================
                HOME OPPORTUNITY PREVIEWS
            ========================== */}

            <section className="home-preview-section">
              <div className="home-preview-heading">
                <div>
                  <p className="edupath-home-eyebrow">
                    EXPLORE UNIVERSITIES
                  </p>

                  <h2>
                    Universities in{' '}
                    {selectedCountryName}
                  </h2>

                  <p>
                    Start by exploring universities
                    available in your selected study
                    destination.
                  </p>
                </div>

                <button
                  type="button"
                  className="home-view-all"
                  onClick={() =>
                    setActivePage('universities')
                  }
                >
                  View All
                </button>
              </div>

              <div className="home-preview-grid">
                {universities
                  .slice(0, 3)
                  .map((university) => (
                    <article
                      className="home-opportunity-card"
                      key={
                        university.university_id
                      }
                    >
                      <div className="home-preview-icon">
                        {'\u{1F393}'}
                      </div>

                      <div>
                        <span className="home-preview-type">
                          UNIVERSITY
                        </span>

                        <h3>
                          {
                            university.university_name
                          }
                        </h3>

                        <p>
                          {[
                            university.city,
                            selectedCountryName,
                          ]
                            .filter(Boolean)
                            .join(' \u2022 ')}
                        </p>
                      </div>

                      <button
                        type="button"
                        className="home-preview-action"
                        onClick={() =>
                          setActivePage(
                            'universities'
                          )
                        }
                      >
                        Explore University
                      </button>
                    </article>
                  ))}
              </div>
            </section>


            <section className="home-preview-section home-program-preview-section">
              <div className="home-preview-heading">
                <div>
                  <p className="edupath-home-eyebrow">
                    STUDY OPTIONS
                  </p>

                  <h2>
                    Featured Programmes
                  </h2>

                  <p>
                    Compare degree levels,
                    study fields and tuition
                    information.
                  </p>
                </div>

                <button
                  type="button"
                  className="home-view-all"
                  onClick={() =>
                    setActivePage('programs')
                  }
                >
                  View All
                </button>
              </div>

              <div className="home-preview-grid">
                {selectedCountryPrograms
                  .slice(0, 3)
                  .map((program) => {
                    const university =
                      universities.find(
                        (item) =>
                          item.university_id ===
                          program.university_id
                      )

                    return (
                      <article
                        className="home-opportunity-card"
                        key={program.program_id}
                      >
                        <div className="home-preview-icon">
                          {'\u{1F4D8}'}
                        </div>

                        <div>
                          <span className="home-preview-type">
                            PROGRAMME
                          </span>

                          <h3>
                            {program.program_name}
                          </h3>

                          <p className="home-preview-subtitle">
                            {
                              university
                                ?.university_name ||
                              'University information unavailable'
                            }
                          </p>

                          <div className="home-preview-meta">
                            {program.degree_level && (
                              <span>
                                {program.degree_level}
                              </span>
                            )}

                            {program.field_of_study && (
                              <span>
                                {
                                  program.field_of_study
                                }
                              </span>
                            )}
                          </div>
                        </div>

                        <button
                          type="button"
                          className="home-preview-action"
                          onClick={() =>
                            setActivePage(
                              'programs'
                            )
                          }
                        >
                          Explore Programme
                        </button>
                      </article>
                    )
                  })}
              </div>
            </section>


            <section className="home-preview-section home-scholarship-preview-section">
              <div className="home-preview-heading">
                <div>
                  <p className="edupath-home-eyebrow">
                    FUNDING OPPORTUNITIES
                  </p>

                  <h2>
                    Featured Scholarships
                  </h2>

                  <p>
                    Explore funding opportunities
                    for your study goals.
                  </p>
                </div>

                <button
                  type="button"
                  className="home-view-all"
                  onClick={() =>
                    setActivePage(
                      'scholarships'
                    )
                  }
                >
                  View All
                </button>
              </div>

              <div className="home-preview-grid">
                {scholarships
                  .slice(0, 3)
                  .map((scholarship) => (
                    <article
                      className="home-opportunity-card"
                      key={
                        scholarship.scholarship_id
                      }
                    >
                      <div className="home-preview-icon">
                        {'\u{1F3C5}'}
                      </div>

                      <div>
                        <span className="home-preview-type">
                          SCHOLARSHIP
                        </span>

                        <h3>
                          {
                            scholarship.scholarship_name
                          }
                        </h3>

                        <p className="home-preview-subtitle">
                          {
                            scholarship.provider_name ||
                            'Scholarship provider'
                          }
                        </p>

                        <div className="home-preview-meta">
                          {scholarship.funding_type && (
                            <span>
                              {
                                scholarship.funding_type
                              }
                            </span>
                          )}

                          {Array.isArray(
                            scholarship.degree_levels
                          ) &&
                            scholarship
                              .degree_levels
                              .length > 0 && (
                              <span>
                                {scholarship
                                  .degree_levels
                                  .slice(0, 2)
                                  .join(', ')}
                              </span>
                            )}
                        </div>
                      </div>

                      <button
                        type="button"
                        className="home-preview-action"
                        onClick={() =>
                          setActivePage(
                            'scholarships'
                          )
                        }
                      >
                        Explore Scholarship
                      </button>
                    </article>
                  ))}
              </div>
            </section>


            <section className="edupath-home-guide">
              <div>
                <p className="edupath-home-eyebrow">
                  HOW EDUPATH WORKS
                </p>

                <h2>
                  Three simple ways to
                  explore your options
                </h2>
              </div>

              <div className="home-guide-grid">
                <article>
                  <span>01</span>

                  <h3>
                    Complete your profile
                  </h3>

                  <p>
                    Tell EduPath about your
                    academic background,
                    study goals and budget.
                  </p>
                </article>

                <article>
                  <span>02</span>

                  <h3>
                    Explore opportunities
                  </h3>

                  <p>
                    Search universities,
                    programmes and
                    scholarships using
                    structured filters.
                  </p>
                </article>

                <article>
                  <span>03</span>

                  <h3>
                    Get matched
                  </h3>

                  <p>
                    Generate personalised
                    recommendations and
                    save opportunities you
                    want to revisit.
                  </p>
                </article>
              </div>
            </section>

          </section>
        )}

        {/* =========================
            SHARED EXPLORE HEADER
        ========================== */}

        {[
          'universities',
          'programs',
          'scholarships',
        ].includes(activePage) && (
          <section className="explore-page-header">

            <div className="explore-page-heading">
              <p className="explore-page-eyebrow">
                EXPLORE OPPORTUNITIES
              </p>

              <h1>
                {activePage === 'universities'
                  ? 'Universities'
                  : activePage === 'programs'
                    ? 'Study Programmes'
                    : 'Scholarships'}
              </h1>

              <p>
                {activePage === 'universities'
                  ? 'Discover universities and explore your study destinations.'
                  : activePage === 'programs'
                    ? 'Compare study programmes, fields, tuition and study options.'
                    : 'Find scholarship opportunities that match your study goals.'}
              </p>
            </div>

            <div className="explore-country-filter">
              <label htmlFor="explore-country">
                Country
              </label>

              <select
                id="explore-country"
                value={selectedCountry}
                onChange={handleCountryChange}
              >
                <option value="">
                  Select a country
                </option>

                {countries.map(
                  (country, index) => {
                    const countryValue =
                      getCountryId(country)

                    const countryLabel =
                      getCountryLabel(country)

                    if (!countryValue) {
                      return null
                    }

                    return (
                      <option
                        key={
                          countryValue ||
                          index
                        }
                        value={countryValue}
                      >
                        {countryLabel}
                      </option>
                    )
                  }
                )}
              </select>
            </div>

          </section>
        )}

        {/* =========================
            UNIVERSITY SECTION
        ========================== */}

        {activePage === 'universities' && (
        <section className="university-section">
          <h2>
            Universities in{' '}
            {selectedCountryName}{' '}
            ({totalUniversities})
          </h2>

          {/* University Search */}

          <input
            className="university-search"
            type="text"
            placeholder="Search by university or city..."
            value={searchTerm}
            onChange={(event) =>
              setSearchTerm(
                event.target.value
              )
            }
          />

          {!loading &&
            !error && (
              <p className="search-result-count">
                Showing{' '}
                {
                  getExplorePageStart(
                    filteredUniversities,
                    universityPage
                  )
                }
                {' - '}
                {
                  getExplorePageEnd(
                    filteredUniversities,
                    universityPage
                  )
                }
                {' of '}
                {
                  filteredUniversities.length
                }{' '}
                universities
              </p>
            )}

          {loading && (
            <p className="status-message">
              Loading universities...
            </p>
          )}

          {error && (
            <p className="no-results">
              {error}
            </p>
          )}

          {!loading &&
            !error &&
            filteredUniversities.length ===
              0 && (
              <p className="no-results">
                No universities found.
              </p>
            )}

          {!loading &&
            !error &&
            filteredUniversities.length >
              0 && (
              <div className="university-grid">
                {getExplorePageItems(
                  filteredUniversities,
                  universityPage
                ).map(
                  (university) => (
                    <UniversityCard
                      key={
                        university.university_id
                      }
                      university={
                        university
                      }
                    />
                  )
                )}

                <ExplorePagination
                  items={filteredUniversities}
                  page={universityPage}
                  onPageChange={(nextPage) => {
                    setUniversityPage(
                      nextPage
                    )

                    window.requestAnimationFrame(
                      () => {
                        document
                          .querySelector(
                            '.university-section'
                          )
                          ?.scrollIntoView({
                            behavior:
                              'smooth',
                            block:
                              'start',
                          })
                      }
                    )
                  }}
                />
              </div>
            )}
        </section>
        )}



        {/* =========================
            PROGRAM SECTION
        ========================== */}

        {activePage === 'programs' && (
        <section className="program-section">
          <h2>
            Programs in{' '}
            {selectedCountryName}{' '}
            (
            {
              selectedCountryPrograms.length
            }
            )
          </h2>

          <input
            className="program-search"
            type="text"
            placeholder="Search programs, fields, or universities..."
            value={
              programSearchTerm
            }
            onChange={(event) =>
              setProgramSearchTerm(
                event.target.value
              )
            }
          />

          {!programLoading &&
            !programError && (
              <p className="program-result-count">
                Showing{' '}
                {
                  getExplorePageStart(
                    filteredPrograms,
                    programPage
                  )
                }
                {' - '}
                {
                  getExplorePageEnd(
                    filteredPrograms,
                    programPage
                  )
                }
                {' of '}
                {
                  filteredPrograms.length
                }{' '}
                programs
              </p>
            )}

          {programLoading && (
            <p className="status-message">
              Loading programs...
            </p>
          )}

          {programError && (
            <p className="no-results">
              {programError}
            </p>
          )}

          {!programLoading &&
            !programError &&
            filteredPrograms.length ===
              0 && (
              <p className="no-results">
                No programs available
                for this country yet.
              </p>
            )}

          {!programLoading &&
            !programError &&
            filteredPrograms.length >
              0 && (
              <div className="program-grid">
                {getExplorePageItems(
                  filteredPrograms,
                  programPage
                ).map(
                  (program) => {
                    const university =
                      universities.find(
                        (
                          university
                        ) =>
                          university.university_id ===
                          program.university_id
                      )

                    return (
                      <ProgramCard
                        key={
                          program.program_id
                        }
                        program={
                          program
                        }
                        universityName={
                          university
                            ?.university_name ||
                          ''
                        }
                        isSaved={
                          savedProgramIds.includes(
                            program.program_id
                          )
                        }
                        saving={
                          savingProgramId ===
                          program.program_id
                        }
                        onToggleSave={
                          handleToggleProgramSave
                        }
                      />
                    )
                  }
                )}

                <ExplorePagination
                  items={filteredPrograms}
                  page={programPage}
                  onPageChange={(nextPage) => {
                    setProgramPage(
                      nextPage
                    )

                    window.requestAnimationFrame(
                      () => {
                        document
                          .querySelector(
                            '.program-section'
                          )
                          ?.scrollIntoView({
                            behavior:
                              'smooth',
                            block:
                              'start',
                          })
                      }
                    )
                  }}
                />
              </div>
            )}
        </section>
        )}



        {/* =========================
            SCHOLARSHIP SECTION
        ========================== */}

        {activePage === 'scholarships' && (
        <section className="scholarship-section">
          <h2>
            Scholarships in{' '}
            {selectedCountryName}{' '}
            ({totalScholarships})
          </h2>

          {/* Scholarship Search */}

          <input
            className="scholarship-search"
            type="text"
            placeholder="Search scholarships, providers, degrees, funding, or universities..."
            value={
              scholarshipSearchTerm
            }
            onChange={(event) =>
              setScholarshipSearchTerm(
                event.target.value
              )
            }
          />

          {/* =========================
              SCHOLARSHIP FILTERS
          ========================== */}

          <div className="scholarship-filters">
            {/* Degree Filter */}

            <select
              value={
                selectedDegree
              }
              onChange={(event) =>
                setSelectedDegree(
                  event.target.value
                )
              }
            >
              <option value="all">
                All Degrees
              </option>

              {scholarshipDegrees.map(
                (degree) => (
                  <option
                    key={degree}
                    value={degree}
                  >
                    {degree}
                  </option>
                )
              )}
            </select>

            {/* Funding Filter */}

            <select
              value={
                selectedFunding
              }
              onChange={(event) =>
                setSelectedFunding(
                  event.target.value
                )
              }
            >
              <option value="all">
                All Funding
              </option>

              {scholarshipFundings.map(
                (funding) => (
                  <option
                    key={funding}
                    value={funding}
                  >
                    {funding}
                  </option>
                )
              )}
            </select>

            {/* Status Filter */}

            <select
              value={
                selectedStatus
              }
              onChange={(event) =>
                setSelectedStatus(
                  event.target.value
                )
              }
            >
              <option value="all">
                All Status
              </option>

              {scholarshipStatuses.map(
                (status) => (
                  <option
                    key={status}
                    value={status}
                  >
                    {status}
                  </option>
                )
              )}
            </select>

            {/* Field Filter */}

            <select
              value={
                selectedField
              }
              onChange={(event) =>
                setSelectedField(
                  event.target.value
                )
              }
            >
              <option value="all">
                All Fields
              </option>

              {scholarshipFields.map(
                (field) => (
                  <option
                    key={field}
                    value={field}
                  >
                    {field}
                  </option>
                )
              )}
            </select>
          </div>

          {/* Reset Scholarship Filters */}

          <button
            className="reset-scholarship-filters"
            type="button"
            onClick={
              resetScholarshipFilters
            }
          >
            Reset Filters
          </button>

          {/* Scholarship Result Count */}

          {!scholarshipLoading &&
            !scholarshipError && (
              <p className="scholarship-result-count">
                Showing{' '}
                {
                  getExplorePageStart(
                    filteredScholarships,
                    scholarshipPage
                  )
                }
                {' - '}
                {
                  getExplorePageEnd(
                    filteredScholarships,
                    scholarshipPage
                  )
                }
                {' of '}
                {
                  filteredScholarships.length
                }{' '}
                scholarships
              </p>
            )}

          {/* Scholarship Loading */}

          {scholarshipLoading && (
            <p className="status-message">
              Loading scholarships...
            </p>
          )}

          {/* Scholarship Error */}

          {scholarshipError && (
            <p className="no-results">
              {scholarshipError}
            </p>
          )}

          {/* No Scholarship Results */}

          {!scholarshipLoading &&
            !scholarshipError &&
            filteredScholarships.length ===
              0 && (
              <p className="status-message">
                No scholarships found
                for this country.
              </p>
            )}

          {/* Scholarship Cards */}

          {!scholarshipLoading &&
            !scholarshipError &&
            filteredScholarships.length >
              0 && (
              <div className="scholarship-grid">
                {getExplorePageItems(
                  filteredScholarships,
                  scholarshipPage
                ).map(
                  (
                    scholarship,
                    index
                  ) => {
                    const hostUniversityName =
                      universityNameById.get(
                        scholarship.host_university_id
                      ) ||
                      scholarship.host_university_name ||
                      scholarship.university_name ||
                      ''

                    return (
                      <ScholarshipCard
                        key={
                          scholarship.scholarship_id ||
                          scholarship._id ||
                          `${scholarship.scholarship_name}-${index}`
                        }
                        scholarship={
                          scholarship
                        }
                        hostUniversityName={
                          hostUniversityName
                        }
                        isSaved={
                          savedScholarshipIds.includes(
                            scholarship.scholarship_id
                          )
                        }
                        saving={
                          savingScholarshipId ===
                          scholarship.scholarship_id
                        }
                        onToggleSave={
                          handleToggleScholarshipSave
                        }
                      />
                    )
                  }
                )}

                <ExplorePagination
                  items={filteredScholarships}
                  page={scholarshipPage}
                  onPageChange={(nextPage) => {
                    setScholarshipPage(
                      nextPage
                    )

                    window.requestAnimationFrame(
                      () => {
                        document
                          .querySelector(
                            '.scholarship-section'
                          )
                          ?.scrollIntoView({
                            behavior:
                              'smooth',
                            block:
                              'start',
                          })
                      }
                    )
                  }}
                />
              </div>
            )}
        </section>
        )}

      

        {/* =========================
            RECOMMENDATIONS PAGE
        ========================== */}

        {activePage === 'recommendations' && (
          <section className="recommendations-page-section">
            <RecommendationModal
              displayMode="page"
            />
          </section>
        )}



        {/* =========================
            SAVED FULL PAGE
        ========================== */}

        {activePage === 'saved' && (
          <section className="saved-main-page-section">
            <SavedPage
              displayMode="page"
            />
          </section>
        )}



        {/* =========================
            PROFILE FULL PAGE
        ========================== */}

        {activePage === 'profile' && (
          <section className="profile-main-page-section">
            <MyProfileModal
              account={currentAccount}
              displayMode="page"
            />
          </section>
        )}

</main>

      {/* =========================
          RECOMMENDATION MODAL
      ========================== */}



      {/* =========================
          SAVED OPPORTUNITIES
      ========================== */}

      {/* =========================
          ANALYSIS DASHBOARD
          FULL-SCREEN MODAL
      ========================== */}

    </>
  )
}

export default App