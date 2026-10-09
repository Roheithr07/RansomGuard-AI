export interface SecurityEvent {
  id: string;
  timestamp: string;
  eventType: 'file_modified' | 'file_created' | 'file_deleted' | 'snapshot_created' | 'threat_blocked';
  description: string;
  sourcePath: string;
  riskLevel: 'info' | 'warning' | 'critical';
}

export const mockSecurityEvents: SecurityEvent[] = [
  {
    id: 'ev-01',
    timestamp: '2 mins ago',
    eventType: 'file_modified',
    description: 'Modified 14 files in /documents/projects',
    sourcePath: 'C:/Users/User/Documents/projects',
    riskLevel: 'info',
  },
  {
    id: 'ev-02',
    timestamp: '15 mins ago',
    eventType: 'snapshot_created',
    description: 'Automated immutable snapshot #snap-20260915-01 created',
    sourcePath: 'Storage Vault / trusted',
    riskLevel: 'info',
  },
  {
    id: 'ev-03',
    timestamp: '1 hour ago',
    eventType: 'threat_blocked',
    description: 'High entropy write rate detected and blocked',
    sourcePath: 'PID: 4892 (suspicious_encryptor.exe)',
    riskLevel: 'critical',
  },
];
