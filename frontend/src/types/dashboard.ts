export interface StatMetric {
  id: string;
  title: string;
  value: string | number;
  change: string;
  isPositive: boolean;
  iconName: string;
}

export interface StorageHealthMetric {
  totalCapacityBytes: number;
  usedCapacityBytes: number;
  freeCapacityBytes: number;
  healthScore: number;
  protectedFilesCount: number;
}

export interface FileActivityPoint {
  time: string;
  reads: number;
  writes: number;
  renames: number;
  deletes: number;
}
