import type { FC, ReactNode } from 'react';

interface GlassCardProps {
  children: ReactNode;
  className?: string;
}

export const GlassCard: FC<GlassCardProps> = ({ children, className = '' }) => {
  return <div className={`liquid-glass liquid-card ${className}`}>{children}</div>;
};
