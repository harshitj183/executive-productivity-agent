import { RotateCcw } from 'lucide-react'

interface HeaderProps {
  totalCalls: number
  conversationTurns: number
  onReset: () => void
  isActive?: boolean
}

export function Header({ totalCalls, conversationTurns, onReset, isActive }: HeaderProps) {
  return (
    <header className="shrink-0 flex items-center justify-between px-4 sm:px-6 h-13 border-b border-white/[0.06] bg-surface-1 sticky top-0 z-30" style={{ height: '52px' }}>

      <div className="flex items-center gap-3 min-w-0">
        <div className="relative shrink-0">
          <div className="w-7 h-7 rounded-md bg-brass-600 flex items-center justify-center">
            <span className="text-[11px] font-bold text-ink-950 tracking-tight">EA</span>
          </div>
          {isActive && (
            <span className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-emerald-500 rounded-full border-2 border-surface-1" />
          )}
        </div>
        <div className="min-w-0">
          <p className="text-sm font-semibold text-ink-50 leading-none tracking-tight truncate">
            Executive Agent
          </p>
          <p className="text-[11px] text-ink-400 mt-0.5 truncate hidden sm:block">
            Arjun Malhotra · VP Sales · week of 21 Sep 2026
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 sm:gap-3 shrink-0">
        {totalCalls > 0 && (
          <div className="hidden sm:flex items-center gap-2.5 text-[11px] text-ink-400 px-2.5 py-1 rounded-md bg-white/[0.03] border border-white/[0.06]">
            <span>{totalCalls} model call{totalCalls !== 1 ? 's' : ''}</span>
            {conversationTurns > 0 && (
              <>
                <span className="w-px h-3 bg-white/10" />
                <span>{conversationTurns} turn{conversationTurns !== 1 ? 's' : ''}</span>
              </>
            )}
          </div>
        )}

        <button
          onClick={onReset}
          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium text-ink-400 hover:text-ink-100 hover:bg-white/[0.05] transition-colors duration-150 focus-ring"
          title="Start over"
        >
          <RotateCcw size={12} strokeWidth={2} />
          <span className="hidden sm:inline">Reset</span>
        </button>
      </div>
    </header>
  )
}
