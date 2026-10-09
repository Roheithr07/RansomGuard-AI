import { useState } from 'react';
import type { FC } from 'react';
import { PageContainer } from '../components/layout/PageContainer';
import { GlassCard } from '../components/common/GlassCard';
import { Button } from '../components/common/Button';
import { ToggleSwitch } from '../components/common/ToggleSwitch';
import { TabGroup } from '../components/common/TabGroup';
import { defaultSettings } from '../data/mockSettings';
import type { SystemSettings } from '../types/settings';
import { CheckCircle2, Save, Shield, Database, Bell, Eye } from 'lucide-react';

export const Settings: FC = () => {
  const [activeTab, setActiveTab] = useState('monitoring');
  const [settings, setSettings] = useState<SystemSettings>(defaultSettings);
  const [saveSuccessToast, setSaveSuccessToast] = useState(false);

  const handleSave = () => {
    setSaveSuccessToast(true);
    setTimeout(() => setSaveSuccessToast(false), 3500);
  };

  return (
    <PageContainer
      title="System Configuration & Preferences"
      subtitle="Configure Watchdog monitoring rules, AI alert thresholds, automated snapshot frequency, and notification preferences"
    >
      <div className="space-y-6">
        {/* Toast Notification */}
        {saveSuccessToast && (
          <div className="p-3.5 bg-emerald-500/15 border border-emerald-500/30 rounded-2xl text-emerald-800 text-xs font-bold flex items-center gap-2 animate-pulse">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>Settings successfully saved and synchronized across telemetry services.</span>
          </div>
        )}

        {/* Settings Navigation Tabs */}
        <GlassCard className="p-2">
          <TabGroup
            tabs={[
              { id: 'monitoring', label: 'File Monitoring' },
              { id: 'backup', label: 'Snapshots & Backup' },
              { id: 'notifications', label: 'Alerts & Notifications' },
              { id: 'appearance', label: 'Appearance & UI' },
            ]}
            activeTab={activeTab}
            onChange={setActiveTab}
          />
        </GlassCard>

        {/* Settings Panel Body */}
        {activeTab === 'monitoring' && (
          <GlassCard className="space-y-6">
            <div className="flex items-center gap-3 pb-3 border-b border-slate-200/80">
              <Shield className="w-5 h-5 text-[#006FA6]" />
              <h3 className="text-base font-bold text-slate-900">File Monitoring Engine Rules</h3>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 bg-white/70 rounded-2xl border border-white/90 shadow-2xs">
                <div>
                  <h4 className="font-bold text-slate-900 text-sm">Real-Time Watchdog Monitoring</h4>
                  <p className="text-xs text-slate-500 font-medium">Continuously track file creation, modification, renaming, and deletion entropy</p>
                </div>
                <ToggleSwitch
                  checked={settings.monitoringEnabled}
                  onChange={(val) => setSettings({ ...settings, monitoringEnabled: val })}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-white/70 rounded-2xl border border-white/90 shadow-2xs space-y-2">
                  <label className="block text-xs font-bold text-slate-800">Scan & Telemetry Interval</label>
                  <select
                    value={settings.monitorIntervalSec}
                    onChange={(e) => setSettings({ ...settings, monitorIntervalSec: Number(e.target.value) })}
                    className="w-full bg-white border border-slate-300 rounded-xl p-2.5 text-xs text-slate-900 focus:outline-none focus:border-[#00ABE4]"
                  >
                    <option value={1}>1 Second (Aggressive Real-Time)</option>
                    <option value={5}>5 Seconds (Recommended Balanced)</option>
                    <option value={15}>15 Seconds (Low Overhead)</option>
                  </select>
                </div>

                <div className="p-4 bg-white/70 rounded-2xl border border-white/90 shadow-2xs space-y-2">
                  <label className="block text-xs font-bold text-slate-800">Entropy Sensitivity Threshold</label>
                  <select
                    value={settings.alertSensitivity}
                    onChange={(e) => setSettings({ ...settings, alertSensitivity: e.target.value as any })}
                    className="w-full bg-white border border-slate-300 rounded-xl p-2.5 text-xs text-slate-900 focus:outline-none focus:border-[#00ABE4]"
                  >
                    <option value="high">High Sensitivity (Triggers on 7.0+ Shannon entropy)</option>
                    <option value="balanced">Balanced (Triggers on 7.5+ Shannon entropy)</option>
                    <option value="low">Low Sensitivity (Triggers on 7.8+ Shannon entropy)</option>
                  </select>
                </div>
              </div>
            </div>
          </GlassCard>
        )}

        {activeTab === 'backup' && (
          <GlassCard className="space-y-6">
            <div className="flex items-center gap-3 pb-3 border-b border-slate-200/80">
              <Database className="w-5 h-5 text-[#006FA6]" />
              <h3 className="text-base font-bold text-slate-900">Immutable Snapshot & Backup Rules</h3>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 bg-white/70 rounded-2xl border border-white/90 shadow-2xs">
                <div>
                  <h4 className="font-bold text-slate-900 text-sm">Automated Snapshot Scheduler</h4>
                  <p className="text-xs text-slate-500 font-medium">Automatically create read-only immutable volume snapshots on background schedule</p>
                </div>
                <ToggleSwitch
                  checked={settings.autoBackupEnabled}
                  onChange={(val) => setSettings({ ...settings, autoBackupEnabled: val })}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-white/70 rounded-2xl border border-white/90 shadow-2xs space-y-2">
                  <label className="block text-xs font-bold text-slate-800">Snapshot Frequency</label>
                  <select
                    value={settings.snapshotIntervalHours}
                    onChange={(e) => setSettings({ ...settings, snapshotIntervalHours: Number(e.target.value) })}
                    className="w-full bg-white border border-slate-300 rounded-xl p-2.5 text-xs text-slate-900 focus:outline-none focus:border-[#00ABE4]"
                  >
                    <option value={1}>Every 1 Hour</option>
                    <option value={4}>Every 4 Hours (Recommended)</option>
                    <option value={12}>Every 12 Hours</option>
                    <option value={24}>Daily (24 Hours)</option>
                  </select>
                </div>

                <div className="flex justify-between items-center p-4 bg-white/70 rounded-2xl border border-white/90 shadow-2xs">
                  <div>
                    <h4 className="font-bold text-slate-900 text-xs">SHA-256 Recovery Verification</h4>
                    <p className="text-[11px] text-slate-500 font-medium">Validate block checksums prior to restoring</p>
                  </div>
                  <ToggleSwitch
                    checked={settings.recoveryVerificationEnabled}
                    onChange={(val) => setSettings({ ...settings, recoveryVerificationEnabled: val })}
                  />
                </div>
              </div>
            </div>
          </GlassCard>
        )}

        {activeTab === 'notifications' && (
          <GlassCard className="space-y-6">
            <div className="flex items-center gap-3 pb-3 border-b border-slate-200/80">
              <Bell className="w-5 h-5 text-[#006FA6]" />
              <h3 className="text-base font-bold text-slate-900">Alerts & Notification Channels</h3>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 bg-white/70 rounded-2xl border border-white/90 shadow-2xs">
                <div>
                  <h4 className="font-bold text-slate-900 text-sm">Desktop Push Notifications</h4>
                  <p className="text-xs text-slate-500 font-medium">Trigger immediate OS alert popup when critical threat detected</p>
                </div>
                <ToggleSwitch
                  checked={settings.desktopNotifications}
                  onChange={(val) => setSettings({ ...settings, desktopNotifications: val })}
                />
              </div>

              <div className="flex justify-between items-center p-4 bg-white/70 rounded-2xl border border-white/90 shadow-2xs">
                <div>
                  <h4 className="font-bold text-slate-900 text-sm">Email Security Alerts</h4>
                  <p className="text-xs text-slate-500 font-medium">Send high entropy event logs to security administrator email</p>
                </div>
                <ToggleSwitch
                  checked={settings.emailAlerts}
                  onChange={(val) => setSettings({ ...settings, emailAlerts: val })}
                />
              </div>

              {settings.emailAlerts && (
                <div className="p-4 bg-white/70 rounded-2xl border border-white/90 shadow-2xs space-y-2">
                  <label className="block text-xs font-bold text-slate-800">Security Admin Email Address</label>
                  <input
                    type="email"
                    value={settings.emailAddress}
                    onChange={(e) => setSettings({ ...settings, emailAddress: e.target.value })}
                    className="w-full bg-white border border-slate-300 rounded-xl p-2.5 text-xs text-slate-900 focus:outline-none focus:border-[#00ABE4]"
                  />
                </div>
              )}
            </div>
          </GlassCard>
        )}

        {activeTab === 'appearance' && (
          <GlassCard className="space-y-6">
            <div className="flex items-center gap-3 pb-3 border-b border-slate-200/80">
              <Eye className="w-5 h-5 text-[#006FA6]" />
              <h3 className="text-base font-bold text-slate-900">Theme & UI Customization</h3>
            </div>

            <div className="p-4 bg-white/70 rounded-2xl border border-white/90 shadow-2xs space-y-2">
              <p className="font-bold text-slate-900 text-sm">Apple Light Liquid Glass Theme Active</p>
              <p className="text-xs text-slate-500 font-medium">
                Configured with fluid light blue atmosphere, frosted translucent glass surfaces, soft shadows, and cyan/blue accents.
              </p>
            </div>
          </GlassCard>
        )}

        {/* Save Bar */}
        <div className="flex justify-end pt-2">
          <Button variant="primary" onClick={handleSave} className="flex items-center gap-2 py-2.5 px-6">
            <Save className="w-4 h-4" />
            <span>Save Settings</span>
          </Button>
        </div>
      </div>
    </PageContainer>
  );
};
