import { Badge } from './Badge';

interface StatusBadgeProps {
  status: 'pending' | 'running' | 'completed' | 'failed' | string;
}

const statusConfig: Record<string, { variant: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info'; label: string }> = {
  pending: { variant: 'warning', label: 'Pending' },
  running: { variant: 'info', label: 'Running' },
  completed: { variant: 'success', label: 'Completed' },
  failed: { variant: 'danger', label: 'Failed' },
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const config = statusConfig[status] || { variant: 'default' as const, label: status };
  return (
    <Badge variant={config.variant} dot>
      {config.label}
    </Badge>
  );
}
