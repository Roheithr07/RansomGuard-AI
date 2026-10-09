import type { FC } from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { StatCard } from '../components/dashboard/StatCard';
import { StorageHealth } from '../components/dashboard/StorageHealth';
import { ThreatOverview } from '../components/dashboard/ThreatOverview';
import { FileActivityChart } from '../components/dashboard/FileActivityChart';
import { SecurityEvents } from '../components/dashboard/SecurityEvents';
import { BackupOverview } from '../components/dashboard/BackupOverview';
import { RecoveryStatus } from '../components/dashboard/RecoveryStatus';
import { useDashboardData } from '../hooks/useDashboardData';
import type { StatMetric, StorageHealthMetric } from '../types/dashboard';
import { ShieldCheck, ShieldAlert, PauseCircle, RefreshCw, AlertTriangle } from 'lucide-react';

export const Dashboard: FC = () => {
  const {
    dashboard,
    recentEvents,
    activeThreats,
    snapshots,
    loading,
    error,
    refetch,
  } = useDashboardData(5000);

  // Fallback metric cards when loading or disconnected
  const statMetrics: StatMetric[] = dashboard
    ? [
        {
          id: '1',
          title: 'FILES MONITORED',
          value: dashboard.files_monitored.toLocaleString(),
          change: dashboard.storage_metrics?.is_monitoring ? 'Watchdog Active' : 'Monitor Inactive',
          isPositive: Boolean(dashboard.storage_metrics?.is_monitoring),
          iconName: 'ShieldCheck',
        },
        {
          id: '2',
          title: 'THREATS DETECTED',
          value: String(dashboard.threats_detected),
          change: dashboard.active_threats > 0 ? `${dashboard.active_threats} In Quarantine` : '0 Active',
          isPositive: dashboard.active_threats === 0,
          iconName: 'ShieldAlert',
        },
        {
          id: '3',
          title: 'STORAGE HEALTH',
          value: `${dashboard.storage_health_percentage}%`,
          change: dashboard.current_risk_level === 'LOW' ? 'Optimal' : dashboard.current_risk_level,
          isPositive: dashboard.current_risk_score < 60,
          iconName: 'HardDrive',
        },
        {
          id: '4',
          title: 'BACKUP POINTS',
          value: String(dashboard.backup_points_count),
          change: dashboard.latest_snapshot ? 'SHA-256 Valid' : 'No Checkpoints',
          isPositive: dashboard.backup_points_count > 0,
          iconName: 'Database',
        },
      ]
    : [
        { id: '1', title: 'FILES MONITORED', value: '--', change: 'Connecting...', isPositive: true, iconName: 'ShieldCheck' },
        { id: '2', title: 'THREATS DETECTED', value: '--', change: 'Connecting...', isPositive: true, iconName: 'ShieldAlert' },
        { id: '3', title: 'STORAGE HEALTH', value: '--', change: 'Connecting...', isPositive: true, iconName: 'HardDrive' },
        { id: '4', title: 'BACKUP POINTS', value: '--', change: 'Connecting...', isPositive: true, iconName: 'Database' },
      ];

  // Map real storage health data
  const storageHealthData: StorageHealthMetric | null = dashboard
    ? {
        totalCapacityBytes: 100 * 1024 * 1024 * 1024, // 100 GB baseline capacity
        usedCapacityBytes: dashboard.monitored_storage_bytes || 2048,
        freeCapacityBytes: Math.max(0, (100 * 1024 * 1024 * 1024) - (dashboard.monitored_storage_bytes || 2048)),
        healthScore: Math.round(dashboard.storage_health_percentage),
        protectedFilesCount: dashboard.files_monitored,
      }
    : null;

  // Determine real monitoring and risk state
  const isMonitoringActive = Boolean(dashboard?.storage_metrics?.is_monitoring);
  const currentRiskScore = dashboard?.current_risk_score ?? 0;
  const isThreatDetected = currentRiskScore >= 60;

  return (
    <PageContainer
      title="RansomGuard AI Security Dashboard"
      subtitle="Real-time ransomware threat intelligence & storage health telemetry"
    >
      <div className="space-y-6">
        {/* Error Connection Banner (if backend unavailable) */}
        {error && (
          <div className="p-4 liquid-glass rounded-2xl border border-red-500/30 flex items-center justify-between text-xs text-red-700 font-semibold shadow-xs">
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 text-red-600 shrink-0" />
              <div>
                <p className="font-bold">Backend Connection Unavailable</p>
                <p className="text-slate-500 font-normal">Could not fetch live telemetry from http://127.0.0.1:8000 ({error}).</p>
              </div>
            </div>
            <button
              onClick={() => refetch()}
              className="px-3 py-1.5 bg-red-600 text-white rounded-xl font-bold flex items-center gap-1.5 hover:bg-red-700 transition-colors cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry</span>
            </button>
          </div>
        )}

        {/* Protection Status Banner (Reflects real backend watchdog & risk state) */}
        <div className="p-4 liquid-glass rounded-2xl border border-white/90 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xs">
          <div className="flex items-center gap-3">
            <div className={`p-3 rounded-2xl border ${
              !isMonitoringActive
                ? 'bg-amber-500/10 border-amber-500/25 text-amber-600'
                : isThreatDetected
                ? 'bg-red-500/10 border-red-500/25 text-red-600'
                : 'bg-emerald-500/10 border-emerald-500/25 text-emerald-600'
            }`}>
              {!isMonitoringActive ? (
                <PauseCircle className="w-6 h-6" />
              ) : isThreatDetected ? (
                <ShieldAlert className="w-6 h-6" />
              ) : (
                <ShieldCheck className="w-6 h-6" />
              )}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-slate-900">
                  {!isMonitoringActive
                    ? 'Storage Monitoring Inactive'
                    : isThreatDetected
                    ? 'Ransomware Threat Flagged!'
                    : 'You are Protected!'}
                </h3>
                <span className={`px-2 py-0.5 text-[10px] font-extrabold rounded-full uppercase tracking-wider border ${
                  !isMonitoringActive
                    ? 'bg-amber-500/15 text-amber-700 border-amber-500/30'
                    : isThreatDetected
                    ? 'bg-red-500/15 text-red-700 border-red-500/30'
                    : 'bg-emerald-500/15 text-emerald-700 border-emerald-500/30'
                }`}>
                  {!isMonitoringActive
                    ? 'MONITORING STOPPED'
                    : isThreatDetected
                    ? 'THREAT DETECTED'
                    : 'SYSTEM PROTECTED'}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                {!isMonitoringActive
                  ? 'Filesystem watchdog surveillance is currently suspended. Resume monitoring in Live Monitor.'
                  : isThreatDetected
                  ? `Elevated risk operations observed (${currentRiskScore}/100 score). Snapshot recovery point available.`
                  : `Active watchdog monitoring on protected storage • ${dashboard?.files_monitored ?? 0} files guarded • Zero active threats.`}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs text-slate-400 font-medium">
            <span className={`w-2.5 h-2.5 rounded-full ${isMonitoringActive ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
            <span>{isMonitoringActive ? 'Auto-syncing every 5s' : 'Offline'}</span>
          </div>
        </div>

        {/* Top Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {statMetrics.map((metric) => (
            <StatCard key={metric.id} metric={metric} loading={loading && !dashboard} />
          ))}
        </div>

        {/* Telemetry Activity & Storage Health */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <FileActivityChart />
          <StorageHealth health={storageHealthData} loading={loading && !dashboard} />
        </div>

        {/* Threat, Events, Backup & Recovery Panel */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <ThreatOverview threats={activeThreats} loading={loading && !dashboard} />
          <SecurityEvents events={recentEvents} loading={loading && !dashboard} />
          <BackupOverview
            snapshots={snapshots}
            latestSnapshot={dashboard?.latest_snapshot}
            loading={loading && !dashboard}
          />
          <RecoveryStatus
            snapshotCount={dashboard?.backup_points_count ?? 0}
            activeThreatsCount={dashboard?.active_threats ?? 0}
            loading={loading && !dashboard}
          />
        </div>
      </div>
    </PageContainer>
  );
};
