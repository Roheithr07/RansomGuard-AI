import { useState, useEffect, useRef, useCallback } from 'react';
import {
  WS_URL,
  getEvents,
  getSystemStatus,
  startMonitoring,
  stopMonitoring,
  triggerSimulation,
} from '../lib/api';
import type { MonitorEvent, MonitorStats, MonitorEventType, RiskLevel, MonitorEventStatus } from '../types/monitor';

export function useLiveMonitor() {
  const [events, setEvents] = useState<MonitorEvent[]>([]);
  const [stats, setStats] = useState<MonitorStats>({
    totalEvents: 0,
    createCount: 0,
    modifyCount: 0,
    renameCount: 0,
    deleteCount: 0,
    avgEventsPerSec: 0,
    anomaliesCount: 0,
    monitoredPathsCount: 1,
    activeFilesCount: 0,
  });

  const [isMonitoringActive, setIsMonitoringActive] = useState<boolean>(true);
  const [wsStatus, setWsStatus] = useState<'connected' | 'reconnecting' | 'disconnected'>('disconnected');
  const [isFeedPaused, setIsFeedPaused] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isMountedRef = useRef<boolean>(true);
  const isFeedPausedRef = useRef<boolean>(false);

  // Keep ref synchronized with state
  useEffect(() => {
    isFeedPausedRef.current = isFeedPaused;
  }, [isFeedPaused]);

  // Helper to map backend event to MonitorEvent
  const mapBackendEvent = (raw: {
    event_id?: string;
    id?: number;
    timestamp: string;
    event_type: string;
    file_name: string;
    file_path: string;
    process_name?: string | null;
    process_id?: number | null;
    entropy?: number;
    risk_score?: number;
    severity?: string;
    status?: string;
  }): MonitorEvent => {
    let eventType: MonitorEventType = 'modified';
    const et = raw.event_type?.toLowerCase();
    if (et === 'created') eventType = 'created';
    else if (et === 'deleted') eventType = 'deleted';
    else if (et === 'renamed' || et === 'moved') eventType = 'renamed';
    else eventType = 'modified';

    let risk: RiskLevel = 'LOW';
    const sev = raw.severity?.toUpperCase();
    if (sev === 'CRITICAL' || sev === 'HIGH') risk = 'HIGH';
    else if (sev === 'MEDIUM') risk = 'MEDIUM';
    else if (sev === 'LOW') risk = 'LOW';
    else risk = 'INFO';

    let status: MonitorEventStatus = 'NORMAL';
    const score = raw.risk_score || 0;
    if (score >= 80 || raw.status === 'blocked') status = 'FLAGGED';
    else if (score >= 60 || raw.status === 'flagged') status = 'SUSPICIOUS';
    else status = 'MONITORED';

    return {
      id: raw.event_id || `evt-${raw.id || Date.now()}-${Math.random()}`,
      timestamp: new Date(raw.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      eventType,
      operation: raw.event_type?.toUpperCase() || eventType.toUpperCase(),
      fileName: raw.file_name,
      path: raw.file_path,
      filePath: raw.file_path,
      processName: raw.process_name || 'system',
      pid: raw.process_id || 0,
      entropy: raw.entropy ? Number(raw.entropy.toFixed(2)) : 0,
      risk,
      riskScore: typeof raw.risk_score === 'number' ? raw.risk_score : 0,
      status,
      isNew: true,
    };
  };

  // Helper to map backend metrics to MonitorStats
  const updateStatsFromMetrics = useCallback((metrics: {
    files_created?: number;
    files_modified?: number;
    files_deleted?: number;
    files_renamed?: number;
    operations_per_second?: number;
    suspicious_operations?: number;
    monitored_files_count?: number;
    is_monitoring?: boolean;
  }) => {
    if (!metrics) return;
    const created = metrics.files_created || 0;
    const modified = metrics.files_modified || 0;
    const deleted = metrics.files_deleted || 0;
    const renamed = metrics.files_renamed || 0;

    setStats((prev) => ({
      ...prev,
      totalEvents: created + modified + deleted + renamed,
      createCount: created,
      modifyCount: modified,
      renameCount: renamed,
      deleteCount: deleted,
      avgEventsPerSec: metrics.operations_per_second || 0,
      anomaliesCount: metrics.suspicious_operations || 0,
      monitoredPathsCount: 1,
      activeFilesCount: metrics.monitored_files_count ?? prev.activeFilesCount,
    }));

    if (typeof metrics.is_monitoring === 'boolean') {
      setIsMonitoringActive(metrics.is_monitoring);
    }
  }, []);

  // Fetch initial data from REST API
  const fetchInitialData = useCallback(async () => {
    try {
      setLoading(true);
      const [eventsRes, statusRes] = await Promise.all([
        getEvents({ limit: 40 }),
        getSystemStatus(),
      ]);

      if (!isMountedRef.current) return;

      if (eventsRes.events) {
        const mapped = eventsRes.events.map(mapBackendEvent);
        setEvents(mapped);
      }

      if (statusRes.metrics) {
        updateStatsFromMetrics(statusRes.metrics);
        setIsMonitoringActive(Boolean(statusRes.monitoring_active));
      }
    } catch (err) {
      console.warn('Initial live monitor REST fetch error:', err);
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  }, [updateStatsFromMetrics]);

  // WebSocket Connection & Reconnection
  const connectWebSocket = useCallback(() => {
    if (!isMountedRef.current) return;

    // Clean up any existing socket
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }

    try {
      const socket = new WebSocket(WS_URL);
      socketRef.current = socket;

      socket.onopen = () => {
        if (!isMountedRef.current) return;
        setWsStatus('connected');
      };

      socket.onmessage = (event) => {
        if (!isMountedRef.current) return;
        try {
          const payload = JSON.parse(event.data);

          if (payload.type === 'CONNECTION_ESTABLISHED') {
            if (payload.metrics) {
              updateStatsFromMetrics(payload.metrics);
            }
          } else if (payload.type === 'MONITORING_STATUS') {
            if (typeof payload.is_monitoring === 'boolean') {
              setIsMonitoringActive(payload.is_monitoring);
            }
            if (payload.metrics) {
              updateStatsFromMetrics(payload.metrics);
            }
          } else if (payload.type === 'FILE_EVENT') {
            if (payload.metrics) {
              updateStatsFromMetrics(payload.metrics);
            }

            if (payload.data && !isFeedPausedRef.current) {
              const newEv = mapBackendEvent(payload.data);
              setEvents((prev) => [newEv, ...prev.slice(0, 99)]); // Keep up to 100 recent live events
            }
          }
        } catch (e) {
          console.error('Error parsing live monitor WebSocket message:', e);
        }
      };

      socket.onclose = () => {
        if (!isMountedRef.current) return;
        setWsStatus('reconnecting');
        // Reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          if (isMountedRef.current) {
            connectWebSocket();
          }
        }, 3000);
      };

      socket.onerror = () => {
        if (!isMountedRef.current) return;
        setWsStatus('disconnected');
      };
    } catch (err) {
      console.warn('Live monitor WebSocket initialization failed:', err);
      if (isMountedRef.current) {
        setWsStatus('reconnecting');
        reconnectTimeoutRef.current = setTimeout(connectWebSocket, 4000);
      }
    }
  }, [updateStatsFromMetrics]);

  useEffect(() => {
    isMountedRef.current = true;
    fetchInitialData();
    connectWebSocket();

    return () => {
      isMountedRef.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  }, [fetchInitialData, connectWebSocket]);

  // Toggle Watchdog Monitoring
  const handleToggleMonitoring = async () => {
    try {
      if (isMonitoringActive) {
        const res = await stopMonitoring();
        setIsMonitoringActive(false);
        setActionMessage(res.message || 'Monitoring suspended');
      } else {
        const res = await startMonitoring();
        setIsMonitoringActive(true);
        setActionMessage(res.message || 'Monitoring activated');
      }
      setTimeout(() => setActionMessage(null), 4000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to change monitoring state';
      setActionMessage(`Error: ${msg}`);
      setTimeout(() => setActionMessage(null), 4000);
    }
  };

  // Trigger Safe Sandboxed Simulation
  const handleRunSimulation = async (intensity: 'low' | 'medium' | 'high' = 'medium') => {
    try {
      setActionMessage('Executing safe sandboxed simulation in protected_storage/demo/...');
      const res = await triggerSimulation(intensity);
      if (res.success) {
        setActionMessage(`Simulation triggered: ${res.files_simulated} test files created/modified in demo sandbox.`);
      } else {
        setActionMessage(res.message || 'Simulation finished');
      }
      setTimeout(() => setActionMessage(null), 5000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Simulation failed';
      setActionMessage(`Error: ${msg}`);
      setTimeout(() => setActionMessage(null), 4000);
    }
  };

  return {
    events,
    stats,
    isMonitoringActive,
    wsStatus,
    isFeedPaused,
    setIsFeedPaused,
    loading,
    actionMessage,
    handleToggleMonitoring,
    handleRunSimulation,
    refreshEvents: fetchInitialData,
  };
}
