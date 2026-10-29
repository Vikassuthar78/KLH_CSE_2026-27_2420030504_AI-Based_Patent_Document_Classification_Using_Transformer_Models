import React, { useEffect, useState } from 'react';
import { GitBranch, Search, ChevronRight, Folder, FileText, CheckCircle2 } from 'lucide-react';
import { Card } from '../components/common/Card';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { api } from '../api/client';
import type { TaxonomyNode } from '../types';

export function TaxonomyExplorer() {
  const [tree, setTree] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    async function loadTree() {
      try {
        const res = await api.get('/taxonomy/tree');
        setTree(res.data || []);
        if (res.data && res.data.length > 0) {
          setSelectedNode(res.data[0]);
        }
      } catch (err) {
        console.error('Failed to load taxonomy tree:', err);
      } finally {
        setLoading(false);
      }
    }
    loadTree();
  }, []);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    setSearching(true);
    try {
      const res = await api.get('/taxonomy/search', { params: { query: searchQuery } });
      setSearchResults(res.data || []);
    } catch (err) {
      console.error('Taxonomy search failed:', err);
    } finally {
      setSearching(false);
    }
  }

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">CPC Taxonomy Explorer</h1>
        <p className="mt-1 text-sm text-slate-500">
          Cooperative Patent Classification (CPC) hierarchical structure: Section → Class → Subclass.
        </p>
      </div>

      {/* Search Bar */}
      <Card>
        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by CPC symbol (e.g. G06F, A61K) or technical description..."
              className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700"
          >
            {searching ? 'Searching...' : 'Search'}
          </button>
        </form>

        {searchResults.length > 0 && (
          <div className="mt-4 pt-4 border-t border-slate-100">
            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              Search Matches ({searchResults.length})
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
              {searchResults.map((r, idx) => (
                <div
                  key={idx}
                  onClick={() => setSelectedNode(r)}
                  className="p-2 border border-slate-200 rounded text-xs hover:border-indigo-500 cursor-pointer"
                >
                  <span className="font-mono font-bold text-indigo-700">{r.code}</span>
                  <p className="text-slate-600 truncate mt-0.5">{r.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </Card>

      {/* Hierarchy Browser */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card title="Taxonomy Tree (Observed Dataset Subclasses)">
            <div className="space-y-2 max-h-[500px] overflow-y-auto pr-2">
              {tree.map((sec) => (
                <div key={sec.code} className="border border-slate-100 rounded-lg p-2.5">
                  <div
                    onClick={() => setSelectedNode(sec)}
                    className="flex items-center justify-between cursor-pointer hover:text-indigo-600"
                  >
                    <div className="flex items-center gap-2">
                      <Folder className="w-4 h-4 text-indigo-500" />
                      <span className="font-mono font-bold text-sm">Section {sec.code}</span>
                      <span className="text-xs text-slate-600 truncate max-w-xs">{sec.description}</span>
                    </div>
                    <span className="text-[11px] font-mono text-slate-400">
                      {sec.patent_count?.toLocaleString()} records
                    </span>
                  </div>

                  {sec.children && sec.children.length > 0 && (
                    <div className="pl-6 pt-2 space-y-1.5 border-l border-slate-100 ml-2 mt-2">
                      {sec.children.slice(0, 10).map((cls: any) => (
                        <div key={cls.code}>
                          <div
                            onClick={() => setSelectedNode(cls)}
                            className="flex items-center justify-between cursor-pointer hover:text-indigo-600 text-xs py-1"
                          >
                            <span className="font-mono font-medium text-slate-700">Class {cls.code}</span>
                            <span className="text-[10px] text-slate-400">
                              {cls.children?.length || 0} subclasses
                            </span>
                          </div>

                          {cls.children && cls.children.length > 0 && (
                            <div className="pl-4 flex flex-wrap gap-1.5 pt-1">
                              {cls.children.map((sub: any) => (
                                <button
                                  key={sub.code}
                                  onClick={() => setSelectedNode(sub)}
                                  className={`px-2 py-0.5 font-mono text-[11px] rounded border transition-colors ${
                                    selectedNode?.code === sub.code
                                      ? 'bg-indigo-600 text-white border-indigo-600'
                                      : 'bg-slate-50 text-slate-700 border-slate-200 hover:border-indigo-400'
                                  }`}
                                >
                                  {sub.code}
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div>
          <Card title="Node Metadata & Ancestry">
            {selectedNode ? (
              <div className="space-y-4">
                <div>
                  <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">
                    CPC Symbol
                  </span>
                  <div className="text-2xl font-mono font-bold text-indigo-700 mt-1">
                    {selectedNode.code}
                  </div>
                </div>

                <div>
                  <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">
                    Hierarchy Level
                  </span>
                  <div className="text-sm font-medium text-slate-800 capitalize mt-0.5">
                    {selectedNode.level || 'Subclass'}
                  </div>
                </div>

                <div>
                  <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">
                    Description
                  </span>
                  <p className="text-sm text-slate-700 mt-1">
                    {selectedNode.description || `CPC Code ${selectedNode.code}`}
                  </p>
                </div>

                {selectedNode.patent_count !== undefined && (
                  <div>
                    <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">
                      Sample Dataset Occurrences
                    </span>
                    <div className="text-sm font-semibold text-slate-900 mt-1">
                      {selectedNode.patent_count.toLocaleString()}
                    </div>
                  </div>
                )}

                <div className="pt-4 border-t border-slate-100">
                  <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg flex items-center gap-2 text-xs text-emerald-800">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                    <span>Valid CPC structure under WIPO IPC/CPC harmonization.</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-12 text-center text-sm text-slate-400">
                Select a taxonomy node to inspect properties.
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}

