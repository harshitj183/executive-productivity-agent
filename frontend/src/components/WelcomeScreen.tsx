interface WelcomeScreenProps {
  onGenerateBrief: () => void
  isLoading?: boolean
}

const sources = [
  {
    label: 'Meeting transcript',
    detail: 'Leadership Sync — Mon 21 Sep, 9:00 AM',
  },
  {
    label: 'Email threads',
    detail: '5 threads — vendor list, Q3 deck, lease, expense, call',
  },
  {
    label: 'Calendars',
    detail: 'Arjun, Neha, Raghav & Divya — full week',
  },
  {
    label: 'Voice notes',
    detail: '2 personal memos from Arjun',
  },
]

export function WelcomeScreen({ onGenerateBrief, isLoading }: WelcomeScreenProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-full px-5 py-12 sm:py-16 animate-fade-in">
      <div className="w-full max-w-lg text-center">

        <p className="text-[11px] font-medium uppercase tracking-[0.14em] text-brass-400 mb-4">
          Daily brief
        </p>

        <h1 className="text-2xl sm:text-[1.75rem] font-semibold text-ink-50 tracking-tight mb-3">
          Good morning, Arjun
        </h1>
        <p className="text-ink-300 text-sm sm:text-[15px] leading-relaxed mb-9 max-w-md mx-auto">
          Sources for the week of{' '}
          <span className="text-ink-100 font-medium">21–25 September 2026</span>{' '}
          are ready. Generate your brief to pull commitments, owners, and deadlines.
        </p>

        <div className="text-left surface rounded-xl divide-y divide-white/[0.05] mb-9 overflow-hidden">
          {sources.map(({ label, detail }) => (
            <div key={label} className="flex items-start gap-3 px-4 py-3.5">
              <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-brass-500/80 shrink-0" />
              <div className="min-w-0">
                <p className="text-sm font-medium text-ink-100">{label}</p>
                <p className="text-[12px] text-ink-400 mt-0.5 leading-relaxed">{detail}</p>
              </div>
            </div>
          ))}
        </div>

        <button
          onClick={onGenerateBrief}
          disabled={isLoading}
          className="inline-flex items-center justify-center gap-2 w-full sm:w-auto min-w-[200px] px-6 py-3 rounded-lg bg-brass-600 hover:bg-brass-500 text-ink-950 text-sm font-semibold transition-colors duration-150 disabled:opacity-65 disabled:cursor-not-allowed focus-ring"
        >
          {isLoading ? (
            <>
              <span className="w-3.5 h-3.5 rounded-full border-2 border-ink-950/30 border-t-ink-950 animate-spin" />
              Building brief…
            </>
          ) : (
            'Generate daily brief'
          )}
        </button>

        <p className="text-[12px] text-ink-500 mt-5 leading-relaxed max-w-sm mx-auto">
          After the brief, you can ask follow-ups. A second pass checks each claim against the source files.
        </p>
      </div>
    </div>
  )
}
