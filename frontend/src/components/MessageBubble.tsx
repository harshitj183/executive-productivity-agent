import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { User, Bot, ShieldCheck, AlertTriangle, Loader2 } from 'lucide-react'
import type { ChatMessage } from '../types'
import { ReasoningTrace } from './ReasoningTrace'
import { ValidationPanel } from './ValidationPanel'

interface MessageBubbleProps {
  message: ChatMessage
  onValidate?: (content: string) => void
  isValidating?: boolean
}

export function MessageBubble({ message, onValidate, isValidating }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  /* ── User bubble ──────────────────────────────────────────────────── */
  if (isUser) {
    return (
      <div className="flex items-end justify-end gap-2.5 animate-fade-in">
        <div className="max-w-[78%] sm:max-w-[68%]">
          <div className="px-4 py-3 rounded-2xl rounded-br-md bg-brand-600/85 text-white text-sm leading-relaxed shadow-glow-sm">
            {message.content}
          </div>
          <p className="text-right text-[10px] text-slate-600 mt-1.5 pr-1">
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>
        <div className="w-7 h-7 rounded-full bg-slate-700/80 border border-white/[0.08] flex items-center justify-center shrink-0 mb-5">
          <User size={12} className="text-slate-300" />
        </div>
      </div>
    )
  }

  /* ── Assistant bubble ─────────────────────────────────────────────── */
  return (
    <div className="flex items-start gap-2.5 animate-slide-up">
      {/* Avatar */}
      <div className="relative shrink-0 mt-0.5">
        <div className="w-7 h-7 rounded-full bg-brand-600/20 border border-brand-500/30 flex items-center justify-center">
          <Bot size={12} className="text-brand-300" />
        </div>
        {message.isStreaming && (
          <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-[#0b0b0f] rounded-full flex items-center justify-center">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          </span>
        )}
      </div>

      <div className="flex-1 min-w-0 space-y-2">
        {/* Main card */}
        <div className="glass rounded-2xl rounded-tl-md px-5 py-4">
          {/* Error state */}
          {message.isError ? (
            <div className="flex items-start gap-2.5">
              <AlertTriangle size={15} className="text-rose-400 shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-rose-300 mb-0.5">Something went wrong</p>
                <p className="text-xs text-slate-400 leading-relaxed">{message.content}</p>
              </div>
            </div>
          ) : message.isStreaming && !message.content ? (
            /* Initial loading — dots */
            <div className="flex items-center gap-2.5 py-0.5">
              <Loader2 size={14} className="text-brand-400 animate-spin-slow shrink-0" />
              <span className="text-sm text-slate-400">Agent is reading your sources…</span>
            </div>
          ) : (
            /* Normal / streaming content */
            <div className={`agent-response text-sm${message.isStreaming ? ' typing-cursor' : ''}`}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Reasoning trace */}
        {((message.logs && message.logs.length > 0) || message.isStreaming) && (
          <ReasoningTrace
            logs={message.logs ?? []}
            isStreaming={message.isStreaming}
          />
        )}

        {/* Footer */}
        <div className="flex items-center justify-between px-1">
          <p className="text-[10px] text-slate-600">
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>

          {/* Validate button — only on complete, non-error messages */}
          {!message.isStreaming && !message.isError && message.content && onValidate && (
            <button
              onClick={() => onValidate(message.content)}
              disabled={isValidating}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium text-slate-500 hover:text-brand-300 hover:bg-brand-500/10 border border-transparent hover:border-brand-500/20 transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed focus-ring"
            >
              {isValidating ? (
                <>
                  <Loader2 size={10} className="animate-spin-slow" />
                  Validating…
                </>
              ) : (
                <>
                  <ShieldCheck size={10} />
                  Validate
                </>
              )}
            </button>
          )}
        </div>

        {/* Validation panel */}
        {message.validationResult && (
          <ValidationPanel content={message.validationResult} />
        )}
      </div>
    </div>
  )
}
