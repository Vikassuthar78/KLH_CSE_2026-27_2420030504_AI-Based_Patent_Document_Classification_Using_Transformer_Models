import { useMemo } from 'react';
import { Tooltip as RechartsTooltip } from 'recharts';

interface ConfusionMatrixProps {
  matrix: number[][];
  labels: string[];
  title?: string;
}

export function ConfusionMatrix({ matrix, labels, title }: ConfusionMatrixProps) {
  const { maxVal, normalizedMatrix } = useMemo(() => {
    const maxVal = Math.max(...matrix.flat(), 1);
    const normalizedMatrix = matrix.map((row) =>
      row.map((val) => val / maxVal)
    );
    return { maxVal, normalizedMatrix };
  }, [matrix]);

  if (matrix.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-sm text-slate-400">
        No confusion matrix data available
      </div>
    );
  }

  const cellSize = Math.min(40, Math.max(24, 500 / labels.length));

  return (
    <div>
      {title && <h4 className="text-sm font-medium text-slate-700 mb-4">{title}</h4>}
      <div className="overflow-auto">
        <div className="inline-block">
          <div className="flex">
            <div style={{ width: cellSize + 20 }} />
            {labels.map((label) => (
              <div
                key={`h-${label}`}
                className="text-[10px] text-slate-500 font-medium text-center overflow-hidden"
                style={{ width: cellSize, minWidth: cellSize }}
                title={label}
              >
                {label.slice(0, 4)}
              </div>
            ))}
          </div>
          {matrix.map((row, i) => (
            <div key={i} className="flex items-center">
              <div
                className="text-[10px] text-slate-500 font-medium text-right pr-2 overflow-hidden"
                style={{ width: cellSize + 20, minWidth: cellSize + 20 }}
                title={labels[i]}
              >
                {labels[i]?.slice(0, 5)}
              </div>
              {row.map((val, j) => {
                const intensity = normalizedMatrix[i][j];
                const bgColor =
                  i === j
                    ? `rgba(79, 70, 229, ${0.1 + intensity * 0.8})`
                    : `rgba(239, 68, 68, ${intensity * 0.6})`;
                const textColor = intensity > 0.5 ? 'white' : '#334155';
                return (
                  <div
                    key={j}
                    className="flex items-center justify-center border border-white/50 text-[10px] font-medium transition-colors hover:ring-2 hover:ring-indigo-400 cursor-default"
                    style={{
                      width: cellSize,
                      height: cellSize,
                      minWidth: cellSize,
                      backgroundColor: bgColor,
                      color: textColor,
                    }}
                    title={`True: ${labels[i]}, Pred: ${labels[j]}, Count: ${val}`}
                  >
                    {val}
                  </div>
                );
              })}
            </div>
          ))}
          <div className="flex items-center gap-2 mt-3 text-[10px] text-slate-500">
            <span>Predicted →</span>
            <span className="ml-auto">True ↓</span>
          </div>
        </div>
      </div>
    </div>
  );
}
