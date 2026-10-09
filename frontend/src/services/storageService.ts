import { mockStorageHealth } from '../data/dashboardData';
import { StorageHealthMetric } from '../types/dashboard';

export const storageService = {
  async getStorageHealth(): Promise<StorageHealthMetric> {
    return Promise.resolve(mockStorageHealth);
  },
};
