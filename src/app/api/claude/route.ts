import Anthropic from '@anthropic-ai/sdk'
import type { Message } from '@/types/claude'

export const runtime = 'nodejs'
export const maxDuration = 30

export async function POST(req: Request) {
  // 1. Origin guard — must be first, before any SDK instantiation
  const origin = req.headers.get('origin')
  const allowedOrigin = process.env.NEXT_PUBLIC_APP_URL

  if (!allowedOrigin || origin !== allowedOrigin) {
    return new Response('Forbidden', { status: 403 })
  }

  // 2. Parse and validate request body
  let messages: Message[]
  let system: string

  try {
    const body = await req.json()
    messages = body.messages
    system = body.system

    if (!Array.isArray(messages) || typeof system !== 'string') {
      return new Response('Bad Request', { status: 400 })
    }
  } catch {
    return new Response('Bad Request', { status: 400 })
  }

  // 3. Instantiate SDK (after origin guard)
  const client = new Anthropic({
    apiKey: process.env.ANTHROPIC_API_KEY,
  })

  // 4. Build a ReadableStream that enqueues only raw text delta bytes
  const encoder = new TextEncoder()

  const stream = new ReadableStream({
    async start(controller) {
      try {
        const anthropicStream = client.messages.stream({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 1024,
          system,
          messages,
        })

        for await (const event of anthropicStream) {
          if (
            event.type === 'content_block_delta' &&
            event.delta.type === 'text_delta'
          ) {
            controller.enqueue(encoder.encode(event.delta.text))
          }
        }

        controller.close()
      } catch (err) {
        controller.error(err)
      }
    },
  })

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'no-cache',
      'X-Content-Type-Options': 'nosniff',
    },
  })
}
