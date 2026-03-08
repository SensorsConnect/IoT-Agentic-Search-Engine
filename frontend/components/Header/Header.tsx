'use client'

import { useCallback, useState, useEffect } from 'react'
import { HamburgerMenuIcon } from '@radix-ui/react-icons'
import { Avatar, Flex, Heading, IconButton } from '@radix-ui/themes'
import cs from 'classnames'
import Image from 'next/image'
import NextLink from 'next/link'
import { usePathname } from 'next/navigation'
import { SignInButton, UserButton, SignedIn, SignedOut } from '@clerk/nextjs'
import { FaGithub, FaMoon, FaSun } from 'react-icons/fa'
import { Link } from '../Link'
import { useTheme } from '../Themes'
import darkIcon from '/public/localelive-dark-icon.png'
import lightIcon from '/public/localelive-light-icon.png'

export const Header = () => {
  const { theme, setTheme, resolvedTheme } = useTheme()
  const [show, setShow] = useState(false)
  const [currentTheme, setCurrentTheme] = useState<'light' | 'dark'>('light')
  const pathname = usePathname()
  const isExplorer = pathname === '/chat'

  useEffect(() => {
    if (resolvedTheme === 'dark' || resolvedTheme === 'light') {
      setCurrentTheme(resolvedTheme)
    }
  }, [resolvedTheme])

  const toggleNavBar = useCallback(() => {
    setShow((state) => !state)
  }, [])

  const toggleTheme = useCallback(() => {
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark'
    setTheme(newTheme)
    setCurrentTheme(newTheme)
  }, [currentTheme, setTheme])

  return (
    <header
      className={cs(
        'block sticky top-0 py-2 px-4 z-20',
        isExplorer
          ? 'bg-[#070810]/80 backdrop-blur-xl border-b border-white/5 shadow-none'
          : 'shadow-sm dark:shadow-gray-500 py-3',
      )}
      style={isExplorer ? undefined : { backgroundColor: 'var(--color-background)' }}
    >
      <Flex align="center" gap="3">
        {currentTheme === 'dark' || isExplorer ? (
          <Image src={darkIcon} alt="Dark Mode Icon" width={70} height={70} className={isExplorer ? 'md:w-[70px] w-[40px]' : ''} />
        ) : (
          <Image src={lightIcon} alt="Light Mode Icon" width={70} height={70} />
        )}
        <NextLink href="/">
          <Heading
            as="h3"
            size="3"
            style={{ maxWidth: 400 }}
            className={isExplorer ? 'text-gray-200' : 'text-gray-900 dark:text-white'}
          >
            <span className={isExplorer ? 'hidden md:inline' : ''}>LocaleLive: Agentic Search Engine For IoT</span>
            {isExplorer && <span className="md:hidden">LocaleLive</span>}
          </Heading>
        </NextLink>
        <Flex align="center" gap="3" className="ml-auto">
          <nav className="hidden md:flex items-center gap-6">
            <NextLink
              href="/"
              className={isExplorer
                ? 'text-gray-400 hover:text-neon-cyan transition-colors'
                : 'text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white'
              }
            >
              Home
            </NextLink>
            <NextLink
              href="/chat"
              className={isExplorer
                ? 'text-gray-400 hover:text-neon-cyan transition-colors'
                : 'text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white'
              }
            >
              Explorer
            </NextLink>
          </nav>
          <Avatar
            color="gray"
            size="2"
            radius="full"
            fallback={
              <Link href="https://github.com/SensorsConnect">
                <FaGithub className={isExplorer ? 'text-gray-400' : ''} />
              </Link>
            }
          />
          <div
            onClick={toggleTheme}
            className={cs(
              'cursor-pointer',
              isExplorer
                ? 'text-gray-400 hover:text-gray-200'
                : 'text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white'
            )}
          >
            {currentTheme === 'dark' || isExplorer ? <FaSun size={20} /> : <FaMoon size={20} />}
          </div>
          <SignedOut>
            <SignInButton mode="modal">
              <button
                className={cs(
                  'text-sm px-3 py-1.5 rounded-lg transition-colors',
                  isExplorer
                    ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30 hover:bg-neon-cyan/30'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                )}
              >
                Sign In
              </button>
            </SignInButton>
          </SignedOut>
          <SignedIn>
            <UserButton afterSignOutUrl="/" />
          </SignedIn>
        </Flex>
        <IconButton
          size="3"
          variant="ghost"
          color="gray"
          className="md:hidden"
          onClick={toggleNavBar}
        >
          <HamburgerMenuIcon width="16" height="16" />
        </IconButton>
      </Flex>
      {show && (
        isExplorer ? (
          /* Compact popover for explorer mobile — absolute so it doesn't push content */
          <div className="md:hidden absolute right-4 top-full mt-1 z-50 bg-surface/95 backdrop-blur-xl border border-white/10 rounded-xl p-2 min-w-[120px] shadow-lg">
            <nav className="flex flex-col gap-1">
              <NextLink
                href="/"
                onClick={() => setShow(false)}
                className="text-gray-400 hover:text-neon-cyan px-3 py-2 rounded-lg hover:bg-white/5 text-sm transition-colors"
              >
                Home
              </NextLink>
              <NextLink
                href="/chat"
                onClick={() => setShow(false)}
                className="text-gray-400 hover:text-neon-cyan px-3 py-2 rounded-lg hover:bg-white/5 text-sm transition-colors"
              >
                Explorer
              </NextLink>
            </nav>
          </div>
        ) : (
          <div className="md:hidden mt-4 pb-4">
            <nav className="flex flex-col gap-4">
              <NextLink
                href="/"
                className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
              >
                Home
              </NextLink>
              <NextLink
                href="/chat"
                className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
              >
                Explorer
              </NextLink>
            </nav>
          </div>
        )
      )}
    </header>
  )
}
