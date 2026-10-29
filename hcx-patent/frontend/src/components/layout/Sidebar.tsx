import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Database,
  FileSearch,
  GitBranch,
  Brain,
  Shield,
  TrendingUp,
  FlaskConical,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import clsx from 'clsx';
import { useState } from 'react';

const navItems = [
  { path: '/', label: 'Overview', icon: LayoutDashboard },
  { path: '/dataset', label: 'Dataset Explorer', icon: Database },
  { path: '/classify', label: 'Classification', icon: FileSearch },
  { path: '/taxonomy', label: 'CPC Taxonomy', icon: GitBranch },
  { path: '/explainability', label: 'Explainability', icon: Brain },
  { path: '/uncertainty', label: 'Uncertainty', icon: Shield },
  { path: '/drift', label: 'Drift Analysis', icon: TrendingUp },
  { path: '/experiments', label: 'Experiments', icon: FlaskConical },
];

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={clsx(
        'fixed left-0 top-0 h-full bg-navy-800 text-white flex flex-col transition-all duration-300 z-40',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-white/10">
        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center shrink-0">
          <FlaskConical className="w-4.5 h-4.5 text-white" />
        </div>
        {!collapsed && (
          <div className="overflow-hidden">
            <h1 className="text-sm font-bold tracking-tight">HCX-Patent</h1>
            <p className="text-[10px] text-slate-400 leading-tight">Classification Platform</p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 overflow-y-auto">
        <ul className="space-y-1 px-2">
          {navItems.map(({ path, label, icon: Icon }) => (
            <li key={path}>
              <NavLink
                to={path}
                end={path === '/'}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20'
                      : 'text-slate-300 hover:text-white hover:bg-white/10'
                  )
                }
                title={collapsed ? label : undefined}
              >
                <Icon className="w-5 h-5 shrink-0" />
                {!collapsed && <span>{label}</span>}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Collapse Toggle */}
      <div className="border-t border-white/10 p-2">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex items-center justify-center w-full p-2.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <ChevronLeft className="w-4 h-4" />
          )}
        </button>
      </div>
    </aside>
  );
}
