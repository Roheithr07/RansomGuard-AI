import type { FC } from 'react';
import { Bell, Search, ShieldCheck, Sun } from 'lucide-react';

export const Header: FC = () => {
  return (
    <header className="h-16 border-b border-white/80 bg-white/40 backdrop-blur-xl px-6 flex items-center justify-between sticky top-0 z-20 shadow-2xs">
      {/* Left: Protection Status Pill */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-xs font-bold text-emerald-700 bg-emerald-500/10 border border-emerald-500/25 px-3.5 py-1.5 rounded-full shadow-2xs backdrop-blur-md">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <span>Protection Active</span>
        </div>
      </div>

      {/* Center: Large Glass Search Bar */}
      <div className="flex-1 max-w-md mx-6">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search files, threats, snapshots..."
            className="w-full bg-white/60 border border-white/90 rounded-full pl-10 pr-4 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-[#00ABE4] focus:ring-2 focus:ring-[#00ABE4]/20 shadow-inner backdrop-blur-md transition-all"
          />
        </div>
      </div>

      {/* Right: Date/Time, Notification, Theme, User Profile */}
      <div className="flex items-center gap-4">
        {/* Date / Time Display */}
        <div className="hidden lg:block text-right text-[11px] font-semibold text-slate-600">
          <p className="font-mono text-slate-700">Mon, 15 Sep 2026</p>
          <p className="text-[10px] text-slate-400">10:42 AM</p>
        </div>

        <div className="flex items-center gap-2">
          {/* Notification Button */}
          <button
            title="Notifications"
            className="relative p-2 rounded-full bg-white/70 hover:bg-white text-slate-600 hover:text-[#006FA6] border border-white/90 shadow-2xs transition-all backdrop-blur-md cursor-pointer"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-red-500 text-white rounded-full text-[9px] font-bold flex items-center justify-center border border-white">
              1
            </span>
          </button>

          {/* Theme Toggle Button */}
          <button
            title="Toggle Theme"
            className="p-2 rounded-full bg-white/70 hover:bg-white text-slate-600 hover:text-[#006FA6] border border-white/90 shadow-2xs transition-all backdrop-blur-md cursor-pointer"
          >
            <Sun className="w-4 h-4" />
          </button>
        </div>

        {/* User Profile */}
        <div className="flex items-center gap-2.5 pl-3 border-l border-slate-300/60">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#00ABE4] to-[#3B82F6] text-white flex items-center justify-center text-xs font-extrabold shadow-sm">
            A
          </div>
          <div className="hidden sm:block text-left text-[11px]">
            <p className="font-bold text-slate-900 leading-tight">System Admin</p>
            <p className="text-[10px] text-slate-500 font-medium">Security Operator</p>
          </div>
        </div>
      </div>
    </header>
  );
};
