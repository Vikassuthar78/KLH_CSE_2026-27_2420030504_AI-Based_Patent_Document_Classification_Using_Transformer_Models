import React from 'react';
import clsx from 'clsx';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface MetricCardProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  change?: number;
  suffix?: string;
  className?: string;
  variant?: 'default' | 'primary' | 'success' | 'warning';
}

const bgClasses = {
  default: 'bg-slate-50',
  primary: 'bg-indigo-50',
  success: 'bg-emerald-50',
  warning: 'bg-amber-50',
};

const iconBgClasses = {
  default: 'bg-slate-200 text-slate-600',
  primary: 'bg-indigo-100 text-indigo-600',
  success: 'bg-emerald-100 text-emerald-600',
  warning: 'bg-amber-100 text-amber-600',
};

export function MetricCard({
  label,
  value,
  icon,
  change,
  suffix,
  className,
  variant = 'default',
}: MetricCardProps) {
  return (
    <div className={clsx('bg-white border border-slate-200 rounded-lg p-5 shadow-sm', className)}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{label}</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">
            {typeof value === 'number' ? value.toLocaleString() : value}
            {suffix && <span className="text-sm font-normal text-slate-400 ml-1">{suffix}</span>}
          </p>
        </div>
        {icon && (
          <div className={clsx('w-10 h-10 rounded-lg flex items-center justify-center', iconBgClasses[variant])}>
            {icon}
          </div>
        )}
      </div>
      {change !== undefined && (
        <div className="flex items-center gap-1 mt-3">
          {change > 0 ? (
            <TrendingUp className="w-3.5 h-3.5 text-emerald-500" />
          ) : change < 0 ? (
            <TrendingDown className="w-3.5 h-3.5 text-red-500" />
          ) : (
            <Minus className="w-3.5 h-3.5 text-slate-400" />
          )}
          <span
            className={clsx(
              'text-xs font-medium',
              change > 0 ? 'text-emerald-600' : change < 0 ? 'text-red-600' : 'text-slate-400'
            )}
          >
            {change > 0 ? '+' : ''}
            {change.toFixed(1)}%
          </span>
        </div>
      )}
    </div>
  );
}
