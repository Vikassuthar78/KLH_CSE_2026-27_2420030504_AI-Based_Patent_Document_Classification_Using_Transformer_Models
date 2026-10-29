import React, { useState, useEffect } from 'react';
import {
  FileSearch,
  Sparkles,
  Upload,
  Clock,
  GitBranch,
  ShieldCheck,
  CheckCircle2,
  Copy,
  Download,
} from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { api } from '../api/client';
import type { ClassificationResult, Prediction } from '../types';

export function ClassificationWorkspace() {
  const [text, setText] = useState('');
  const [models, setModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState('TF-IDF Baseline');
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ClassificationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadModels() {
      try {
        const res = await api.get('/patents/models');
        if (res.data?.models) {
          setModels(res.data.models);
          setSelectedModel(res.data.models[0]);
        }
      } catch (err) {
        console.error('Failed to load models:', err);
      }
    }
    loadModels();
  }, []);

  async function loadSamplePatent() {
    try {
      const res = await api.get('/patents/sample');
      if (res.data?.text) {
        setText(res.data.text);
      }
    } catch (err) {
      console.error('Failed to load sample:', err);
    }
  }

  async function handleClassify() {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.post('/patents/classify', {
        text,
        model_name: selectedModel,
        top_k: topK,
      });
      setResult(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Classification failed.');
    } finally {
      setLoading(false);
    }
  }

  function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      setText(content);
    };
    reader.readAsText(file);
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Patent Classification Workspace</h1>
          <p className="mt-1 text-sm text-slate-500">
            Multi-label hierarchical prediction with taxonomy paths, confidence calibration, and latency profiling.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="secondary" onClick={loadSamplePatent}>
            <Sparkles className="w-4 h-4 mr-2 text-indigo-600" />
            Load Sample Patent
          </Button>
          <label className="cursor-pointer">
            <input type="file" accept=".txt" className="hidden" onChange={handleFileUpload} />
            <span className="inline-flex items-center px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium text-slate-700 bg-white hover:bg-slate-50 cursor-pointer shadow-sm">
              <Upload className="w-4 h-4 mr-2" />
              Upload TXT
            </span>
          </label>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Input Form */}
        <div className="lg:col-span-2 space-y-6">
          <Card title="Patent Document Text">
            <div className="space-y-4">
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste patent abstract, claims, or technical description here..."
                rows={12}
                className="w-full rounded-lg border border-slate-300 p-3 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-sans"
              />
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-700">Model</label>
                    <select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      className="mt-1 block rounded-md border-slate-300 py-1.5 pl-3 pr-8 text-xs focus:border-indigo-500 focus:ring-indigo-500"
                    >
                      {models.map((m) => (
                        <option key={m} value={m}>{m}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-700">Top Candidates (k)</label>
                    <select
                      value={topK}
                      onChange={(e) => setTopK(Number(e.target.value))}
                      className="mt-1 block rounded-md border-slate-300 py-1.5 pl-3 pr-8 text-xs focus:border-indigo-500 focus:ring-indigo-500"
                    >
                      <option value={3}>3</option>
                      <option value={5}>5</option>
                      <option value={10}>10</option>
                    </select>
                  </div>
                </div>

                <Button onClick={handleClassify} disabled={loading || !text.trim()} className="w-full sm:w-auto">
                  {loading ? <LoadingSpinner size="sm" /> : <FileSearch className="w-4 h-4 mr-2" />}
                  Classify Patent
                </Button>
              </div>
            </div>
          </Card>

          {error && (
            <div className="p-4 rounded-lg bg-rose-50 border border-rose-200 text-sm text-rose-700">
              {error}
            </div>
          )}
        </div>

        {/* Right Column: Prediction Results & Hierarchy Paths */}
        <div className="space-y-6">
          <Card title="Classification Results">
            {result ? (
              <div className="space-y-6">
                <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg text-xs">
                  <div className="flex items-center text-slate-600">
                    <Clock className="w-4 h-4 mr-1 text-slate-400" />
                    Latency: <span className="font-semibold text-slate-800 ml-1">{result.inference_time_ms} ms</span>
                  </div>
                  <div className="text-slate-600">
                    Model: <span className="font-medium text-slate-800">{result.model_name}</span>
                  </div>
                </div>

                <div className="space-y-3">
                  <h4 className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                    Top-{topK} CPC Predictions
                  </h4>
                  {result.predictions.map((p, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-lg border border-slate-200 bg-white hover:border-indigo-300 transition-colors space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-mono font-bold text-sm text-indigo-700">{p.code}</span>
                        <div className="flex items-center gap-1.5">
                          <div className="w-16 bg-slate-100 rounded-full h-2 overflow-hidden">
                            <div
                              className="bg-indigo-600 h-2 rounded-full"
                              style={{ width: `${Math.round(p.confidence * 100)}%` }}
                            />
                          </div>
                          <span className="text-xs font-semibold text-slate-700">
                            {(p.confidence * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>

                      {/* Hierarchy Path Breadcrumb */}
                      {p.hierarchy_path && p.hierarchy_path.length > 0 && (
                        <div className="flex items-center gap-1 text-[11px] text-slate-500 flex-wrap">
                          <GitBranch className="w-3 h-3 text-slate-400 shrink-0" />
                          {p.hierarchy_path.map((node, nIdx) => (
                            <React.Fragment key={nIdx}>
                              {nIdx > 0 && <span className="text-slate-300">/</span>}
                              <span className="px-1.5 py-0.5 bg-slate-100 rounded font-mono text-[10px] text-slate-700">
                                {node}
                              </span>
                            </React.Fragment>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="py-12 text-center text-sm text-slate-400">
                Enter patent text and click &quot;Classify Patent&quot; to inspect predictions.
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
