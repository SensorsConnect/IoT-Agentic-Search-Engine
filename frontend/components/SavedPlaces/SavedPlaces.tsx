'use client'

import { useCallback, useEffect, useState } from 'react'
import { useAuth } from '@clerk/nextjs'
import { Box, Flex, Heading, IconButton, ScrollArea, Text } from '@radix-ui/themes'
import { AiOutlineCloseCircle } from 'react-icons/ai'
import { FiMapPin } from 'react-icons/fi'
import { apiJson } from '@/lib/api'

interface SavedPlace {
  id: string
  place_name: string
  place_data: Record<string, unknown> | null
  note: string | null
  created_at: string
}

export const SavedPlaces = () => {
  const { getToken } = useAuth()
  const [places, setPlaces] = useState<SavedPlace[]>([])
  const [loading, setLoading] = useState(true)

  const fetchPlaces = useCallback(async () => {
    try {
      const token = await getToken()
      const data = await apiJson<SavedPlace[]>('/saved-places', {}, token)
      setPlaces(data)
    } catch (e) {
      console.error('Failed to fetch saved places:', e)
    } finally {
      setLoading(false)
    }
  }, [getToken])

  useEffect(() => {
    fetchPlaces()
  }, [fetchPlaces])

  const handleDelete = async (id: string) => {
    try {
      const token = await getToken()
      await apiJson(`/saved-places/${id}`, { method: 'DELETE' }, token)
      setPlaces((prev) => prev.filter((p) => p.id !== id))
    } catch (e) {
      console.error('Failed to delete saved place:', e)
    }
  }

  if (loading) {
    return (
      <Flex align="center" justify="center" className="p-8">
        <Text>Loading saved places...</Text>
      </Flex>
    )
  }

  if (places.length === 0) {
    return (
      <Flex direction="column" align="center" justify="center" className="p-8" gap="3">
        <FiMapPin size={48} className="text-gray-400" />
        <Text className="text-gray-500">No saved places yet</Text>
        <Text size="1" className="text-gray-400">
          Save places from chat responses to see them here
        </Text>
      </Flex>
    )
  }

  return (
    <ScrollArea style={{ height: '100%' }} type="auto">
      <Flex direction="column" gap="3" className="p-4">
        <Heading size="4">Saved Places</Heading>
        {places.map((place) => (
          <Box
            key={place.id}
            className="p-3 rounded-lg border border-gray-200 dark:border-gray-700"
          >
            <Flex justify="between" align="start">
              <Flex direction="column" gap="1">
                <Text weight="medium">{place.place_name}</Text>
                {place.note && (
                  <Text size="1" className="text-gray-500">
                    {place.note}
                  </Text>
                )}
                <Text size="1" className="text-gray-400">
                  Saved {new Date(place.created_at).toLocaleDateString()}
                </Text>
              </Flex>
              <IconButton
                size="1"
                variant="ghost"
                color="gray"
                className="cursor-pointer"
                onClick={() => handleDelete(place.id)}
              >
                <AiOutlineCloseCircle className="size-4" />
              </IconButton>
            </Flex>
          </Box>
        ))}
      </Flex>
    </ScrollArea>
  )
}

export default SavedPlaces
