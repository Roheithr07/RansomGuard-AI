import type { AIAnalysisMetric, BehaviorRates, ModelInfo, AITimelinePoint } from '../types/ai';

export const mockAIMetrics: AIAnalysisMetric = {
  overallScore: 0.04,
  confidence: 99.4,
  riskLevel: 'low',
};

export const mockBehaviorRates: BehaviorRates = {
  modificationRatePerMin: 12,
  renameRatePerMin: 2,
  deleteRatePerMin: 0,
  operationFreqPerSec: 4.2,
  entropyScore: 1.18,
};

export const mockModels: ModelInfo[] = [
  {
    id: 'mdl-1',
    name: 'XGBoost Supervised Classifier',
    version: 'v2.4.0',
    type: 'supervised',
    lastTrained: '2026-09-14 02:00:00',
    accuracyPercent: 99.6,
    status: 'active',
  },
  {
    id: 'mdl-2',
    name: 'Isolation Forest Anomaly Detector',
    version: 'v1.8.2',
    type: 'unsupervised',
    lastTrained: '2026-09-15 00:00:00',
    accuracyPercent: 98.9,
    status: 'active',
  },
  {
    id: 'mdl-3',
    name: 'Entropy & Rapid Modification Rule Engine',
    version: 'v3.1.0',
    type: 'heuristic',
    lastTrained: 'System Embedded',
    accuracyPercent: 99.9,
    status: 'active',
  },
];

export const mockAITimeline: AITimelinePoint[] = [
  { time: '00:00', anomalyScore: 0.02, baselineScore: 0.05 },
  { time: '04:00', anomalyScore: 0.01, baselineScore: 0.05 },
  { time: '08:00', anomalyScore: 0.04, baselineScore: 0.05 },
  { time: '10:42', anomalyScore: 0.94, baselineScore: 0.05 },
  { time: '12:00', anomalyScore: 0.08, baselineScore: 0.05 },
  { time: '16:00', anomalyScore: 0.04, baselineScore: 0.05 },
];
