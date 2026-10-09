import type { FC } from 'react';

interface StatusIndicatorProps {
  status?: 'active' | 'warning' | 'critical' | 'info' | 'paused';
  label?: string;
  pulse?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusIndicator: FC<StatusIndicatorProps> = ({
  status = 'active',
  label,
  pulse = true,
  size = 'md',
}) => {
  const dotSizes = {
    sm: 'w-2 h-2',
    md: 'w-2.5 h-2.5',
    lg: 'w-3 h-3',
  };

  const colors = {
    active: 'bg-emerald-400 text-emerald-400',
    warning: 'bg-amber-400 text-amber-400',
    critical: 'bg-red-500 text-red-400',
    info: 'bg-cyan-400 text-cyan-400',
    paused: 'bg-slate-500 text-slate-400',
  };

  return (
    <div className="inline-flex items-center gap-2">
      <span className="relative flex">
        {pulse && status === 'active' && (
          <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${colors[status].split(' ')[0]}`} />
        )}
        <span className={`relative inline-flex rounded-full ${dotSizes[size]} ${colors[status].split(' ')[0]}`} />
      </span>
      {label && <span className={`text-xs font-semibold ${colors[status].split(' ')[1]}`}>{label}</span>}
    </div>
  );
};
