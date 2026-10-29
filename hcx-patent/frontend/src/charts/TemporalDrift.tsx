import { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface TemporalDriftProps {
  performanceByYear: Record<string, Record<string, number>>;
  title?: string;
}

const METRIC_COLORS: Record<string, string> = {
  macro_f1: '#4f46e5',
  micro_f1: '#7c3aed',
  accuracy: '#2563eb',
  precision: '#0891b2',
  recall: '#059669',
};

const DEFAULT_COLORS = ['#4f46e5', '#7c3aed', '#2563eb', '#0891b2', '#059669'];

export function TemporalDrift({ performanceByYear, title }: TemporalDriftProps) {
  const { chartData, metricKeys } = useMemo(() => {
    const entries = Object.entries(performanceByYear).sort((a, b) => a[0].localeCompare(b[0]));
    if (entries.length === 0) return { chartData: [], metricKeys: [] };

    const allMetrics = new Set<string>();
    entries.forEach(([, metrics]) => Object.keys(metrics).forEach((k) => allMetrics.add(k)));
    const metricKeys = Array.from(allMetrics);

    const chartData = entries.map(([year, metrics]) => ({
      year,
      ...Object.fromEntries(
        Object.entries(metrics).map(([k, v]) => [k, +(v * 100).toFixed(1)])
      ),
    }));

    return { chartData, metricKeys };
  }, [performanceByYear]);

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-sm text-slate-400">
        No temporal data available
      </div>
    );
  }

  return (
    <div>
      {title && <h4 className="text-sm font-medium text-slate-700 mb-4">{title}</h4>}
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={chartData} margin={{ left: 10, right: 20, top: 5, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="year" tick={{ fontSize: 12 }} stroke="#94a3b8" />
          <YAxis
            tick={{ fontSize: 12 }}
            stroke="#94a3b8"
            domain={[0, 100]}
            label={{ value: 'Score (%)', angle: -90, position: 'insideLeft', fontSize: 12, fill: '#64748b' }}
          />
          <Tooltip
            contentStyle={{
              background: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              fontSize: '13px',
            }}
            formatter={(value: number) => [`${value}%`, '']}
          />
          <Legend wrapperStyle={{ fontSize: '12px' }} />
          {metricKeys.map((key, i) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              stroke={METRIC_COLORS[key] || DEFAULT_COLORS[i % DEFAULT_COLORS.length]}
              strokeWidth={2}
              dot={{ r: 3 }}
              name={key.replace(/_/g, ' ')}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
