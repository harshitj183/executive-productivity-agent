import { useState } from 'react'
import { ChevronDown, ChevronRight, ShieldCheck, ShieldAlert, ShieldX } from 'lucide-react'
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
  if (u.includes('VERDICT: PARTIAL') || u.includes('**PARTIAL**') || u.includes('PARTIAL'))   return 'PARTIAL'
  return null
}

const verdictConfig = {
  PASS: {
    Icon: ShieldCheck,
    label: 'Validation passed',
    pill: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20',
    header: 'bg-emerald-500/[0.06] border-emerald-500/15',
    dot: 'bg-emerald-400',
  },
  FAIL: {
    Icon: ShieldX,
    label: 'Validation failed',
    pill: 'bg-rose-500/10 text-rose-300 border-rose-500/20',
    header: 'bg-rose-500/[0.06] border-rose-500/15',
    dot: 'bg-rose-400',
  },
  PARTIAL: {
    Icon: ShieldAlert,
    label: 'Partial pass',
    pill: 'bg-amber-500/10 text-amber-300 border-amber-500/20',
    header: 'bg-amber-500/[0.06] border-amber-500/15',
    dot: 'bg-amber-400',
  },
}

export function ValidationPanel({ content }: ValidationPanelProps) {
  const [expanded, setExpanded] = useState(true)
  const verdict = detectVerdict(content)
  const cfg = verdict ? verdictConfig[verdict] : verdictConfig.PARTIAL

  return (
    <div className={`mt-3 rounded-xl border overflow-hidden animate-slide-up ${cfg.header}`}>
      {/* Toggle header */}
      <button
        onClick={() => setExpanded(v => !v)}
        className="w-full flex items-center gap-2.5 px-4 py-2.5 text-left hover:brightness-110 transition-all"
      >
        <cfg.Icon size={13} className={`shrink-0 ${cfg.pill.split(' ')[1]}`} />
        <span className={`text-xs font-semibold ${cfg.pill.split(' ')[1]}`}>
          Validator · {cfg.label}
        </span>
        {verdict && (
          <span className={`ml-auto flex items-center gap-1.5 text-[10px] font-bold tracking-wider uppercase ${cfg.pill.split(' ')[1]}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
            {verdict}
          </span>
        )}
        <span className={`${verdict ? '' : 'ml-auto'} text-slate-500`}>
          {expanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
        </span>
      </button>

      {/* Content */}
      {expanded && (
        <div className="px-4 pb-4 pt-1 border-t border-white/[0.05] animate-slide-down">
          <div className="agent-response text-sm">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  )
}
