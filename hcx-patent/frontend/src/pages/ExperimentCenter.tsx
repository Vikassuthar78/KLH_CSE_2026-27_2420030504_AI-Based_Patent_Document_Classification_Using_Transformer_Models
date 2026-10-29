import React, { useState, useEffect } from 'react';
import {
  FlaskConical,
  Play,
  Download,
  BarChart2,
  CheckCircle2,
  Clock,
  Layers,
  ArrowRight,
  FileText,
} from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { StatusBadge } from '../components/common/StatusBadge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { MetricComparison } from '../charts/MetricComparison';
import { api } from '../api/client';
import type { Experiment } from '../types';

export function ExperimentCenter() {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [selectedExp, setSelectedExp] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [jobProgress, setJobProgress] = useState<number | null>(null);

  // Form state
  const [name, setName] = useState('Classical TF-IDF Baseline');
  const [expType, setExpType] = useState('baseline');
  const [sampleSize, setSampleSize] = useState(5000);
  const [seed, setSeed] = useState(42);

  useEffect(() => {
    loadExperiments();
  }, []);

  async function loadExperiments() {
    try {
      const res = await api.get('/experiments');
      setExperiments(res.data || []);
      if (res.data && res.data.length > 0) {
        loadExperimentDetails(res.data[0].id);
      }
    } catch (err) {
      console.error('Failed to load experiments:', err);
    } finally {
      setLoading(false);
    }
  }

  async function loadExperimentDetails(id: string | number) {
    try {
      const res = await api.get(`/experiments/${id}`);
      setSelectedExp(res.data);
    } catch (err) {
      console.error('Failed to load experiment details:', err);
    }
  }

  async function handleLaunch() {
    setRunning(true);
    setJobProgress(0);
    try {
      // 1. Create experiment record
      const createRes = await api.post('/experiments/create', {
        name,
        type: expType,
        config: {
          sample_size: sampleSize,
          random_seed: seed,
          split_strategy: 'random',
        },
      });
      const expId = createRes.data.id;

      // 2. Launch execution
      const runRes = await api.post(`/experiments/${expId}/run`);
      const jobId = runRes.data.job_id;

      // 3. Poll job status
      const interval = setInterval(async () => {
        try {
          const jobRes = await api.get(`/experiments/jobs/${jobId}`);
          const job = jobRes.data;
          if (job.progress !== undefined) {
            setJobProgress(Math.round(job.progress * 100));
          }

          if (job.status === 'completed' || job.status === 'failed') {
            clearInterval(interval);
            setRunning(false);
            setJobProgress(null);
            await loadExperiments();
            await loadExperimentDetails(expId);
          }
        } catch (e) {
          clearInterval(interval);
          setRunning(false);
        }
      }, 1500);
    } catch (err) {
      console.error('Failed to launch experiment:', err);
      setRunning(false);
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Experiment Center</h1>
        <p className="mt-1 text-sm text-slate-500">
          Configure, train, evaluate, and track reproducible patent classification pipelines.
        </p>
      </div>

      {/* Launch Configuration Form */}
      <Card title="Launch New Experiment Pipeline">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-700">Experiment Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-1.5 text-xs focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700">Model Pipeline Architecture</label>
            <select
              value={expType}
              onChange={(e) => {
                setExpType(e.target.value);
                if (e.target.value === 'baseline') setName('Classical TF-IDF Baseline');
                else if (e.target.value === 'hierarchy') setName('Hierarchy-Aware Classifier');
                else if (e.target.value === 'transformer') setName('Transformer BERT Experiment');
              }}
              className="mt-1 w-full rounded-md border border-slate-300 py-1.5 pl-3 pr-8 text-xs focus:border-indigo-500 focus:ring-indigo-500"
            >
              <option value="baseline">TF-IDF + OneVsRest Logistic Regression</option>
              <option value="hierarchy">Hierarchy-Aware Consistency Model</option>
              <option value="transformer">Transformer BERT Model</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700">Dataset Sample Size</label>
            <select
              value={sampleSize}
              onChange={(e) => setSampleSize(Number(e.target.value))}
              className="mt-1 w-full rounded-md border border-slate-300 py-1.5 pl-3 pr-8 text-xs focus:border-indigo-500 focus:ring-indigo-500"
            >
              <option value={2000}>2,000 records (Rapid Dev)</option>
              <option value={5000}>5,000 records (Standard Dev)</option>
              <option value={10000}>10,000 records (Benchmark)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700">Random Seed</label>
            <input
              type="number"
              value={seed}
              onChange={(e) => setSeed(Number(e.target.value))}
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-1.5 text-xs font-mono focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
        </div>

        <div className="mt-5 flex items-center justify-between pt-4 border-t border-slate-100">
          {jobProgress !== null && (
            <div className="flex items-center gap-3 text-xs text-indigo-700 font-medium">
              <LoadingSpinner size="sm" />
              <span>Training in background: {jobProgress}% complete...</span>
            </div>
          )}
          <div className="ml-auto">
            <Button onClick={handleLaunch} disabled={running}>
              {running ? <LoadingSpinner size="sm" /> : <Play className="w-4 h-4 mr-2" />}
              Launch Pipeline
            </Button>
          </div>
        </div>
      </Card>

      {/* Experiments Master-Detail */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="space-y-4">
          <Card title={`All Recorded Runs (${experiments.length})`}>
            {experiments.length === 0 ? (
              <div className="py-12 text-center text-sm text-slate-400">
                No experiments recorded yet.
              </div>
            ) : (
              <div className="divide-y divide-slate-100 max-h-[500px] overflow-y-auto pr-1">
                {experiments.map((exp) => (
                  <div
                    key={exp.id}
                    onClick={() => loadExperimentDetails(exp.id)}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      selectedExp?.id === exp.id
                        ? 'bg-indigo-50 border border-indigo-200'
                        : 'hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-xs text-slate-900">{exp.name}</span>
                      <StatusBadge status={exp.status} />
                    </div>
                    <div className="flex items-center justify-between text-[11px] text-slate-500 mt-2">
                      <span className="capitalize">{exp.type}</span>
                      {exp.metrics && (
                        <span className="font-mono font-semibold text-indigo-600">
                          F1: {exp.metrics.macro_f1?.toFixed(3)}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>

        {/* Detail Panel */}
        <div className="lg:col-span-2 space-y-6">
          <Card title="Experiment Evaluation & Metrics">
            {selectedExp?.metrics ? (
              <div className="space-y-6">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="p-3 bg-slate-50 rounded-lg text-center">
                    <span className="text-[10px] text-slate-500 uppercase font-semibold">Macro F1</span>
                    <div className="text-xl font-bold font-mono text-indigo-600 mt-1">
                      {selectedExp.metrics.macro_f1?.toFixed(4)}
                    </div>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg text-center">
                    <span className="text-[10px] text-slate-500 uppercase font-semibold">Micro F1</span>
                    <div className="text-xl font-bold font-mono text-slate-800 mt-1">
                      {selectedExp.metrics.micro_f1?.toFixed(4)}
                    </div>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg text-center">
                    <span className="text-[10px] text-slate-500 uppercase font-semibold">Subset Acc</span>
                    <div className="text-xl font-bold font-mono text-slate-800 mt-1">
                      {selectedExp.metrics.accuracy?.toFixed(4)}
                    </div>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg text-center">
                    <span className="text-[10px] text-slate-500 uppercase font-semibold">Hamming Loss</span>
                    <div className="text-xl font-bold font-mono text-emerald-600 mt-1">
                      {selectedExp.metrics.hamming_loss?.toFixed(4)}
                    </div>
                  </div>
                </div>

                {/* Additional metrics */}
                <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-2">
                  <div className="flex justify-between">
                    <span className="text-slate-600">Macro Precision:</span>
                    <span className="font-mono font-semibold">{selectedExp.metrics.macro_precision?.toFixed(4)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Macro Recall:</span>
                    <span className="font-mono font-semibold">{selectedExp.metrics.macro_recall?.toFixed(4)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Training Duration:</span>
                    <span className="font-mono font-semibold">{selectedExp.metrics.training_time_seconds?.toFixed(1)} s</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Inference Latency:</span>
                    <span className="font-mono font-semibold">{selectedExp.metrics.inference_latency_ms?.toFixed(2)} ms/patent</span>
                  </div>
                </div>

                {/* Export Buttons */}
                {selectedExp.runs && selectedExp.runs.length > 0 && (
                  <div className="flex gap-3 pt-2">
                    <a
                      href={`http://localhost:8000/api/v1/exports/${selectedExp.runs[0].run_id}/csv`}
                      download
                      className="inline-flex items-center px-3 py-1.5 border border-slate-300 rounded text-xs font-medium text-slate-700 bg-white hover:bg-slate-50"
                    >
                      <Download className="w-3.5 h-3.5 mr-1.5" />
                      Download Predictions CSV
                    </a>
                    <a
                      href={`http://localhost:8000/api/v1/exports/${selectedExp.runs[0].run_id}/json`}
                      download
                      className="inline-flex items-center px-3 py-1.5 border border-slate-300 rounded text-xs font-medium text-slate-700 bg-white hover:bg-slate-50"
                    >
                      <FileText className="w-3.5 h-3.5 mr-1.5" />
                      Download Metrics JSON
                    </a>
                  </div>
                )}
              </div>
            ) : (
              <div className="py-16 text-center text-sm text-slate-400">
                Select an experiment or launch a new run to view metrics.
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}

