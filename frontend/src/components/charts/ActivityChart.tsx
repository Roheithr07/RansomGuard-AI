import type { FC } from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';

interface ActivityChartProps {
  data: Array<{ time: string; reads: number; writes: number }>;
}

export const ActivityChart: FC<ActivityChartProps> = ({ data }) => {
  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorReads" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#00ABE4" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#00ABE4" stopOpacity={0.0} />
            </linearGradient>
            <linearGradient id="colorWrites" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <XAxis dataKey="time" stroke="#94a3b8" tick={{ fontSize: 11 }} />
          <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />
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
          <Area type="monotone" dataKey="reads" stroke="#00ABE4" strokeWidth={2.5} fill="url(#colorReads)" />
          <Area type="monotone" dataKey="writes" stroke="#3B82F6" strokeWidth={2.5} fill="url(#colorWrites)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
