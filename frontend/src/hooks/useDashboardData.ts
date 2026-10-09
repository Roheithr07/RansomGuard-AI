import { useState, useEffect, useCallback, useRef } from 'react';
import {
  getDashboard,
  getEvents,
  getThreats,
  getSnapshots,
} from '../lib/api';
import type {
  DashboardResponse,
  ThreatRecord,
  SnapshotItem,
} from '../lib/api';

export interface DashboardEventItem {
  id: string;
  eventId: string;
  timestamp: string;
  eventType: string;
  filePath: string;
  fileName: string;
  fileSize: number;
  entropy: number;
  riskScore: number;
  severity: string;
  description: string;
  status: string;
}

export function useDashboardData(pollIntervalMs: number = 5000) {
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [recentEvents, setRecentEvents] = useState<DashboardEventItem[]>([]);
  const [activeThreats, setActiveThreats] = useState<ThreatRecord[]>([]);
  const [snapshots, setSnapshots] = useState<SnapshotItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const isMountedRef = useRef<boolean>(true);

  const fetchData = useCallback(async () => {
    try {
      // 1. Fetch main dashboard summary
      const dash = await getDashboard();
      if (!isMountedRef.current) return;
      setDashboard(dash);
      setError(null);

      // 2. Fetch recent events (sorted newest first)
      try {
        const eventsRes = await getEvents({ limit: 6 });
        if (isMountedRef.current && eventsRes.events) {
          const mapped: DashboardEventItem[] = eventsRes.events.map((e) => {
            let desc = `${e.file_name} (${e.event_type})`;
            try {
              const parsed = typeof e.detection_reasons === 'string' ? JSON.parse(e.detection_reasons) : e.detection_reasons;
              if (Array.isArray(parsed) && parsed.length > 0) {
                desc = parsed[0];
              }
            } catch {
              // fallback
            }

            return {
              id: e.event_id || String(e.id),
              eventId: e.event_id,
              timestamp: new Date(e.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
              eventType: e.event_type,
              filePath: e.file_path,
              fileName: e.file_name,
              fileSize: e.file_size,
              entropy: e.entropy,
              riskScore: e.risk_score,
              severity: e.severity,
              description: desc,
              status: e.status,
            };
          });
          setRecentEvents(mapped);
        }
      } catch {
        // Fallback to recent_events included in dashboard response if separate call fails
        if (dash.recent_events) {
          const fallbackEvents: DashboardEventItem[] = dash.recent_events.map((e) => ({
            id: e.event_id,
            eventId: e.event_id,
            timestamp: new Date(e.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
            eventType: e.event_type,
            filePath: e.file_name,
            fileName: e.file_name,
            fileSize: e.file_size,
            entropy: e.entropy,
            riskScore: e.risk_score,
            severity: e.severity,
            description: e.file_name,
            status: e.status,
          }));
          setRecentEvents(fallbackEvents);
        }
      }

      // 3. Fetch threats
      try {
        const threatsRes = await getThreats({ limit: 5 });
        if (isMountedRef.current && threatsRes.threats) {
          setActiveThreats(threatsRes.threats.filter((t) => t.status !== 'Resolved'));
        }
      } catch {
        // non-blocking
      }

      // 4. Fetch snapshots
      try {
        const snapsRes = await getSnapshots();
        if (isMountedRef.current && snapsRes.snapshots) {
          setSnapshots(snapsRes.snapshots);
        }
      } catch {
        // non-blocking
      }
    } catch (err: unknown) {
      if (isMountedRef.current) {
        const msg = err instanceof Error ? err.message : 'Failed to connect to backend server';
        setError(msg);
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    isMountedRef.current = true;
    fetchData();

    // Auto-polling interval
    const timer = setInterval(() => {
      fetchData();
    }, pollIntervalMs);

    return () => {
      isMountedRef.current = false;
      clearInterval(timer);
    };
  }, [fetchData, pollIntervalMs]);

  return {
    dashboard,
    recentEvents,
    activeThreats,
    snapshots,
    loading,
    error,
    refetch: fetchData,
  };
}
