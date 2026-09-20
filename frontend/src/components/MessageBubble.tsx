import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ShieldCheck, AlertTriangle } from 'lucide-react'
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

  if (isUser) {
    return (
      <div className="flex justify-end animate-fade-in">
        <div className="max-w-[85%] sm:max-w-[72%]">
          <div className="px-3.5 py-2.5 rounded-xl rounded-br-md bg-brass-600/90 text-ink-950 text-sm leading-relaxed">
            {message.content}
          </div>
          <p className="text-right text-[10px] text-ink-500 mt-1.5 pr-0.5">
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="animate-slide-up">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-[11px] font-semibold text-ink-300 tracking-wide">
          Executive Agent
        </span>
        {message.isStreaming && (
          <span className="text-[10px] text-brass-400 font-medium">working</span>
        )}
      </div>

      <div className="space-y-2">
        <div className="surface rounded-xl px-4 sm:px-5 py-4">
          {message.isError ? (
            <div className="flex items-start gap-2.5">
              <AlertTriangle size={15} className="text-rose-400 shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-rose-300 mb-0.5">Couldn’t complete that</p>
                <p className="text-xs text-ink-400 leading-relaxed">{message.content}</p>
              </div>
            </div>
          ) : message.isStreaming && !message.content ? (
            <div className="flex items-center gap-2.5 py-0.5">
              <span className="w-3.5 h-3.5 rounded-full border-2 border-brass-500/30 border-t-brass-400 animate-spin shrink-0" />
              <span className="text-sm text-ink-400">Reading your sources…</span>
            </div>
          ) : (
            <div className={`agent-response text-sm${message.isStreaming ? ' typing-cursor' : ''}`}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {((message.logs && message.logs.length > 0) || message.isStreaming) && (
          <ReasoningTrace
            logs={message.logs ?? []}
            isStreaming={message.isStreaming}
          />
        )}

        <div className="flex items-center justify-between px-0.5">
          <p className="text-[10px] text-ink-500">
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </p>

          {!message.isStreaming && !message.isError && message.content && onValidate && (
            <button
              onClick={() => onValidate(message.content)}
              disabled={isValidating}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium text-ink-400 hover:text-brass-200 hover:bg-brass-500/10 border border-transparent hover:border-brass-500/20 transition-colors duration-150 disabled:opacity-40 disabled:cursor-not-allowed focus-ring"
            >
              {isValidating ? (
                <>
                  <span className="w-2.5 h-2.5 rounded-full border border-ink-400/40 border-t-ink-300 animate-spin" />
                  Checking sources…
                </>
              ) : (
                <>
                  <ShieldCheck size={11} strokeWidth={2} />
                  Check against sources
                </>
              )}
            </button>
          )}
        </div>

        {message.validationResult && (
          <ValidationPanel content={message.validationResult} />
        )}
      </div>
    </div>
  )
}
