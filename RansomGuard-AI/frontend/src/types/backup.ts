export interface BackupSnapshot {
  id: string;
  snapshotId: string;
  createdAt: string;
  type: 'trusted' | 'temporary';
  sizeBytes: number;
  fileCount: number;
  integrityHash: string;
  status: 'healthy' | 'corrupted' | 'verifying';
  totalFolders: number;
}

export interface BackupStats {
  totalSnapshots: number;
  latestSnapshotDate: string;
  totalSizeBytes: number;
  integrityPercent: number;
}
