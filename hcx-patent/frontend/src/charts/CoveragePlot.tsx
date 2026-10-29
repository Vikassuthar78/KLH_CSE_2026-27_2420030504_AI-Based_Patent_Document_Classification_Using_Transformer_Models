import { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

interface CoveragePlotProps {
  coverageByClass: Record<string, number>;
  targetCoverage: number;
  title?: string;
}

export function CoveragePlot({ coverageByClass, targetCoverage, title }: CoveragePlotProps) {
  const chartData = useMemo(() => {
    return Object.entries(coverageByClass)
      .map(([cls, coverage]) => ({
        class: cls,
        coverage: +(coverage * 100).toFixed(1),
      }))
      .sort((a, b) => b.coverage - a.coverage);
  }, [coverageByClass]);

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-sm text-slate-400">
        No coverage data available
      </div>
    );
  }

  return (
    <div>
      {title && <h4 className="text-sm font-medium text-slate-700 mb-4">{title}</h4>}
      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={chartData} margin={{ left: 10, right: 10, top: 5, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
          <XAxis dataKey="class" tick={{ fontSize: 10 }} stroke="#94a3b8" />
          <YAxis
            tick={{ fontSize: 12 }}
            stroke="#94a3b8"
            domain={[0, 100]}
            label={{ value: 'Coverage (%)', angle: -90, position: 'insideLeft', fontSize: 12, fill: '#64748b' }}
          />
          <Tooltip
            contentStyle={{
              background: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              fontSize: '13px',
            }}
            formatter={(value: number) => [`${value}%`, 'Coverage']}
          />
          <ReferenceLine
            y={targetCoverage * 100}
            stroke="#dc2626"
            strokeDasharray="5 5"
            label={{
              value: `Target: ${(targetCoverage * 100).toFixed(0)}%`,
              fill: '#dc2626',
              fontSize: 11,
            }}
          />
          <Bar dataKey="coverage" fill="#4f46e5" radius={[4, 4, 0, 0]} maxBarSize={30} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
