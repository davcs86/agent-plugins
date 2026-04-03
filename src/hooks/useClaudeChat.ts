'use client'

import { useState, useCallback } from 'react'
import type { Message } from '@/types/claude'

export function useClaudeChat(system: string) {
  const [messages, setMessages] = useState<Message[]>([])
  const [streaming, setStreaming] = useState(false)

  const send = useCallback(
    async (userInput: string) => {
      if (streaming || !userInput.trim()) return

      const userMessage: Message = { role: 'user', content: userInput.trim() }
      const nextMessages: Message[] = [...messages, userMessage]

      // Append user message + empty assistant placeholder optimistically
      setMessages([...nextMessages, { role: 'assistant', content: '' }])
      setStreaming(true)

      try {
        const res = await fetch('/api/claude', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ messages: nextMessages, system }),
        })

        if (!res.ok || !res.body) {
          throw new Error(`Request failed: ${res.status}`)
        }

        const reader = res.body.getReader()
        // { stream: true } buffers incomplete multi-byte sequences across chunks
        const decoder = new TextDecoder('utf-8', { fatal: false })

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value, { stream: true })

          setMessages((prev) => {
            const updated = [...prev]
            const last = updated[updated.length - 1]
            if (last?.role === 'assistant') {
              updated[updated.length - 1] = {
                ...last,
                content: last.content + chunk,
              }
            }
            return updated
          })
        }
      } catch (err) {
        console.error('[useClaudeChat] stream error:', err)
        // Remove the empty assistant placeholder on error
        setMessages((prev) =>
          prev[prev.length - 1]?.content === '' ? prev.slice(0, -1) : prev,
        )
      } finally {
        setStreaming(false)
      }
    },
    [messages, streaming, system],
  )

  return { messages, send, streaming }
}
