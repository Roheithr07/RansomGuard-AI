import type { FC } from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { GlassCard } from '../components/common/GlassCard';
import { Badge } from '../components/common/Badge';
import { AITimelineChart } from '../components/charts/AITimelineChart';
import { mockAIMetrics, mockBehaviorRates, mockModels, mockAITimeline } from '../data/mockAI';
import { Cpu, ShieldCheck, Zap } from 'lucide-react';

export const AIAnalysis: FC = () => {
  return (
    <PageContainer
      title="Machine Learning Threat Analysis & Anomaly Engine"
      subtitle="Real-time Isolation Forest and XGBoost behavioral telemetry, entropy anomaly scoring, and model diagnostics"
    >
      <div className="space-y-6">
        {/* Top Metric Overview */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <GlassCard>
            <div className="flex justify-between items-start">
              <div>
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Threat Score</p>
                <h4 className="text-2xl font-extrabold text-slate-900 mt-1">12 / 100</h4>
              </div>
              <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl text-emerald-600">
                <ShieldCheck className="w-5 h-5" />
              </div>
            </div>
          </GlassCard>

          <GlassCard>
            <div className="flex justify-between items-start">
              <div>
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">AI Confidence</p>
                <h4 className="text-2xl font-extrabold text-slate-900 mt-1">{mockAIMetrics.confidence}%</h4>
              </div>
              <div className="p-2.5 bg-[#00ABE4]/10 border border-cyan-500/20 rounded-2xl text-[#006FA6]">
                <Cpu className="w-5 h-5" />
              </div>
            </div>
          </GlassCard>

          <GlassCard>
            <div className="flex justify-between items-start">
              <div>
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Risk Level</p>
                <h4 className="text-2xl font-extrabold text-emerald-600 mt-1">LOW</h4>
              </div>
              <Badge variant="success font-bold">SAFE</Badge>
            </div>
          </GlassCard>

          <GlassCard>
            <div className="flex justify-between items-start">
              <div>
                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Entropy Level</p>
                <h4 className="text-2xl font-extrabold text-[#006FA6] mt-1">{mockBehaviorRates.entropyScore} (Low)</h4>
              </div>
              <div className="p-2.5 bg-blue-500/10 border border-blue-500/20 rounded-2xl text-blue-600">
                <Zap className="w-5 h-5" />
              </div>
            </div>
          </GlassCard>
        </div>

        {/* Behavior Telemetry Rates */}
        <GlassCard>
          <h3 className="text-base font-bold text-slate-900 mb-4">Real-Time Process Behavior Telemetry Rates</h3>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 bg-white/70 rounded-2xl border border-white/90 shadow-2xs space-y-1">
              <p className="text-xs text-slate-500 font-semibold">File Modification Rate</p>
              <h4 className="text-xl font-extrabold text-slate-900">{mockBehaviorRates.modificationRatePerMin} / min</h4>
              <span className="text-[11px] text-emerald-700 font-bold">Normal Baseline</span>
            </div>

            <div className="p-4 bg-white/70 rounded-2xl border border-white/90 shadow-2xs space-y-1">
              <p className="text-xs text-slate-500 font-semibold">Batch Rename Rate</p>
              <h4 className="text-xl font-extrabold text-slate-900">{mockBehaviorRates.renameRatePerMin} / min</h4>
              <span className="text-[11px] text-emerald-700 font-bold">Normal Baseline</span>
            </div>

            <div className="p-4 bg-white/70 rounded-2xl border border-white/90 shadow-2xs space-y-1">
              <p className="text-xs text-slate-500 font-semibold">File Delete Rate</p>
              <h4 className="text-xl font-extrabold text-slate-900">{mockBehaviorRates.deleteRatePerMin} / min</h4>
              <span className="text-[11px] text-emerald-700 font-bold">Zero Anomaly</span>
            </div>

            <div className="p-4 bg-white/70 rounded-2xl border border-white/90 shadow-2xs space-y-1">
              <p className="text-xs text-slate-500 font-semibold">Operation Frequency</p>
              <h4 className="text-xl font-extrabold text-[#006FA6]">{mockBehaviorRates.operationFreqPerSec} ops/sec</h4>
              <span className="text-[11px] text-[#006FA6] font-bold">Telemetry Active</span>
            </div>
          </div>
        </GlassCard>

        {/* Timeline Chart */}
        <GlassCard>
          <h3 className="text-base font-bold text-slate-900 mb-4">24-Hour AI Anomaly Scoring vs Safety Baseline</h3>
          <AITimelineChart data={mockAITimeline} />
        </GlassCard>

        {/* Detection Models Status */}
        <GlassCard>
          <h3 className="text-base font-bold text-slate-900 mb-4">Active Detection Machine Learning Models</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {mockModels.map((mdl) => (
              <div key={mdl.id} className="p-4 bg-white/70 rounded-2xl border border-white/90 shadow-2xs space-y-2">
                <div className="flex justify-between items-start">
                  <h4 className="font-bold text-slate-900 text-sm">{mdl.name}</h4>
                  <Badge variant="success">{mdl.status.toUpperCase()}</Badge>
                </div>
                <p className="text-xs text-slate-500 font-medium">Type: <strong className="text-[#006FA6] uppercase">{mdl.type}</strong></p>
                <p className="text-xs text-slate-500 font-medium">Accuracy: <strong className="text-emerald-700">{mdl.accuracyPercent}%</strong></p>
                <p className="text-xs text-slate-400 font-mono">Last Trained: {mdl.lastTrained}</p>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </PageContainer>
  );
};
