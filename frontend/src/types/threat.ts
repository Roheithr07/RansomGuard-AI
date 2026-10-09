export type ThreatSeverity = 'low' | 'medium' | 'high' | 'critical';
export type ThreatStatus = 'detected' | 'quarantined' | 'mitigated' | 'resolved';

export interface ThreatItem {
  id: string;
  timestamp: string;
  processName: string;
  pid: number;
  severity: ThreatSeverity;
  riskScore: number;
  affectedFiles: string[];
  status: ThreatStatus;
  detectedBy: 'IsolationForest' | 'XGBoost' | 'RuleEngine';
  threatType: string;
  entropyScore: number;
}

export interface ThreatTimelinePoint {
  timestamp: string;
  riskScore: number;
  eventCount: number;
}
