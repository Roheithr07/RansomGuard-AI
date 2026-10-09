import { mockBackups } from '../data/mockBackups';
import type { BackupSnapshot } from '../types/backup';

export const backupService = {
  async getSnapshots(): Promise<BackupSnapshot[]> {
    return Promise.resolve(mockBackups);
  },
};
