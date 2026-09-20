import { useState, useRef, KeyboardEvent } from 'react'
import { Send, Square } from 'lucide-react'

interface ChatInputProps {
  onSend: (message: string) => void
  onStop?: () => void
  disabled?: boolean
  isStreaming?: boolean
  placeholder?: string
}

const QUICK_PROMPTS = [
  "What did I promise Raghav?",
  "What's overdue?",
  "What's still unresolved?",
  "Who owns the Mumbai lease?",
  "Summarize my actions today",
]

export function ChatInput({ onSend, onStop, disabled, isStreaming, placeholder }: ChatInputProps) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const canSend = value.trim().length > 0 && !disabled && !isStreaming

  const handleSend = () => {
    if (!canSend) return
    onSend(value.trim())
    setValue('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInput = () => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 148)}px`
  }

  return (
    <div className="shrink-0 border-t border-white/[0.05] bg-black/30 backdrop-blur-xl shadow-up px-4 sm:px-5 pt-3 pb-4 sm:pb-5">

      {/* Quick prompts */}
      <div className="flex items-center gap-2 mb-3 overflow-x-auto scrollbar-none">
        <span className="text-[10px] text-slate-600 shrink-0 font-medium tracking-wide uppercase">Quick</span>
        {QUICK_PROMPTS.map(p => (
          <button
            key={p}
            onClick={() => { if (!disabled && !isStreaming) onSend(p) }}
            disabled={disabled || isStreaming}
            className="shrink-0 px-3 py-1 rounded-full text-[11px] font-medium text-slate-400 bg-white/[0.04] border border-white/[0.07] hover:border-brand-500/30 hover:text-brand-300 hover:bg-brand-500/[0.07] transition-all duration-150 disabled:opacity-30 disabled:cursor-not-allowed whitespace-nowrap focus-ring"
          >
            {p}
          </button>
        ))}
      </div>

      {/* Input row */}
      <div className="flex items-end gap-3">
        {/* Textarea wrapper */}
        <div className="flex-1 glass rounded-2xl px-4 py-3 focus-within:border-brand-500/30 focus-within:shadow-glow-sm transition-all duration-200">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={e => { setValue(e.target.value); handleInput() }}
            onKeyDown={handleKeyDown}
            placeholder={isStreaming ? 'Agent is responding…' : (placeholder ?? 'Ask about your commitments or deadlines…')}
            rows={1}
            disabled={disabled || isStreaming}
            className="w-full bg-transparent text-sm text-slate-200 placeholder-slate-600 resize-none outline-none leading-relaxed disabled:opacity-50"
            style={{ minHeight: '22px', maxHeight: '148px' }}
          />
        </div>

        {/* Action button */}
        {isStreaming ? (
          <button
            onClick={onStop}
            className="w-10 h-10 rounded-xl bg-rose-600 hover:bg-rose-500 flex items-center justify-center shrink-0 transition-all duration-150 shadow-lg focus-ring"
            title="Stop generation"
          >
            <Square size={13} className="text-white fill-white" />
          </button>
        ) : (
          <button
            onClick={handleSend}
            disabled={!canSend}
            className="w-10 h-10 rounded-xl bg-brand-600 hover:bg-brand-500 flex items-center justify-center shrink-0 transition-all duration-150 shadow-glow-sm disabled:opacity-35 disabled:cursor-not-allowed focus-ring"
          >
            <Send size={13} className="text-white" />
          </button>
        )}
      </div>

      {/* Hint */}
      <p className="text-[10px] text-slate-700 mt-2.5 text-center">
        {isStreaming ? 'Click the red button to stop generation' : 'Enter to send · Shift+Enter for a new line · All claims grounded in source data'}
      </p>
    </div>
  )
}
