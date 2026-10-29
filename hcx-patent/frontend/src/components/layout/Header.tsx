import { useLocation } from 'react-router-dom';
import { Bell, Search, HelpCircle } from 'lucide-react';

const pageTitles: Record<string, { title: string; subtitle: string }> = {
  '/': { title: 'Research Overview', subtitle: 'System status and experiment summary' },
  '/dataset': { title: 'Dataset Explorer', subtitle: 'Inspect and profile your patent data' },
  '/classify': { title: 'Classification Workspace', subtitle: 'Classify patents with trained models' },
  '/taxonomy': { title: 'CPC Taxonomy', subtitle: 'Browse the CPC classification hierarchy' },
  '/explainability': { title: 'Explainability Lab', subtitle: 'Understand model predictions' },
  '/uncertainty': { title: 'Uncertainty Lab', subtitle: 'Conformal prediction & calibration' },
  '/drift': { title: 'Drift Analysis', subtitle: 'Temporal and taxonomy drift detection' },
  '/experiments': { title: 'Experiment Center', subtitle: 'Manage and compare experiments' },
};

export function Header() {
  const location = useLocation();
  const page = pageTitles[location.pathname] || { title: 'HCX-Patent', subtitle: '' };

  return (
    <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-md border-b border-slate-200">
      <div className="flex items-center justify-between px-8 py-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900">{page.title}</h1>
          <p className="text-sm text-slate-500">{page.subtitle}</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors">
            <Search className="w-5 h-5" />
          </button>
          <button className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors">
            <HelpCircle className="w-5 h-5" />
          </button>
          <button className="relative p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors">
            <Bell className="w-5 h-5" />
          </button>
          <div className="w-px h-6 bg-slate-200 mx-1" />
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs font-bold">
              R
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
