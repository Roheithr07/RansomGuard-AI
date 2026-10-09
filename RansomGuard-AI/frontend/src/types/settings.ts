export interface SystemSettings {
  monitoringEnabled: boolean;
  monitorIntervalSec: number;
  entropyThreshold: number;
  autoBackupEnabled: boolean;
  snapshotIntervalHours: number;
  recoveryVerificationEnabled: boolean;
  emailAlerts: boolean;
  emailAddress: string;
  desktopNotifications: boolean;
  alertSensitivity: 'low' | 'balanced' | 'high';
}
