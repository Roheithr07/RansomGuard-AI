import { useState } from 'react';
import { mockFileActivityData } from '../data/dashboardData';

export function useFileMonitor() {
  const [activity] = useState(mockFileActivityData);
  const [isMonitoring] = useState(true);

  return { activity, isMonitoring };
}
