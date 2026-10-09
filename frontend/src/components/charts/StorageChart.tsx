import type { FC } from 'react';

interface StorageChartProps {
  usedPercent: number;
}

export const StorageChart: FC<StorageChartProps> = ({ usedPercent }) => {
  return (
    <div className="w-full bg-slate-200/80 rounded-full h-3.5 overflow-hidden my-3 shadow-inner border border-white/60">
      <div
        className="bg-gradient-to-r from-[#00ABE4] to-[#3B82F6] h-full transition-all duration-500 rounded-full"
        style={{ width: `${usedPercent}%` }}
      />
    </div>
  );
};
