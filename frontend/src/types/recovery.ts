export interface RecoveryPoint {
  id: string;
  snapshotId: string;
  timestamp: string;
  fileCount: number;
  sizeBytes: number;
  affectedFilesCount: number;
  verificationStatus: 'verified' | 'pending' | 'warning';
}

export interface RecoveryJob {
  id: string;
  startedAt: string;
  targetSnapshotId: string;
  filesToRestoreCount: number;
  filesRestoredCount: number;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  estimatedTimeRemainingSeconds?: number;
}

export interface RecoveryHistoryItem {
  id: string;
  timestamp: string;
  targetSnapshotId: string;
  filesRestored: number;
  status: 'success' | 'partial' | 'failed';
  durationSec: number;
}
