'use client'

import { Fragment, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { ThemeProviderProps, UseThemeProps } from './interface'
import { ThemeContext } from './ThemeContext'
import ThemeScript from './ThemeScript'
import { ColorSchemes, disableAnimation, getSystemTheme, MEDIA } from './utils'

export const ThemeProvider = (props: ThemeProviderProps) => {
  const context = useContext(ThemeContext)

  // Ignore nested context providers, just passthrough children
  if (context) return <Fragment>{props.children}</Fragment>
  return <Theme {...props} />
}

const Theme = ({
  forcedTheme,
  disableTransitionOnChange = false,
  enableSystem = true,
  enableColorScheme = true,
  storageKey = 'theme',
  themes = ['light', 'dark'],
  defaultTheme = enableSystem ? 'system' : 'light',
  attribute = 'class',
  value,
  children,
  nonce
}: ThemeProviderProps) => {
  const [theme, setThemeState] = useState<string>()
  const [resolvedTheme, setResolvedTheme] = useState<string>()
  const attrs = !value ? themes : Object.values(value)

  const applyTheme = useCallback(
    (theme: string) => {
      let resolved = theme
      if (!resolved) return

      // If theme is system, resolve it before setting theme
      if (theme === 'system' && enableSystem) {
        resolved = getSystemTheme()
      }

      const name = value ? value[resolved] : resolved
      const enable = disableTransitionOnChange ? disableAnimation() : null
      const root = document.documentElement

      if (attribute === 'class') {
        root.classList.remove(...attrs)

        if (name) root.classList.add(name)
      } else {
        if (name) {
          root.setAttribute(attribute, name)
        } else {
          root.removeAttribute(attribute)
        }
      }

      if (enableColorScheme) {
        const fallback = ColorSchemes.includes(defaultTheme) ? defaultTheme : null
        const colorScheme = ColorSchemes.includes(resolved) ? resolved : fallback
        root.style.colorScheme = colorScheme!
      }

      enable?.()
    },
    [
      attribute,
      attrs,
      defaultTheme,
      disableTransitionOnChange,
      enableColorScheme,
      enableSystem,
      value
    ]
  )

  const setTheme = useCallback<React.Dispatch<string>>(
    (theme) => {
      setThemeState(theme)

      // Save to storage with better error handling
      try {
        if (typeof window !== 'undefined') {
          localStorage.setItem(storageKey, theme)
        }
      } catch (e) {
        console.warn('Failed to save theme preference:', e)
      }
    },
    [storageKey]
  )

  const handleMediaQuery = useCallback(
    (e: MediaQueryListEvent | MediaQueryList) => {
      const resolved = getSystemTheme(e)
      setResolvedTheme(resolved)

      if (theme === 'system' && enableSystem && !forcedTheme) {
        // Add a small delay to prevent flickering on mobile
        setTimeout(() => {
          applyTheme('system')
        }, 50)
      }
    },
    [theme, enableSystem, forcedTheme, applyTheme]
  )

  // Always listen to System preference with better mobile support
  useEffect(() => {
    if (typeof window === 'undefined') return

    const media = window.matchMedia(MEDIA)
    
    // Use modern event listener if available
    if (media.addEventListener) {
      media.addEventListener('change', handleMediaQuery)
    } else {
      // Fallback for older browsers
      media.addListener(handleMediaQuery)
    }
    
    handleMediaQuery(media)

    return () => {
      if (media.removeEventListener) {
        media.removeEventListener('change', handleMediaQuery)
      } else {
        // Fallback for older browsers
        media.removeListener(handleMediaQuery)
      }
    }
  }, [handleMediaQuery])

  // localStorage event handling
  useEffect(() => {
    const handleStorage = (e: StorageEvent) => {
      if (e.key !== storageKey) {
        return
      }

      // If default theme set, use it if localstorage === null (happens on local storage manual deletion)
      const theme = e.newValue || defaultTheme
      setTheme(theme)
    }

    window.addEventListener('storage', handleStorage)
    return () => window.removeEventListener('storage', handleStorage)
  }, [defaultTheme, setTheme, storageKey])

  // Whenever theme or forcedTheme changes, apply it
  useEffect(() => {
    return applyTheme(forcedTheme ?? theme!)
  }, [applyTheme, forcedTheme, theme])

  useEffect(() => {
    const theme = localStorage.getItem(storageKey)
    setThemeState(theme || defaultTheme)
    setResolvedTheme(theme!)
  }, [defaultTheme, storageKey])

  const providerValue = useMemo(
    () =>
      ({
        theme,
        setTheme,
        forcedTheme,
        resolvedTheme: theme === 'system' ? resolvedTheme : theme,
        themes: enableSystem ? [...themes, 'system'] : themes,
        systemTheme: (enableSystem ? resolvedTheme : undefined) as 'light' | 'dark' | undefined
      }) as UseThemeProps,
    [theme, setTheme, forcedTheme, resolvedTheme, enableSystem, themes]
  )

  return (
    <ThemeContext.Provider value={providerValue}>
      <ThemeScript
        {...{
          forcedTheme,
          disableTransitionOnChange,
          enableSystem,
          enableColorScheme,
          storageKey,
          themes,
          defaultTheme,
          attribute,
          value,
          children,
          attrs,
          nonce
        }}
      />
      {children}
    </ThemeContext.Provider>
  )
}
