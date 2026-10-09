import type { MonitoredFolder, StorageVolume, FileTypeDistribution, StorageActivityLog } from '../types/storage';

export const mockVolumes: StorageVolume[] = [
  {
    id: 'vol-1',
    name: 'Primary OS & Data Drive (C:)',
    mountPoint: 'C:/',
    totalBytes: 1000000000000,
    usedBytes: 420000000000,
    type: 'local',
  },
  {
    id: 'vol-2',
    name: 'Immutable Snapshot Vault (V:)',
    mountPoint: 'V:/RansomGuardVault',
    totalBytes: 800000000000,
    usedBytes: 380000000000,
    type: 'immutable_vault',
  },
  {
    id: 'vol-3',
    name: 'Secure Network Storage (N:)',
    mountPoint: '//nas01/secure_share',
    totalBytes: 2000000000000,
    usedBytes: 500000000000,
    type: 'network',
  },
];

export const mockMonitoredFolders: MonitoredFolder[] = [
  {
    id: 'fld-1',
    path: 'C:/Users/Admin/Documents/Financials',
    fileCount: 42800,
    totalSizeBytes: 125000000000,
    status: 'active',
    lastScanTime: '2 mins ago',
  },
  {
    id: 'fld-2',
    path: 'C:/Users/Admin/Projects/RansomGuard-AI',
    fileCount: 18900,
    totalSizeBytes: 45000000000,
    status: 'active',
    lastScanTime: 'Just now',
  },
  {
    id: 'fld-3',
    path: 'C:/Data/Databases/SQLite',
    fileCount: 3400,
    totalSizeBytes: 89000000000,
    status: 'active',
    lastScanTime: '5 mins ago',
  },
  {
    id: 'fld-4',
    path: 'C:/System/Config/Credentials',
    fileCount: 820,
    totalSizeBytes: 2100000000,
    status: 'warning',
    lastScanTime: '1 hour ago',
  },
];

export const mockFileTypeDistribution: FileTypeDistribution[] = [
  { name: 'Documents & PDFs', bytes: 297500000000, percentage: 35, color: '#06b6d4' },
  { name: 'Media & Visuals', bytes: 212500000000, percentage: 25, color: '#3b82f6' },
  { name: 'System Telemetry', bytes: 170000000000, percentage: 20, color: '#10b981' },
  { name: 'Databases & Logs', bytes: 127500000000, percentage: 15, color: '#f59e0b' },
  { name: 'Encrypted Archives', bytes: 42500000000, percentage: 5, color: '#8b5cf6' },
];

export const mockStorageActivityLogs: StorageActivityLog[] = [
  {
    id: 'act-101',
    timestamp: '2026-09-15 16:28:10',
    action: 'Immutable Snapshot Auto-Sync',
    targetPath: 'V:/RansomGuardVault/snap-20260915-090000',
    sizeBytes: 452000000,
  },
  {
    id: 'act-102',
    timestamp: '2026-09-15 16:10:05',
    action: 'Folder Rule Verified',
    targetPath: 'C:/Users/Admin/Documents/Financials',
    sizeBytes: 12500000,
  },
  {
    id: 'act-103',
    timestamp: '2026-09-15 15:45:22',
    action: 'Deduplication Cleanup Completed',
    targetPath: 'C:/Data/Databases/SQLite',
    sizeBytes: 1890000000,
  },
];
