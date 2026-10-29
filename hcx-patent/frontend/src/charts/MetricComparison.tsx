import { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface MetricComparisonProps {
  data: Record<string, Record<string, number>>;
  title?: string;
}

const METRIC_COLORS: Record<string, string> = {
  'macro_f1': '#4f46e5',
  'micro_f1': '#7c3aed',
  'accuracy': '#2563eb',
  'precision': '#0891b2',
  'recall': '#059669',
  'hamming_loss': '#d97706',
};

const DEFAULT_COLORS = ['#4f46e5', '#7c3aed', '#2563eb', '#0891b2', '#059669', '#d97706'];

export function MetricComparison({ data, title }: MetricComparisonProps) {
  const { chartData, metricKeys } = useMemo(() => {
    const entries = Object.entries(data);
    if (entries.length === 0) return { chartData: [], metricKeys: [] };

    const allMetrics = new Set<string>();
    entries.forEach(([, metrics]) => Object.keys(metrics).forEach((k) => allMetrics.add(k)));
    const metricKeys = Array.from(allMetrics);

    const chartData = entries.map(([name, metrics]) => ({
      name,
      ...metrics,
    }));

    return { chartData, metricKeys };
  }, [data]);

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-sm text-slate-400">
        No comparison data available
      </div>
    );
  }

  return (
    <div>
      {title && <h4 className="text-sm font-medium text-slate-700 mb-4">{title}</h4>}
      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={chartData} margin={{ left: 10, right: 10, top: 5, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
          <XAxis dataKey="name" tick={{ fontSize: 11 }} stroke="#94a3b8" />
          <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" domain={[0, 1]} />
          <Tooltip
            contentStyle={{
              background: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              fontSize: '13px',
            }}
            formatter={(value: number) => [value.toFixed(4), '']}
          />
          <Legend wrapperStyle={{ fontSize: '12px' }} />
          {metricKeys.map((key, i) => (
            <Bar
              key={key}
              dataKey={key}
              fill={METRIC_COLORS[key] || DEFAULT_COLORS[i % DEFAULT_COLORS.length]}
              radius={[4, 4, 0, 0]}
              maxBarSize={30}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
