import React, { useEffect, useState } from 'react';
import { Database, CheckCircle2, AlertTriangle, FileText, RefreshCw, BarChart2, Filter } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { DataTable } from '../components/common/DataTable';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ClassDistribution } from '../charts/ClassDistribution';
import { DateDistribution } from '../charts/DateDistribution';
import { api } from '../api/client';

export function DatasetExplorer() {
  const [files, setFiles] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState<string>('');
  const [profile, setProfile] = useState<any>(null);
  const [preview, setPreview] = useState<any>({ records: [], total_rows: 0, page: 1 });
  const [validation, setValidation] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [profiling, setProfiling] = useState(false);
  const [page, setPage] = useState(1);

  useEffect(() => {
    async function loadDiscovery() {
      try {
        const res = await api.get('/datasets/discover');
        setFiles(res.data || []);
        if (res.data && res.data.length > 0) {
          const first = res.data[0].path;
          setSelectedFile(first);
          await loadPreview(first, 1);
          await loadProfile(first);
        }
      } catch (err) {
        console.error('Failed to discover files:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDiscovery();
  }, []);

  async function loadPreview(filePath: string, pageNum: number) {
    try {
      const res = await api.get('/datasets/preview', {
        params: { file_path: filePath, page: pageNum, page_size: 10 },
      });
      setPreview(res.data);
      setPage(pageNum);
    } catch (err) {
      console.error('Preview load failed:', err);
    }
  }

  async function loadProfile(filePath: string) {
    setProfiling(true);
    try {
      const res = await api.post('/datasets/profile', { path: filePath });
      setProfile(res.data);
    } catch (err) {
      console.error('Profile failed:', err);
    } finally {
      setProfiling(false);
    }
  }

  async function runValidation() {
    try {
      const res = await api.post('/datasets/validate', null, {
        params: { file_path: selectedFile },
      });
      setValidation(res.data);
    } catch (err) {
      console.error('Validation error:', err);
    }
  }

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  const columnsDef = [
    { key: 'id', header: 'Patent ID' },
    { key: 'date', header: 'Publication Date' },
    { key: 'cpc_ids', header: 'CPC Codes' },
    {
      key: 'text',
      header: 'Text (Abstract/Claims)',
      render: (row: Record<string, any>) => (
        <span className="text-xs text-slate-600 line-clamp-2 max-w-md">
          {row.text || 'N/A'}
        </span>
      ),
    },
  ];

  const cpcRecord: Record<string, number> = profile?.stats?.cpc_distribution || {};
  const dateRecord: Record<string, number> = profile?.stats?.date_distribution?.yearly_counts || {};

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Dataset Explorer</h1>
          <p className="mt-1 text-sm text-slate-500">
            Offline USPTO-3M dataset inspection, quality validation, and distribution profiling.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="secondary" onClick={() => loadProfile(selectedFile)} disabled={profiling}>
            <RefreshCw className={`w-4 h-4 mr-2 ${profiling ? 'animate-spin' : ''}`} />
            Re-profile File
          </Button>
          <Button onClick={runValidation}>
            <CheckCircle2 className="w-4 h-4 mr-2" />
            Validate Quality
          </Button>
        </div>
      </div>

      {/* Discovered Files Selector */}
      <Card title="Discovered Dataset Partitions">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
          {files.map((f) => (
            <button
              key={f.path}
              onClick={() => {
                setSelectedFile(f.path);
                loadPreview(f.path, 1);
                loadProfile(f.path);
              }}
              className={`p-3 text-left rounded-lg border text-xs transition-all ${
                selectedFile === f.path
                  ? 'border-indigo-600 bg-indigo-50/50 ring-1 ring-indigo-600'
                  : 'border-slate-200 bg-white hover:border-slate-300'
              }`}
            >
              <div className="flex items-center gap-2 font-medium text-slate-800 truncate">
                <FileText className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
                <span className="truncate">{f.name}</span>
              </div>
              <div className="mt-2 text-[11px] text-slate-500 flex justify-between">
                <span>{(f.size_bytes / (1024 * 1024)).toFixed(1)} MB</span>
                <span className="uppercase">{f.format}</span>
              </div>
            </button>
          ))}
        </div>
      </Card>

      {/* Validation Results if run */}
      {validation && (
        <Card title="Data Quality Audit Report">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className={`px-2.5 py-1 text-xs font-semibold rounded-full ${
                validation.is_valid ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
              }`}>
                {validation.is_valid ? 'Passed All Integrity Checks' : 'Quality Issues Detected'}
              </span>
              <span className="text-xs text-slate-500">
                Checked {validation.samples_checked} records from {selectedFile.slice(-30)}
              </span>
            </div>
            {validation.issues.length === 0 ? (
              <p className="text-sm text-emerald-600 flex items-center">
                <CheckCircle2 className="w-4 h-4 mr-1.5" /> No null values, missing identifiers, or corrupt records found.
              </p>
            ) : (
              <div className="space-y-2 mt-2">
                {validation.issues.map((iss: any, idx: number) => (
                  <div key={idx} className="p-2.5 bg-slate-50 border border-slate-200 rounded text-xs flex items-center justify-between">
                    <span className="font-medium text-slate-700">{iss.message}</span>
                    <span className="text-slate-500 font-mono">Count: {iss.count}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Distribution Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Top CPC Subclass Frequencies">
          {Object.keys(cpcRecord).length > 0 ? (
            <ClassDistribution data={cpcRecord} />
          ) : (
            <div className="h-64 flex items-center justify-center text-sm text-slate-400">
              No class frequency data available
            </div>
          )}
        </Card>

        <Card title="Publication Year Distribution">
          {Object.keys(dateRecord).length > 0 ? (
            <DateDistribution data={dateRecord} />
          ) : (
            <div className="h-64 flex items-center justify-center text-sm text-slate-400">
              No publication year data available
            </div>
          )}
        </Card>
      </div>

      {/* Paginated Data Preview */}
      <Card title="Interactive Records Preview">
        <DataTable
          columns={columnsDef}
          data={preview.records || []}
          page={page}
          pageSize={10}
          totalRows={preview.total_rows || 0}
          onPageChange={(p) => loadPreview(selectedFile, p)}
        />
      </Card>
    </div>
  );
}
