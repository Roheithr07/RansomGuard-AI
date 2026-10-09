import type { FC } from 'react';
import { GlassCard } from '../common/GlassCard';
import { Badge } from '../common/Badge';
import type { DashboardEventItem } from '../../hooks/useDashboardData';

interface SecurityEventsProps {
  events?: DashboardEventItem[];
  loading?: boolean;
}

export const SecurityEvents: FC<SecurityEventsProps> = ({ events, loading = false }) => {
  const getBadgeVariant = (severity: string): 'info' | 'success' | 'warning' | 'danger' => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL':
      case 'HIGH':
        return 'danger';
      case 'MEDIUM':
        return 'warning';
      case 'LOW':
        return 'success';
      default:
        return 'info';
    }
  };

  return (
    <GlassCard>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-base font-bold text-slate-900">Recent Security Events</h3>
        <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Live Log</span>
      </div>

      {loading ? (
        <div className="space-y-2.5">
          {[1, 2, 3].map((i) => (
            <div key={i} className="p-3 bg-white/40 rounded-xl border border-white/60 animate-pulse h-14" />
          ))}
        </div>
      ) : !events || events.length === 0 ? (
        <div className="p-3.5 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-xs text-emerald-700 font-medium text-center">
          No suspicious security events logged. Filesystem is clean.
        </div>
      ) : (
        <div className="space-y-2.5">
          {events.map((ev) => (
            <div key={ev.id} className="p-3 bg-white/70 backdrop-blur-md rounded-xl border border-white/90 shadow-2xs text-xs transition-colors hover:bg-white/90">
              <div className="flex justify-between items-center mb-1">
                <span className="font-bold text-slate-900 truncate max-w-[190px]" title={ev.description}>
                  {ev.description}
                </span>
                <Badge variant={getBadgeVariant(ev.severity)}>{ev.timestamp}</Badge>
              </div>
              <div className="flex justify-between items-center text-[11px] text-slate-500 font-mono">
                <span className="truncate max-w-[200px]" title={ev.filePath}>{ev.filePath || ev.fileName}</span>
                <span className="font-sans font-semibold text-slate-600">Risk: {ev.riskScore}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </GlassCard>
  );
};
