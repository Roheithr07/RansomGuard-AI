import type { StatMetric, StorageHealthMetric, FileActivityPoint } from '../types/dashboard';

export const mockStatMetrics: StatMetric[] = [
  {
    id: '1',
    title: 'FILES MONITORED',
    value: '12,450',
    change: '+1,240 Today',
    isPositive: true,
    iconName: 'ShieldCheck',
  },
  {
    id: '2',
    title: 'THREATS DETECTED',
    value: '3',
    change: 'In Quarantine',
    isPositive: false,
    iconName: 'ShieldAlert',
  },
  {
    id: '3',
    title: 'STORAGE HEALTH',
    value: '98.7%',
    change: 'Optimal',
    isPositive: true,
    iconName: 'HardDrive',
  },
  {
    id: '4',
    title: 'BACKUP POINTS',
    value: '24',
    change: '100% Verified',
    isPositive: true,
    iconName: 'Database',
  },
];

export const mockStorageHealth: StorageHealthMetric = {
  totalCapacityBytes: 2000000000000,
  usedCapacityBytes: 850000000000,
  freeCapacityBytes: 1150000000000,
  healthScore: 98,
  protectedFilesCount: 1284910,
};

export const mockFileActivityData: FileActivityPoint[] = [
  { time: '00:00', reads: 120, writes: 45, renames: 2, deletes: 0 },
  { time: '04:00', reads: 80, writes: 20, renames: 0, deletes: 0 },
  { time: '08:00', reads: 450, writes: 190, renames: 12, deletes: 3 },
  { time: '12:00', reads: 890, writes: 410, renames: 25, deletes: 8 },
  { time: '16:00', reads: 720, writes: 310, renames: 18, deletes: 4 },
  { time: '20:00', reads: 310, writes: 110, renames: 5, deletes: 1 },
];
