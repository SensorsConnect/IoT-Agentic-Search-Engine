'use client'

import { useCallback, useState, useEffect } from 'react'
import { HamburgerMenuIcon } from '@radix-ui/react-icons'
import { Avatar, Flex, Heading, IconButton } from '@radix-ui/themes'
import cs from 'classnames'
import Image from 'next/image'
import NextLink from 'next/link'
import { FaGithub, FaMoon, FaSun } from 'react-icons/fa'
import { Link } from '../Link'
import { useTheme } from '../Themes'
import darkIcon from '/public/dark-icon.png'
import lightIcon from '/public/light-icon.png'

export const Header = () => {
  const { theme, setTheme, resolvedTheme } = useTheme()
  const [show, setShow] = useState(false)
  const [currentTheme, setCurrentTheme] = useState<'light' | 'dark'>('light')

  useEffect(() => {
    // Update current theme whenever resolvedTheme changes
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
      className={cs('block shadow-sm sticky top-0 dark:shadow-gray-500 py-3 px-4 z-20')}
      style={{ backgroundColor: 'var(--color-background)' }}
    >
      <Flex align="center" gap="3">
        {currentTheme === 'dark' ? (
          <Image src={darkIcon} alt="Dark Mode Icon" width={70} height={70} />
        ) : (
          <Image src={lightIcon} alt="Light Mode Icon" width={70} height={70} />
        )}
        <NextLink href="/">
          <Heading as="h3" size="3" style={{ maxWidth: 400 }} className="text-gray-900 dark:text-white">
            LocaleLive: Agentic Search Engine For IoT
          </Heading>
        </NextLink>
        <Flex align="center" gap="3" className="ml-auto">
          <nav className="hidden md:flex items-center gap-6">
            <NextLink href="/" className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white">
              Home
            </NextLink>
            <NextLink href="/chat" className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white">
              Chat
            </NextLink>
          </nav>
          <Avatar
            color="gray"
            size="2"
            radius="full"
            fallback={
              <Link href="https://github.com/SensorsConnect">
                <FaGithub />
              </Link>
            }
          />
          <div 
            onClick={toggleTheme}
            className="cursor-pointer text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
          >
            {currentTheme === 'dark' ? <FaSun size={20} /> : <FaMoon size={20} />}
          </div>
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
      {/* Mobile Navigation Menu */}
      {show && (
        <div className="md:hidden mt-4 pb-4">
          <nav className="flex flex-col gap-4">
            <NextLink href="/" className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white">
              Home
            </NextLink>
            <NextLink href="/chat" className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white">
              Chat
            </NextLink>
          </nav>
        </div>
      )}
    </header>
  )
}
