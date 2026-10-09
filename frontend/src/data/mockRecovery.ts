import type { RecoveryPoint, RecoveryHistoryItem } from '../types/recovery';

export const mockRecoveryPoints: RecoveryPoint[] = [
  {
    id: 'rec-01',
    snapshotId: 'snap-20260915-160000',
    timestamp: '2026-09-15 16:00:00',
    fileCount: 1284910,
    sizeBytes: 452000000000,
    affectedFilesCount: 0,
    verificationStatus: 'verified',
  },
  {
    id: 'rec-02',
    snapshotId: 'snap-20260915-120000',
    timestamp: '2026-09-15 12:00:00',
    fileCount: 1284200,
    sizeBytes: 451800000000,
    affectedFilesCount: 2,
    verificationStatus: 'verified',
  },
  {
    id: 'rec-03',
    snapshotId: 'snap-20260915-080000',
    timestamp: '2026-09-15 08:00:00',
    fileCount: 1283900,
    sizeBytes: 451500000000,
    affectedFilesCount: 0,
    verificationStatus: 'verified',
  },
];

export const mockRecoveryHistory: RecoveryHistoryItem[] = [
  {
    id: 'rh-101',
    timestamp: '2026-09-14 18:25:00',
    targetSnapshotId: 'snap-20260914-120000',
    filesRestored: 2,
    status: 'success',
    durationSec: 1.4,
  },
  {
    id: 'rh-100',
    timestamp: '2026-09-10 09:12:00',
    targetSnapshotId: 'snap-20260910-080000',
    filesRestored: 14,
    status: 'success',
    durationSec: 4.8,
  },
];
