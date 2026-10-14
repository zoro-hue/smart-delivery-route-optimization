import React from 'react';
import {
  LayoutDashboard,
  Database,
  BarChart3,
  Car,
  MapPin,
  Route,
  GitCompare,
  History,
  Settings,
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  datasetCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  datasetCount,
}) => {
  const navItems = [
    { id: 'overview', label: 'Overview Dashboard', icon: LayoutDashboard },
    {
      id: 'datasets',
      label: 'Dataset Management',
      icon: Database,
      badge: datasetCount > 0 ? `${datasetCount}/6` : undefined,
    },
    { id: 'analytics', label: 'Data Quality & Analytics', icon: BarChart3 },
    { id: 'traffic', label: 'Live/Simulated Traffic', icon: Car },
    { id: 'map', label: 'Delivery Map', icon: MapPin },
    { id: 'optimization', label: 'Route Optimization', icon: Route },
    { id: 'comparison', label: 'Classical vs Quantum', icon: GitCompare },
    { id: 'history', label: 'Experiment History', icon: History },
    { id: 'settings', label: 'System Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 text-slate-300 flex flex-col justify-between shrink-0">
      <div className="py-5 px-3">
        <div className="px-3 mb-5">
          <span className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
            Logistics & Optimization
          </span>
        </div>

        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={`h-4.5 w-4.5 ${
                      isActive ? 'text-white' : 'text-slate-400'
                    }`}
                  />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span
                    className={`text-[11px] px-2 py-0.5 rounded-full font-semibold ${
                      isActive
                        ? 'bg-white/20 text-white'
                        : 'bg-slate-800 text-slate-300 border border-slate-700'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      <div className="p-4 border-t border-slate-800 text-xs text-slate-400">
        <div className="flex items-center justify-between mb-1">
          <span>Engine Status</span>
          <span className="text-emerald-400 font-medium">Online</span>
        </div>
        <p className="text-[11px] text-slate-400">
          UROP Research Project 2026
        </p>
      </div>
    </aside>
  );
};
