import { mockThreats } from '../data/mockThreats';
import { ThreatItem } from '../types/threat';

export const threatService = {
  async getActiveThreats(): Promise<ThreatItem[]> {
    return Promise.resolve(mockThreats);
  },
};
