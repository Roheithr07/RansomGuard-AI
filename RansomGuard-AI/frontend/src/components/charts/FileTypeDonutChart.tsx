import type { FC } from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
import type { FileTypeDistribution } from '../../types/storage';

interface FileTypeDonutChartProps {
  data: FileTypeDistribution[];
}

export const FileTypeDonutChart: FC<FileTypeDonutChartProps> = ({ data }) => {
  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={85}
            paddingAngle={4}
            dataKey="bytes"
            nameKey="name"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} stroke="rgba(255,255,255,0.8)" strokeWidth={2} />
            ))}
          </Pie>
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
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
