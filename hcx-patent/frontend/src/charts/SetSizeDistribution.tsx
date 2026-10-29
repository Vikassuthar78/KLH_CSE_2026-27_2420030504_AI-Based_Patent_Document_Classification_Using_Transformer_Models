import { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface SetSizeDistributionProps {
  predictionSets: { set_size: number }[];
  title?: string;
}

export function SetSizeDistribution({ predictionSets, title }: SetSizeDistributionProps) {
  const chartData = useMemo(() => {
    const counts: Record<number, number> = {};
    predictionSets.forEach((ps) => {
      counts[ps.set_size] = (counts[ps.set_size] || 0) + 1;
    });
    return Object.entries(counts)
      .map(([size, count]) => ({ size: Number(size), count }))
      .sort((a, b) => a.size - b.size);
  }, [predictionSets]);

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-sm text-slate-400">
        No prediction set data available
      </div>
    );
  }

  return (
    <div>
      {title && <h4 className="text-sm font-medium text-slate-700 mb-4">{title}</h4>}
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{ left: 10, right: 10, top: 5, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
          <XAxis
            dataKey="size"
            tick={{ fontSize: 12 }}
            stroke="#94a3b8"
            label={{ value: 'Set Size', position: 'bottom', fontSize: 12, fill: '#64748b' }}
          />
          <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" />
          <Tooltip
            contentStyle={{
              background: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              fontSize: '13px',
            }}
            formatter={(value: number) => [value.toLocaleString(), 'Count']}
          />
          <Bar dataKey="count" fill="#7c3aed" radius={[4, 4, 0, 0]} maxBarSize={40} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
