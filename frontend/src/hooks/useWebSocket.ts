import { useCallback, useRef, useState } from 'react'
import { useStore } from '../store'
import type { TriggerEvent } from '../types/api'

const WS_BASE = (import.meta.env.VITE_WS_URL as string | undefined) ?? 'ws://localhost:8000'

function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`
}

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const applyWebSocketMessage = useStore((s) => s.applyWebSocketMessage)
  const triggerAlertFlash = useStore((s) => s.triggerAlertFlash)

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setIsConnected(false)
  }, [])

  const startInvestigation = useCallback(
    (trigger: TriggerEvent) => {
      // Close any existing connection
      disconnect()

      const sessionId = generateSessionId()
      const url = `${WS_BASE}/ws/${sessionId}`

      let ws: WebSocket
      try {
        ws = new WebSocket(url)
      } catch (err) {
        console.error('[IHEE] Failed to open WebSocket:', err)
        return
      }

      wsRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
        // Send the investigation start command
        ws.send(
          JSON.stringify({
            trigger: trigger.description,
            entity: trigger.entity,
            ticker: trigger.ticker,
          })
        )
      }

      ws.onmessage = (event: MessageEvent) => {
        try {
          const msg = JSON.parse(event.data as string)
          applyWebSocketMessage(msg)
          if (msg.type === 'CONVERGENCE_REACHED') {
            triggerAlertFlash()
          }
          if (msg.type === 'INVESTIGATION_COMPLETE') {
            setIsConnected(false)
          }
        } catch (err) {
          console.error('[IHEE] Failed to parse WS message:', err)
        }
      }

      ws.onerror = (err) => {
        console.error('[IHEE] WebSocket error:', err)
        setIsConnected(false)
      }

      ws.onclose = () => {
        setIsConnected(false)
        wsRef.current = null
      }
    },
    [applyWebSocketMessage, triggerAlertFlash, disconnect]
  )

  return { startInvestigation, isConnected, disconnect }
}
