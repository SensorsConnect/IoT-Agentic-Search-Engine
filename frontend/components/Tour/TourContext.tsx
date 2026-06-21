'use client'

import { createContext, useContext, ReactNode } from 'react'

interface TourContextType {
  startTour: () => void
}

const TourContext = createContext<TourContextType>({ startTour: () => {} })

export function TourProvider({ children, startTour }: { children: ReactNode; startTour: () => void }) {
  return <TourContext.Provider value={{ startTour }}>{children}</TourContext.Provider>
}

export function useTourContext() {
  return useContext(TourContext)
}
