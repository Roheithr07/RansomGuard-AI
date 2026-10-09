import type { FC } from 'react';
import { Routes, Route } from 'react-router-dom';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { Dashboard } from '../pages/Dashboard';
import { Storage } from '../pages/Storage';
import { LiveMonitor } from '../pages/LiveMonitor';
import { ThreatCenter } from '../pages/ThreatCenter';
import { BackupSnapshots } from '../pages/BackupSnapshots';
import { Recovery } from '../pages/Recovery';
import { AIAnalysis } from '../pages/AIAnalysis';
import { Reports } from '../pages/Reports';
import { Settings } from '../pages/Settings';

export const AppRoutes: FC = () => {
  return (
    <Routes>
      <Route path="/" element={<DashboardLayout />}>
        <Route index element={<Dashboard />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="storage" element={<Storage />} />
        <Route path="live-monitor" element={<LiveMonitor />} />
        <Route path="monitor" element={<LiveMonitor />} />
        <Route path="threats" element={<ThreatCenter />} />
        <Route path="backups" element={<BackupSnapshots />} />
        <Route path="recovery" element={<Recovery />} />
        <Route path="ai-analysis" element={<AIAnalysis />} />
        <Route path="reports" element={<Reports />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  );
};
