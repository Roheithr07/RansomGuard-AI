import type { FC } from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import type { AITimelinePoint } from '../../types/ai';

interface AITimelineChartProps {
  data: AITimelinePoint[];
}

export const AITimelineChart: FC<AITimelineChartProps> = ({ data }) => {
  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <XAxis dataKey="time" stroke="#94a3b8" tick={{ fontSize: 11 }} />
          <YAxis stroke="#94a3b8" domain={[0, 1]} tick={{ fontSize: 11 }} />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              borderColor: 'rgba(255, 255, 255, 0.9)',
              color: '#0f172a',
              borderRadius: '16px',
              boxShadow: '0 10px 25px -5px rgba(0, 171, 228, 0.15)',
              fontSize: '12px',
              fontWeight: 600,
            }}
          />
          <Legend wrapperStyle={{ fontSize: '11px', color: '#475569', fontWeight: 600 }} />
          <Line type="monotone" dataKey="anomalyScore" name="Anomaly Risk Score" stroke="#EF4444" strokeWidth={2.5} dot={{ r: 4 }} />
          <Line type="monotone" dataKey="baselineScore" name="Safety Baseline" stroke="#10B981" strokeWidth={2.5} strokeDasharray="4 4" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
