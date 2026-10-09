import { useState, useEffect } from 'react';
import type { ThreatItem } from '../types/threat';
import { threatService } from '../services/threatService';

export function useThreats() {
  const [threats, setThreats] = useState<ThreatItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    threatService.getActiveThreats().then((data) => {
      setThreats(data);
      setLoading(false);
    });
  }, []);

  return { threats, loading };
}
