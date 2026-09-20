import { Zap, RotateCcw, Activity } from 'lucide-react'

interface HeaderProps {
  totalCalls: number
  conversationTurns: number
  onReset: () => void
  isActive?: boolean
}

export function Header({ totalCalls, conversationTurns, onReset, isActive }: HeaderProps) {
  return (
    <header className="shrink-0 flex items-center justify-between px-5 sm:px-6 h-14 border-b border-white/[0.06] bg-black/40 backdrop-blur-xl sticky top-0 z-30">

      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="relative">
          <div className="w-7 h-7 rounded-lg bg-brand-600 flex items-center justify-center shadow-glow-sm">
            <Zap size={14} className="text-white" strokeWidth={2.5} />
          </div>
          {isActive && (
            <span className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-emerald-400 rounded-full border-2 border-[#0b0b0f]" />
          )}
        </div>
        <div className="hidden sm:block">
          <p className="text-sm font-semibold text-white leading-none tracking-tight">
            Executive Agent
          </p>
          <p className="text-[11px] text-slate-500 mt-0.5">
            Arjun Malhotra · VP Sales · 21–25 Sep 2026
          </p>
        </div>
        <div className="sm:hidden">
          <p className="text-sm font-semibold text-white">Executive Agent</p>
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-2 sm:gap-3">

        {/* LLM call counter */}
        {totalCalls > 0 && (
          <div className="hidden sm:flex items-center gap-3 text-[11px] text-slate-500 px-3 py-1.5 rounded-lg bg-white/[0.03] border border-white/[0.05]">
            <span className="flex items-center gap-1.5">
              <Activity size={10} className="text-brand-400" />
              {totalCalls} LLM call{totalCalls !== 1 ? 's' : ''}
            </span>
            {conversationTurns > 0 && (
              <>
                <span className="w-px h-3 bg-white/10" />
                <span>{conversationTurns} turn{conversationTurns !== 1 ? 's' : ''}</span>
              </>
            )}
          </div>
        )}

        {/* Reset */}
        <button
          onClick={onReset}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-white/[0.07] transition-all duration-150 focus-ring"
          title="Reset conversation"
        >
          <RotateCcw size={12} />
          <span className="hidden sm:inline">Reset</span>
        </button>
      </div>
    </header>
  )
}
