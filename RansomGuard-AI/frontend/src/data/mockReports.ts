import type { ReportItem, SecurityStatSummary } from '../types/reports';

export const mockSecuritySummary: SecurityStatSummary = {
  totalIncidentsBlocked: 14,
  avgResponseTimeMs: 120,
  protectedStorageTB: 2.0,
  systemUptimePercent: 99.99,
};

export const mockReports: ReportItem[] = [
  {
    id: 'rep-01',
    title: 'Monthly Security & Ransomware Threat Intelligence Report - August 2026',
    generatedAt: '2026-09-01 00:00:00',
    type: 'threat',
    fileSizeBytes: 2450000,
    format: 'PDF',
  },
  {
    id: 'rep-02',
    title: 'Storage Optimization & Deduplication Audit Log Q3',
    generatedAt: '2026-09-10 09:30:00',
    type: 'storage',
    fileSizeBytes: 1840000,
    format: 'PDF',
  },
  {
    id: 'rep-03',
    title: 'Immutable Snapshots Integrity Verification Certificate',
    generatedAt: '2026-09-15 08:00:00',
    type: 'compliance',
    fileSizeBytes: 520000,
    format: 'CSV',
  },
  {
    id: 'rep-04',
    title: 'System Telemetry & Full System Audit Trail',
    generatedAt: '2026-09-15 12:00:00',
    type: 'full_audit',
    fileSizeBytes: 8900000,
    format: 'PDF',
  },
];
