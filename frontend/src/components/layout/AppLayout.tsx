import type { FC, ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

interface AppLayoutProps {
  children: ReactNode;
}

export const AppLayout: FC<AppLayoutProps> = ({ children }) => {
  return (
    <div className="relative flex min-h-screen w-full bg-gradient-to-br from-[#e9f1fa] via-[#f5f9ff] to-[#dceeff] text-slate-900 overflow-x-hidden font-sans">
      {/* Background Animated Liquid Glass Blobs */}
      <div className="liquid-blob-1" />
      <div className="liquid-blob-2" />
      <div className="liquid-blob-3" />

      {/* Main Layout Container */}
      <Sidebar />
      <div className="relative z-10 flex-1 flex flex-col min-w-0 w-full overflow-x-hidden">
        <Header />
        <main className="flex-1 w-full overflow-x-hidden">
          {children}
        </main>
      </div>
    </div>
  );
};
