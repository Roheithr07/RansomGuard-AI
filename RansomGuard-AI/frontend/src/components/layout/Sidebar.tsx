import type { FC } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  HardDrive,
  Activity,
  ShieldAlert,
  Database,
  RotateCcw,
  Cpu,
  FileText,
  Settings as SettingsIcon,
  ShieldCheck,
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/storage', label: 'Storage', icon: HardDrive },
  { path: '/live-monitor', label: 'Live Monitor', icon: Activity },
  { path: '/threats', label: 'Threat Center', icon: ShieldAlert },
  { path: '/backups', label: 'Backup & Snapshots', icon: Database },
  { path: '/recovery', label: 'Recovery', icon: RotateCcw },
  { path: '/ai-analysis', label: 'AI Analysis', icon: Cpu },
  { path: '/reports', label: 'Reports', icon: FileText },
  { path: '/settings', label: 'Settings', icon: SettingsIcon },
];

export const Sidebar: FC = () => {
  return (
    <aside className="w-64 bg-white/60 backdrop-blur-xl border-r border-white/80 flex flex-col h-screen sticky top-0 z-30 shadow-lg shadow-cyan-900/5 select-none rounded-r-3xl">
      {/* Top Logo */}
      <div className="p-6 border-b border-white/60 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00ABE4] to-[#3B82F6] flex items-center justify-center font-bold text-white text-lg shadow-md shadow-cyan-500/25">
          RG
        </div>
        <div>
          <h1 className="font-extrabold text-slate-900 text-base tracking-tight leading-none">RansomGuard AI</h1>
          <p className="text-[11px] text-[#006FA6] font-semibold mt-1">Storage Security</p>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 px-4 py-5 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-xs font-bold transition-all duration-200 ${
                  isActive
                    ? 'liquid-nav-active'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-white/60'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Bottom Status Card */}
      <div className="p-4 m-3 bg-white/70 backdrop-blur-md rounded-2xl border border-white/90 shadow-xs space-y-3">
        <div className="flex items-center gap-2 text-[11px] font-bold text-emerald-700 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping shrink-0" />
          <span>System Status</span>
        </div>
        <p className="text-[11px] text-slate-500 font-semibold px-0.5">All Systems Operational</p>

        <div className="space-y-1 pt-1">
          <div className="flex justify-between text-[11px] font-bold">
            <span className="text-slate-500">Storage Protected</span>
            <span className="text-[#006FA6]">1.82 TB</span>
          </div>
          <div className="w-full bg-slate-200/80 h-1.5 rounded-full overflow-hidden">
            <div className="bg-gradient-to-r from-[#00ABE4] to-[#3B82F6] h-full w-[56%]" />
          </div>
        </div>

        <div className="text-[10px] text-slate-400 text-center font-medium pt-1 border-t border-slate-200/60">
          Protect • Detect • Recover
        </div>
      </div>
    </aside>
  );
};
