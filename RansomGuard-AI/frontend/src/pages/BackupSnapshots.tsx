import { useState } from 'react';
import type { FC } from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { GlassCard } from '../components/common/GlassCard';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Modal } from '../components/common/Modal';
import { TabGroup } from '../components/common/TabGroup';
import { mockBackups, mockBackupStats } from '../data/mockBackups';
import { formatBytes } from '../utils/formatters';
import type { BackupSnapshot } from '../types/backup';
import { Database, ShieldCheck, HardDrive, Plus, CheckCircle2, Lock } from 'lucide-react';

export const BackupSnapshots: FC = () => {
  const [filter, setFilter] = useState('all');
  const [snapshots, setSnapshots] = useState<BackupSnapshot[]>(mockBackups);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [snapshotType, setSnapshotType] = useState<'trusted' | 'temporary'>('trusted');
  const [isSuccessToast, setIsSuccessToast] = useState(false);

  const filteredSnapshots = snapshots.filter((snap) => {
    if (filter === 'all') return true;
    return snap.type === filter;
  });

  const handleCreateSnapshot = (e: React.FormEvent) => {
    e.preventDefault();
    const now = new Date();
    const snapId = `Snapshot_${snapshots.length + 1}`;
    const newSnap: BackupSnapshot = {
      id: `snap-${Date.now()}`,
      snapshotId: snapId,
      createdAt: `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')} AM (Today)`,
      type: snapshotType,
      sizeBytes: 452000000000,
      fileCount: 1284910,
      integrityHash: `sha256:${Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join('')}`,
      status: 'healthy',
      totalFolders: 14,
    };

    setSnapshots([newSnap, ...snapshots]);
    setIsModalOpen(false);
    setIsSuccessToast(true);
    setTimeout(() => setIsSuccessToast(false), 4000);
  };

  return (
    <PageContainer
      title="Immutable Snapshots & Data Vaults"
      subtitle="Manage point-in-time immutable volume snapshots, SHA-256 integrity hashes, and zero-trust recovery anchors"
    >
      <div className="space-y-6">
        {/* Banner notification */}
        {isSuccessToast && (
          <div className="p-4 bg-emerald-500/15 border border-emerald-500/30 rounded-2xl text-emerald-800 text-xs font-bold flex items-center gap-3 animate-pulse">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
            <span>Immutable snapshot successfully generated and verified with 100% SHA-256 integrity.</span>
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <GlassCard>
            <div className="flex justify-between items-start">
              <div>
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Total Snapshots</p>
                <h4 className="text-2xl font-extrabold text-slate-900 mt-1">{mockBackupStats.totalSnapshots}</h4>
              </div>
              <div className="p-2.5 bg-[#00ABE4]/10 border border-cyan-500/20 rounded-2xl text-[#006FA6]">
                <Database className="w-5 h-5" />
              </div>
            </div>
          </GlassCard>

          <GlassCard>
            <div className="flex justify-between items-start">
              <div>
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Latest Snapshot</p>
                <h4 className="text-2xl font-extrabold text-slate-900 mt-1">{mockBackupStats.latestSnapshotDate}</h4>
              </div>
              <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl text-emerald-600">
                <ShieldCheck className="w-5 h-5" />
              </div>
            </div>
          </GlassCard>

          <GlassCard>
            <div className="flex justify-between items-start">
              <div>
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Storage Used</p>
                <h4 className="text-2xl font-extrabold text-slate-900 mt-1">{formatBytes(mockBackupStats.totalSizeBytes)}</h4>
              </div>
              <div className="p-2.5 bg-blue-500/10 border border-blue-500/20 rounded-2xl text-blue-600">
                <HardDrive className="w-5 h-5" />
              </div>
            </div>
          </GlassCard>

          <GlassCard>
            <div className="flex justify-between items-start">
              <div>
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Integrity Score</p>
                <h4 className="text-2xl font-extrabold text-emerald-600 mt-1">{mockBackupStats.integrityPercent}%</h4>
              </div>
              <Badge variant="success">100% VERIFIED</Badge>
            </div>
          </GlassCard>
        </div>

        {/* Snapshot Management Table */}
        <GlassCard className="space-y-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">Snapshot Vault Registry</h3>
              <p className="text-xs text-slate-500">Immutable read-only snapshots stored in dedicated storage vault</p>
            </div>
            <div className="flex items-center gap-3 flex-wrap">
              <TabGroup
                tabs={[
                  { id: 'all', label: 'All', count: snapshots.length },
                  { id: 'trusted', label: 'Trusted Vault' },
                  { id: 'temporary', label: 'Temporary' },
                ]}
                activeTab={filter}
                onChange={setFilter}
              />
              <Button variant="primary" onClick={() => setIsModalOpen(true)} className="flex items-center gap-2">
                <Plus className="w-4 h-4" />
                <span>Create Snapshot</span>
              </Button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-200/80 text-[11px] font-bold text-slate-500 uppercase tracking-wider bg-white/40">
                  <th className="py-3 px-4">SNAPSHOT ID</th>
                  <th className="py-3 px-4">TIMESTAMP</th>
                  <th className="py-3 px-4">TYPE</th>
                  <th className="py-3 px-4">FILES / SIZE</th>
                  <th className="py-3 px-4">CHECKSUM</th>
                  <th className="py-3 px-4">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200/60">
                {filteredSnapshots.map((snap) => (
                  <tr key={snap.id} className="hover:bg-white/80 transition-colors">
                    <td className="py-3.5 px-4 font-bold font-mono text-slate-900 text-xs flex items-center gap-2">
                      <Lock className="w-3.5 h-3.5 text-[#006FA6]" />
                      {snap.snapshotId}
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 font-medium">{snap.createdAt}</td>
                    <td className="py-3.5 px-4">
                      <Badge variant={snap.type === 'trusted' ? 'success' : 'warning'}>
                        {snap.type.toUpperCase()}
                      </Badge>
                    </td>
                    <td className="py-3.5 px-4 text-slate-700">
                      {snap.fileCount.toLocaleString()} files • {formatBytes(snap.sizeBytes)}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-[11px] text-slate-500 truncate max-w-xs">{snap.integrityHash}</td>
                    <td className="py-3.5 px-4">
                      <Badge variant="success">HEALTHY</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      </div>

      {/* Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create Volume Snapshot">
        <form onSubmit={handleCreateSnapshot} className="space-y-4 text-xs">
          <p className="text-slate-600 font-medium">
            This freezes current volume states and generates an immutable read-only SHA-256 snapshot anchor.
          </p>

          <div>
            <label className="block font-bold text-slate-800 mb-1">Snapshot Type</label>
            <select
              value={snapshotType}
              onChange={(e) => setSnapshotType(e.target.value as 'trusted' | 'temporary')}
              className="w-full bg-white border border-slate-300 rounded-xl p-2.5 text-xs text-slate-900 focus:outline-none focus:border-[#00ABE4]"
            >
              <option value="trusted">Trusted Vault Snapshot (Permanent)</option>
              <option value="temporary">Temporary Ephemeral Snapshot (24-Hour Hold)</option>
            </select>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="secondary" onClick={() => setIsModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">Generate Snapshot</Button>
          </div>
        </form>
      </Modal>
    </PageContainer>
  );
};
