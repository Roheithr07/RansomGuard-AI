import type { FC } from 'react';

interface ToggleSwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
}

export const ToggleSwitch: FC<ToggleSwitchProps> = ({ checked, onChange, label }) => {
  return (
    <label className="flex items-center gap-3 cursor-pointer select-none">
      <div
        onClick={() => onChange(!checked)}
        className={`w-11 h-6 flex items-center rounded-full p-1 transition-all duration-300 shadow-inner ${
          checked ? 'bg-gradient-to-r from-[#00ABE4] to-[#3B82F6] justify-end' : 'bg-slate-300/80 justify-start'
        }`}
      >
        <div className="w-4 h-4 bg-white rounded-full shadow-md transition-all transform"></div>
      </div>
      {label && <span className="text-xs font-semibold text-slate-700">{label}</span>}
    </label>
  );
};
