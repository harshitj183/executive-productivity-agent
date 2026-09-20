import { useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface ValidationPanelProps {
  content: string
}

type Verdict = 'PASS' | 'FAIL' | 'PARTIAL'

function detectVerdict(text: string): Verdict | null {
  const u = text.toUpperCase()
  if (u.includes('VERDICT: PASS') || u.includes('**PASS**') || u.includes('VERDICT:**PASS')) return 'PASS'
  if (u.includes('VERDICT: FAIL') || u.includes('**FAIL**') || u.includes('VERDICT:**FAIL')) return 'FAIL'
  if (u.includes('VERDICT: PARTIAL') || u.includes('**PARTIAL**')) return 'PARTIAL'
  return null
}

const verdictConfig = {
  PASS: {
    label: 'Sources check out',
    tone: 'text-emerald-300',
    border: 'border-emerald-500/20',
    bg: 'bg-emerald-500/[0.05]',
    dot: 'bg-emerald-400',
  },
  FAIL: {
    label: 'Issues found',
    tone: 'text-rose-300',
    border: 'border-rose-500/20',
    bg: 'bg-rose-500/[0.05]',
    dot: 'bg-rose-400',
  },
  PARTIAL: {
    label: 'Partial match',
    tone: 'text-amber-200',
    border: 'border-amber-500/20',
    bg: 'bg-amber-500/[0.05]',
    dot: 'bg-amber-400',
  },
}

export function ValidationPanel({ content }: ValidationPanelProps) {
  const [expanded, setExpanded] = useState(true)
  const verdict = detectVerdict(content)
  const cfg = verdict ? verdictConfig[verdict] : {
    label: 'Source check',
    tone: 'text-ink-300',
    border: 'border-white/[0.08]',
    bg: 'bg-white/[0.02]',
    dot: 'bg-ink-400',
  }

  return (
    <div className={`mt-2 rounded-lg border overflow-hidden animate-slide-up ${cfg.border} ${cfg.bg}`}>
      <button
        onClick={() => setExpanded(v => !v)}
        className="w-full flex items-center gap-2 px-3.5 py-2.5 text-left hover:bg-white/[0.02] transition-colors focus-ring"
      >
        <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${cfg.dot}`} />
        <span className={`text-xs font-semibold ${cfg.tone}`}>
          {cfg.label}
        </span>
        {verdict && (
          <span className={`ml-auto text-[10px] font-semibold tracking-wide uppercase ${cfg.tone}`}>
            {verdict}
          </span>
        )}
        <span className={`${verdict ? 'ml-2' : 'ml-auto'} text-ink-500`}>
          {expanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
        </span>
      </button>

      {expanded && (
        <div className="px-3.5 pb-3.5 pt-1 border-t border-white/[0.05] animate-slide-down">
          <div className="agent-response text-sm">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  )
}
