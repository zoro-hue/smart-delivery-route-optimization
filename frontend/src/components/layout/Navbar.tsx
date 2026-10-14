import React, { useState, useEffect } from 'react';
import {
  Route,
  Database,
  BarChart3,
  History,
  Settings,
  RotateCw,
  Menu,
  X,
  Sun,
  Moon,
} from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

interface NavbarProps {
  isBackendHealthy: boolean;
  activeTab: string;
  onSelectTab: (tab: string) => void;
  datasetCount: number;
  onScanWorkspace: () => void;
  onRefresh: () => void;
  isScanning: boolean;
  isRefreshing: boolean;
  onNavigateHome?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  isBackendHealthy,
  activeTab,
  onSelectTab,
  datasetCount,
  onScanWorkspace,
  onRefresh,
  isScanning,
  isRefreshing,
  onNavigateHome,
}) => {
  const { theme, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const scrolled = window.scrollY > 12;
      setIsScrolled((prev) => (prev !== scrolled ? scrolled : prev));
    };
    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

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
    <header className="sticky top-0 z-50 w-full px-6 sm:px-8 lg:px-10 h-16 flex items-center justify-between bg-transparent border-none shadow-none pointer-events-none">
      {/* ─── 1. FAR LEFT: ROUTE/IQ BRAND WORDMARK (NO BOXED BACKGROUND) ────────── */}
      <div
        className="flex items-center gap-2.5 cursor-pointer shrink-0 select-none z-10 group pointer-events-auto"
        onClick={onNavigateHome}
        title="Return to ROUTE/IQ Overview Homepage"
      >
        <div className="h-8 w-8 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform duration-300">
          <img src="/logo.png" alt="ROUTE/IQ Logo" className="h-full w-full object-contain" />
        </div>

        <div className="flex items-center gap-1.5">
          <span className="text-xl font-heading font-bold tracking-tight text-[#080808] dark:text-[#F5F5F7]">
            ROUTE<span className="text-[#B7FF00]">/</span>IQ
          </span>
        </div>
      </div>

      {/* ─── 2. CENTER: TRULY CENTERED FLOATING GLASSMORPHIC NAVIGATION PILL ──── */}
      <nav
        aria-label="Main Navigation"
        className="hidden md:flex absolute left-1/2 -translate-x-1/2 items-center gap-1 p-1 rounded-full bg-white/75 dark:bg-[#18181B]/85 backdrop-blur-[26px] backdrop-saturate-[190%] border border-black/10 dark:border-[#29292E] shadow-lg dark:shadow-[0_8px_32px_rgba(0,0,0,0.7)] z-20 pointer-events-auto"
      >
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-heading tracking-tight transition-all duration-200 ease-out cursor-pointer active:scale-95 ${
                isActive
                  ? 'bg-[#080808] dark:bg-[#202024] text-white dark:text-[#F5F5F7] border border-transparent dark:border-white/10 shadow-xs font-bold scale-[1.02]'
                  : 'text-[#444444] dark:text-[#A1A1AA] hover:text-[#080808] dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 font-medium hover:scale-[1.01]'
              }`}
            >
              <Icon
                className={`h-3.5 w-3.5 transition-colors ${
                  isActive ? 'text-[#B7FF00]' : 'text-[#777777] dark:text-[#A1A1AA]'
                }`}
              />
              <span>{item.label}</span>
              {item.badge && (
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded-full font-heading font-bold ml-0.5 ${
                    isActive
                      ? 'bg-black/60 dark:bg-black/80 text-white dark:text-[#F5F5F7]'
                      : 'bg-black/10 dark:bg-white/10 text-[#555555] dark:text-[#D4D4D8]'
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* ─── 3. FAR RIGHT: COMPACT QISKIT 2.4.1 STATUS & THEME TOGGLE ──────── */}
      <div className="flex items-center gap-2.5 shrink-0 z-10 pointer-events-auto">
        {/* Compact Engine Status Indicator Pill */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/75 dark:bg-[#18181B]/85 backdrop-blur-[24px] backdrop-saturate-[180%] border border-black/10 dark:border-[#29292E] text-xs font-heading font-medium text-[#171717] dark:text-[#F5F5F7] shadow-sm">
          <span
            className={`h-2 w-2 rounded-full shrink-0 ${
              isBackendHealthy
                ? 'bg-[#22C55E] shadow-[0_0_8px_#22C55E]'
                : 'bg-[#999999]'
            }`}
          />
          <span className="hidden sm:inline">
            {isBackendHealthy ? 'Qiskit 2.4.1' : 'Qiskit 2.4.1 (Offline)'}
          </span>
          <span className="sm:hidden">
            Qiskit 2.4.1
          </span>
        </div>

        {/* Light / Dark Mode Toggle Button */}
        <button
          onClick={toggleTheme}
          className="flex items-center justify-center h-8 w-8 rounded-full bg-white/75 dark:bg-[#18181B]/85 backdrop-blur-[24px] backdrop-saturate-[180%] hover:bg-white dark:hover:bg-[#202024] text-[#171717] dark:text-[#F5F5F7] border border-black/10 dark:border-[#29292E] transition-all duration-300 shadow-sm cursor-pointer group"
          title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          aria-label="Toggle light/dark theme"
        >
          {theme === 'dark' ? (
            <Sun className="h-4 w-4 text-[#B7FF00] transition-transform duration-300 group-hover:rotate-45" />
          ) : (
            <Moon className="h-4 w-4 text-[#171717] transition-transform duration-300 group-hover:-rotate-12" />
          )}
        </button>

        {/* Mobile Menu Toggle Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-1.5 rounded-lg border border-black/10 dark:border-[#29292E] text-[#080808] dark:text-white hover:bg-black/5 dark:hover:bg-white/5 cursor-pointer ml-1"
          aria-label="Toggle navigation menu"
        >
          {mobileMenuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
        </button>
      </div>

      {/* ─── MOBILE ACCORDION MENU (ON SMALL SCREENS ONLY) ─── */}
      {mobileMenuOpen && (
        <div className="md:hidden absolute top-16 inset-x-4 border border-white/80 dark:border-white/10 bg-white/90 dark:bg-[#18181B]/90 backdrop-blur-[26px] backdrop-saturate-[180%] px-4 py-3 shadow-2xl rounded-2xl z-50 animate-fadeIn">
          <nav className="flex flex-col gap-1.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    onSelectTab(item.id);
                    setMobileMenuOpen(false);
                  }}
                  className={`flex items-center justify-between px-3.5 py-2 rounded-xl text-xs font-heading font-medium tracking-tight transition-all cursor-pointer ${
                    isActive
                      ? 'bg-[#080808] dark:bg-[#B7FF2A] text-[#B7FF2A] dark:text-[#080808] font-bold'
                      : 'text-[#555555] dark:text-[#A1A1AA] hover:text-[#080808] dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded-full font-bold font-heading ${
                        isActive
                          ? 'bg-[#B7FF2A] text-[#080808]'
                          : 'bg-black/10 text-[#555555]'
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
      )}
    </header>
  );
};
