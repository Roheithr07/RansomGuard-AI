import type { FC } from 'react';

export const LoadingSpinner: FC = () => {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="w-8 h-8 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin"></div>
    </div>
  );
};
