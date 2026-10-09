import { useState } from 'react';
import type { FC } from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { GlassCard } from '../components/common/GlassCard';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Modal } from '../components/common/Modal';
import { ActivityChart } from '../components/charts/ActivityChart';
import { mockReports, mockSecuritySummary } from '../data/mockReports';
import { mockFileActivityData } from '../data/dashboardData';
import { formatBytes } from '../utils/formatters';
import type { ReportItem } from '../types/reports';
import { FileText, Download, ShieldCheck, Zap, HardDrive, Clock, Plus, CheckCircle2 } from 'lucide-react';

export const Reports: FC = () => {
  const [reports, setReports] = useState<ReportItem[]>(mockReports);
  const [isGenerateModalOpen, setIsGenerateModalOpen] = useState(false);
  const [reportTitle, setReportTitle] = useState('');
  const [reportType, setReportType] = useState<'threat' | 'storage' | 'compliance' | 'full_audit'>('full_audit');
  const [reportFormat, setReportFormat] = useState<'PDF' | 'CSV'>('PDF');
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const handleGenerateReport = (e: React.FormEvent) => {
    e.preventDefault();
    const newReport: ReportItem = {
      id: `rep-${Date.now()}`,
      title: reportTitle || `Generated ${reportType.toUpperCase()} Audit Report`,
      generatedAt: new Date().toISOString().replace('T', ' ').substring(0, 19),
      type: reportType,
      fileSizeBytes: Math.floor(Math.random() * 3000000) + 500000,
      format: reportFormat,
    };

    setReports([newReport, ...reports]);
    setIsGenerateModalOpen(false);
    setReportTitle('');
    setToastMessage(`Report "${newReport.title}" successfully compiled.`);
    setTimeout(() => setToastMessage(null), 4000);
  };

  return (
    <PageContainer
      title="Security, Telemetry & Compliance Reports"
      subtitle="Exportable ransomware audit logs, storage telemetry trends, and immutable snapshot integrity certificates"
    >
      <div className="space-y-6">
        {/* Toast */}
        {toastMessage && (
          <div className="p-3.5 bg-emerald-500/15 border border-emerald-500/30 rounded-2xl text-emerald-800 text-xs font-bold flex items-center gap-2 animate-pulse">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{toastMessage}</span>
          </div>
        )}

        {/* Security Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <GlassCard>
            <div className="flex justify-between items-start">
              <div>
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Incidents Blocked</p>
                <h4 className="text-2xl font-extrabold text-slate-900 mt-1">{mockSecuritySummary.totalIncidentsBlocked}</h4>
              </div>
              <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl text-emerald-600">
                <ShieldCheck className="w-5 h-5" />
              </div>
            </div>
          </GlassCard>

          <GlassCard>
            <div className="flex justify-between items-start">
              <div>
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Avg Response Time</p>
                <h4 className="text-2xl font-extrabold text-[#006FA6] mt-1">{mockSecuritySummary.avgResponseTimeMs} ms</h4>
              </div>
              <div className="p-2.5 bg-[#00ABE4]/10 border border-cyan-500/20 rounded-2xl text-[#006FA6]">
                <Zap className="w-5 h-5" />
              </div>
            </div>
          </GlassCard>

          <GlassCard>
            <div className="flex justify-between items-start">
              <div>
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Protected Storage</p>
                <h4 className="text-2xl font-extrabold text-slate-900 mt-1">{mockSecuritySummary.protectedStorageTB} TB</h4>
              </div>
              <div className="p-2.5 bg-blue-500/10 border border-blue-500/20 rounded-2xl text-blue-600">
                <HardDrive className="w-5 h-5" />
              </div>
            </div>
          </GlassCard>

          <GlassCard>
            <div className="flex justify-between items-start">
              <div>
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">System Uptime</p>
                <h4 className="text-2xl font-extrabold text-emerald-600 mt-1">{mockSecuritySummary.systemUptimePercent}%</h4>
              </div>
              <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl text-emerald-600">
                <Clock className="w-5 h-5" />
              </div>
            </div>
          </GlassCard>
        </div>

        {/* Charts Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <GlassCard>
            <h3 className="text-base font-bold text-slate-900 mb-4">Historical Activity & Incident Trend Chart</h3>
            <ActivityChart data={mockFileActivityData} />
          </GlassCard>

          <GlassCard>
            <h3 className="text-base font-bold text-slate-900 mb-4">Backup & Snapshot Audit Statistics</h3>
            <div className="space-y-4 text-xs">
              <div className="p-4 bg-white/70 rounded-2xl border border-white/90 shadow-2xs space-y-1">
                <div className="flex justify-between font-bold text-slate-900">
                  <span>Snapshot Vault Consistency</span>
                  <span className="text-emerald-700">100%</span>
                </div>
                <p className="text-slate-500 font-medium">SHA-256 Hashes verified cleanly across 48 snapshot points.</p>
              </div>

              <div className="p-4 bg-white/70 rounded-2xl border border-white/90 shadow-2xs space-y-1">
                <div className="flex justify-between font-bold text-slate-900">
                  <span>Smart Recovery Readiness</span>
                  <span className="text-emerald-700">OPTIMAL</span>
                </div>
                <p className="text-slate-500 font-medium">Instant point-in-time restoration index available.</p>
              </div>
            </div>
          </GlassCard>
        </div>

        {/* Generated Reports Table */}
        <GlassCard className="space-y-4">
          <div className="flex justify-between items-center flex-wrap gap-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">Exportable Audit & Telemetry Reports</h3>
              <p className="text-xs text-slate-500">System audit trails compiled for compliance verification</p>
            </div>
            <Button variant="primary" onClick={() => setIsGenerateModalOpen(true)} className="flex items-center gap-2">
              <Plus className="w-4 h-4" />
              <span>Generate Report</span>
            </Button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-200/80 text-[11px] font-bold text-slate-500 uppercase tracking-wider bg-white/40">
                  <th className="py-3 px-4">REPORT TITLE</th>
                  <th className="py-3 px-4">TYPE</th>
                  <th className="py-3 px-4">GENERATED DATE</th>
                  <th className="py-3 px-4">SIZE</th>
                  <th className="py-3 px-4">FORMAT</th>
                  <th className="py-3 px-4">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200/60">
                {reports.map((rep) => (
                  <tr key={rep.id} className="hover:bg-white/80 transition-colors">
                    <td className="py-3.5 px-4 font-bold text-slate-900 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-[#006FA6] shrink-0" />
                      {rep.title}
                    </td>
                    <td className="py-3.5 px-4">
                      <Badge variant="info">{rep.type.toUpperCase()}</Badge>
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 font-medium">{rep.generatedAt}</td>
                    <td className="py-3.5 px-4 text-slate-700 font-semibold">{formatBytes(rep.fileSizeBytes)}</td>
                    <td className="py-3.5 px-4 font-mono font-bold text-amber-700">{rep.format}</td>
                    <td className="py-3.5 px-4">
                      <Button variant="secondary" className="flex items-center gap-1.5 py-1 px-3 text-xs">
                        <Download className="w-3.5 h-3.5" />
                        <span>Download</span>
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      </div>

      {/* Modal */}
      <Modal isOpen={isGenerateModalOpen} onClose={() => setIsGenerateModalOpen(false)} title="Generate Audit Report">
        <form onSubmit={handleGenerateReport} className="space-y-4 text-xs">
          <div>
            <label className="block font-bold text-slate-800 mb-1">Custom Report Title (Optional)</label>
            <input
              type="text"
              placeholder="e.g. Q3 Security & Threat Telemetry Report"
              value={reportTitle}
              onChange={(e) => setReportTitle(e.target.value)}
              className="w-full bg-white border border-slate-300 rounded-xl p-2.5 text-xs text-slate-900 focus:outline-none focus:border-[#00ABE4]"
            />
          </div>

          <div>
            <label className="block font-bold text-slate-800 mb-1">Report Category</label>
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value as any)}
              className="w-full bg-white border border-slate-300 rounded-xl p-2.5 text-xs text-slate-900 focus:outline-none focus:border-[#00ABE4]"
            >
              <option value="full_audit">Full System Audit & Telemetry</option>
              <option value="threat">Threat Intelligence & Anomaly Incidents</option>
              <option value="storage">Storage Health & Optimization</option>
              <option value="compliance">Immutable Vault Compliance Certificate</option>
            </select>
          </div>

          <div>
            <label className="block font-bold text-slate-800 mb-1">Export Format</label>
            <div className="flex gap-4">
              <label className="flex items-center gap-2 cursor-pointer text-slate-700 font-semibold">
                <input
                  type="radio"
                  name="format"
                  value="PDF"
                  checked={reportFormat === 'PDF'}
                  onChange={() => setReportFormat('PDF')}
                />
                PDF Document
              </label>
              <label className="flex items-center gap-2 cursor-pointer text-slate-700 font-semibold">
                <input
                  type="radio"
                  name="format"
                  value="CSV"
                  checked={reportFormat === 'CSV'}
                  onChange={() => setReportFormat('CSV')}
                />
                CSV Spreadsheet Data
              </label>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="secondary" onClick={() => setIsGenerateModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">Compile & Generate</Button>
          </div>
        </form>
      </Modal>
    </PageContainer>
  );
};
