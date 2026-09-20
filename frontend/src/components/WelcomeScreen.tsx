import { Zap, FileText, Mail, Calendar, Mic, ArrowRight } from 'lucide-react'

interface WelcomeScreenProps {
  onGenerateBrief: () => void
  isLoading?: boolean
}

const sources = [
  {
    icon: FileText,
    label: 'Meeting Transcript',
    detail: 'Leadership Sync — Mon 21 Sep, 9:00 AM',
    color: 'text-violet-400',
    bg: 'bg-violet-500/8',
  },
  {
    icon: Mail,
    label: '5 Email Threads',
    detail: 'Vendor list, Q3 deck, lease, expense, call',
    color: 'text-sky-400',
    bg: 'bg-sky-500/8',
  },
  {
    icon: Calendar,
    label: 'Calendars',
    detail: 'Arjun, Neha, Raghav & Divya — full week',
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/8',
  },
  {
    icon: Mic,
    label: 'Voice Notes',
    detail: '2 personal memos recorded by Arjun',
    color: 'text-amber-400',
    bg: 'bg-amber-500/8',
  },
]

export function WelcomeScreen({ onGenerateBrief, isLoading }: WelcomeScreenProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-full px-5 py-12 sm:py-16 text-center animate-fade-in">

      {/* Icon */}
      <div className="relative mb-6">
        <div className="w-14 h-14 rounded-2xl bg-brand-600 flex items-center justify-center shadow-glow">
          <Zap size={24} className="text-white" strokeWidth={2.5} />
        </div>
        <div className="absolute inset-0 rounded-2xl bg-brand-600 blur-xl opacity-30 -z-10" />
      </div>

      {/* Greeting */}
      <h1 className="text-2xl sm:text-3xl font-semibold text-white tracking-tight mb-2">
        Good morning, Arjun.
      </h1>
      <p className="text-slate-400 text-sm sm:text-base max-w-md leading-relaxed mb-10">
        I've gone through your sources for the week of{' '}
        <span className="text-slate-200 font-medium">21–25 September 2026</span>.
        Ready to pull your commitments and build your daily brief.
      </p>

      {/* Source grid */}
      <div className="grid grid-cols-2 gap-3 w-full max-w-md mb-10">
        {sources.map(({ icon: Icon, label, detail, color, bg }, i) => (
          <div
            key={label}
            className="glass rounded-2xl p-4 text-left animate-slide-up"
            style={{ animationDelay: `${i * 60}ms` }}
          >
            <div className={`w-8 h-8 rounded-xl ${bg} flex items-center justify-center mb-3`}>
              <Icon size={15} className={color} />
            </div>
            <p className="text-xs font-semibold text-slate-200 leading-snug">{label}</p>
            <p className="text-[11px] text-slate-500 mt-0.5 leading-relaxed">{detail}</p>
          </div>
        ))}
      </div>

      {/* CTA */}
      <button
        onClick={onGenerateBrief}
        disabled={isLoading}
        className="group relative flex items-center gap-2.5 px-7 py-3.5 rounded-2xl bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold transition-all duration-200 shadow-glow disabled:opacity-70 disabled:cursor-not-allowed focus-ring"
      >
        {isLoading ? (
          <>
            <span className="flex gap-1">
              {[0, 1, 2].map(i => (
                <span
                  key={i}
                  className="w-1.5 h-1.5 rounded-full bg-white/70 animate-bounce"
                  style={{ animationDelay: `${i * 150}ms` }}
                />
              ))}
            </span>
            Generating brief…
          </>
        ) : (
          <>
            <Zap size={15} strokeWidth={2.5} />
            Generate Daily Brief
            <ArrowRight
              size={14}
              className="opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-200"
            />
          </>
        )}
      </button>

      <p className="text-[11px] text-slate-600 mt-5 max-w-xs leading-relaxed">
        Two agents run in sequence — the main agent extracts commitments,
        the validator checks every claim against source data.
      </p>
    </div>
  )
}
