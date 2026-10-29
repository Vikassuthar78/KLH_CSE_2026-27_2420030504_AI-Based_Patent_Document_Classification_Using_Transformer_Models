import { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface ClassDistributionProps {
  data: Record<string, number>;
  maxItems?: number;
  title?: string;
}

const COLORS = [
  '#4f46e5', '#7c3aed', '#2563eb', '#0891b2', '#059669',
  '#d97706', '#dc2626', '#e11d48', '#9333ea', '#0d9488',
  '#6366f1', '#8b5cf6', '#3b82f6', '#06b6d4', '#10b981',
];

export function ClassDistribution({ data, maxItems = 20, title }: ClassDistributionProps) {
  const chartData = useMemo(() => {
    return Object.entries(data)
      .sort((a, b) => b[1] - a[1])
      .slice(0, maxItems)
      .map(([code, count]) => ({ code, count }));
  }, [data, maxItems]);

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-sm text-slate-400">
        No class distribution data available
      </div>
    );
  }

  return (
    <div>
      {title && <h4 className="text-sm font-medium text-slate-700 mb-4">{title}</h4>}
      <ResponsiveContainer width="100%" height={Math.max(300, chartData.length * 28)}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 60, right: 20, top: 5, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
          <XAxis type="number" tick={{ fontSize: 12 }} stroke="#94a3b8" />
          <YAxis
            type="category"
            dataKey="code"
            tick={{ fontSize: 11 }}
            stroke="#94a3b8"
            width={55}
          />
          <Tooltip
            contentStyle={{
              background: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              fontSize: '13px',
            }}
            formatter={(value: number) => [value.toLocaleString(), 'Count']}
          />
          <Bar dataKey="count" radius={[0, 4, 4, 0]} maxBarSize={20}>
            {chartData.map((_, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
