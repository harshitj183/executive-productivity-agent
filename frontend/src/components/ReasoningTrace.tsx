import { useState, useEffect, useRef } from 'react'
import { ChevronDown, ChevronRight, Terminal, Wrench, CheckCircle2, AlertCircle, Cpu } from 'lucide-react'
import type { AgentEvent } from '../types'

interface ReasoningTraceProps {
  logs: AgentEvent[]
  isStreaming?: boolean
}

function stepIcon(type: AgentEvent['type']) {
  switch (type) {
    case 'tool_call':   return <Wrench      size={10} className="text-amber-400  shrink-0 mt-[3px]" />
    case 'tool_result': return <CheckCircle2 size={10} className="text-emerald-400 shrink-0 mt-[3px]" />
    case 'error':       return <AlertCircle  size={10} className="text-rose-400   shrink-0 mt-[3px]" />
    default:            return <Terminal     size={10} className="text-slate-500  shrink-0 mt-[3px]" />
  }
}

function stepColor(type: AgentEvent['type']) {
  switch (type) {
    case 'tool_call':   return 'text-amber-300/75'
    case 'tool_result': return 'text-emerald-300/75'
    case 'error':       return 'text-rose-300'
    default:            return 'text-slate-400'
  }
}

export function ReasoningTrace({ logs, isStreaming }: ReasoningTraceProps) {
  const [expanded, setExpanded] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-open while streaming so live tool calls are visible
  useEffect(() => {
    if (isStreaming && logs.length > 0) setExpanded(true)
    if (!isStreaming) setExpanded(false)
  }, [isStreaming, logs.length])

  // Auto-scroll inside the trace as new steps arrive
  useEffect(() => {
    if (expanded && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [logs.length, expanded])

  if (logs.length === 0 && !isStreaming) return null

  const toolCalls = logs.filter(l => l.type === 'tool_call').length
  const label = isStreaming
    ? `Reasoning${toolCalls > 0 ? ` · ${toolCalls} tool call${toolCalls > 1 ? 's' : ''}` : ''}…`
    : `${logs.length} step${logs.length !== 1 ? 's' : ''} · ${toolCalls} tool call${toolCalls !== 1 ? 's' : ''}`

  return (
    <div className="mt-2 rounded-xl overflow-hidden border border-white/[0.05] bg-black/25">
      {/* Header row */}
      <button
        onClick={() => setExpanded(v => !v)}
        className="w-full flex items-center gap-2 px-3.5 py-2 text-[11px] text-slate-500 hover:text-slate-400 transition-colors text-left select-none"
      >
        <Cpu
          size={10}
          className={isStreaming ? 'text-brand-400 animate-pulse' : 'text-slate-600'}
        />
        {expanded ? <ChevronDown size={10} /> : <ChevronRight size={10} />}
        <span className="flex-1 font-mono">{label}</span>
        {isStreaming && (
          <span className="flex gap-0.5 shrink-0">
            {[0, 1, 2].map(i => (
              <span
                key={i}
                className="w-1 h-1 rounded-full bg-brand-400 animate-bounce"
                style={{ animationDelay: `${i * 120}ms` }}
              />
            ))}
          </span>
        )}
      </button>

      {/* Step list */}
      {expanded && (
        <div
          ref={scrollRef}
          className="px-3.5 pb-3 max-h-56 overflow-y-auto space-y-1.5 animate-slide-down"
        >
          {logs.map((log, i) => (
            <div key={i} className="flex items-start gap-2 log-step">
              {stepIcon(log.type)}
              <span className={`text-[11px] font-mono leading-relaxed break-all ${stepColor(log.type)}`}>
                {log.message}
              </span>
            </div>
          ))}
          {isStreaming && (
            <div className="flex items-center gap-2 opacity-40">
              <Terminal size={10} className="text-slate-600 shrink-0" />
              <span className="text-[11px] font-mono text-slate-600 typing-cursor">processing</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
