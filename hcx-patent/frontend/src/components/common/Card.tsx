import React from 'react';
import clsx from 'clsx';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  noPadding?: boolean;
}

export function Card({ children, className, title, subtitle, icon, action, noPadding }: CardProps) {
  return (
    <div
      className={clsx(
        'bg-white border border-slate-200 rounded-lg shadow-sm',
        className
      )}
    >
      {(title || action) && (
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <div className="flex items-center gap-3">
            {icon && (
              <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-indigo-50 text-indigo-600">
                {icon}
              </div>
            )}
            <div>
              {title && <h3 className="text-sm font-semibold text-slate-900">{title}</h3>}
              {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
            </div>
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className={clsx(!noPadding && 'p-6')}>{children}</div>
    </div>
  );
}
