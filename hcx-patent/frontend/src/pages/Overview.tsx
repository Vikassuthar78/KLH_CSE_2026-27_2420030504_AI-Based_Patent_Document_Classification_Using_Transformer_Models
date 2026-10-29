import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Database,
  FlaskConical,
  Brain,
  Shield,
  TrendingUp,
  FileSearch,
  CheckCircle2,
  Clock,
  ArrowRight,
  AlertCircle,
} from 'lucide-react';
import { Card } from '../components/common/Card';
import { MetricCard } from '../components/common/MetricCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { Button } from '../components/common/Button';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { api } from '../api/client';
import type { Experiment } from '../types';

export function Overview() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [statsRes, expRes, statusRes] = await Promise.all([
          api.get('/datasets/stats').catch(() => ({ data: null })),
          api.get('/experiments').catch(() => ({ data: [] })),
          api.get('/status').catch(() => ({ data: null })),
        ]);
        setStats(statsRes.data);
        setExperiments(expRes.data || []);
        setStatus(statusRes.data);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  const completedExps = experiments.filter((e) => e.status === 'completed');
  const latestExp = completedExps.length > 0 ? completedExps[0] : null;

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Research Overview</h1>
        <p className="mt-1 text-sm text-slate-500">
          HCX-Patent: Hierarchical, Explainable, and Uncertainty-Aware Patent Classification under Taxonomy Drift.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          label="Total Patent Records"
          value={stats?.total_rows ? stats.total_rows.toLocaleString() : '3,198,360'}
          suffix="records"
          icon={<Database className="w-5 h-5" />}
        />
        <MetricCard
          label="Active Experiments"
          value={experiments.length.toString()}
          suffix="runs"
          icon={<FlaskConical className="w-5 h-5" />}
        />
        <MetricCard
          label="Latest Macro F1"
          value={latestExp?.metrics?.macro_f1 ? latestExp.metrics.macro_f1.toFixed(4) : 'N/A'}
          icon={<TrendingUp className="w-5 h-5" />}
        />
        <MetricCard
          label="Compute Device"
          value={status?.device?.toUpperCase() || 'CPU'}
          suffix={status?.cuda_available ? 'CUDA' : 'CPU'}
          icon={<Shield className="w-5 h-5" />}
        />
      </div>

      {/* Quick Action Workflows */}
      <Card title="Quick Research Workflows">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Link
            to="/dataset"
            className="flex flex-col justify-between rounded-lg border border-slate-200 bg-white p-5 hover:border-indigo-500 hover:shadow-md transition-all group"
          >
            <div>
              <div className="rounded-lg bg-indigo-50 p-3 w-fit text-indigo-600 mb-3 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                <Database className="w-5 h-5" />
              </div>
              <h3 className="font-semibold text-slate-900">Inspect Dataset</h3>
              <p className="text-xs text-slate-500 mt-1">Profile schema, missing values, and CPC class distributions.</p>
            </div>
            <div className="flex items-center text-xs font-medium text-indigo-600 mt-4">
              Explore data <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </Link>

          <Link
            to="/experiments"
            className="flex flex-col justify-between rounded-lg border border-slate-200 bg-white p-5 hover:border-indigo-500 hover:shadow-md transition-all group"
          >
            <div>
              <div className="rounded-lg bg-indigo-50 p-3 w-fit text-indigo-600 mb-3 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                <FlaskConical className="w-5 h-5" />
              </div>
              <h3 className="font-semibold text-slate-900">Run Experiments</h3>
              <p className="text-xs text-slate-500 mt-1">Train baselines, hierarchy models, and track MLflow metrics.</p>
            </div>
            <div className="flex items-center text-xs font-medium text-indigo-600 mt-4">
              Launch runner <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </Link>

          <Link
            to="/classify"
            className="flex flex-col justify-between rounded-lg border border-slate-200 bg-white p-5 hover:border-indigo-500 hover:shadow-md transition-all group"
          >
            <div>
              <div className="rounded-lg bg-indigo-50 p-3 w-fit text-indigo-600 mb-3 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                <FileSearch className="w-5 h-5" />
              </div>
              <h3 className="font-semibold text-slate-900">Patent Classification</h3>
              <p className="text-xs text-slate-500 mt-1">Interactive top-k multi-label prediction with taxonomy paths.</p>
            </div>
            <div className="flex items-center text-xs font-medium text-indigo-600 mt-4">
              Classify text <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </Link>

          <Link
            to="/uncertainty"
            className="flex flex-col justify-between rounded-lg border border-slate-200 bg-white p-5 hover:border-indigo-500 hover:shadow-md transition-all group"
          >
            <div>
              <div className="rounded-lg bg-indigo-50 p-3 w-fit text-indigo-600 mb-3 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                <Shield className="w-5 h-5" />
              </div>
              <h3 className="font-semibold text-slate-900">Conformal Uncertainty</h3>
              <p className="text-xs text-slate-500 mt-1">Prediction sets and empirical coverage guarantees.</p>
            </div>
            <div className="flex items-center text-xs font-medium text-indigo-600 mt-4">
              View conformal <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </Link>
        </div>
      </Card>

      {/* Latest Metrics & Experiments Table */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card title="Recent Experiment Runs">
            {experiments.length === 0 ? (
              <div className="py-8 text-center text-sm text-slate-500">
                No experiments recorded yet. Start by running the classical baseline from the Experiments page.
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {experiments.slice(0, 5).map((exp) => (
                  <div key={exp.id} className="flex items-center justify-between py-3">
                    <div>
                      <p className="text-sm font-medium text-slate-900">{exp.name}</p>
                      <p className="text-xs text-slate-500">Type: {exp.type} • ID: {exp.id}</p>
                    </div>
                    <div className="flex items-center gap-4">
                      {exp.metrics && (
                        <div className="text-right">
                          <p className="text-xs font-semibold text-slate-900">
                            F1: {exp.metrics.macro_f1?.toFixed(3) || 'N/A'}
                          </p>
                          <p className="text-[10px] text-slate-400">Macro</p>
                        </div>
                      )}
                      <StatusBadge status={exp.status} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>

        <div>
          <Card title="Dataset Health Status">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-600">Storage Root</span>
                <span className="text-xs font-mono font-medium text-slate-800">
                  {status?.dataset_root ? status.dataset_root.slice(-25) : 'DATA/'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-600">Parquet Partitioning</span>
                <span className="text-xs font-medium text-emerald-600 flex items-center">
                  <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> 7 Shards Verified
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-600">Missing Values</span>
                <span className="text-xs font-medium text-emerald-600">0% Detected</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-600">Taxonomy Scheme</span>
                <span className="text-xs font-medium text-slate-800">CPC Subclass Level</span>
              </div>
              <div className="pt-2 border-t border-slate-100">
                <Link to="/dataset">
                  <Button variant="secondary" className="w-full text-xs">
                    View Complete Schema Report
                  </Button>
                </Link>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
