import type { ReactNode } from 'react';

export interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (item: T) => string;
  emptyMessage?: string;
  rowClassName?: (item: T) => string;
}

export function DataTable<T>({
  columns,
  data,
  keyExtractor,
  emptyMessage = 'No data available',
  rowClassName,
}: DataTableProps<T>) {
  return (
    <div className="overflow-x-auto w-full rounded-2xl border border-white/80 shadow-2xs bg-white/30 backdrop-blur-md">
      <table className="w-full text-left text-xs border-collapse min-w-full">
        <thead>
          <tr className="border-b border-slate-200/80 text-[11px] font-bold text-slate-500 uppercase tracking-wider bg-white/40">
            {columns.map((col) => (
              <th key={col.key} className={`py-3 px-4 ${col.className || ''}`}>
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200/60">
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="py-8 text-center text-xs text-slate-500 font-medium">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((item) => (
              <tr
                key={keyExtractor(item)}
                className={`transition-colors duration-150 hover:bg-white/80 ${
                  rowClassName ? rowClassName(item) : ''
                }`}
              >
                {columns.map((col) => (
                  <td key={col.key} className={`py-3 px-4 text-xs text-slate-800 ${col.className || ''}`}>
                    {col.render ? col.render(item) : (item as any)[col.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
