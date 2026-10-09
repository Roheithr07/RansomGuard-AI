import type { FC } from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';

const mockThreatData = [
  { time: '00:00', normal: 10, suspicious: 2, critical: 0 },
  { time: '04:00', normal: 15, suspicious: 1, critical: 0 },
  { time: '08:00', normal: 28, suspicious: 4, critical: 1 },
  { time: '12:00', normal: 42, suspicious: 8, critical: 2 },
  { time: '16:00', normal: 35, suspicious: 12, critical: 5 },
  { time: '20:00', normal: 20, suspicious: 3, critical: 1 },
];

export const ThreatChart: FC = () => {
  return (
    <div className="w-full h-56">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={mockThreatData}>
          <defs>
            <linearGradient id="colorNormal" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#00ABE4" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#00ABE4" stopOpacity={0.0} />
            </linearGradient>
            <linearGradient id="colorSuspicious" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#F59E0B" stopOpacity={0.0} />
            </linearGradient>
            <linearGradient id="colorCritical" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#EF4444" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#EF4444" stopOpacity={0.0} />
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
          <Area type="monotone" dataKey="normal" name="Normal Activity" stroke="#00ABE4" strokeWidth={2.5} fill="url(#colorNormal)" />
          <Area type="monotone" dataKey="suspicious" name="Suspicious" stroke="#F59E0B" strokeWidth={2.5} fill="url(#colorSuspicious)" />
          <Area type="monotone" dataKey="critical" name="Critical" stroke="#EF4444" strokeWidth={2.5} fill="url(#colorCritical)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
