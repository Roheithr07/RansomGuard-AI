import type { BackupSnapshot, BackupStats } from '../types/backup';

export const mockBackupStats: BackupStats = {
  totalSnapshots: 48,
  latestSnapshotDate: '10 minutes ago',
  totalSizeBytes: 452000000000,
  integrityPercent: 100,
};

export const mockBackups: BackupSnapshot[] = [
  {
    id: 'snap-001',
    snapshotId: 'snap-20260915-160000',
    createdAt: '2026-09-15 16:00:00 (10 mins ago)',
    type: 'trusted',
    sizeBytes: 452000000000,
    fileCount: 1284910,
    integrityHash: 'sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    status: 'healthy',
    totalFolders: 14,
  },
  {
    id: 'snap-002',
    snapshotId: 'snap-20260915-120000',
    createdAt: '2026-09-15 12:00:00',
    type: 'trusted',
    sizeBytes: 451800000000,
    fileCount: 1284200,
    integrityHash: 'sha256:8f4e2c1098fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852a123',
    status: 'healthy',
    totalFolders: 14,
  },
  {
    id: 'snap-003',
    snapshotId: 'snap-20260915-080000',
    createdAt: '2026-09-15 08:00:00',
    type: 'temporary',
    sizeBytes: 451500000000,
    fileCount: 1283900,
    integrityHash: 'sha256:9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b',
    status: 'healthy',
    totalFolders: 14,
  },
  {
    id: 'snap-004',
    snapshotId: 'snap-20260914-200000',
    createdAt: '2026-09-14 20:00:00',
    type: 'trusted',
    sizeBytes: 450000000000,
    fileCount: 1281000,
    integrityHash: 'sha256:1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b',
    status: 'healthy',
    totalFolders: 13,
  },
];
