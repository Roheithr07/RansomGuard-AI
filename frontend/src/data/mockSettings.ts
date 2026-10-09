import type { SystemSettings } from '../types/settings';

export const defaultSettings: SystemSettings = {
  monitoringEnabled: true,
  monitorIntervalSec: 5,
  entropyThreshold: 7.5,
  autoBackupEnabled: true,
  snapshotIntervalHours: 4,
  recoveryVerificationEnabled: true,
  emailAlerts: true,
  emailAddress: 'secops@ransomguard.internal',
  desktopNotifications: true,
  alertSensitivity: 'high',
};
