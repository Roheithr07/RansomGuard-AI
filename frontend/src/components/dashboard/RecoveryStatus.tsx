import type { FC } from 'react';
import { GlassCard } from '../common/GlassCard';
import { ShieldCheck, AlertTriangle } from 'lucide-react';

interface RecoveryStatusProps {
  snapshotCount?: number;
  activeThreatsCount?: number;
  loading?: boolean;
}

export const RecoveryStatus: FC<RecoveryStatusProps> = ({
  snapshotCount = 0,
  activeThreatsCount = 0,
  loading = false,
}) => {
  return (
    <GlassCard>
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-base font-bold text-slate-900">Smart Recovery System</h3>
        <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Rollback Engine</span>
      </div>
      <p className="text-xs text-slate-500 mb-4 font-medium">Ready to restore files from clean immutable snapshots.</p>

      {loading ? (
        <div className="p-3 bg-white/40 rounded-xl border border-white/60 animate-pulse h-14" />
      ) : activeThreatsCount > 0 ? (
        <div className="p-3 bg-red-500/10 border border-red-500/25 rounded-xl text-xs text-red-700 font-bold flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-red-600 shrink-0" />
          <span>Action Recommended • Threat flagged • Snapshots ready for rollback</span>
        </div>
      ) : (
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/25 rounded-xl text-xs text-emerald-700 font-bold flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>System Operational • {snapshotCount} snapshot checkpoint(s) online</span>
        </div>
      )}
    </GlassCard>
  );
};
