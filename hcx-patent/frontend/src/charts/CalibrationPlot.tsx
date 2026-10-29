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
  ReferenceLine,
} from 'recharts';

interface CalibrationPlotProps {
  bins: { predicted: number; actual: number; count: number }[];
  title?: string;
}

export function CalibrationPlot({ bins, title }: CalibrationPlotProps) {
  const chartData = useMemo(() => {
    return bins.map((bin) => ({
      predicted: +(bin.predicted * 100).toFixed(1),
      actual: +(bin.actual * 100).toFixed(1),
      count: bin.count,
    }));
  }, [bins]);

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-sm text-slate-400">
        No calibration data available
      </div>
    );
  }

  const perfectData = [
    { predicted: 0, perfect: 0 },
    { predicted: 100, perfect: 100 },
  ];

  return (
    <div>
      {title && <h4 className="text-sm font-medium text-slate-700 mb-4">{title}</h4>}
      <ResponsiveContainer width="100%" height={350}>
        <LineChart margin={{ left: 10, right: 20, top: 5, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis
            type="number"
            dataKey="predicted"
            domain={[0, 100]}
            tick={{ fontSize: 12 }}
            stroke="#94a3b8"
            label={{ value: 'Predicted Confidence (%)', position: 'bottom', fontSize: 12, fill: '#64748b' }}
          />
          <YAxis
            type="number"
            domain={[0, 100]}
            tick={{ fontSize: 12 }}
            stroke="#94a3b8"
            label={{ value: 'Actual Accuracy (%)', angle: -90, position: 'insideLeft', fontSize: 12, fill: '#64748b' }}
          />
          <Tooltip
            contentStyle={{
              background: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              fontSize: '13px',
            }}
          />
          <Legend wrapperStyle={{ fontSize: '12px' }} />
          <Line
            data={perfectData}
            type="linear"
            dataKey="perfect"
            stroke="#94a3b8"
            strokeDasharray="5 5"
            dot={false}
            name="Perfect Calibration"
          />
          <Line
            data={chartData}
            type="monotone"
            dataKey="actual"
            stroke="#4f46e5"
            strokeWidth={2}
            dot={{ fill: '#4f46e5', r: 4 }}
            name="Model Calibration"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
