'use client'

import { useEffect, useState, useCallback, useRef } from 'react'
import { Joyride, STATUS, EVENTS, type Step, type EventData } from 'react-joyride'
import { useMapContext } from '@/components/Explorer'
import { useAuth } from '@clerk/nextjs'
import { useLocation } from '@/components/Location'
import { config } from '@/utils/environment'

const TOUR_STORAGE_KEY = 'localelive_tour_done'
const DEMO_QUERY = 'find a coffee shop close to me'

// ─── Tour step definitions ───────────────────────────────────────────────────
// To add, reorder, or update steps, edit the arrays below.
// Targets use stable data-tour attributes — never fragile class names.

const DESKTOP_STEPS: Step[] = [
  {
    target: '[data-tour="location-btn"]',
    title: 'Set your precise location',
    content:
      'Your location is currently approximate (IP-based). Tap this button to switch to precise GPS — search results will be much more accurate.',
    placement: 'left',
    skipBeacon: true,
  },
  {
    target: '[data-tour="search-input"]',
    title: 'Search anything nearby',
    content:
      'Type what you\'re looking for — e.g. "find a coffee shop close to me". We\'ll pre-fill a demo query so you can see how it works.',
    placement: 'bottom',
    skipBeacon: true,
  },
  {
    target: '[data-tour="search-submit"]',
    title: 'Run your search',
    content:
      'Hit the send button to search. We\'ll fire the demo query for you now — watch the map come to life!',
    placement: 'bottom',
    skipBeacon: true,
  },
  // Steps 3–4 (place cards + detail panel) are appended dynamically once results arrive
  {
    target: '[data-tour="profile-menu"]',
    title: 'Your account',
    content: 'Sign in to save your search history and personalise recommendations.',
    placement: 'bottom',
    skipBeacon: true,
  },
]

const MOBILE_STEPS: Step[] = [
  {
    target: '[data-tour="location-btn"]',
    title: 'Set your precise location',
    content:
      'Your location is currently approximate (IP-based). Tap this button to switch to precise GPS — search results will be much more accurate.',
    placement: 'top',
    skipBeacon: true,
  },
  {
    target: '[data-tour="mobile-search-input"]',
    title: 'Search anything nearby',
    content:
      'Type what you\'re looking for — e.g. "find a coffee shop close to me". We\'ll pre-fill a demo query so you can see how it works.',
    placement: 'top',
    skipBeacon: true,
  },
  {
    target: '[data-tour="mobile-search-submit"]',
    title: 'Run your search',
    content: 'Tap the send button to search. We\'ll fire the demo query for you now!',
    placement: 'top',
    skipBeacon: true,
  },
  {
    target: '[data-tour="profile-menu"]',
    title: 'Your account',
    content: 'Sign in to save your search history and personalise recommendations.',
    placement: 'bottom',
    skipBeacon: true,
  },
]

const RESULTS_STEP_DESKTOP: Step = {
  target: '[data-tour="place-cards"]',
  title: 'Your results',
  content:
    'Here are the results! Each card shows live occupancy, travel time, and open/closed status. Click a card to see full details.',
  placement: 'top',
  skipBeacon: true,
}

const RESULTS_STEP_MOBILE: Step = {
  target: '[data-tour="mobile-place-cards"]',
  title: 'Your results',
  content:
    'Here are the results! Each card shows live occupancy, travel time, and open/closed status. Tap a card to see full details.',
  placement: 'top',
  skipBeacon: true,
}

const DETAIL_STEP: Step = {
  target: '[data-tour="place-detail"]',
  title: 'Place details',
  content:
    'This panel shows everything about the place: phone number, website, live occupancy, estimated service time, and a directions button.',
  placement: 'left',
  skipBeacon: true,
}

// ─── Joyride tooltip styling ─────────────────────────────────────────────────

const TOUR_STYLES = {
  tooltip: {
    borderRadius: '16px',
    boxShadow: '0 8px 32px rgba(0,0,0,0.18)',
    padding: '20px 24px',
    maxWidth: 320,
    background: 'rgba(255,255,255,0.97)',
  },
  tooltipTitle: {
    fontSize: '15px',
    fontWeight: 600,
    marginBottom: 8,
    color: '#1f2937',
  },
  tooltipContent: {
    fontSize: '14px',
    lineHeight: 1.6,
    color: '#374151',
  },
  buttonPrimary: {
    backgroundColor: '#2563eb',
    borderRadius: '8px',
    fontSize: '13px',
    padding: '8px 16px',
  },
  buttonBack: {
    color: '#6b7280',
    fontSize: '13px',
  },
  buttonSkip: {
    color: '#9ca3af',
    fontSize: '13px',
  },
  overlay: {
    backgroundColor: 'rgba(0,0,0,0.45)',
  },
}

interface AppTourProps {
  run: boolean
  onStop: () => void
}

export default function AppTour({ run, onStop }: AppTourProps) {
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    setIsMobile(window.innerWidth < 768)
    // Reset any scroll that happened before the tour mounted
    window.scrollTo(0, 0)
  }, [])

  const baseSteps = isMobile ? MOBILE_STEPS : DESKTOP_STEPS
  const [steps, setSteps] = useState<Step[]>(baseSteps)
  const [stepIndex, setStepIndex] = useState(0)

  // Track which enrichment steps have been inserted so we only add them once
  const addedResults = useRef(false)
  const addedDetail = useRef(false)
  // The submit step is always index 2 (0-based)
  const submitStepIndex = 2
  // Fallback timer — advances the tour if the API call never resolves
  const fallbackTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    return () => {
      if (fallbackTimerRef.current) clearTimeout(fallbackTimerRef.current)
    }
  }, [])

  const { getToken } = useAuth()
  const { location: contextLocation } = useLocation()
  const {
    activePlaces,
    selectedPlaceId,
    setActivePlaces,
    setActiveUserLocation,
    setAiResponse,
    setIsQuerying,
    setSelectedPlaceId,
    setMobileMapRatio,
    setPendingQuery,
  } = useMapContext()

  // Re-initialise steps when isMobile resolves
  useEffect(() => {
    setSteps(isMobile ? MOBILE_STEPS : DESKTOP_STEPS)
    addedResults.current = false
    addedDetail.current = false
  }, [isMobile])

  // Insert results step once places arrive, then advance the tour to that step
  useEffect(() => {
    if (!run || addedResults.current || activePlaces.length === 0) return
    addedResults.current = true

    // Cancel the fallback timer — real results arrived in time
    if (fallbackTimerRef.current) {
      clearTimeout(fallbackTimerRef.current)
      fallbackTimerRef.current = null
    }

    const resultsStep = isMobile ? RESULTS_STEP_MOBILE : RESULTS_STEP_DESKTOP

    setSteps((prev) => {
      const next = [...prev]
      // Insert just before the profile/account step (last step)
      next.splice(next.length - 1, 0, resultsStep)
      return next
    })
    // Advance to the results step (submitStepIndex + 1 = 3)
    setStepIndex(submitStepIndex + 1)
  }, [activePlaces, run, isMobile])

  // Insert detail step once a place is selected (desktop only)
  useEffect(() => {
    if (!run || addedDetail.current || !selectedPlaceId || isMobile) return
    addedDetail.current = true

    setSteps((prev) => {
      const next = [...prev]
      const insertAt = next.findIndex((s) => s.target === '[data-tour="profile-menu"]')
      if (insertAt !== -1) next.splice(insertAt, 0, DETAIL_STEP)
      return next
    })
  }, [selectedPlaceId, run, isMobile])

  const fireDemo = useCallback(async () => {
    setIsQuerying(true)
    setActivePlaces([])
    setAiResponse(null)
    setSelectedPlaceId(null)
    if (isMobile) setMobileMapRatio(50)

    const effectiveLocation =
      contextLocation && contextLocation.latitude !== null && contextLocation.longitude !== null
        ? { latitude: contextLocation.latitude, longitude: contextLocation.longitude }
        : null

    try {
      const token = await getToken()
      const response = await fetch(`${config.apiUrl}/api/v1/query`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ text: DEMO_QUERY, location: effectiveLocation }),
      })
      if (response.ok) {
        const parsed = await response.json()
        setAiResponse(parsed.answer || '')
        setActivePlaces(parsed.places || [])
        if (parsed.userLocation) setActiveUserLocation(parsed.userLocation)
      }
    } catch {
      // Fail silently — the tour continues regardless of query success
    } finally {
      setIsQuerying(false)
    }
  }, [contextLocation, getToken, isMobile, setActivePlaces, setActiveUserLocation, setAiResponse, setIsQuerying, setMobileMapRatio, setSelectedPlaceId])

  const handleEvent = useCallback(
    (data: EventData) => {
      const { status, type, index, action } = data

      // Tour finished or skipped
      if (status === STATUS.FINISHED || status === STATUS.SKIPPED) {
        localStorage.setItem(TOUR_STORAGE_KEY, '1')
        onStop()
        return
      }

      // Pre-fill the search input when the user clicks Next on the input step (step 1)
      if (type === EVENTS.STEP_AFTER && index === submitStepIndex - 1 && action !== 'prev') {
        setPendingQuery(DEMO_QUERY)
      }

      // When the user clicks Next on the submit step, click the real search button
      // so they see the spinner and live results loading. The tour pauses here (no
      // stepIndex advance) and resumes when activePlaces arrives via the effect above.
      // A 15 s fallback advances the tour if the API never responds.
      if (type === EVENTS.STEP_AFTER && index === submitStepIndex && action !== 'prev') {
        const selector = isMobile ? '[data-tour="mobile-search-submit"]' : '[data-tour="search-submit"]'
        const btn = document.querySelector<HTMLButtonElement>(selector)
        if (btn && !btn.disabled) {
          btn.click()
        } else {
          // Button is disabled (input empty) — fire the demo query directly as fallback
          fireDemo()
        }
        // Fallback: advance anyway after 15 s to prevent a permanent hang
        fallbackTimerRef.current = setTimeout(() => {
          setStepIndex(submitStepIndex + 1)
        }, 15000)
        // Return early — don't advance stepIndex now; the activePlaces effect handles it
        return
      }

      // Normal step progression for all other steps
      if (type === EVENTS.STEP_AFTER || type === EVENTS.TARGET_NOT_FOUND) {
        setStepIndex((i) => i + (action === 'prev' ? -1 : 1))
      }
    },
    [fireDemo, isMobile, onStop, setPendingQuery],
  )

  if (!run) return null

  return (
    <Joyride
      steps={steps}
      stepIndex={stepIndex}
      run={run}
      continuous
      styles={TOUR_STYLES}
      options={{
        showProgress: true,
        buttons: ['back', 'skip', 'primary'],
        overlayClickAction: false,
        skipScroll: true,
        zIndex: 9999,
        primaryColor: '#2563eb',
        overlayColor: 'rgba(0,0,0,0.45)',
      }}
      onEvent={handleEvent}
      locale={{
        back: 'Back',
        close: 'Close',
        last: 'Finish',
        next: 'Next',
        skip: 'Skip tour',
      }}
    />
  )
}
