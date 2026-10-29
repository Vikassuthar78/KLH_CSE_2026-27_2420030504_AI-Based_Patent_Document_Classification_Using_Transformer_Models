import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';
import clsx from 'clsx';

interface Column<T> {
  key: string;
  header: string;
  render?: (row: T, index: number) => React.ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  totalRows?: number;
  page?: number;
  pageSize?: number;
  onPageChange?: (page: number) => void;
  loading?: boolean;
  emptyMessage?: string;
  rowKey?: (row: T, index: number) => string;
}

export function DataTable<T extends Record<string, any>>({
  columns,
  data,
  totalRows,
  page = 1,
  pageSize = 20,
  onPageChange,
  loading,
  emptyMessage = 'No data available',
  rowKey,
}: DataTableProps<T>) {
  const totalPages = totalRows ? Math.ceil(totalRows / pageSize) : 1;

  return (
    <div className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={clsx(
                    'px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider bg-slate-50/50',
                    col.className
                  )}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              <tr>
                <td colSpan={columns.length} className="px-4 py-12 text-center text-slate-400">
                  <div className="flex items-center justify-center gap-2">
                    <div className="w-4 h-4 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
                    Loading...
                  </div>
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-4 py-12 text-center text-slate-400">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              data.map((row, i) => (
                <tr
                  key={rowKey ? rowKey(row, i) : i}
                  className="data-row transition-colors"
                >
                  {columns.map((col) => (
                    <td key={col.key} className={clsx('px-4 py-3 text-slate-700', col.className)}>
                      {col.render ? col.render(row, i) : row[col.key]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {onPageChange && totalRows && totalRows > pageSize && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-slate-100">
          <p className="text-xs text-slate-500">
            Showing {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, totalRows)} of{' '}
            {totalRows.toLocaleString()} rows
          </p>
          <div className="flex items-center gap-1">
            <button
              className="p-1.5 rounded hover:bg-slate-100 text-slate-500 disabled:opacity-30"
              disabled={page <= 1}
              onClick={() => onPageChange(1)}
            >
              <ChevronsLeft className="w-4 h-4" />
            </button>
            <button
              className="p-1.5 rounded hover:bg-slate-100 text-slate-500 disabled:opacity-30"
              disabled={page <= 1}
              onClick={() => onPageChange(page - 1)}
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-3 py-1 text-xs font-medium text-slate-700">
              {page} / {totalPages}
            </span>
            <button
              className="p-1.5 rounded hover:bg-slate-100 text-slate-500 disabled:opacity-30"
              disabled={page >= totalPages}
              onClick={() => onPageChange(page + 1)}
            >
              <ChevronRight className="w-4 h-4" />
            </button>
            <button
              className="p-1.5 rounded hover:bg-slate-100 text-slate-500 disabled:opacity-30"
              disabled={page >= totalPages}
              onClick={() => onPageChange(totalPages)}
            >
              <ChevronsRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
