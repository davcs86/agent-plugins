'use client'

import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import { useClaudeChat } from '@/hooks/useClaudeChat'

const SYSTEM_PROMPT = `You are an expert rental property management assistant. You help landlords, \
property managers, and tenants with questions about:
- Lease agreements and terms
- Tenant screening and communications
- Maintenance requests and vendor management
- Rent collection and late fees
- Local landlord-tenant law and compliance
- Property inspections
- Security deposit handling

Be concise, practical, and reference relevant legal considerations where appropriate. \
Always recommend consulting a local attorney for jurisdiction-specific legal advice.`

export default function RentalManagementPage() {
  const { messages, send, streaming } = useClaudeChat(SYSTEM_PROMPT)
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || streaming) return
    const value = input
    setInput('')
    await send(value)
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-4 flex-shrink-0">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-900">
              Rental Management Assistant
            </h1>
            <p className="text-sm text-gray-500">Powered by Claude</p>
          </div>
          <Link
            href="/"
            className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
          >
            ← All artifacts
          </Link>
        </div>
      </header>

      {/* Message list */}
      <div className="flex-1 overflow-y-auto py-6 px-4">
        <div className="max-w-3xl mx-auto space-y-4">
          {messages.length === 0 && (
            <p className="text-center text-gray-400 mt-16 text-sm">
              Ask me anything about rental property management.
            </p>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                  msg.role === 'user'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-white border border-gray-200 text-gray-800'
                }`}
              >
                {msg.content}
                {msg.role === 'assistant' &&
                  streaming &&
                  i === messages.length - 1 && (
                    <span className="inline-block w-1.5 h-4 ml-0.5 bg-gray-400 animate-pulse rounded-sm align-middle" />
                  )}
              </div>
            </div>
          ))}

          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input form */}
      <div className="border-t border-gray-200 bg-white px-4 py-4 flex-shrink-0">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={streaming}
            placeholder="Ask about leases, tenants, maintenance..."
            className="flex-1 rounded-xl border border-gray-300 bg-gray-50 px-4 py-3 text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={streaming || !input.trim()}
            className="px-5 py-3 bg-indigo-600 text-white text-sm font-medium rounded-xl hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {streaming ? 'Sending…' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  )
}
