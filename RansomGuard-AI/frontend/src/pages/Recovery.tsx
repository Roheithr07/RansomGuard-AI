import { useState } from 'react';
import type { FC } from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { GlassCard } from '../components/common/GlassCard';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Modal } from '../components/common/Modal';
import { mockRecoveryPoints, mockRecoveryHistory } from '../data/mockRecovery';
import { formatBytes } from '../utils/formatters';
import type { RecoveryPoint } from '../types/recovery';
import { RotateCcw, ShieldCheck, CheckCircle2 } from 'lucide-react';

export const Recovery: FC = () => {
  const [selectedPoint, setSelectedPoint] = useState<RecoveryPoint | null>(mockRecoveryPoints[0]);
  const [isRestoring, setIsRestoring] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isCompleteModal, setIsCompleteModal] = useState(false);

  const startSimulatedRecovery = () => {
    setIsRestoring(true);
    setProgress(10);
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsRestoring(false);
          setIsCompleteModal(true);
          return 100;
        }
        return prev + 25;
      });
    }, 400);
  };

  return (
    <PageContainer
      title="Smart Recovery & File Restoration Engine"
      subtitle="Restore compromised or modified files from clean, uncorrupted immutable point-in-time snapshots"
    >
      <div className="space-y-6">
        {/* Top Banner */}
        <div className="p-5 liquid-glass rounded-2xl border border-white/80 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-emerald-500/10 text-emerald-600 rounded-2xl border border-emerald-500/20">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">Smart Recovery Engine Ready</h3>
              <p className="text-xs text-slate-500">Zero files currently damaged • {mockRecoveryPoints.length} Clean snapshots verified</p>
            </div>
          </div>
          <Button variant="primary" onClick={startSimulatedRecovery} className="flex items-center gap-2">
            <RotateCcw className="w-4 h-4" />
            <span>Simulate Full System Recovery</span>
          </Button>
        </div>

        {/* Stepper Selection & Point List */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <GlassCard className="lg:col-span-2">
            <h3 className="text-base font-bold text-slate-900 mb-4">Select Target Recovery Snapshot Point</h3>
            <div className="space-y-3">
              {mockRecoveryPoints.map((pt) => {
                const isSelected = selectedPoint?.id === pt.id;
                return (
                  <div
                    key={pt.id}
                    onClick={() => setSelectedPoint(pt)}
                    className={`p-4 rounded-2xl border transition-all cursor-pointer flex justify-between items-center ${
                      isSelected
                        ? 'bg-white text-slate-900 border-[#00ABE4] shadow-md shadow-cyan-500/15 ring-2 ring-[#00ABE4]/20'
                        : 'bg-white/50 border-white/80 hover:bg-white/80 text-slate-700'
                    }`}
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-slate-900 text-sm">{pt.snapshotId}</span>
                        <Badge variant={pt.verificationStatus === 'verified' ? 'success' : 'warning'}>
                          {pt.verificationStatus.toUpperCase()}
                        </Badge>
                      </div>
                      <p className="text-xs text-slate-500 font-medium">Timestamp: {pt.timestamp}</p>
                      <p className="text-xs text-slate-600 font-semibold">
                        {pt.fileCount.toLocaleString()} Files • {formatBytes(pt.sizeBytes)}
                      </p>
                    </div>

                    <div className="text-right">
                      {isSelected ? (
                        <span className="text-xs px-3 py-1 bg-[#00ABE4] text-white font-bold rounded-full shadow-2xs">
                          SELECTED
                        </span>
                      ) : (
                        <span className="text-xs text-slate-400 font-semibold hover:text-[#006FA6]">Select</span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </GlassCard>

          {/* Selected Target Summary */}
          <GlassCard>
            <h3 className="text-base font-bold text-slate-900 mb-4">Recovery Target Details</h3>
            {selectedPoint ? (
              <div className="space-y-4 text-xs">
                <div className="p-4 bg-white/80 rounded-2xl border border-white/90 shadow-2xs space-y-2">
                  <p className="text-slate-500">Target Snapshot: <strong className="text-[#006FA6] font-mono">{selectedPoint.snapshotId}</strong></p>
                  <p className="text-slate-500">Date: <strong className="text-slate-900">{selectedPoint.timestamp}</strong></p>
                  <p className="text-slate-500">Total Files: <strong className="text-slate-900">{selectedPoint.fileCount.toLocaleString()}</strong></p>
                  <p className="text-slate-500">Affected Files: <strong className="text-emerald-700">{selectedPoint.affectedFilesCount}</strong></p>
                  <p className="text-slate-500">Integrity: <strong className="text-emerald-700">SHA-256 Validated</strong></p>
                </div>

                <div className="p-3.5 bg-cyan-500/10 border border-cyan-500/25 rounded-2xl text-[#006FA6]">
                  <p className="font-bold flex items-center gap-1.5 mb-1 text-xs">
                    <CheckCircle2 className="w-4 h-4 text-[#00ABE4]" /> Non-Destructive Restore
                  </p>
                  Files will be verified against SHA-256 vault hashes before replacing local items.
                </div>

                <Button variant="primary" onClick={startSimulatedRecovery} className="w-full py-2.5">
                  <RotateCcw className="w-4 h-4" />
                  <span>Start Restoration</span>
                </Button>
              </div>
            ) : (
              <p className="text-xs text-slate-500">Select a snapshot to view details.</p>
            )}
          </GlassCard>
        </div>

        {/* Progress simulation card when active */}
        {isRestoring && (
          <GlassCard className="border-cyan-500/40 animate-pulse">
            <div className="space-y-3">
              <div className="flex justify-between items-center text-xs sm:text-sm">
                <span className="font-bold text-slate-900 flex items-center gap-2">
                  <RotateCcw className="w-4 h-4 text-[#00ABE4] animate-spin" />
                  Restoring Files from Snapshot {selectedPoint?.snapshotId}...
                </span>
                <span className="font-mono text-[#006FA6] font-bold">{progress}%</span>
              </div>
              <div className="w-full bg-slate-200 h-3 rounded-full overflow-hidden">
                <div className="bg-gradient-to-r from-[#00ABE4] to-[#3B82F6] h-full transition-all duration-300" style={{ width: `${progress}%` }} />
              </div>
              <p className="text-xs text-slate-500">Verifying file headers and uncompressing blocks from immutable storage vault...</p>
            </div>
          </GlassCard>
        )}

        {/* Past Recovery History */}
        <GlassCard>
          <h3 className="text-base font-bold text-slate-900 mb-4">Historical Recovery Audit Log</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-200/80 text-[11px] font-bold text-slate-500 uppercase tracking-wider bg-white/40">
                  <th className="py-3 px-4">JOB ID</th>
                  <th className="py-3 px-4">TIMESTAMP</th>
                  <th className="py-3 px-4">SOURCE SNAPSHOT</th>
                  <th className="py-3 px-4">RESTORED FILES</th>
                  <th className="py-3 px-4">DURATION</th>
                  <th className="py-3 px-4">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200/60">
                {mockRecoveryHistory.map((rh) => (
                  <tr key={rh.id} className="hover:bg-white/80 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-bold text-slate-900">{rh.id}</td>
                    <td className="py-3.5 px-4 text-slate-600">{rh.timestamp}</td>
                    <td className="py-3.5 px-4 font-mono text-[#006FA6]">{rh.targetSnapshotId}</td>
                    <td className="py-3.5 px-4 text-slate-800 font-semibold">{rh.filesRestored} files</td>
                    <td className="py-3.5 px-4 text-slate-500">{rh.durationSec}s</td>
                    <td className="py-3.5 px-4">
                      <Badge variant="success">SUCCESSFUL</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      </div>

      {/* Completion Modal */}
      <Modal isOpen={isCompleteModal} onClose={() => setIsCompleteModal(false)} title="Restoration Complete">
        <div className="space-y-4 text-xs text-center p-2">
          <div className="w-12 h-12 rounded-full bg-emerald-500/15 text-emerald-600 flex items-center justify-center mx-auto border border-emerald-500/30">
            <CheckCircle2 className="w-8 h-8" />
          </div>
          <h4 className="text-base font-bold text-slate-900">Simulated Restoration Successful</h4>
          <p className="text-slate-600 font-medium">
            All files from snapshot <strong className="text-[#006FA6] font-mono">{selectedPoint?.snapshotId}</strong> have been verified and restored to clean state.
          </p>
          <div className="pt-2">
            <Button variant="primary" onClick={() => setIsCompleteModal(false)}>Close Summary</Button>
          </div>
        </div>
      </Modal>
    </PageContainer>
  );
};
