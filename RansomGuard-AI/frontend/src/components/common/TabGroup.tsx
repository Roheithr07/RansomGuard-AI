import type { FC } from 'react';

export interface TabItem {
  id: string;
  label: string;
  count?: number;
}

interface TabGroupProps {
  tabs: TabItem[];
  activeTab: string;
  onChange: (tabId: string) => void;
  className?: string;
}

export const TabGroup: FC<TabGroupProps> = ({ tabs, activeTab, onChange, className = '' }) => {
  return (
    <div className={`flex items-center gap-1.5 p-1 bg-white/50 backdrop-blur-md rounded-2xl border border-white/80 shadow-2xs ${className}`}>
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all duration-200 cursor-pointer flex items-center gap-2 ${
              isActive
                ? 'bg-white text-[#006FA6] shadow-md border border-cyan-500/25'
                : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
            }`}
          >
            <span>{tab.label}</span>
            {tab.count !== undefined && (
              <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${isActive ? 'bg-[#00ABE4]/15 text-[#006FA6]' : 'bg-slate-200 text-slate-700'}`}>
                {tab.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
};
