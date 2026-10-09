import type { FC } from 'react';
import { GlassCard } from '../common/GlassCard';
import { Badge } from '../common/Badge';
import { formatBytes } from '../../utils/formatters';
import type { SnapshotItem } from '../../lib/api';

interface BackupOverviewProps {
  snapshots?: SnapshotItem[];
  latestSnapshot?: {
    snapshot_id: string;
    created_at: string;
    file_count: number;
    total_size_bytes: number;
  } | null;
  loading?: boolean;
}

export const BackupOverview: FC<BackupOverviewProps> = ({
  snapshots,
  latestSnapshot,
  loading = false,
}) => {
  const displayList = snapshots && snapshots.length > 0 ? snapshots.slice(0, 3) : null;

  return (
    <GlassCard>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-base font-bold text-slate-900">Backup & Snapshot Status</h3>
        <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">SHA-256 Vault</span>
      </div>

      {loading ? (
        <div className="space-y-2.5">
          {[1, 2].map((i) => (
            <div key={i} className="p-3 bg-white/40 rounded-xl border border-white/60 animate-pulse h-14" />
          ))}
        </div>
      ) : displayList ? (
        <div className="space-y-2.5">
          {displayList.map((snap) => (
            <div
              key={snap.snapshot_id}
              className="flex justify-between items-center p-3 bg-white/70 backdrop-blur-md rounded-xl border border-white/90 shadow-2xs text-xs"
            >
              <div>
                <p className="font-bold text-slate-900 font-mono text-[11px] truncate max-w-[170px]" title={snap.snapshot_id}>
                  {snap.snapshot_id}
                </p>
                <p className="text-slate-500 text-[11px]">
                  {new Date(snap.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} • {snap.file_count} files ({formatBytes(snap.total_size_bytes)})
                </p>
              </div>
              <Badge variant={snap.integrity_status === 'Valid' ? 'success' : 'danger'}>
                {snap.integrity_status === 'Valid' ? 'VERIFIED' : 'CHECK'}
              </Badge>
            </div>
          ))}
        </div>
      ) : latestSnapshot ? (
        <div className="p-3 bg-white/70 backdrop-blur-md rounded-xl border border-white/90 shadow-2xs text-xs">
          <div className="flex justify-between items-center">
            <div>
              <p className="font-bold text-slate-900 font-mono text-[11px] truncate max-w-[170px]">
                {latestSnapshot.snapshot_id}
              </p>
              <p className="text-slate-500 text-[11px]">
                {new Date(latestSnapshot.created_at).toLocaleDateString()} • {latestSnapshot.file_count} files
              </p>
            </div>
            <Badge variant="success">ACTIVE</Badge>
          </div>
        </div>
      ) : (
        <div className="p-3.5 bg-slate-100/60 border border-slate-200/60 rounded-xl text-xs text-slate-500 text-center">
          No snapshot checkpoints created yet.
        </div>
      )}
    </GlassCard>
  );
};
