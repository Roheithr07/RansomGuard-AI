export type MonitorEventType = 'created' | 'modified' | 'renamed' | 'deleted';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'INFO';
export type MonitorEventStatus = 'NORMAL' | 'MONITORED' | 'SUSPICIOUS' | 'FLAGGED';

export interface MonitorEvent {
  id: string;
  timestamp: string;
  eventType: MonitorEventType;
  fileName: string;
  path: string;
  filePath: string;
  processName: string;
  pid: number;
  entropy: number;
  risk: RiskLevel;
  status: MonitorEventStatus;
  isNew?: boolean;
}

export interface MonitorStats {
  totalEvents: number;
  createCount: number;
  modifyCount: number;
  renameCount: number;
  deleteCount: number;
  avgEventsPerSec: number;
  anomaliesCount: number;
  monitoredPathsCount: number;
  activeFilesCount: number;
}
