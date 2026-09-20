import { useState, useEffect, useRef } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import type { AgentEvent } from '../types'

interface ReasoningTraceProps {
  logs: AgentEvent[]
  isStreaming?: boolean
}

function stepTone(type: AgentEvent['type']) {
  switch (type) {
    case 'tool_call':   return 'text-amber-200/80'
    case 'tool_result': return 'text-emerald-300/80'
    case 'error':       return 'text-rose-300'
    default:            return 'text-ink-400'
  }
}

function stepPrefix(type: AgentEvent['type']) {
  switch (type) {
    case 'tool_call':   return 'tool'
    case 'tool_result': return 'result'
    case 'error':       return 'error'
    default:            return 'step'
  }
}

export function ReasoningTrace({ logs, isStreaming }: ReasoningTraceProps) {
  const [expanded, setExpanded] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isStreaming && logs.length > 0) setExpanded(true)
    if (!isStreaming) setExpanded(false)
  }, [isStreaming, logs.length])

  useEffect(() => {
    if (expanded && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [logs.length, expanded])

  if (logs.length === 0 && !isStreaming) return null

  const toolCalls = logs.filter(l => l.type === 'tool_call').length
  const label = isStreaming
    ? `Activity${toolCalls > 0 ? ` · ${toolCalls} tool${toolCalls > 1 ? 's' : ''}` : ''}…`
    : `${logs.length} step${logs.length !== 1 ? 's' : ''}${toolCalls > 0 ? ` · ${toolCalls} tool${toolCalls !== 1 ? 's' : ''}` : ''}`

  return (
    <div className="rounded-lg overflow-hidden border border-white/[0.05] bg-ink-950/60">
      <button
        onClick={() => setExpanded(v => !v)}
        className="w-full flex items-center gap-2 px-3 py-2 text-[11px] text-ink-400 hover:text-ink-300 transition-colors text-left select-none focus-ring"
      >
        {expanded ? <ChevronDown size={11} /> : <ChevronRight size={11} />}
        <span className="flex-1 font-medium">{label}</span>
        {isStreaming && (
          <span className="w-1.5 h-1.5 rounded-full bg-brass-500 animate-pulse shrink-0" />
        )}
      </button>

      {expanded && (
        <div
          ref={scrollRef}
          className="px-3 pb-3 max-h-52 overflow-y-auto space-y-1.5 animate-slide-down border-t border-white/[0.04]"
        >
          {logs.map((log, i) => (
            <div key={i} className="flex items-start gap-2 log-step pt-1.5 first:pt-2">
              <span className="text-[10px] uppercase tracking-wide text-ink-500 shrink-0 w-10 pt-0.5 font-medium">
                {stepPrefix(log.type)}
              </span>
              <span className={`text-[11px] font-mono leading-relaxed break-all ${stepTone(log.type)}`}>
                {log.message}
              </span>
            </div>
          ))}
          {isStreaming && (
            <div className="flex items-center gap-2 opacity-50 pt-1">
              <span className="text-[10px] uppercase tracking-wide text-ink-600 shrink-0 w-10">…</span>
              <span className="text-[11px] font-mono text-ink-500">processing</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
