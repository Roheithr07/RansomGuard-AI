import { useState, useEffect } from 'react';
import type { StorageHealthMetric } from '../types/dashboard';
import { storageService } from '../services/storageService';

export function useStorage() {
  const [health, setHealth] = useState<StorageHealthMetric | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    storageService.getStorageHealth().then((data) => {
      setHealth(data);
      setLoading(false);
    });
  }, []);

  return { health, loading };
}
