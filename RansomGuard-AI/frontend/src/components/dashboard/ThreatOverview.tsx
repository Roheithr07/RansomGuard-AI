import type { FC } from 'react';
import { GlassCard } from '../common/GlassCard';
import { Badge } from '../common/Badge';
import type { ThreatRecord } from '../../lib/api';

interface ThreatOverviewProps {
  threats?: ThreatRecord[];
  loading?: boolean;
}

export const ThreatOverview: FC<ThreatOverviewProps> = ({ threats = [], loading = false }) => {
  return (
    <GlassCard>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-base font-bold text-slate-900">Threat Overview</h3>
        <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">AI Guard</span>
      </div>

      {loading ? (
        <div className="space-y-2.5">
          <div className="p-3 bg-white/40 rounded-xl border border-white/60 animate-pulse h-16" />
        </div>
      ) : threats.length === 0 ? (
        <div className="p-3.5 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-xs text-emerald-700 font-medium">
          <p className="font-bold mb-0.5">System Operating Securely</p>
          <p className="text-[11px] text-emerald-600">Zero ransomware incidents active. Storage watchdog surveillance normal.</p>
        </div>
      ) : (
        <div className="space-y-2.5">
          {threats.map((t) => {
            const reason = Array.isArray(t.detection_reasons) && t.detection_reasons.length > 0
              ? t.detection_reasons[0]
              : 'Suspicious filesystem pattern';

            return (
              <div key={t.id || t.threat_id} className="flex items-center justify-between p-3 bg-white/70 backdrop-blur-md rounded-xl border border-white/90 shadow-2xs">
                <div className="min-w-0 flex-1 pr-2">
                  <p className="text-xs font-bold text-slate-900 truncate" title={reason}>{reason}</p>
                  <p className="text-[11px] text-slate-500 font-mono">
                    {t.threat_id} • Score: {t.risk_score}/100
                  </p>
                </div>
                <Badge variant={t.severity === 'CRITICAL' || t.severity === 'HIGH' ? 'danger' : 'warning'}>
                  {t.severity}
                </Badge>
              </div>
            );
          })}
        </div>
      )}
    </GlassCard>
  );
};
