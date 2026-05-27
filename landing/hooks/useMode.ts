'use client'
import { createContext, useContext, useState, type ReactNode } from 'react'

type Mode = 'human' | 'agent'

interface ModeContextType {
  mode: Mode
  setMode: (m: Mode) => void
  toggle: () => void
}

const ModeContext = createContext<ModeContextType>({
  mode: 'human',
  setMode: () => {},
  toggle: () => {},
})

export function ModeProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<Mode>('human')
  const toggle = () => setMode(m => m === 'human' ? 'agent' : 'human')
  return (
    <ModeContext.Provider value={{ mode, setMode, toggle }}>
      {children}
    </ModeContext.Provider>
  )
}

export function useMode() {
  return useContext(ModeContext)
}

export function useModeStore() {
  return useMode()
}
