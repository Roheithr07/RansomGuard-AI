export interface AIAnalysisMetric {
  overallScore: number;
  confidence: number;
  riskLevel: 'low' | 'moderate' | 'high' | 'critical';
}

export interface BehaviorRates {
  modificationRatePerMin: number;
  renameRatePerMin: number;
  deleteRatePerMin: number;
  operationFreqPerSec: number;
  entropyScore: number;
}

export interface ModelInfo {
  id: string;
  name: string;
  version: string;
  type: 'supervised' | 'unsupervised' | 'heuristic';
  lastTrained: string;
  accuracyPercent: number;
  status: 'active' | 'training' | 'idle';
}

export interface AITimelinePoint {
  time: string;
  anomalyScore: number;
  baselineScore: number;
}
