import { useState, useRef, useEffect, useCallback } from 'react'
import { Header } from './components/Header'
import { WelcomeScreen } from './components/WelcomeScreen'
import { MessageBubble } from './components/MessageBubble'
import { ChatInput } from './components/ChatInput'
import { generateBrief, sendChat, validateContent, resetSession, getStatus } from './api'
import type { ChatMessage, AgentEvent, AppState } from './types'

const uid = () => Math.random().toString(36).slice(2)

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [appState, setAppState] = useState<AppState>('idle')
  const [totalCalls, setTotalCalls] = useState(0)
  const [conversationTurns, setConversationTurns] = useState(0)
  const [validatingId, setValidatingId] = useState<string | null>(null)

  const bottomRef = useRef<HTMLDivElement>(null)
  const abortRef = useRef<AbortController | null>(null)
  // Keep a live ref to messages to avoid stale closure in async handlers
  const messagesRef = useRef<ChatMessage[]>([])
  messagesRef.current = messages

  /* ── Scroll to bottom on new messages ─────────────────────────────── */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  /* ── Poll LLM usage while active ──────────────────────────────────── */
  useEffect(() => {
    if (appState === 'idle' || appState === 'ready') return
    const id = setInterval(async () => {
      try {
        const s = await getStatus()
        setTotalCalls(s.total_llm_calls)
        setConversationTurns(s.conversation_turns)
      } catch { /* network hiccup — ignore */ }
    }, 2500)
    return () => clearInterval(id)
  }, [appState])

  /* ── Message helpers ───────────────────────────────────────────────── */
  const addMessage = useCallback((msg: ChatMessage) => {
    setMessages(prev => [...prev, msg])
  }, [])

  const patchMessage = useCallback((id: string, patch: Partial<ChatMessage>) => {
    setMessages(prev => prev.map(m => m.id === id ? { ...m, ...patch } : m))
  }, [])

  /* ── Core SSE streamer ─────────────────────────────────────────────── */
  const streamInto = async (
    gen: AsyncGenerator<AgentEvent>,
    msgId: string,
  ): Promise<boolean> => {
    const logs: AgentEvent[] = []
    let ok = true
    try {
      for await (const ev of gen) {
        switch (ev.type) {
          case 'log':
          case 'tool_call':
          case 'tool_result':
            logs.push(ev)
            patchMessage(msgId, { logs: [...logs], isStreaming: true })
            break
          case 'result':
            patchMessage(msgId, { content: ev.content ?? '', logs: [...logs], isStreaming: true })
            break
          case 'error':
            patchMessage(msgId, {
              content: ev.message ?? 'Something went wrong. Please try again.',
              isError: true, isStreaming: false, logs: [...logs],
            })
            ok = false
            break
          case 'done':
            break
        }
        if (ev.type === 'error') break
      }
    } catch (e: unknown) {
      // AbortError = user clicked Stop — not a real error
      if (!(e instanceof Error && e.name === 'AbortError')) ok = false
    }
    patchMessage(msgId, { isStreaming: false, logs: [...logs] })
    return ok
  }

  /* ── Refresh usage stats ───────────────────────────────────────────── */
  const refreshStats = async () => {
    try {
      const s = await getStatus()
      setTotalCalls(s.total_llm_calls)
      setConversationTurns(s.conversation_turns)
    } catch { /* ignore */ }
  }

  /* ── Handlers ──────────────────────────────────────────────────────── */
  const handleStop = () => {
    abortRef.current?.abort()
    abortRef.current = null
    setAppState('ready')
  }

  const handleGenerateBrief = async () => {
    if (appState !== 'idle') return
    const ctrl = new AbortController()
    abortRef.current = ctrl
    setAppState('generating_brief')

    const id = uid()
    addMessage({ id, role: 'assistant', content: '', timestamp: new Date(), logs: [], isStreaming: true })

    await streamInto(generateBrief(ctrl.signal), id)
    abortRef.current = null
    setAppState('ready')
    await refreshStats()
  }

  const handleChat = async (text: string) => {
    if (appState !== 'ready') return
    const ctrl = new AbortController()
    abortRef.current = ctrl

    addMessage({ id: uid(), role: 'user', content: text, timestamp: new Date() })
    setAppState('chatting')

    const aid = uid()
    addMessage({ id: aid, role: 'assistant', content: '', timestamp: new Date(), logs: [], isStreaming: true })

    await streamInto(sendChat(text, ctrl.signal), aid)
    abortRef.current = null
    setAppState('ready')
    await refreshStats()
  }

  const handleValidate = async (content: string) => {
    // Find the message by content using the live ref (no stale closure)
    const target = [...messagesRef.current]
      .reverse()
      .find(m => m.content === content && m.role === 'assistant')
    if (!target) return

    const ctrl = new AbortController()
    abortRef.current = ctrl
    setValidatingId(target.id)
    setAppState('validating')

    const validatorLogs: AgentEvent[] = []
    let result = ''
    try {
      for await (const ev of validateContent(content, ctrl.signal)) {
        if (ev.type === 'log' || ev.type === 'tool_call' || ev.type === 'tool_result') {
          validatorLogs.push(ev)
        } else if (ev.type === 'validation_result') {
          result = ev.content ?? ''
        } else if (ev.type === 'done' || ev.type === 'error') {
          break
        }
      }
    } catch { /* abort — ignore */ }

    patchMessage(target.id, { validationResult: result || 'Validation complete.' })
    abortRef.current = null
    setValidatingId(null)
    setAppState('ready')
    await refreshStats()
  }

  const handleReset = async () => {
    abortRef.current?.abort()
    abortRef.current = null
    await resetSession()
    setMessages([])
    setAppState('idle')
    setTotalCalls(0)
    setConversationTurns(0)
  }

  /* ── Derived state ─────────────────────────────────────────────────── */
  const isIdle      = appState === 'idle'
  const isStreaming  = appState === 'generating_brief' || appState === 'chatting'
  const showWelcome = (isIdle || appState === 'generating_brief') && messages.length === 0

  /* ── Render ────────────────────────────────────────────────────────── */
  return (
    <div className="h-screen flex flex-col bg-[#0b0b0f] overflow-hidden">
      <Header
        totalCalls={totalCalls}
        conversationTurns={conversationTurns}
        onReset={handleReset}
        isActive={isStreaming}
      />

      <main className="flex-1 overflow-y-auto overscroll-none">
        {showWelcome ? (
          <WelcomeScreen
            onGenerateBrief={handleGenerateBrief}
            isLoading={appState === 'generating_brief'}
          />
        ) : (
          <div className="max-w-3xl mx-auto w-full px-4 sm:px-6 py-6 space-y-5 pb-4">
            {messages.map((msg, i) => (
              <MessageBubble
                key={msg.id}
                message={msg}
                onValidate={
                  msg.role === 'assistant' && !msg.isStreaming && !msg.isError && msg.content
                    ? handleValidate
                    : undefined
                }
                isValidating={validatingId === msg.id}
              />
            ))}
            <div ref={bottomRef} className="h-1" />
          </div>
        )}
      </main>

      {/* Input bar — only after session starts */}
      {!isIdle && (
        <ChatInput
          onSend={handleChat}
          onStop={handleStop}
          disabled={appState === 'validating'}
          isStreaming={isStreaming}
          placeholder="Ask about your commitments, deadlines, or action items…"
        />
      )}
    </div>
  )
}
