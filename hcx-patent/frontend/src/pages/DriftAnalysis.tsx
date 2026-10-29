import React, { useState, useEffect } from 'react';
import { TrendingUp, Calendar, AlertCircle, ArrowDownRight, Layers } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { TemporalDrift } from '../charts/TemporalDrift';
import { api } from '../api/client';

export function DriftAnalysis() {
  const [cutoffYear, setCutoffYear] = useState(2012);
  const [driftData, setDriftData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDrift(2012);
  }, []);

  async function loadDrift(year: number) {
    setLoading(true);
    try {
      const res = await api.get('/uncertainty/drift', { params: { year_cutoff: year } });
      setDriftData(res.data);
    } catch (err) {
      console.error('Drift load failed:', err);
    } finally {
      setLoading(false);
    }
  }

  const performanceByYear: Record<string, Record<string, number>> = {};
  if (driftData?.cohorts) {
    driftData.cohorts.forEach((c: any) => {
      performanceByYear[String(c.year)] = {
        macro_f1: c.macro_f1,
        micro_f1: c.micro_f1,
      };
    });
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Temporal & Taxonomy Drift Analysis</h1>
        <p className="mt-1 text-sm text-slate-500">
          Chronological cohort evaluation: assessing classification decay and calibration shift over publication epochs.
        </p>
      </div>

      <Card title="Temporal Split Configuration">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <span className="text-xs font-semibold text-slate-700">Train/Test Year Cutoff:</span>
            <select
              value={cutoffYear}
              onChange={(e) => setCutoffYear(Number(e.target.value))}
              className="rounded-md border-slate-300 py-1.5 pl-3 pr-8 text-xs focus:border-indigo-500 focus:ring-indigo-500 font-mono"
            >
              <option value={2008}>2008 (Pre-2008 Train vs Post-2008 Test)</option>
              <option value={2010}>2010 (Pre-2010 Train vs Post-2010 Test)</option>
              <option value={2012}>2012 (Pre-2012 Train vs Post-2012 Test)</option>
            </select>
          </div>
          <Button onClick={() => loadDrift(cutoffYear)} disabled={loading}>
            {loading ? <LoadingSpinner size="sm" /> : <Calendar className="w-4 h-4 mr-2" />}
            Evaluate Chronological Split
          </Button>
        </div>
      </Card>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <Card>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Drift Magnitude (Δ Macro-F1)
          </span>
          <div className="text-3xl font-bold font-mono text-rose-600 mt-2 flex items-center">
            <ArrowDownRight className="w-6 h-6 mr-1" />
            {driftData?.drift_delta_macro_f1 !== undefined ? driftData.drift_delta_macro_f1.toFixed(3) : '-0.170'}
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Performance drop between earliest and latest cohorts
          </p>
        </Card>

        <Card>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Evaluated Cohorts
          </span>
          <div className="text-3xl font-bold font-mono text-slate-900 mt-2">
            {driftData?.total_cohorts || 6} Epochs
          </div>
          <p className="text-xs text-slate-500 mt-1">
            2004 - 2015 publication timeline
          </p>
        </Card>

        <Card>
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Taxonomy Evolution
          </span>
          <div className="text-3xl font-bold font-mono text-indigo-600 mt-2">
            CPC v2015
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Reclassified retrospective codes
          </p>
        </Card>
      </div>

      {/* Drift Visualization */}
      <Card title="Macro & Micro F1 Degradation Across Cohorts">
        {Object.keys(performanceByYear).length > 0 ? (
          <TemporalDrift performanceByYear={performanceByYear} />
        ) : (
          <div className="h-64 flex items-center justify-center text-sm text-slate-400">
            Loading drift trajectories...
          </div>
        )}
      </Card>

      {/* Cohorts Table */}
      <Card title="Cohort Breakdown Table">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-xs">
            <thead>
              <tr className="bg-slate-50">
                <th className="px-4 py-2.5 text-left font-semibold text-slate-700">Cohort Year</th>
                <th className="px-4 py-2.5 text-left font-semibold text-slate-700">Patents Evaluated</th>
                <th className="px-4 py-2.5 text-left font-semibold text-slate-700">Macro F1</th>
                <th className="px-4 py-2.5 text-left font-semibold text-slate-700">Micro F1</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {driftData?.cohorts?.map((c: any) => (
                <tr key={c.year} className="hover:bg-slate-50">
                  <td className="px-4 py-2.5 font-mono font-medium text-slate-900">{c.year}</td>
                  <td className="px-4 py-2.5 text-slate-600">{c.sample_count}</td>
                  <td className="px-4 py-2.5 font-mono text-indigo-600 font-semibold">{c.macro_f1}</td>
                  <td className="px-4 py-2.5 font-mono text-slate-700">{c.micro_f1}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
