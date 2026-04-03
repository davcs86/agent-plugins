# my-claude-artifacts

A portfolio of AI-powered tools built with [Claude](https://anthropic.com) and Next.js 15.

## Stack

- **Next.js 15.5** (App Router, TypeScript)
- **React 19**
- **Tailwind CSS 3.4**
- **@anthropic-ai/sdk**

---

## Local Setup

### 1. Install dependencies

```bash
npm install
```

### 2. Configure environment

```bash
cp .env.local.example .env.local
```

Edit `.env.local` and set both variables:

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Your key from [console.anthropic.com](https://console.anthropic.com) |
| `NEXT_PUBLIC_APP_URL` | `http://localhost:3000` for local dev |

> **Important:** `NEXT_PUBLIC_APP_URL` must match exactly (no trailing slash) — it is used as the origin guard in the API route.

### 3. Run the dev server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## Project Structure

```
src/
  app/
    api/claude/route.ts        # Streaming route handler (server-side only)
    globals.css                # Tailwind directives
    layout.tsx                 # Root layout
    page.tsx                   # Landing page / artifact list
    rental-management/
      page.tsx                 # Rental management chat UI
  hooks/
    useClaudeChat.ts           # Shared streaming chat hook
  types/
    claude.ts                  # Message / Role types
```

---

## How to Add a New Artifact

1. **Create a new route** under `src/app/<your-artifact>/page.tsx`
2. Mark it `'use client'` and import `useClaudeChat`
3. Write a scoped `SYSTEM_PROMPT` constant for your artifact's domain
4. Build a self-contained chat UI using `{ messages, send, streaming }` from the hook
5. **Add a card** to the `artifacts` array in `src/app/page.tsx`

```tsx
// src/app/my-new-artifact/page.tsx
'use client'

import { useState } from 'react'
import { useClaudeChat } from '@/hooks/useClaudeChat'

const SYSTEM_PROMPT = `You are an expert in ...`

export default function MyNewArtifactPage() {
  const { messages, send, streaming } = useClaudeChat(SYSTEM_PROMPT)
  // ... your UI
}
```

No changes to the shared route handler or hook are needed.

---

## Vercel Deployment

1. **Import** the repo at [vercel.com/new](https://vercel.com/new)
2. **Add Environment Secrets** in the Vercel dashboard under *Settings → Environment Variables*:

| Secret | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `NEXT_PUBLIC_APP_URL` | Your production URL, e.g. `https://my-claude-artifacts.vercel.app` |

3. **Deploy** — Vercel auto-detects Next.js. The `vercel.json` sets `maxDuration: 30` on the API route to accommodate streaming response times.

> On the Vercel Hobby plan, `maxDuration` is capped at 60 s; Pro allows higher limits.

---

## Security Model

### Why this public repo is safe

The Anthropic API key is **never present in the client bundle**. It lives exclusively in server-side environment variables and is read only inside `src/app/api/claude/route.ts` — a Next.js Route Handler that runs on the server.

### Origin guard

Every request to `/api/claude` is validated before the Anthropic SDK is instantiated:

```ts
const origin = req.headers.get('origin')
const allowedOrigin = process.env.NEXT_PUBLIC_APP_URL

if (!allowedOrigin || origin !== allowedOrigin) {
  return new Response('Forbidden', { status: 403 })
}
```

Requests from any origin other than your configured app URL are rejected with `403` before any Anthropic API call is made. This prevents third-party sites from proxying your key by embedding your API route in their own pages.

> **Note:** The origin header is set by browsers automatically and cannot be spoofed by client-side JavaScript on a different origin. Server-to-server requests (which can set arbitrary headers) are a separate threat model — rate limiting and spend alerts in the Anthropic console are recommended for production.
