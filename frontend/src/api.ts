import type { AgentEvent, StatusResponse } from './types'

const BASE = '/api'

/**
 * Parse an SSE stream into AgentEvent objects.
 * Accepts an AbortSignal so the caller can cancel mid-stream.
 */
async function* parseSSEStream(
  response: Response,
  signal?: AbortSignal
): AsyncGenerator<AgentEvent> {
  const reader = response.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  try {
    while (true) {
      if (signal?.aborted) break

      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() ?? ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const raw = line.slice(6).trim()
          if (!raw) continue
          try {
            const event: AgentEvent = JSON.parse(raw)
            yield event
          } catch {
            // malformed — skip
          }
        }
      }
    }
  } finally {
    reader.cancel()
  }
}

export async function* generateBrief(signal?: AbortSignal): AsyncGenerator<AgentEvent> {
  const res = await fetch(`${BASE}/brief`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    signal,
  })
  if (!res.ok) {
    yield { type: 'error', message: `HTTP ${res.status}: ${res.statusText}` }
    return
  }
  yield* parseSSEStream(res, signal)
}

export async function* sendChat(message: string, signal?: AbortSignal): AsyncGenerator<AgentEvent> {
  const res = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
    signal,
  })
  if (!res.ok) {
    yield { type: 'error', message: `HTTP ${res.status}: ${res.statusText}` }
    return
  }
  yield* parseSSEStream(res, signal)
}

export async function* validateContent(content: string, signal?: AbortSignal): AsyncGenerator<AgentEvent> {
  const res = await fetch(`${BASE}/validate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
    signal,
  })
  if (!res.ok) {
    yield { type: 'error', message: `HTTP ${res.status}: ${res.statusText}` }
    return
  }
  yield* parseSSEStream(res, signal)
}

export async function resetSession(): Promise<void> {
  await fetch(`${BASE}/reset`, { method: 'POST' })
}

export async function getStatus(): Promise<StatusResponse> {
  const res = await fetch(`${BASE}/status`)
  return res.json()
}
