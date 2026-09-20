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
  'What did I promise Raghav?',
  "What's overdue?",
  "What's still unresolved?",
  'Who owns the Mumbai lease?',
  'Summarize my actions today',
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
    <div className="shrink-0 border-t border-white/[0.06] bg-surface-1 shadow-lift px-4 sm:px-5 pt-3 pb-4 sm:pb-5">

      <div className="flex items-center gap-2 mb-3 overflow-x-auto scrollbar-none">
        {QUICK_PROMPTS.map(p => (
          <button
            key={p}
            onClick={() => { if (!disabled && !isStreaming) onSend(p) }}
            disabled={disabled || isStreaming}
            className="shrink-0 px-3 py-1.5 rounded-md text-[12px] font-medium text-ink-300 bg-white/[0.03] border border-white/[0.07] hover:border-brass-500/35 hover:text-brass-200 hover:bg-brass-500/[0.06] transition-colors duration-150 disabled:opacity-35 disabled:cursor-not-allowed whitespace-nowrap focus-ring"
          >
            {p}
          </button>
        ))}
      </div>

      <div className="flex items-end gap-2.5">
        <div className="flex-1 surface rounded-xl px-3.5 py-2.5 focus-within:border-brass-500/35 transition-colors duration-150">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={e => { setValue(e.target.value); handleInput() }}
            onKeyDown={handleKeyDown}
            placeholder={isStreaming ? 'Working on your question…' : (placeholder ?? 'Ask about commitments or deadlines…')}
            rows={1}
            disabled={disabled || isStreaming}
            className="w-full bg-transparent text-sm text-ink-100 placeholder-ink-500 resize-none outline-none leading-relaxed disabled:opacity-50"
            style={{ minHeight: '22px', maxHeight: '148px' }}
          />
        </div>

        {isStreaming ? (
          <button
            onClick={onStop}
            className="w-10 h-10 rounded-lg bg-rose-700 hover:bg-rose-600 flex items-center justify-center shrink-0 transition-colors duration-150 focus-ring"
            title="Stop"
          >
            <Square size={12} className="text-white fill-white" />
          </button>
        ) : (
          <button
            onClick={handleSend}
            disabled={!canSend}
            className="w-10 h-10 rounded-lg bg-brass-600 hover:bg-brass-500 flex items-center justify-center shrink-0 transition-colors duration-150 disabled:opacity-35 disabled:cursor-not-allowed focus-ring"
            title="Send"
          >
            <Send size={13} className="text-ink-950" strokeWidth={2.25} />
          </button>
        )}
      </div>

      <p className="text-[11px] text-ink-500 mt-2.5 text-center">
        {isStreaming
          ? 'Stop anytime with the button above'
          : 'Enter to send · Shift+Enter for a new line'}
      </p>
    </div>
  )
}
