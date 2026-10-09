import type { FC, ReactNode } from 'react';

interface BadgeProps {
  children: ReactNode;
  variant?: 'info' | 'success' | 'warning' | 'danger';
}

export const Badge: FC<BadgeProps> = ({ children, variant = 'info' }) => {
  const styles = {
    info: 'bg-cyan-500/15 text-[#006FA6] border-cyan-500/30',
    success: 'bg-emerald-500/15 text-emerald-700 border-emerald-500/30',
    warning: 'bg-amber-500/15 text-amber-700 border-amber-500/30',
    danger: 'bg-red-500/15 text-red-600 border-red-500/30',
  };

  return (
    <span className={`px-2.5 py-0.5 text-[11px] font-bold rounded-full border shadow-2xs backdrop-blur-xs uppercase tracking-wider ${styles[variant]}`}>
      {children}
    </span>
  );
};
