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

interface FeatureImportanceProps {
  features: Record<string, number>;
  maxItems?: number;
  title?: string;
}

export function FeatureImportance({ features, maxItems = 15, title }: FeatureImportanceProps) {
  const chartData = useMemo(() => {
    return Object.entries(features)
      .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
      .slice(0, maxItems)
      .map(([feature, importance]) => ({
        feature: feature.length > 20 ? feature.slice(0, 20) + '…' : feature,
        importance: +importance.toFixed(4),
        fullFeature: feature,
      }));
  }, [features, maxItems]);

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-sm text-slate-400">
        No feature importance data available
      </div>
    );
  }

  return (
    <div>
      {title && <h4 className="text-sm font-medium text-slate-700 mb-4">{title}</h4>}
      <ResponsiveContainer width="100%" height={Math.max(300, chartData.length * 28)}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 100, right: 20, top: 5, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
          <XAxis type="number" tick={{ fontSize: 12 }} stroke="#94a3b8" />
          <YAxis
            type="category"
            dataKey="feature"
            tick={{ fontSize: 11 }}
            stroke="#94a3b8"
            width={95}
          />
          <Tooltip
            contentStyle={{
              background: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              fontSize: '13px',
            }}
            formatter={(value: number, _: any, props: any) => [
              value.toFixed(4),
              props.payload.fullFeature,
            ]}
          />
          <Bar dataKey="importance" fill="#059669" radius={[0, 4, 4, 0]} maxBarSize={20} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
