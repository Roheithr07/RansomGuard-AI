import { useState } from 'react';
import type { FC } from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { GlassCard } from '../components/common/GlassCard';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { DataTable, type Column } from '../components/common/DataTable';
import { FileTypeDonutChart } from '../components/charts/FileTypeDonutChart';
import { mockVolumes, mockMonitoredFolders, mockFileTypeDistribution, mockStorageActivityLogs } from '../data/mockStorage';
import { formatBytes } from '../utils/formatters';
import type { MonitoredFolder } from '../types/storage';
import { HardDrive, FolderPlus, ShieldCheck, Database, RefreshCw, Trash2, Folder, FileText } from 'lucide-react';

export const Storage: FC = () => {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newFolderPath, setNewFolderPath] = useState('');
  const [folders, setFolders] = useState<MonitoredFolder[]>(mockMonitoredFolders);
  const [actionToast, setActionToast] = useState<string | null>(null);

  const handleAddFolder = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFolderPath) return;
    const newEntry: MonitoredFolder = {
      id: `fld-${Date.now()}`,
      path: newFolderPath,
      fileCount: 0,
      totalSizeBytes: 0,
      status: 'active',
      lastScanTime: 'Just now',
    };
    setFolders([newEntry, ...folders]);
    setNewFolderPath('');
    setIsAddModalOpen(false);
    showToast(`Added protected folder path: ${newFolderPath}`);
  };

  const handleScanFolder = (path: string) => {
    setFolders((prev) =>
      prev.map((f) => (f.path === path ? { ...f, lastScanTime: 'Just now' } : f))
    );
    showToast(`Scan initiated for ${path}`);
  };

  const handleRemoveFolder = (id: string, path: string) => {
    setFolders((prev) => prev.filter((f) => f.id !== id));
    showToast(`Removed path ${path} from monitoring list.`);
  };

  const showToast = (msg: string) => {
    setActionToast(msg);
    setTimeout(() => setActionToast(null), 3500);
  };

  const totalBytes = mockVolumes.reduce((acc, v) => acc + v.totalBytes, 0);
  const usedBytes = mockVolumes.reduce((acc, v) => acc + v.usedBytes, 0);
  const freeBytes = totalBytes - usedBytes;

  const folderColumns: Column<MonitoredFolder>[] = [
    {
      key: 'path',
      header: 'DIRECTORY',
      render: (fld) => (
        <div className="flex items-center gap-2">
          <Folder className="w-4 h-4 text-blue-600 shrink-0" />
          <span className="font-mono text-xs text-blue-700 font-semibold">{fld.path}</span>
        </div>
      ),
    },
    {
      key: 'fileCount',
      header: 'FILES',
      render: (fld) => <span className="text-slate-800 font-medium">{fld.fileCount.toLocaleString()}</span>,
    },
    {
      key: 'totalSizeBytes',
      header: 'SIZE',
      render: (fld) => <span className="text-slate-800 font-medium">{formatBytes(fld.totalSizeBytes)}</span>,
    },
    {
      key: 'lastScanTime',
      header: 'LAST SCANNED',
      render: (fld) => <span className="text-slate-500 text-xs">{fld.lastScanTime}</span>,
    },
    {
      key: 'status',
      header: 'STATUS',
      render: (fld) => (
        <Badge variant={fld.status === 'active' ? 'success' : 'warning'}>
          {fld.status.toUpperCase()}
        </Badge>
      ),
    },
    {
      key: 'actions',
      header: 'ACTIONS',
      render: (fld) => (
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleScanFolder(fld.path)}
            title="Scan Now"
            className="p-1.5 rounded-xl bg-white/80 hover:bg-blue-50 text-blue-600 border border-slate-200 shadow-sm transition-all"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => handleRemoveFolder(fld.id, fld.path)}
            title="Remove Path"
            className="p-1.5 rounded-xl bg-white/80 hover:bg-red-50 text-red-500 border border-slate-200 shadow-sm transition-all"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      ),
    },
  ];

  return (
    <PageContainer
      title="Storage Management & Vaults"
      subtitle="Overview of protected storage volumes, monitored paths, and immutable data vaults"
    >
      <div className="space-y-6">
        {/* Toast Notification */}
        {actionToast && (
          <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-2xl text-emerald-800 text-xs flex items-center gap-2 shadow-sm animate-fadeIn">
            <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
            <span className="font-medium">{actionToast}</span>
          </div>
        )}

        {/* Top Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <GlassCard>
            <div className="flex justify-between items-start">
              <div>
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Total Storage</p>
                <h4 className="text-2xl font-extrabold text-slate-900 mt-1">{formatBytes(totalBytes)}</h4>
              </div>
              <div className="p-2.5 bg-blue-50 border border-blue-100 rounded-2xl text-blue-600 shadow-sm">
                <HardDrive className="w-5 h-5" />
              </div>
            </div>
          </GlassCard>

          <GlassCard>
            <div className="flex justify-between items-start">
              <div>
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Used Storage</p>
                <h4 className="text-2xl font-extrabold text-slate-900 mt-1">{formatBytes(usedBytes)}</h4>
              </div>
              <div className="p-2.5 bg-indigo-50 border border-indigo-100 rounded-2xl text-indigo-600 shadow-sm">
                <Database className="w-5 h-5" />
              </div>
            </div>
          </GlassCard>

          <GlassCard>
            <div className="flex justify-between items-start">
              <div>
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Free Storage</p>
                <h4 className="text-2xl font-extrabold text-slate-900 mt-1">{formatBytes(freeBytes)}</h4>
              </div>
              <div className="p-2.5 bg-emerald-50 border border-emerald-100 rounded-2xl text-emerald-600 shadow-sm">
                <ShieldCheck className="w-5 h-5" />
              </div>
            </div>
          </GlassCard>

          <GlassCard>
            <div className="flex justify-between items-start">
              <div>
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Storage Health</p>
                <h4 className="text-2xl font-extrabold text-emerald-600 mt-1">98 / 100</h4>
              </div>
              <Badge variant="success">EXCELLENT</Badge>
            </div>
          </GlassCard>
        </div>

        {/* Storage Volume & File Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Horizontal Storage Volume Rows */}
          <GlassCard className="lg:col-span-2">
            <h3 className="text-base font-bold text-slate-900 mb-4">Storage Volumes & Vault Status</h3>
            <div className="space-y-3">
              {mockVolumes.map((vol) => {
                const pct = Math.round((vol.usedBytes / vol.totalBytes) * 100);
                return (
                  <div key={vol.id} className="p-4 bg-white/70 rounded-2xl border border-white/90 space-y-2.5 shadow-sm hover:border-blue-200 transition-colors">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                      <div>
                        <div className="flex items-center gap-2">
                          <HardDrive className="w-4 h-4 text-blue-600 shrink-0" />
                          <span className="font-bold text-slate-900 text-sm">{vol.name}</span>
                        </div>
                        <p className="text-[11px] font-mono text-slate-500 mt-0.5">{vol.mountPoint}</p>
                      </div>

                      <div className="flex items-center gap-3">
                        <span className="text-xs font-mono text-slate-600 font-semibold">
                          {formatBytes(vol.usedBytes)} / {formatBytes(vol.totalBytes)} ({pct}%)
                        </span>
                        <Badge variant={vol.type === 'immutable_vault' ? 'success' : vol.type === 'network' ? 'warning' : 'info'}>
                          {vol.type.replace('_', ' ').toUpperCase()}
                        </Badge>
                      </div>
                    </div>

                    <div className="w-full bg-slate-200/80 h-2.5 rounded-full overflow-hidden p-0.5">
                      <div
                        className={`h-full rounded-full transition-all duration-300 ${
                          pct > 85 ? 'bg-gradient-to-r from-amber-500 to-red-500' : 'bg-gradient-to-r from-blue-500 to-emerald-500'
                        }`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </GlassCard>

          {/* File Type Distribution */}
          <GlassCard className="flex flex-col justify-between">
            <div>
              <h3 className="text-base font-bold text-slate-900 mb-4">File Type Distribution</h3>
              <FileTypeDonutChart data={mockFileTypeDistribution} />
            </div>
          </GlassCard>
        </div>

        {/* Monitored Protected Paths Table */}
        <GlassCard>
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h3 className="text-base font-bold text-slate-900">Monitored Protected Paths</h3>
                <p className="text-xs text-slate-500">Folders actively monitored for encryption anomalies and file tampered events</p>
              </div>
              <Button variant="primary" onClick={() => setIsAddModalOpen(true)} className="flex items-center gap-2 text-xs py-2 px-3.5">
                <FolderPlus className="w-4 h-4" />
                <span>Add Protected Path</span>
              </Button>
            </div>

            <DataTable
              columns={folderColumns}
              data={folders}
              keyExtractor={(fld) => fld.id}
              emptyMessage="No monitored folder paths configured."
            />
          </div>
        </GlassCard>

        {/* Recent Storage Activity */}
        <GlassCard>
          <h3 className="text-base font-bold text-slate-900 mb-4">Recent Storage Activity</h3>
          <div className="space-y-2.5">
            {mockStorageActivityLogs.map((log) => (
              <div key={log.id} className="flex justify-between items-center p-3 bg-white/70 rounded-2xl border border-white/90 text-xs shadow-sm">
                <div className="flex items-center gap-3">
                  <FileText className="w-4 h-4 text-blue-600 shrink-0" />
                  <div>
                    <p className="font-bold text-slate-900">{log.action}</p>
                    <p className="text-slate-500 font-mono text-[11px]">{log.targetPath}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-slate-800 font-bold">{formatBytes(log.sizeBytes)}</p>
                  <p className="text-slate-400 text-[11px]">{log.timestamp}</p>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>

      {/* Add Folder Modal */}
      <Modal isOpen={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} title="Add Protected Path">
        <form onSubmit={handleAddFolder} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Directory Path</label>
            <input
              type="text"
              placeholder="e.g. C:/Users/Admin/CriticalData"
              value={newFolderPath}
              onChange={(e) => setNewFolderPath(e.target.value)}
              className="w-full bg-white/90 border border-slate-200 rounded-xl p-2.5 text-sm text-slate-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none"
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="secondary" onClick={() => setIsAddModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">Add Folder</Button>
          </div>
        </form>
      </Modal>
    </PageContainer>
  );
};
