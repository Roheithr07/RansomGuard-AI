import type { FC, ReactNode } from 'react';

interface PageContainerProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
}

export const PageContainer: FC<PageContainerProps> = ({ title, subtitle, children }) => {
  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-[1600px] w-full mx-auto box-sizing-border font-sans">
      <div>
        <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight">{title}</h2>
        {subtitle && <p className="text-xs sm:text-sm text-slate-500 mt-1 font-medium">{subtitle}</p>}
      </div>
      <div>{children}</div>
    </div>
  );
};
