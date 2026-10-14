import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import {
  Cpu,
  ArrowRight,
  Database,
  ExternalLink,
  Route,
  FileText,
  BookOpen,
  PlayCircle,
  GraduationCap,
  Download,
  X,
} from 'lucide-react';
import { AnalyticsSummary, Dataset } from '../types';
import { LogisticsRouteCube } from '../components/hero/LogisticsRouteCube';
import { useSettings } from '../context/SettingsContext';
import { useTheme } from '../context/ThemeContext';

interface OverviewProps {
  analytics: AnalyticsSummary | null;
  datasets: Dataset[];
  backendHealth?: any;
  onNavigate: (tab: string) => void;
  onScanDatasets: () => void;
  isScanning: boolean;
}

// Reference Research Papers Data
interface ResearchPaper {
  id: string;
  title: string;
  category: 'draft' | 'reference';
  venue: string;
  year: string;
  filename: string;
  description: string;
  relevance: string;
}

const RESEARCH_PAPERS: ResearchPaper[] = [
  {
    id: 'urop-survey',
    title: 'Hybrid Big Data and Quantum Computing Framework for Urban Delivery Route Optimization',
    category: 'draft',
    venue: 'UROP Research Survey & System Architecture Draft',
    year: '2026',
    filename: 'literature_survey.pdf',
    description:
      'Our primary drafted research paper presenting the ROUTE/IQ framework: integrating real NYC Open Data logistics with classical heuristics, OR-Tools, and quantum-classical algorithms (QAOA, QIGA).',
    relevance: 'Primary System Specification & Literature Survey',
  },
  {
    id: 'qaoa-vrp',
    title: 'Solving Vehicle Routing Problem Using Quantum Approximate Optimization Algorithm',
    category: 'reference',
    venue: 'IEEE / Quantum Science & Optimization',
    year: '2020',
    filename: 'Solving_Vehicle_Routing_Problem_Using_Quantum_Approximate_Optimization_Algorithm.pdf',
    description:
      'Foundational paper formulating Vehicle Routing Problem instances into Quadratic Unconstrained Binary Optimization (QUBO) graphs solvable with parameterized QAOA quantum circuits.',
    relevance: 'Algorithmic foundation for QAOA solver in ROUTE/IQ',
  },
  {
    id: 'grover-vrp',
    title: 'Solving Vehicle Routing Problem Using Grover Adaptive Search Algorithm',
    category: 'reference',
    venue: 'Quantum Information & Computation',
    year: '2021',
    filename: 'Solving_Vehicle_Routing_Problem_Using_Grover_Adaptive_Search_Algorithm.pdf',
    description:
      'Investigates quadratic speedup for combinatorial search over vehicle routing constraints using Grover Adaptive Search (GAS).',
    relevance: 'Benchmark reference for quantum speedup limits in routing',
  },
  {
    id: 'systematic-review',
    title: 'A Systematic Literature Review of Quantum Computing for Routing Problems',
    category: 'reference',
    venue: 'ACM Computing Surveys / IEEE Access',
    year: '2022',
    filename: '1_A_Systematic_Literature_Review_of_Quantum_Computing_for_Routing_Problems.pdf',
    description:
      'Comprehensive comparative study classifying quantum heuristics (annealing, QAOA, VQE, and Grover) across TSP, CVRP, and Pickup-and-Delivery instances.',
    relevance: 'Taxonomy of quantum formulations and feasibility bounds',
  },
  {
    id: 'qiga-opt',
    title: 'Quantum-Inspired Genetic Algorithms (QIGA/IQGA) for Combinatorial Optimization',
    category: 'reference',
    venue: 'ADCAIJ / Evolutionary Computation',
    year: '2021',
    filename: 'ADCAIJ-v14-19-32876.pdf',
    description:
      'Detailed study on using quantum bit representation and quantum rotation gate operators within genetic evolutionary frameworks for constrained optimization.',
    relevance: 'Direct basis for the QIGA/IQGA engine in ROUTE/IQ',
  },
  {
    id: 'transportation-survey',
    title: 'Quantum Computing in Transportation Engineering: A Survey',
    category: 'reference',
    venue: 'Transportation Research Interdisciplinary Review',
    year: '2023',
    filename: 'Quantum_Computing_in_Transportation_Engineering_A_Survey (1).pdf',
    description:
      'Reviews applications of quantum algorithms to urban traffic control, arterial signal timing, route guidance, and large-scale fleet logistics.',
    relevance: 'Urban mobility and dynamic traffic integration review',
  },
  {
    id: 'scientometric-its',
    title: 'A Scientometric Analysis of Quantum-Driven Innovations in Intelligent Transportation Systems',
    category: 'reference',
    venue: 'Journal of Intelligent Transportation Systems',
    year: '2024',
    filename: 'A scientometric analysis of quantum driven innovations in intelligent transportation systems.pdf',
    description:
      'Global trend analysis mapping the convergence of big data analytics, urban transport pipelines, and NISQ-era quantum computing.',
    relevance: 'Project context and state-of-the-art benchmarks',
  },
];

// Curated Video Resources
const VIDEO_RESOURCES = [
  {
    title: 'Quantum Approximate Optimization Algorithm (QAOA) Explained',
    channel: 'IBM Quantum',
    duration: '24 min',
    url: 'https://www.youtube.com/watch?v=AOKM9BkweVU',
    description:
      'In-depth walkthrough of QAOA circuit formulation, Hamiltonian cost terms, and variational parameter optimization.',
  },
  {
    title: 'Vehicle Routing Problem & Operations Research Optimization',
    channel: 'Operations Research Society',
    duration: '18 min',
    url: 'https://www.youtube.com/watch?v=9jR4UfW07Fw',
    description:
      'Core principles of CVRP, capacity constraints, Clarke-Wright savings heuristics, and OR-Tools solvers.',
  },
  {
    title: 'Quantum Computing for Logistics & Supply Chain Optimization',
    channel: 'Qiskit Community',
    duration: '32 min',
    url: 'https://www.youtube.com/watch?v=0hK27wM5_4U',
    description:
      'Demonstration of hybrid classical-quantum pipelines for industrial logistics scheduling and routing.',
  },
];

export const OverviewDashboard: React.FC<OverviewProps> = ({ onNavigate }) => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // Mouse coordinate state for ambient glow tracking
  const [mousePos, setMousePos] = useState({ x: 50, y: 50 });
  const [showPapersModal, setShowPapersModal] = useState<boolean>(false);
  const [showVideoModal, setShowVideoModal] = useState<boolean>(false);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    setMousePos({ x: Math.round(x), y: Math.round(y) });
  };

  return (
    <div className="space-y-12 pb-8">
      {/* ─────────────────────────────────────────────────────────────
          1. REFINED AMBIENT HERO SURFACE
          Preserved untouched as specified in requirements.
          ───────────────────────────────────────────────────────────── */}
      <section
        onMouseMove={handleMouseMove}
        className="relative w-full rounded-3xl overflow-hidden min-h-[520px] lg:min-h-[560px] flex items-center bg-white dark:bg-[#111113] border border-black/10 dark:border-[#29292E] shadow-[0_4px_24px_-4px_rgba(0,0,0,0.04)] dark:shadow-[0_8px_32px_rgba(0,0,0,0.6)] transition-all duration-300"
        style={{
          background: isDark
            ? '#111113'
            : `
              radial-gradient(circle at ${mousePos.x}% ${mousePos.y}%, rgba(183, 255, 42, 0.08) 0%, rgba(255, 255, 255, 0) 45%),
              radial-gradient(ellipse 60% 50% at 75% 50%, rgba(183, 255, 42, 0.05) 0%, rgba(255, 255, 255, 0) 70%),
              #FFFFFF
            `,
        }}
      >
        <div className="absolute inset-0 pointer-events-none bg-gradient-to-r from-transparent via-transparent to-black/[0.015]" />

        <div className="w-full max-w-7xl mx-auto px-6 sm:px-10 py-10 lg:py-12 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center relative z-10">
          {/* Left Column */}
          <div className="lg:col-span-6 space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-black/5 dark:bg-[#18181B] border border-black/5 dark:border-[#29292E] text-xs font-semibold tracking-wider uppercase text-[#555555] dark:text-[#A1A1AA]">
              <span className="h-2 w-2 rounded-full bg-[#B7FF00] animate-pulse" />
              <span>Smart Logistics Engine</span>
            </div>

            <div className="space-y-3">
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-heading font-bold text-[#080808] dark:text-[#F5F5F7] leading-[1.05] tracking-tight">
                Smarter Routes. <br />
                <span className="text-[#080808] dark:text-[#F5F5F7] border-b-4 border-[#B7FF00]">
                  Optimized Deliveries.
                </span>
              </h1>
              <p className="text-base sm:text-lg text-[#666666] dark:text-[#A1A1AA] font-normal leading-relaxed max-w-md pt-2">
                Unifying real-world NYC logistics data with classical and quantum-classical optimization to build efficient, constraint-aware delivery routes.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3 pt-2">
              <button
                onClick={() => onNavigate('plan')}
                className="flex items-center gap-2 px-7 py-3.5 bg-[#080808] dark:bg-[#18181B] hover:bg-[#1a1a1a] dark:hover:bg-[#202024] text-[#B7FF00] font-semibold text-sm rounded-full transition-all duration-150 cursor-pointer shadow-sm hover:shadow-md border border-transparent dark:border-[#29292E]"
              >
                <span>Plan Deliveries</span>
                <ArrowRight className="h-4 w-4" />
              </button>

              <button
                onClick={() => onNavigate('datasets')}
                className="px-6 py-3.5 text-[#080808] dark:text-[#F5F5F7] hover:bg-black/5 dark:hover:bg-white/5 font-semibold text-sm rounded-full border border-black/15 dark:border-[#29292E] transition-all duration-150 cursor-pointer"
              >
                Inspect Datasets
              </button>
            </div>
          </div>

          {/* Right Column: 3D Logistics Route Cube Animation */}
          <div className="lg:col-span-6 w-full h-[400px] sm:h-[460px] lg:h-[500px] flex items-center justify-center relative">
            <LogisticsRouteCube />
          </div>
        </div>
      </section>

      {/* ─── GLASSMORPHIC SECTION TRANSITION BRIDGE (Hero → How It Works) ─── */}
      <div className="glass-section-bridge my-6 relative z-10">
        <div className="glass-section-bridge-bar" />
        <div className="absolute left-1/2 -translate-x-1/2 -translate-y-1/2 top-1/2 glass-floating-pill px-5 py-2 rounded-full flex items-center gap-2.5 text-[10px] font-bold tracking-widest uppercase text-[#555555] dark:text-[#A1A1AA] shadow-xs cursor-default">
          <span className="h-2 w-2 rounded-full bg-[#B7FF2A] animate-ping" />
          <span>Architecture & Telemetry Pipeline</span>
        </div>
      </div>

      {/* ─────────────────────────────────────────────────────────────
          2. HOW IT WORKS
          Spacious two-column layout in translucent glassmorphic container:
          Left: Pipeline overview & horizontal 3-step workflow
          Right: Compact NYC Logistics live simulation video
          ───────────────────────────────────────────────────────────── */}
      {/* ─────────────────────────────────────────────────────────────
          2. HOW IT WORKS
          Spacious two-column layout in translucent glassmorphic container:
          Left: Pipeline overview & horizontal 3-step workflow
          Right: Compact NYC Logistics live simulation video
          ───────────────────────────────────────────────────────────── */}
      <section className="breathy-scroll-section p-6 sm:p-8 lg:p-10 rounded-3xl bg-white/70 dark:bg-[#111113] backdrop-blur-xl border border-white/80 dark:border-[#29292E] shadow-sm space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
          {/* Left Column (7 cols): Heading, description & horizontal 3-step process */}
          <div className="lg:col-span-7 space-y-6">
            <div className="space-y-2">
              <span className="text-xs font-bold uppercase tracking-widest text-[#777777] dark:text-[#71717A]">
                HOW IT WORKS
              </span>
              <h2 className="text-3xl sm:text-4xl font-heading font-bold text-[#080808] dark:text-[#F5F5F7] leading-[1.1] tracking-tight">
                From Real-World Data to Optimized Delivery Routes.
              </h2>
              <p className="text-sm sm:text-base text-[#666666] dark:text-[#A1A1AA] leading-relaxed max-w-xl pt-1">
                We combine NYC logistics data with classical and quantum-classical algorithms to generate efficient, constraint-aware routes.
              </p>
            </div>

            {/* Horizontal three-step process connected with thin radium-lime arrows */}
            <div className="pt-2">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-2 items-start">
                {/* Step 1 — Big Data */}
                <div className="space-y-2.5">
                  <div className="flex items-center justify-between">
                    <div className="h-10 w-10 rounded-2xl bg-black/5 dark:bg-[#18181B] border border-transparent dark:border-[#29292E] flex items-center justify-center text-[#080808] dark:text-[#B7FF00]">
                      <Database className="h-5 w-5" />
                    </div>
                    <div className="hidden sm:flex flex-1 items-center px-2">
                      <div className="h-[1px] flex-1 bg-[#B7FF00]" />
                      <ArrowRight className="h-3.5 w-3.5 text-[#B7FF00] -ml-1 shrink-0" />
                    </div>
                  </div>
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
                      Step 1
                    </span>
                    <h3 className="text-sm font-heading font-bold text-[#080808] dark:text-[#F5F5F7] mt-0.5">
                      Big Data
                    </h3>
                    <p className="text-xs text-[#666666] dark:text-[#A1A1AA] mt-1 leading-snug">
                      Ingest and process real NYC logistics data.
                    </p>
                  </div>
                </div>

                {/* Step 2 — Quantum + Classical */}
                <div className="space-y-2.5">
                  <div className="flex items-center justify-between">
                    <div className="h-10 w-10 rounded-2xl bg-black/5 dark:bg-[#18181B] border border-transparent dark:border-[#29292E] flex items-center justify-center text-[#080808] dark:text-[#B7FF00]">
                      <Cpu className="h-5 w-5" />
                    </div>
                    <div className="hidden sm:flex flex-1 items-center px-2">
                      <div className="h-[1px] flex-1 bg-[#B7FF00]" />
                      <ArrowRight className="h-3.5 w-3.5 text-[#B7FF00] -ml-1 shrink-0" />
                    </div>
                  </div>
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
                      Step 2
                    </span>
                    <h3 className="text-sm font-heading font-bold text-[#080808] dark:text-[#F5F5F7] mt-0.5">
                      Quantum + Classical
                    </h3>
                    <p className="text-xs text-[#666666] dark:text-[#A1A1AA] mt-1 leading-snug">
                      Optimize routes using supported classical and quantum-classical algorithms.
                    </p>
                  </div>
                </div>

                {/* Step 3 — Optimized Routes */}
                <div className="space-y-2.5">
                  <div className="flex items-center justify-between">
                    <div className="h-10 w-10 rounded-2xl bg-black/5 dark:bg-[#18181B] border border-transparent dark:border-[#29292E] flex items-center justify-center text-[#080808] dark:text-[#B7FF00]">
                      <Route className="h-5 w-5" />
                    </div>
                  </div>
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A] block">
                      Step 3
                    </span>
                    <h3 className="text-sm font-heading font-bold text-[#080808] dark:text-[#F5F5F7] mt-0.5">
                      Optimized Routes
                    </h3>
                    <p className="text-xs text-[#666666] dark:text-[#A1A1AA] mt-1 leading-snug">
                      Generate feasible, efficient delivery plans.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column (5 cols): Route Simulation Video Preview */}
          <div className="lg:col-span-5 h-[340px] sm:h-[370px] rounded-3xl overflow-hidden border border-black/10 dark:border-[#29292E] shadow-sm relative bg-[#080808] group flex items-center justify-center">
            <video
              src="/delivery_route_preview.mp4"
              autoPlay
              loop
              muted
              playsInline
              className="w-full h-full object-cover"
            />

            {/* Subtle Legend / Telemetry Badge */}
            <div className="absolute bottom-3 left-3 bg-white/90 dark:bg-[#18181B]/90 backdrop-blur-md px-3 py-1.5 rounded-full text-[10px] z-10 border border-black/10 dark:border-[#29292E] flex items-center gap-2 shadow-xs">
              <span className="h-2 w-2 rounded-full bg-[#B7FF00] border border-black animate-pulse" />
              <span className="font-semibold text-[#080808] dark:text-[#F5F5F7]">Live Route Simulation</span>
            </div>
          </div>
        </div>
      </section>

      {/* ─── GLASSMORPHIC SECTION TRANSITION BRIDGE (How It Works → Research) ─── */}
      <div className="glass-section-bridge my-6 relative z-10">
        <div className="glass-section-bridge-bar" />
        <div className="absolute left-1/2 -translate-x-1/2 -translate-y-1/2 top-1/2 glass-floating-pill px-5 py-2 rounded-full flex items-center gap-2.5 text-[10px] font-bold tracking-widest uppercase text-[#555555] dark:text-[#A1A1AA] shadow-xs cursor-default">
          <span className="h-2 w-2 rounded-full bg-[#B7FF00] animate-pulse" />
          <span>Research Foundations & Publications</span>
        </div>
      </div>

      {/* ─────────────────────────────────────────────────────────────
          3. EXPLORE THE RESEARCH
          Spacious card container with translucent glass styling
          ───────────────────────────────────────────────────────────── */}
      <section className="breathy-scroll-section p-6 sm:p-8 lg:p-10 rounded-3xl bg-white/70 dark:bg-[#111113] backdrop-blur-xl border border-white/80 dark:border-[#29292E] shadow-sm space-y-6">
        <span className="text-xs font-bold uppercase tracking-widest text-[#777777] dark:text-[#71717A] block">
          EXPLORE THE RESEARCH
        </span>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-0 lg:divide-x lg:divide-black/10 dark:lg:divide-[#29292E]">
          {/* Resource 1 — Our Research Paper */}
          <div className="lg:pr-6 space-y-2">
            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4 text-[#B7FF00]" />
              <h4 className="text-sm font-heading font-bold text-[#080808] dark:text-[#F5F5F7]">
                Our Research Paper
              </h4>
            </div>
            <p className="text-xs text-[#666666] dark:text-[#A1A1AA] leading-relaxed">
              Read our drafted UROP survey & research paper on hybrid quantum-classical vehicle routing.
            </p>
            <a
              href="/papers/literature_survey.pdf"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs font-bold text-[#080808] dark:text-[#B7FF00] hover:underline pt-1 cursor-pointer"
            >
              <span>Read Paper Draft (PDF)</span>
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>

          {/* Resource 2 — Watch & Learn */}
          <div className="lg:px-6 space-y-2">
            <div className="flex items-center gap-2">
              <PlayCircle className="h-4 w-4 text-[#B7FF00]" />
              <h4 className="text-sm font-heading font-bold text-[#080808] dark:text-[#F5F5F7]">
                Watch & Learn
              </h4>
            </div>
            <p className="text-xs text-[#666666] dark:text-[#A1A1AA] leading-relaxed">
              Watch relevant lectures & demonstrations on QAOA and vehicle routing optimization.
            </p>
            <button
              onClick={() => setShowVideoModal(true)}
              className="inline-flex items-center gap-1.5 text-xs font-bold text-[#080808] dark:text-[#B7FF00] hover:underline pt-1 cursor-pointer"
            >
              <span>Watch Video Walkthroughs</span>
              <ExternalLink className="h-3 w-3" />
            </button>
          </div>

          {/* Resource 3 — Reference Papers */}
          <div className="lg:px-6 space-y-2">
            <div className="flex items-center gap-2">
              <BookOpen className="h-4 w-4 text-[#B7FF00]" />
              <h4 className="text-sm font-heading font-bold text-[#080808] dark:text-[#F5F5F7]">
                Reference Papers
              </h4>
            </div>
            <p className="text-xs text-[#666666] dark:text-[#A1A1AA] leading-relaxed">
              Published papers used as key references: PAQS, IQGA, and QAOA for VRP.
            </p>
            <button
              onClick={() => setShowPapersModal(true)}
              className="inline-flex items-center gap-1.5 text-xs font-bold text-[#080808] dark:text-[#B7FF00] hover:underline pt-1 cursor-pointer"
            >
              <span>Inspect Reference Literature</span>
              <ExternalLink className="h-3 w-3" />
            </button>
          </div>

          {/* Resource 4 / Final link — View More Papers */}
          <div className="lg:pl-6 space-y-2 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2">
                <GraduationCap className="h-4 w-4 text-[#B7FF00]" />
                <h4 className="text-sm font-heading font-bold text-[#080808] dark:text-[#F5F5F7]">
                  Research Library
                </h4>
              </div>
              <p className="text-xs text-[#666666] dark:text-[#A1A1AA] leading-relaxed mt-1">
                Complete list of all reference papers with publication notes and source links.
              </p>
            </div>
            <button
              onClick={() => setShowPapersModal(true)}
              className="inline-flex items-center gap-1.5 text-xs font-bold text-[#080808] dark:text-[#B7FF00] hover:underline pt-1 cursor-pointer group"
            >
              <span>View More Papers</span>
              <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-1" />
            </button>
          </div>
        </div>
      </section>

      {/* ─────────────────────────────────────────────────────────────
          4. REFINED INTEGRATED FOOTER
          Preserved untouched as specified in requirements.
          ───────────────────────────────────────────────────────────── */}
      <footer className="pt-8 mt-12 border-t border-black/10 dark:border-[#29292E] flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#777777] dark:text-[#A1A1AA]">
        <div className="flex items-center gap-2.5">
          <img
            src="/logo.png"
            alt="ROUTE/IQ Logo"
            className="h-6 w-6 rounded-lg object-cover border border-black/10 dark:border-[#29292E] shadow-xs"
          />
          <span className="font-heading font-bold text-sm tracking-wider text-[#080808] dark:text-[#F5F5F7]">
            ROUTE/IQ
          </span>
          <span className="text-black/20 dark:text-white/20">|</span>
          <span className="text-[#666666] dark:text-[#A1A1AA]">
            Smart Delivery Route Optimization System
          </span>
        </div>

        <div className="flex items-center gap-6">
          <button
            onClick={() => onNavigate('plan')}
            className="hover:text-[#080808] dark:hover:text-[#B7FF2A] font-medium transition-colors cursor-pointer"
          >
            Plan Deliveries
          </button>
          <button
            onClick={() => onNavigate('datasets')}
            className="hover:text-[#080808] dark:hover:text-[#B7FF2A] font-medium transition-colors cursor-pointer"
          >
            Datasets
          </button>
          <button
            onClick={() => onNavigate('results')}
            className="hover:text-[#080808] dark:hover:text-[#B7FF2A] font-medium transition-colors cursor-pointer"
          >
            Results
          </button>
          <button
            onClick={() => onNavigate('experiments')}
            className="hover:text-[#080808] dark:hover:text-[#B7FF2A] font-medium transition-colors cursor-pointer"
          >
            Experiments
          </button>
          <button
            onClick={() => onNavigate('settings')}
            className="hover:text-[#080808] dark:hover:text-[#B7FF2A] font-medium transition-colors cursor-pointer"
          >
            Settings
          </button>
        </div>
      </footer>

      {/* ─────────────────────────────────────────────────────────────
          MODAL: RESEARCH PAPERS LIBRARY
          Dedicated dialog listing our paper draft and all published references
          ───────────────────────────────────────────────────────────── */}
      {/* ─────────────────────────────────────────────────────────────
          MODAL: RESEARCH PAPERS LIBRARY
          Dedicated dialog listing our paper draft and all published references
          ───────────────────────────────────────────────────────────── */}
      {showPapersModal &&
        createPortal(
          <div
            className="fixed inset-0 bg-black/40 backdrop-blur-[2px] flex items-center justify-center p-4 sm:p-6 z-[99999] animate-fadeIn"
            onClick={() => setShowPapersModal(false)}
          >
            <div
              className="bg-white dark:bg-[#111113] border border-black/10 dark:border-[#29292E] rounded-3xl max-w-3xl w-full p-6 sm:p-8 shadow-2xl dark:shadow-[0_24px_64px_rgba(0,0,0,0.85)] space-y-6 max-h-[85vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="flex items-start justify-between pb-4 border-b border-black/10 dark:border-[#29292E]">
                <div className="space-y-1">
                  <div className="inline-flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-[#B7FF00]" />
                    <span className="text-[11px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A]">
                      Academic Literature & Survey
                    </span>
                  </div>
                  <h3 className="text-xl sm:text-2xl font-heading font-bold text-[#080808] dark:text-[#F5F5F7]">
                    Research Papers & Reference Library
                  </h3>
                  <p className="text-xs text-[#777777] dark:text-[#A1A1AA]">
                    Curated literature collection supporting ROUTE/IQ: including our drafted UROP survey and published reference papers.
                  </p>
                </div>

                <button
                  onClick={() => setShowPapersModal(false)}
                  className="h-8 w-8 rounded-full flex items-center justify-center bg-black/5 dark:bg-[#18181B] hover:bg-black/10 dark:hover:bg-[#202024] text-[#080808] dark:text-[#F5F5F7] border border-transparent dark:border-[#29292E] transition-colors cursor-pointer text-sm font-bold"
                  title="Close"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              {/* Papers List */}
              <div className="space-y-4">
                {RESEARCH_PAPERS.map((paper) => (
                  <div
                    key={paper.id}
                    className={`p-4 sm:p-5 rounded-2xl border transition-all ${
                      paper.category === 'draft'
                        ? 'bg-[#B7FF00]/10 dark:bg-[#B7FF00]/5 border-[#B7FF00]/40'
                        : 'bg-black/[0.02] dark:bg-[#18181B] border-black/10 dark:border-[#29292E]'
                    }`}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                      <div className="space-y-1 flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                              paper.category === 'draft'
                                ? 'bg-[#080808] text-[#B7FF00] dark:bg-[#B7FF00] dark:text-[#000000]'
                                : 'bg-black/5 dark:bg-[#202024] text-[#777777] dark:text-[#A1A1AA]'
                            }`}
                          >
                            {paper.category === 'draft' ? 'Our Project Draft' : 'Published Reference Paper'}
                          </span>
                          <span className="text-[11px] font-semibold text-[#777777] dark:text-[#A1A1AA]">
                            {paper.venue} · {paper.year}
                          </span>
                        </div>

                        <h4 className="text-sm sm:text-base font-heading font-bold text-[#080808] dark:text-[#F5F5F7]">
                          {paper.title}
                        </h4>

                        <p className="text-xs text-[#555555] dark:text-[#A1A1AA] leading-relaxed pt-0.5">
                          {paper.description}
                        </p>

                        <div className="text-[11px] text-[#777777] dark:text-[#71717A] pt-1">
                          <strong>Project Relevance:</strong> {paper.relevance}
                        </div>
                      </div>

                      <a
                        href={`/papers/${paper.filename}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-full bg-[#080808] hover:bg-[#171717] dark:bg-[#B7FF00] dark:hover:bg-[#a3e600] text-[#B7FF00] dark:text-black text-xs font-bold transition-all cursor-pointer shrink-0 self-start sm:self-center"
                      >
                        <Download className="h-3.5 w-3.5" />
                        <span>Open PDF</span>
                      </a>
                    </div>
                  </div>
                ))}
              </div>

              {/* Modal Footer */}
              <div className="pt-2 flex justify-end border-t border-black/10 dark:border-[#29292E]">
                <button
                  onClick={() => setShowPapersModal(false)}
                  className="px-5 py-2.5 bg-[#080808] hover:bg-[#171717] dark:bg-[#18181B] dark:hover:bg-[#202024] border border-transparent dark:border-[#29292E] text-[#B7FF00] rounded-xl text-xs font-bold transition-all cursor-pointer"
                >
                  Close Library
                </button>
              </div>
            </div>
          </div>,
          document.body
        )}

      {/* ─────────────────────────────────────────────────────────────
          MODAL: WATCH & LEARN VIDEOS
          ───────────────────────────────────────────────────────────── */}
      {showVideoModal &&
        createPortal(
          <div
            className="fixed inset-0 bg-black/40 backdrop-blur-[2px] flex items-center justify-center p-4 sm:p-6 z-[99999] animate-fadeIn"
            onClick={() => setShowVideoModal(false)}
          >
            <div
              className="bg-white dark:bg-[#111113] border border-black/10 dark:border-[#29292E] rounded-3xl max-w-2xl w-full p-6 sm:p-8 shadow-2xl dark:shadow-[0_24px_64px_rgba(0,0,0,0.85)] space-y-6 max-h-[85vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-start justify-between pb-4 border-b border-black/10 dark:border-[#29292E]">
                <div className="space-y-1">
                  <div className="inline-flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-[#B7FF00]" />
                    <span className="text-[11px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A]">
                      Educational Walkthroughs
                    </span>
                  </div>
                  <h3 className="text-xl sm:text-2xl font-heading font-bold text-[#080808] dark:text-[#F5F5F7]">
                    Watch & Learn: Quantum & Logistics Optimization
                  </h3>
                </div>

                <button
                  onClick={() => setShowVideoModal(false)}
                  className="h-8 w-8 rounded-full flex items-center justify-center bg-black/5 dark:bg-[#18181B] hover:bg-black/10 dark:hover:bg-[#202024] text-[#080808] dark:text-[#F5F5F7] border border-transparent dark:border-[#29292E] transition-colors cursor-pointer text-sm font-bold"
                  title="Close"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              <div className="space-y-3">
                {VIDEO_RESOURCES.map((video, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-2xl border border-black/10 dark:border-[#29292E] bg-black/[0.02] dark:bg-[#18181B] flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <PlayCircle className="h-4 w-4 text-red-500" />
                        <span className="text-[11px] font-semibold text-[#777777] dark:text-[#A1A1AA]">
                          {video.channel} · {video.duration}
                        </span>
                      </div>
                      <h4 className="text-sm font-heading font-bold text-[#080808] dark:text-[#F5F5F7]">
                        {video.title}
                      </h4>
                      <p className="text-xs text-[#666666] dark:text-[#A1A1AA]">
                        {video.description}
                      </p>
                    </div>

                    <a
                      href={video.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-[#080808] hover:bg-[#171717] dark:bg-[#B7FF00] dark:hover:bg-[#a3e600] text-[#B7FF00] dark:text-black text-xs font-bold transition-all cursor-pointer shrink-0 self-start sm:self-center"
                    >
                      <span>Watch Video</span>
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </div>
                ))}
              </div>

              <div className="pt-2 flex justify-end border-t border-black/10 dark:border-[#29292E]">
                <button
                  onClick={() => setShowVideoModal(false)}
                  className="px-5 py-2.5 bg-[#080808] hover:bg-[#171717] dark:bg-[#18181B] dark:hover:bg-[#202024] border border-transparent dark:border-[#29292E] text-[#B7FF00] rounded-xl text-xs font-bold transition-all cursor-pointer"
                >
                  Close
                </button>
              </div>
            </div>
          </div>,
          document.body
        )}
    </div>
  );
};

export default OverviewDashboard;
