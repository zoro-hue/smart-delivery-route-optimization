import React, { useState } from 'react';
import {
  Route,
  Database,
  BarChart3,
  History,
  Settings,
  Menu,
  X,
  Compass,
} from 'lucide-react';

interface TopGlassNavigationProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  datasetCount: number;
}

export const TopGlassNavigation: React.FC<TopGlassNavigationProps> = ({
  currentTab,
  onSelectTab,
  datasetCount,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Five focused navigation destinations per specification:
  // 1. Plan | 2. Datasets | 3. Results | 4. Experiments | 5. Settings
  const navItems = [
    { id: 'plan', label: 'Plan', icon: Route },
    {
      id: 'datasets',
      label: 'Datasets',
      icon: Database,
      badge: datasetCount > 0 ? `${datasetCount}` : undefined,
    },
    { id: 'results', label: 'Results', icon: BarChart3 },
    { id: 'experiments', label: 'Experiments', icon: History },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="w-full flex justify-center py-2 px-4 z-40 sticky top-16 pointer-events-none">
      {/* Desktop Floating Glass Pill */}
      <nav
        aria-label="Main Navigation"
        className="pointer-events-auto hidden md:flex items-center gap-1 px-3 py-1.5 glass transition-all duration-200"
      >
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs font-semibold tracking-tight transition-all duration-150 cursor-pointer ${
                isActive
                  ? 'bg-[#080808] text-white shadow-sm'
                  : 'text-[#171717] hover:text-[#080808] hover:bg-black/5'
              }`}
            >
              <Icon
                className={`h-3.5 w-3.5 transition-colors ${
                  isActive ? 'text-[#B7FF2A]' : 'text-[#777777]'
                }`}
              />
              <span>{item.label}</span>
              {item.badge && (
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold font-mono ml-0.5 ${
                    isActive
                      ? 'bg-[#B7FF2A] text-[#080808]'
                      : 'bg-black/5 text-[#777777]'
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Mobile Glass Navigation Toggle */}
      <div className="pointer-events-auto md:hidden w-full max-w-xs flex items-center justify-between px-4 py-2 glass">
        <div className="flex items-center gap-2">
          <Compass className="h-4 w-4 text-[#080808]" />
          <span className="text-xs font-bold uppercase tracking-wider text-[#171717]">
            {navItems.find((n) => n.id === currentTab)?.label || 'Navigate'}
          </span>
        </div>
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="p-1 rounded-md text-[#171717] hover:bg-black/5"
          aria-label="Toggle Navigation Menu"
        >
          {mobileMenuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
        </button>
      </div>

      {/* Mobile Dropdown Panel */}
      {mobileMenuOpen && (
        <div className="pointer-events-auto md:hidden fixed top-32 inset-x-6 bg-white/95 backdrop-blur-2xl border border-white/60 rounded-3xl p-3 shadow-2xl z-50 flex flex-col gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  onSelectTab(item.id);
                  setMobileMenuOpen(false);
                }}
                className={`flex items-center justify-between px-4 py-2.5 rounded-2xl text-xs font-semibold ${
                  isActive
                    ? 'bg-[#080808] text-white'
                    : 'text-[#171717] hover:bg-black/5'
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon
                    className={`h-4 w-4 ${
                      isActive ? 'text-[#B7FF2A]' : 'text-[#777777]'
                    }`}
                  />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-black/5 text-[#777777] font-mono">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};
