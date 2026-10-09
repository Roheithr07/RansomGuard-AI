export interface ReportItem {
  id: string;
  title: string;
  generatedAt: string;
  type: 'threat' | 'storage' | 'compliance' | 'full_audit';
  fileSizeBytes: number;
  format: 'PDF' | 'CSV';
}

export interface SecurityStatSummary {
  totalIncidentsBlocked: number;
  avgResponseTimeMs: number;
  protectedStorageTB: number;
  systemUptimePercent: number;
}
