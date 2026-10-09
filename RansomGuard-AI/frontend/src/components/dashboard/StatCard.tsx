import type { FC } from 'react';
import { GlassCard } from '../common/GlassCard';
import type { StatMetric } from '../../types/dashboard';

interface StatCardProps {
  metric: StatMetric;
  loading?: boolean;
}

export const StatCard: FC<StatCardProps> = ({ metric, loading = false }) => {
  if (loading) {
    return (
      <GlassCard>
        <div className="animate-pulse space-y-2">
          <div className="h-3 bg-slate-200/60 rounded-full w-24" />
          <div className="h-7 bg-slate-200/80 rounded-lg w-16" />
        </div>
      </GlassCard>
    );
  }

  return (
    <GlassCard>
      <div className="flex justify-between items-start">
        <div>
          <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">{metric.title}</p>
          <h4 className="text-2xl font-extrabold text-slate-900 mt-1 tracking-tight">{metric.value}</h4>
        </div>
        <span className={`text-[11px] px-2.5 py-1 rounded-full font-bold shadow-2xs border ${
          metric.isPositive 
            ? 'text-emerald-700 bg-emerald-500/10 border-emerald-500/20' 
            : 'text-red-600 bg-red-500/10 border-red-500/20'
        }`}>
          {metric.change}
        </span>
      </div>
    </GlassCard>
  );
};
