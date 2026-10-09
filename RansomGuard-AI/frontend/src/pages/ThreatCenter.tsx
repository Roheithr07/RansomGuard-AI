import { useState } from 'react';
import type { FC } from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { GlassCard } from '../components/common/GlassCard';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Modal } from '../components/common/Modal';
import { TabGroup } from '../components/common/TabGroup';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, PieChart, Pie, Cell } from 'recharts';
import { mockThreats, mockThreatTimeline } from '../data/mockThreats';
import type { ThreatItem } from '../types/threat';
import { ShieldAlert, ShieldCheck, Cpu, Search, Eye, Filter, MoreHorizontal, Lock, RefreshCw, CheckCircle2, FileText } from 'lucide-react';

const threatTypeDistribution = [
  { name: 'Ransomware', value: 42, color: '#3B82F6' },
  { name: 'Malware', value: 21, color: '#F59E0B' },
  { name: 'Trojan', value: 15, color: '#8B5CF6' },
  { name: 'Suspicious Scripts', value: 12, color: '#EC4899' },
  { name: 'Other', value: 10, color: '#06B6D4' },
];

export const ThreatCenter: FC = () => {
  const [activeTab, setActiveTab] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedThreat, setSelectedThreat] = useState<ThreatItem | null>(null);
  const [threatList, setThreatList] = useState<ThreatItem[]>(mockThreats);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const filteredThreats = threatList.filter((th) => {
    if (activeTab === 'critical' && th.severity !== 'critical') return false;
    if (activeTab === 'quarantined' && th.status !== 'quarantined') return false;
    if (activeTab === 'resolved' && th.status !== 'resolved' && th.status !== 'mitigated') return false;

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      return (
        th.processName.toLowerCase().includes(q) ||
        th.threatType.toLowerCase().includes(q) ||
        th.detectedBy.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const handleResolve = (id: string, name: string) => {
    setThreatList((prev) =>
      prev.map((t) => (t.id === id ? { ...t, status: 'resolved' as const } : t))
    );
    if (selectedThreat?.id === id) setSelectedThreat(null);
    showToast(`Threat incident "${name}" resolved.`);
  };

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  return (
    <PageContainer
      title="Ransomware Threat Intelligence & Quarantine Center"
      subtitle="AI-powered threat detection, behavior analysis, and automated quarantine management"
    >
      <div className="space-y-6">
        {/* Toast */}
        {toastMessage && (
          <div className="p-3.5 bg-emerald-500/15 border border-emerald-500/30 rounded-2xl text-emerald-700 text-xs font-bold flex items-center gap-2 animate-pulse">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{toastMessage}</span>
          </div>
        )}

        {/* Top KPI Cards (Reference Image Layout) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <GlassCard className="flex justify-between items-center">
            <div>
              <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Threat Level</p>
              <h4 className="text-2xl font-extrabold text-slate-900 mt-0.5">LOW</h4>
              <p className="text-xs text-emerald-600 font-bold mt-0.5">0.04 Score</p>
            </div>
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl text-emerald-600">
              <ShieldCheck className="w-6 h-6" />
            </div>
          </GlassCard>

          <GlassCard className="flex justify-between items-center">
            <div>
              <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Active Threats</p>
              <div className="flex items-baseline gap-2">
                <h4 className="text-2xl font-extrabold text-slate-900 mt-0.5">
                  {threatList.filter((t) => t.status === 'quarantined').length}
                </h4>
                <span className="text-xs text-red-500 font-bold">+1</span>
              </div>
              <p className="text-xs text-slate-500 font-medium">In Quarantine</p>
            </div>
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-2xl text-red-500">
              <ShieldAlert className="w-6 h-6" />
            </div>
          </GlassCard>

          <GlassCard className="flex justify-between items-center">
            <div>
              <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">AI Models Active</p>
              <h4 className="text-2xl font-extrabold text-slate-900 mt-0.5">3</h4>
              <p className="text-[11px] text-slate-500 font-medium truncate">Isolation Forest, XGBoost</p>
            </div>
            <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-2xl text-[#00ABE4]">
              <Cpu className="w-6 h-6" />
            </div>
          </GlassCard>

          <GlassCard className="flex justify-between items-center">
            <div>
              <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Files Scanned</p>
              <h4 className="text-2xl font-extrabold text-slate-900 mt-0.5">1.28M</h4>
              <p className="text-xs text-emerald-600 font-bold">Today</p>
            </div>
            <div className="p-3 bg-cyan-500/10 border border-cyan-500/20 rounded-2xl text-cyan-600">
              <FileText className="w-6 h-6" />
            </div>
          </GlassCard>
        </div>

        {/* Charts & AI Analysis Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Threat Detection Timeline */}
          <GlassCard className="lg:col-span-2">
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-[#00ABE4]" />
                <h3 className="text-base font-bold text-slate-900">Threat Detection Timeline</h3>
              </div>
              <span className="text-xs font-semibold text-slate-500 bg-white/60 px-3 py-1 rounded-full border border-slate-200/80">
                Last 24 Hours
              </span>
            </div>
            <div className="w-full h-56">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={mockThreatTimeline}>
                  <defs>
                    <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00ABE4" stopOpacity={0.35} />
                      <stop offset="95%" stopColor="#00ABE4" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="timestamp" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#94a3b8" domain={[0, 1]} tick={{ fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(255, 255, 255, 0.95)',
                      borderColor: 'rgba(255, 255, 255, 0.9)',
                      color: '#0f172a',
                      borderRadius: '16px',
                      boxShadow: '0 10px 25px -5px rgba(0, 171, 228, 0.15)',
                      fontSize: '12px',
                    }}
                  />
                  <Area type="monotone" dataKey="riskScore" stroke="#00ABE4" strokeWidth={3} fill="url(#riskGrad)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>

          {/* AI Analysis Panel */}
          <GlassCard className="flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex justify-between items-center border-b border-slate-200/60 pb-3">
                <div className="flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-[#00ABE4]" />
                  <h3 className="text-base font-bold text-slate-900">AI Analysis</h3>
                </div>
                <MoreHorizontal className="w-4 h-4 text-slate-400" />
              </div>

              {/* Confidence Donut Meter */}
              <div className="text-center py-2">
                <div className="w-24 h-24 rounded-full border-4 border-[#00ABE4] flex flex-col items-center justify-center mx-auto bg-white/60 shadow-md">
                  <span className="text-xl font-extrabold text-slate-900">97.4%</span>
                  <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">Confidence</span>
                </div>
                <p className="text-xs font-semibold text-slate-600 mt-2">Model: <strong className="text-slate-900">Isolation Forest</strong></p>
              </div>

              {/* Feature Checklist */}
              <div className="space-y-1.5 text-xs text-slate-700 font-medium">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span>Behavior Analysis</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span>Entropy Analysis</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span>Pattern Recognition</span>
                </div>
              </div>
            </div>

            <Button variant="secondary" className="w-full mt-4 text-xs font-bold py-2">
              View Analysis Details →
            </Button>
          </GlassCard>
        </div>

        {/* Threat List Table & Quarantine Actions Row */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Detected Threats Table */}
          <GlassCard className="lg:col-span-3 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <h3 className="text-base font-bold text-slate-900">Detected Threats</h3>
              <div className="flex items-center gap-3 flex-wrap">
                <TabGroup
                  tabs={[
                    { id: 'all', label: 'All', count: threatList.length },
                    { id: 'critical', label: 'Critical', count: threatList.filter((t) => t.severity === 'critical').length },
                    { id: 'quarantined', label: 'Quarantined', count: threatList.filter((t) => t.status === 'quarantined').length },
                    { id: 'resolved', label: 'Resolved' },
                  ]}
                  activeTab={activeTab}
                  onChange={setActiveTab}
                />

                <div className="relative">
                  <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    placeholder="Search threats..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="bg-white/60 border border-white/90 rounded-full pl-8 pr-3 py-1 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-[#00ABE4]"
                  />
                </div>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-200/80 text-[11px] font-bold text-slate-500 uppercase tracking-wider bg-white/40">
                    <th className="py-3 px-3">THREAT NAME</th>
                    <th className="py-3 px-3">TYPE</th>
                    <th className="py-3 px-3">RISK LEVEL</th>
                    <th className="py-3 px-3">DETECTION METHOD</th>
                    <th className="py-3 px-3">AFFECTED FILES</th>
                    <th className="py-3 px-3">STATUS</th>
                    <th className="py-3 px-3">ACTIONS</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200/60">
                  {filteredThreats.map((t) => (
                    <tr key={t.id} className="hover:bg-white/80 transition-colors">
                      <td className="py-3 px-3 font-bold text-slate-900 font-mono">
                        {t.processName}
                        <p className="text-[10px] text-slate-400 font-normal">PID: {t.pid}</p>
                      </td>
                      <td className="py-3 px-3 text-slate-700">{t.threatType}</td>
                      <td className="py-3 px-3">
                        <Badge variant={t.severity === 'critical' ? 'danger' : t.severity === 'medium' ? 'warning' : 'info'}>
                          {t.severity.toUpperCase()}
                        </Badge>
                      </td>
                      <td className="py-3 px-3 text-slate-600 font-medium">{t.detectedBy}</td>
                      <td className="py-3 px-3 font-mono text-[11px] text-[#006FA6]">{t.affectedFiles.length} files</td>
                      <td className="py-3 px-3">
                        <Badge variant={t.status === 'quarantined' ? 'danger' : 'success'}>
                          {t.status.toUpperCase()}
                        </Badge>
                      </td>
                      <td className="py-3 px-3">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => setSelectedThreat(t)}
                            title="View Telemetry"
                            className="p-1.5 rounded-lg bg-white/80 hover:bg-white text-slate-600 hover:text-[#006FA6] border border-slate-200 transition-colors"
                          >
                            <Eye className="w-3.5 h-3.5" />
                          </button>
                          {t.status !== 'resolved' && (
                            <button
                              onClick={() => handleResolve(t.id, t.processName)}
                              title="Resolve Threat"
                              className="p-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-700 border border-emerald-500/30 transition-colors"
                            >
                              <CheckCircle2 className="w-3.5 h-3.5" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </GlassCard>

          {/* Quarantine Actions Card */}
          <GlassCard className="space-y-4">
            <h3 className="text-base font-bold text-slate-900 border-b border-slate-200/60 pb-3">
              Quarantine Actions
            </h3>
            <div className="space-y-2.5">
              <Button variant="primary" className="w-full justify-start py-2.5">
                <Lock className="w-4 h-4" />
                <span>Isolate Threat</span>
              </Button>
              <Button variant="secondary" className="w-full justify-start py-2.5">
                <RefreshCw className="w-4 h-4" />
                <span>Run Full Scan</span>
              </Button>
              <Button variant="secondary" className="w-full justify-start py-2.5">
                <Cpu className="w-4 h-4" />
                <span>Update AI Models</span>
              </Button>
              <Button variant="secondary" className="w-full justify-start py-2.5">
                <ShieldCheck className="w-4 h-4" />
                <span>Whitelist File</span>
              </Button>
            </div>
          </GlassCard>
        </div>
      </div>

      {/* Detail Modal */}
      <Modal isOpen={!!selectedThreat} onClose={() => setSelectedThreat(null)} title="Threat Incident Details">
        {selectedThreat && (
          <div className="space-y-4 text-xs">
            <div className="p-4 bg-white/80 rounded-2xl border border-slate-200 space-y-1.5">
              <p className="text-slate-500">Process Name: <strong className="text-slate-900 font-mono">{selectedThreat.processName}</strong></p>
              <p className="text-slate-500">PID: <strong className="text-slate-900 font-mono">{selectedThreat.pid}</strong></p>
              <p className="text-slate-500">Detection Method: <strong className="text-[#006FA6]">{selectedThreat.detectedBy}</strong></p>
              <p className="text-slate-500">Threat Type: <strong className="text-red-600">{selectedThreat.threatType}</strong></p>
            </div>

            <div>
              <p className="font-bold text-slate-900 mb-1">Target Files:</p>
              <ul className="list-disc list-inside space-y-1 font-mono text-[#006FA6] bg-white/70 p-3 rounded-xl border border-slate-200">
                {selectedThreat.affectedFiles.map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <Button variant="secondary" onClick={() => setSelectedThreat(null)}>Close</Button>
              {selectedThreat.status !== 'resolved' && (
                <Button variant="danger" onClick={() => handleResolve(selectedThreat.id, selectedThreat.processName)}>
                  Quarantine & Resolve
                </Button>
              )}
            </div>
          </div>
        )}
      </Modal>
    </PageContainer>
  );
};
