import clsx from 'clsx';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
  className?: string;
}

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-8 h-8',
  lg: 'w-12 h-12',
};

export function LoadingSpinner({ size = 'md', message, className }: LoadingSpinnerProps) {
  return (
    <div className={clsx('flex flex-col items-center justify-center py-12 gap-3', className)}>
      <Loader2 className={clsx('animate-spin text-indigo-600', sizeClasses[size])} />
      {message && <p className="text-sm text-slate-500">{message}</p>}
    </div>
  );
}
