import { useCallback, useRef, useState } from 'react'
import { useStore } from '../store'
import type { TriggerEvent } from '../types/api'

const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000'

export function useSSEInvestigation() {
  const abortControllerRef = useRef<AbortController | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const applyWebSocketMessage = useStore((s) => s.applyWebSocketMessage)
  const triggerAlertFlash = useStore((s) => s.triggerAlertFlash)

  const disconnect = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    setIsConnected(false)
  }, [])

  const startCachedInvestigation = useCallback(
    async (entity: string) => {
      // Close any existing connection
      disconnect()

      const abortController = new AbortController()
      abortControllerRef.current = abortController

      try {
        setIsConnected(true)

        const response = await fetch(`${API_BASE}/api/investigate/cached`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ entity }),
          signal: abortController.signal,
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const reader = response.body?.getReader()
        if (!reader) {
          throw new Error('No response body')
        }

        const decoder = new TextDecoder()
        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()

          if (done) {
            setIsConnected(false)
            break
          }

          buffer += decoder.decode(value, { stream: true })

          // Split by double newline (SSE message boundary)
          const messages = buffer.split('\n\n')
          buffer = messages.pop() || '' // Keep incomplete message in buffer

          for (const message of messages) {
            if (!message.trim()) continue

            // Parse SSE message
            const lines = message.split('\n')
            let eventType = 'message'
            let data = ''

            for (const line of lines) {
              if (line.startsWith('event:')) {
                eventType = line.substring(6).trim()
              } else if (line.startsWith('data:')) {
                data = line.substring(5).trim()
              }
            }

            if (data) {
              try {
                const parsed = JSON.parse(data)
                const msg = { type: eventType, ...parsed }

                // Apply message to store (same format as WebSocket)
                applyWebSocketMessage(msg)

                if (msg.type === 'CONVERGENCE_REACHED') {
                  triggerAlertFlash()
                }

                if (msg.type === 'INVESTIGATION_COMPLETE') {
                  setIsConnected(false)
                }
              } catch (err) {
                console.error('[IHEE] Failed to parse SSE message:', err, data)
              }
            }
          }
        }
      } catch (err: any) {
        if (err.name !== 'AbortError') {
          console.error('[IHEE] SSE error:', err)
        }
        setIsConnected(false)
      }
    },
    [applyWebSocketMessage, triggerAlertFlash, disconnect]
  )

  const startLiveInvestigation = useCallback(
    async (trigger: TriggerEvent) => {
      // Close any existing connection
      disconnect()

      const abortController = new AbortController()
      abortControllerRef.current = abortController

      try {
        setIsConnected(true)

        const response = await fetch(`${API_BASE}/api/investigate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            entity: trigger.entity,
            trigger: {
              entity: trigger.entity,
              event: trigger.description,
              date: new Date().toISOString().split('T')[0],
              magnitude: trigger.magnitude || 'N/A',
              description: trigger.description,
            },
            mode: 'live',
          }),
          signal: abortController.signal,
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const reader = response.body?.getReader()
        if (!reader) {
          throw new Error('No response body')
        }

        const decoder = new TextDecoder()
        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()

          if (done) {
            setIsConnected(false)
            break
          }

          buffer += decoder.decode(value, { stream: true })

          const messages = buffer.split('\n\n')
          buffer = messages.pop() || ''

          for (const message of messages) {
            if (!message.trim()) continue

            const lines = message.split('\n')
            let eventType = 'message'
            let data = ''

            for (const line of lines) {
              if (line.startsWith('event:')) {
                eventType = line.substring(6).trim()
              } else if (line.startsWith('data:')) {
                data = line.substring(5).trim()
              }
            }

            if (data) {
              try {
                const parsed = JSON.parse(data)
                const msg = { type: eventType, ...parsed }

                applyWebSocketMessage(msg)

                if (msg.type === 'CONVERGENCE_REACHED') {
                  triggerAlertFlash()
                }

                if (msg.type === 'INVESTIGATION_COMPLETE') {
                  setIsConnected(false)
                }
              } catch (err) {
                console.error('[IHEE] Failed to parse SSE message:', err, data)
              }
            }
          }
        }
      } catch (err: any) {
        if (err.name !== 'AbortError') {
          console.error('[IHEE] SSE error:', err)
        }
        setIsConnected(false)
      }
    },
    [applyWebSocketMessage, triggerAlertFlash, disconnect]
  )

  return {
    startCachedInvestigation,
    startLiveInvestigation,
    isConnected,
    disconnect,
  }
}
