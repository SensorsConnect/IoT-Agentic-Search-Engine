'use client'

import {
  forwardRef,
  useCallback,
  useContext,
  useEffect,
  useImperativeHandle,
  useRef,
  useState
} from 'react'
import { Flex, Heading, IconButton, ScrollArea, Tooltip } from '@radix-ui/themes'
import ContentEditable from 'react-contenteditable'
import toast from 'react-hot-toast'
import { AiOutlineClear, AiOutlineLoading3Quarters, AiOutlineUnorderedList, AiOutlineInfoCircle, AiOutlineEnvironment } from 'react-icons/ai'
import { FiSend } from 'react-icons/fi'
import ChatContext from './chatContext'
import type { Chat, ChatMessage } from './interface'
import Message from './Message'
import { config } from '@/utils/environment'
import { LocationButton, useLocation } from '@/components/Location'

import './index.scss'

const HTML_REGULAR =
  /<(?!img|table|\/table|thead|\/thead|tbody|\/tbody|tr|\/tr|td|\/td|th|\/th|br|\/br).*?>/gi

export interface ChatProps {}

export interface ChatGPInstance {
  setConversation: (messages: ChatMessage[]) => void
  getConversation: () => ChatMessage[]
  focus: () => void
}

const postChatOrQuestion = async (chat: Chat, messages: any[], input: string, location?: { latitude: number; longitude: number } | null) => {
  const url = `${config.apiUrl}/query`
  
  const data: any = {
    "threadId": chat.id,
    text: input
  }

  // Add location data if available and valid
  if (location && location.latitude !== null && location.longitude !== null) {
    data.location = {
      latitude: location.latitude,
      longitude: location.longitude
    }
    console.log('✅ Adding location to request:', data.location)
  } else {
    data.location = null
    console.log('❌ No valid location to add. Location value:', location)
  }

  console.log('=== FINAL REQUEST PAYLOAD ===')
  console.log('URL:', url)
  console.log('Method: PUT')
  console.log('Payload:', JSON.stringify(data, null, 2))
  console.log('============================')

  return await fetch(url, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
}

const Chat = (props: ChatProps, ref: any) => {
  const { debug, currentChatRef, saveMessages, onToggleSidebar, forceUpdate } =
    useContext(ChatContext)

  // Get location from context as a fallback
  const { location: contextLocation, requestLocation } = useLocation()

  const [isLoading, setIsLoading] = useState(false)
  const [currentLocation, setCurrentLocation] = useState<{ latitude: number; longitude: number } | null>(null)
  const [isLocationLoading, setIsLocationLoading] = useState(true) // Track location loading state

  // Wrapped setter to log when location is set
  const handleLocationChange = useCallback((location: { latitude: number; longitude: number } | null) => {
    console.log('📍 handleLocationChange called with:', location)
    setCurrentLocation(location)
    setIsLocationLoading(false) // Location is ready
  }, [])

  // Debug: Log when currentLocation changes
  useEffect(() => {
    console.log('🔄 Location state changed (via setState):', currentLocation)
    if (currentLocation) {
      console.log('   ✅ State has location:', {
        lat: currentLocation.latitude,
        lng: currentLocation.longitude
      })
    }
  }, [currentLocation])

  // Debug: Log when context location changes
  useEffect(() => {
    console.log('🔄 Context location changed:', contextLocation)
    if (contextLocation) {
      console.log('   ✅ Context has location:', {
        lat: contextLocation.latitude,
        lng: contextLocation.longitude,
        source: contextLocation.source
      })
    }
  }, [contextLocation])

  // Auto-sync context location to local state when context changes
  useEffect(() => {
    if (contextLocation && contextLocation.latitude !== null && contextLocation.longitude !== null) {
      console.log('🔄 Auto-syncing context location to local state:', contextLocation)
      // Always sync from context to state, not just when currentLocation is null
      setCurrentLocation({
        latitude: contextLocation.latitude,
        longitude: contextLocation.longitude
      })
      setIsLocationLoading(false) // Location is ready
    } else if (!contextLocation && currentLocation) {
      // Clear local state if context location is cleared
      console.log('🔄 Clearing local state as context location is null')
      setCurrentLocation(null)
    }
  }, [contextLocation]) // Remove currentLocation from dependencies to avoid circular updates

  // Stop loading after 3 seconds even if location fails
  useEffect(() => {
    const timeout = setTimeout(() => {
      if (isLocationLoading) {
        console.log('⏱️ Location loading timeout - allowing user to send without location')
        setIsLocationLoading(false)
      }
    }, 3000)

    return () => clearTimeout(timeout)
  }, [isLocationLoading])

  // Auto-request location when chat page loads
  useEffect(() => {
    const autoRequestLocation = async () => {
      console.log('� Auto-requesting location on page load...')
      console.log('Initial state - contextLocation:', contextLocation, 'currentLocation:', currentLocation)
      
      // Only auto-request if we don't already have a location
      if (!contextLocation) {
        console.log('📍 No context location found, requesting...')
        const location = await requestLocation()
        if (location && location.latitude !== null && location.longitude !== null) {
          console.log('✅ Auto-location obtained from requestLocation:', location)
          // The context will be updated automatically, which will trigger the sync effect
        } else {
          console.log('❌ Location request returned null')
          // toast.error('Could not detect location. Please click the location button or mention your location.')
        }
      } else {
        console.log('📍 Context location already available:', contextLocation)
      }
    }

    // Add a small delay to ensure context is initialized
    const timer = setTimeout(() => {
      autoRequestLocation()
    }, 100)

    return () => clearTimeout(timer)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []) // Run only once on mount

  // Debug: Log current state every 2 seconds (remove after debugging)
  useEffect(() => {
    const interval = setInterval(() => {
      console.log('⏰ PERIODIC CHECK:', {
        currentLocation,
        contextLocation,
        hasStateLocation: currentLocation !== null,
        hasContextLocation: contextLocation !== null
      })
    }, 5000) // Every 5 seconds

    return () => clearInterval(interval)
  }, [currentLocation, contextLocation])

  const conversationRef = useRef<ChatMessage[]>()

  const [message, setMessage] = useState('')

  const [currentMessage, setCurrentMessage] = useState<string>('')

  const textAreaRef = useRef<HTMLElement>(null)

  const conversation = useRef<ChatMessage[]>([])

  const bottomOfChatRef = useRef<HTMLDivElement>(null)
  const sendMessage = useCallback(
    async (e: any) => {
      if (!isLoading) {
        e.preventDefault()
        const input = textAreaRef.current?.innerHTML?.replace(HTML_REGULAR, '') || ''

        if (input.length < 1) {
          toast.error('Please type a message to continue.')
          return
        }

        // Debug: Log current location state before sending
        console.log('=== SENDING MESSAGE ===')
        console.log('Current location state (from state):', currentLocation)
        console.log('Context location:', contextLocation)
        
        // Use currentLocation from state if available, otherwise fall back to context location
        const effectiveLocation = currentLocation || (contextLocation && contextLocation.latitude !== null && contextLocation.longitude !== null ? {
          latitude: contextLocation.latitude,
          longitude: contextLocation.longitude
        } : null)
        
        console.log('Effective location to send:', effectiveLocation)
        console.log('Location exists:', effectiveLocation !== null)
        if (effectiveLocation) {
          console.log('Location details:', {
            latitude: effectiveLocation.latitude,
            longitude: effectiveLocation.longitude
          })
        }

        const message = [...conversation.current]
        conversation.current = [...conversation.current, { content: input, role: 'user' }]
        setMessage('')
        setIsLoading(true)
        try {
          const response = await postChatOrQuestion(currentChatRef?.current!, message, input, effectiveLocation)

          if (response.ok) {
            const data = response.body
            if (!data) {
              throw new Error('No data')
            }

            const reader = data.getReader()
            const decoder = new TextDecoder('utf-8')
            let done = false
            let resultContent = ''

            while (!done) {
              try {
                const { value, done: readerDone } = await reader.read()
                const char = decoder.decode(value)
                if (char) {
                  setCurrentMessage((state) => {
                    if (debug) {
                      console.log({ char })
                    }
                    resultContent = state + char
                    return resultContent
                  })
                }
                done = readerDone
              } catch {
                done = true
              }
            }
            // The delay of timeout can not be 0 as it will cause the message to not be rendered in racing condition
            setTimeout(() => {
                 // Parse the accumulated resultContent as JSON and access the 'answer' key
              const parsedData = JSON.parse(resultContent);
              const answer = parsedData.answer;
              if (debug) {
                console.log({ resultContent })
              }
              conversation.current = [
                ...conversation.current,
                { content: answer, role: 'assistant' }
              ]

              setCurrentMessage('')
            }, 1)
          } else {
            const result = await response.json()
            if (response.status === 401) {
              conversation.current.pop()
              location.href =
                result.redirect +
                `?callbackUrl=${encodeURIComponent(location.pathname + location.search)}`
            } else {
              toast.error(result.error)
            }
          }

          setIsLoading(false)
        } catch (error: any) {
          console.error(error)
          toast.error(error.message)
          setIsLoading(false)
        }
      }
    },
    [currentChatRef, debug, isLoading, currentLocation, contextLocation]
  )

  const handleKeypress = useCallback(
    (e: any) => {
      if (e.keyCode == 13 && !e.shiftKey) {
        // Prevent sending if location is still loading
        if (isLocationLoading) {
          console.log('⏸️ Cannot send while location is loading')
          // toast('Please wait, detecting your location...', { icon: '🔄' })
          e.preventDefault()
          return
        }
        sendMessage(e)
        e.preventDefault()
      }
    },
    [sendMessage, isLocationLoading]
  )

  const clearMessages = () => {
    conversation.current = []
    forceUpdate?.()
  }

  useEffect(() => {
    if (textAreaRef.current) {
      textAreaRef.current.style.height = '50px'
      textAreaRef.current.style.height = `${textAreaRef.current.scrollHeight + 2}px`
    }
  }, [message, textAreaRef])

  useEffect(() => {
    if (bottomOfChatRef.current) {
      bottomOfChatRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [conversation, currentMessage])

  useEffect(() => {
    conversationRef.current = conversation.current
    if (currentChatRef?.current?.id) {
      saveMessages?.(conversation.current)
    }
  }, [currentChatRef, conversation.current, saveMessages])

  useEffect(() => {
    if (!isLoading) {
      textAreaRef.current?.focus()
    }
  }, [isLoading])

  useImperativeHandle(ref, () => {
    return {
      setConversation(messages: ChatMessage[]) {
        conversation.current = messages
        forceUpdate?.()
      },
      getConversation() {
        return conversationRef.current
      },
      focus: () => {
        textAreaRef.current?.focus()
      }
    }
  })

  return (
    <Flex direction="column" height="100%" className="relative" gap="3">
      <Flex
        justify="between"
        align="center"
        py="3"
        px="4"
        style={{ backgroundColor: 'var(--gray-a2)' }}
      >
        <Heading size="4">{currentChatRef?.current?.persona?.name || 'None'}</Heading>
      </Flex>
      <ScrollArea
        className="flex-1 px-4"
        type="auto"
        scrollbars="vertical"
        style={{ height: '100%' }}
      >
        {conversation.current.map((item, index) => (
          <Message key={index} message={item} />
        ))}
        {currentMessage && <Message message={{ content: currentMessage, role: 'assistant' }} />}
        <div ref={bottomOfChatRef}></div>
      </ScrollArea>
      <div className="px-4 pb-3">
        <Flex align="end" justify="between" gap="3" className="relative">
          <div className="rt-TextAreaRoot rt-r-size-1 rt-variant-surface flex-1 rounded-3xl chat-textarea">
            <ContentEditable
              innerRef={textAreaRef}
              style={{
                minHeight: '24px',
                maxHeight: '200px',
                overflowY: 'auto',
                opacity: isLocationLoading ? 0.5 : 1
              }}
              className="rt-TextAreaInput text-base"
              html={message}
              disabled={isLoading}
              onChange={(e) => {
                setMessage(e.target.value.replace(HTML_REGULAR, ''))
              }}
              onKeyDown={(e) => {
                handleKeypress(e)
              }}
            />
            <div className="rt-TextAreaChrome"></div>
          </div>
          <Flex gap="3" className="absolute right-0 pr-4 bottom-2 pt">
            {isLoading && (
              <Flex
                width="6"
                height="6"
                align="center"
                justify="center"
                style={{ color: 'var(--accent-11)' }}
              >
                <AiOutlineLoading3Quarters className="animate-spin size-4" />
              </Flex>
            )}
            <Tooltip content={isLocationLoading ? 'Detecting location...' : 'Send Message'}>
              <IconButton
                variant="soft"
                disabled={isLoading || isLocationLoading}
                color="gray"
                size="2"
                className="rounded-xl cursor-pointer"
                onClick={sendMessage}
              >
                {isLocationLoading ? (
                  <AiOutlineLoading3Quarters className="size-4 animate-spin" />
                ) : (
                  <FiSend className="size-4" />
                )}
              </IconButton>
            </Tooltip>
            <Tooltip content={'Clear History'}>
              <IconButton
                variant="soft"
                color="gray"
                size="2"
                className="rounded-xl cursor-pointer"
                disabled={isLoading}
                onClick={clearMessages}
              >
                <AiOutlineClear className="size-4" />
              </IconButton>
            </Tooltip>
            <Tooltip content={'Toggle Sidebar'}>
              <IconButton
                variant="soft"
                color="gray"
                size="2"
                className="rounded-xl md:hidden cursor-pointer"
                disabled={isLoading}
                onClick={onToggleSidebar}
              >
                <AiOutlineUnorderedList className="size-4" />
              </IconButton>
            </Tooltip>
          </Flex>
        </Flex>
        
        {/* Location Status and Button Row */}
        <Flex direction="column" gap="2" className="px-4 py-2">
          {isLocationLoading && (
            <Flex align="center" justify="center" gap="2" className="text-sm text-blue-500">
              <AiOutlineLoading3Quarters className="size-4 animate-spin" />
              <span>Detecting your location...</span>
            </Flex>
          )}
          {!isLocationLoading && currentLocation && (
            <Flex align="center" justify="center" gap="2" className="text-sm text-green-600">
              <AiOutlineEnvironment className="size-4" />
              <span>Location detected: {currentLocation.latitude.toFixed(4)}, {currentLocation.longitude.toFixed(4)}</span>
            </Flex>
          )}
          <Flex justify="center">
            <LocationButton onLocationChange={handleLocationChange} />
          </Flex>
        </Flex>
        
        <div className="mt-2 text-sm text-gray-500 text-center space-y-1">
          <p className="flex items-center justify-center gap-2">
            <AiOutlineInfoCircle className="size-4 text-blue-500" />
            This demo is an implementation for the Agentic Search Engine for Real-Time IoT Data
          </p>
          <p className="flex items-center justify-center gap-2">
            <AiOutlineEnvironment className="size-4 text-green-500" />
            Assistant assumes user location in downtown Toronto, but you can explicitly mention your location, city or region and localelive assistant can serve you
          </p>
        </div>
      </div>
    </Flex>
  )
}

export default forwardRef<ChatGPInstance, ChatProps>(Chat)
