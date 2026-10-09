export interface MonitoredFolder {
  id: string;
  path: string;
  fileCount: number;
  totalSizeBytes: number;
  status: 'active' | 'paused' | 'warning';
  lastScanTime: string;
}

export interface StorageVolume {
  id: string;
  name: string;
  mountPoint: string;
  totalBytes: number;
  usedBytes: number;
  type: 'local' | 'network' | 'immutable_vault';
}

export interface FileTypeDistribution {
  name: string;
  bytes: number;
  percentage: number;
  color: string;
}

export interface StorageActivityLog {
  id: string;
  timestamp: string;
  action: string;
  targetPath: string;
  sizeBytes: number;
}
