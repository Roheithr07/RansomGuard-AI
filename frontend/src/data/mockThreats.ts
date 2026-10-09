import type { ThreatItem, ThreatTimelinePoint } from '../types/threat';

export const mockThreats: ThreatItem[] = [
  {
    id: 'th-101',
    timestamp: '2026-09-15 10:42:15',
    processName: 'suspicious_encryptor.exe',
    pid: 4892,
    severity: 'critical',
    riskScore: 0.96,
    affectedFiles: ['C:/Data/Finance/Q3_Report.docx', 'C:/Data/Finance/Ledger.xlsx'],
    status: 'quarantined',
    detectedBy: 'IsolationForest',
    threatType: 'High Entropy Rapid File Encryptor',
    entropyScore: 7.92,
  },
  {
    id: 'th-102',
    timestamp: '2026-09-14 18:15:02',
    processName: 'rapid_renamer.vbs',
    pid: 7120,
    severity: 'medium',
    riskScore: 0.65,
    affectedFiles: ['C:/Data/Temp/test_file.tmp'],
    status: 'mitigated',
    detectedBy: 'RuleEngine',
    threatType: 'Automated Batch Renaming Anomaly',
    entropyScore: 4.12,
  },
  {
    id: 'th-103',
    timestamp: '2026-09-13 14:00:00',
    processName: 'unknown_cmd_runner.exe',
    pid: 1890,
    severity: 'low',
    riskScore: 0.25,
    affectedFiles: ['C:/Users/Public/temp.bat'],
    status: 'resolved',
    detectedBy: 'XGBoost',
    threatType: 'Unusual Shell Execution Pattern',
    entropyScore: 2.10,
  },
];

export const mockThreatTimeline: ThreatTimelinePoint[] = [
  { timestamp: '00:00', riskScore: 0.02, eventCount: 12 },
  { timestamp: '04:00', riskScore: 0.01, eventCount: 8 },
  { timestamp: '08:00', riskScore: 0.05, eventCount: 45 },
  { timestamp: '10:42', riskScore: 0.96, eventCount: 198 },
  { timestamp: '12:00', riskScore: 0.12, eventCount: 89 },
  { timestamp: '16:00', riskScore: 0.04, eventCount: 34 },
];
