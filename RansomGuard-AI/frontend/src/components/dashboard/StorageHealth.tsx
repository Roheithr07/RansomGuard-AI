import type { FC } from 'react';
import { GlassCard } from '../common/GlassCard';
import { StorageChart } from '../charts/StorageChart';
import type { StorageHealthMetric } from '../../types/dashboard';
import { formatBytes } from '../../utils/formatters';

interface StorageHealthProps {
  health: StorageHealthMetric | null;
  loading?: boolean;
}

export const StorageHealth: FC<StorageHealthProps> = ({ health, loading = false }) => {
  if (loading || !health) {
    return (
      <GlassCard>
        <h3 className="text-base font-bold text-slate-900 mb-2">Storage Health</h3>
        <div className="flex justify-between text-xs text-slate-400 font-semibold mb-2">
          <span>Loading telemetry...</span>
        </div>
        <div className="h-44 flex items-center justify-center">
          <div className="w-28 h-28 rounded-full border-4 border-slate-200 border-t-[#00ABE4] animate-spin" />
        </div>
      </GlassCard>
    );
  }

  const usedPercent = Math.min(100, Math.max(1, (health.usedCapacityBytes / Math.max(1, health.totalCapacityBytes)) * 100));

  return (
    <GlassCard>
      <h3 className="text-base font-bold text-slate-900 mb-2">Storage Health</h3>
      <div className="flex justify-between text-xs text-slate-500 font-semibold mb-2">
        <span>Monitored: {formatBytes(health.usedCapacityBytes)}</span>
        <span>Capacity: {formatBytes(health.totalCapacityBytes)}</span>
      </div>
      <StorageChart usedPercent={usedPercent} />
      <div className="flex justify-between text-xs text-slate-600 mt-2 font-medium">
        <span>Score: <strong className="text-emerald-600 font-extrabold">{health.healthScore}/100</strong></span>
        <span>Files: <strong className="text-slate-900 font-bold">{health.protectedFilesCount.toLocaleString()}</strong></span>
      </div>
    </GlassCard>
  );
};
