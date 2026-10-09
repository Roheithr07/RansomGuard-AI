import type { RecoveryJob } from '../types/recovery';

export const recoveryService = {
  async getRecoveryStatus(): Promise<RecoveryJob | null> {
    return Promise.resolve(null);
  },
};
