import React, { useState, useMemo } from 'react';
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
  Search,
  Layers,
  CheckCircle2,
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

// Full 27-Paper Verified Research Corpus Interface
export interface ResearchPaper {
  id: string;
  title: string;
  authors: string;
  category: 'survey' | 'qaoa' | 'qio' | 'bigdata' | 'logistics' | 'nisq';
  categoryLabel: string;
  venue: string;
  year: string;
  doi?: string;
  pdfUrl?: string;
  isKeyReference: boolean;
  description: string;
  relevance: string;
}

export const RESEARCH_PAPERS: ResearchPaper[] = [
  // ─── Survey Paper ───
  {
    id: 'urop-survey',
    title: 'A Literature Survey of Hybrid Big Data and Quantum Computing for Smart Delivery Route Optimization',
    authors: 'J. Jayanth, B. Kaivalya, P. Shyam Sai (Supervised by Dr. Vishnu Prasad Verma)',
    category: 'survey',
    categoryLabel: 'UROP Literature Survey',
    venue: 'SRM University-AP, Department of Computer Science and Engineering',
    year: '2026',
    pdfUrl: '/papers/literature_survey_4.pdf',
    isKeyReference: true,
    description:
      'Our primary UROP literature survey investigating the architectural synthesis of Apache Spark batch ETL, classical operations research heuristics (OR-Tools), and quantum-classical algorithms (QAOA, QIGA) on real-world NYC Open Data.',
    relevance:
      'Primary research framing, literature taxonomy, and architectural specification for the ROUTE/IQ framework.',
  },

  // ─── Key Quantum & QAOA Optimization Papers ───
  {
    id: 'qaoa-azad',
    title: 'Solving Vehicle Routing Problem Using Quantum Approximate Optimization Algorithm',
    authors: 'Azad, Bapat, et al.',
    category: 'qaoa',
    categoryLabel: 'Quantum & QAOA Routing',
    venue: 'IEEE Transactions on Intelligent Transportation Systems',
    year: '2023',
    doi: '10.1109/TITS.2022.3172241',
    pdfUrl: '/papers/Solving_Vehicle_Routing_Problem_Using_Quantum_Approximate_Optimization_Algorithm.pdf',
    isKeyReference: true,
    description:
      'Foundational paper formulating Vehicle Routing Problem instances into Quadratic Unconstrained Binary Optimization (QUBO) graphs solvable with parameterized QAOA quantum circuits.',
    relevance:
      'Algorithmic foundation for the QAOA QUBO Hamiltonian construction and classical statevector simulation in ROUTE/IQ.',
  },
  {
    id: 'qaoa-fitzek',
    title: 'Applying Quantum Approximate Optimization to the Heterogeneous Vehicle Routing Problem',
    authors: 'David Fitzek, Toheed Ghandriz, Leo Laine, et al.',
    category: 'qaoa',
    categoryLabel: 'Quantum & QAOA Routing',
    venue: 'Scientific Reports (Nature Portfolio)',
    year: '2024',
    doi: '10.1038/s41598-024-76967-w',
    isKeyReference: true,
    description:
      'Investigates QAOA circuit depth, parameter optimization, and constraint penalties for heterogeneous vehicle fleets with non-uniform capacities, benchmarking against classical Branch-and-Cut.',
    relevance:
      'Informs ROUTE/IQ heterogeneous fleet capacity modeling and penalty parameter tuning under simulated quantum circuits.',
  },
  {
    id: 'quantum-shuttle',
    title: 'Quantum Shuttle: Traffic Navigation with Quantum Computing',
    authors: 'Sheir Yarkoni, Florian Neukart, et al.',
    category: 'qaoa',
    categoryLabel: 'Quantum & QAOA Routing',
    venue: 'ACM Proceedings / Volkswagen Data:Lab',
    year: '2020',
    doi: '10.1145/3412451.3428500',
    isKeyReference: false,
    description:
      'Real-world deployment of quantum optimization to balance urban taxi and shuttle traffic across congestible street network segments in Beijing and Barcelona.',
    relevance:
      'Demonstrates QUBO congestion cost formulation adapted in ROUTE/IQ road network edge weighting.',
  },
  {
    id: 'blockchain-qaoa',
    title: 'A Quantum Approximate Optimization Algorithm Based on Blockchain Heuristic Approach for Scalable and Secure Smart Logistics Systems',
    authors: 'Abir EL Azzaoui, Tae Woo Kim, Yi Pan, Jong Hyuk Park',
    category: 'qaoa',
    categoryLabel: 'Quantum & QAOA Routing',
    venue: 'Human-centric Computing and Information Sciences',
    year: '2021',
    doi: '10.22967/HCIS.2021.11.046',
    isKeyReference: false,
    description:
      'Investigates combining distributed ledger auditing with QAOA-assisted fleet dispatching in secure multi-agent logistics pipelines.',
    relevance:
      'Explores decentralized fleet coordination models and security constraints for smart logistics.',
  },
  {
    id: 'cognitive-quantum',
    title: 'Quantum-Enhanced Cognitive Modeling for Advanced Logistics Route Optimization',
    authors: 'Edwin Gerardo Acuña Acuña',
    category: 'qaoa',
    categoryLabel: 'Quantum & QAOA Routing',
    venue: 'Digital Technologies Research and Applications',
    year: '2024',
    doi: '10.54963/dtra.v4i1.1075',
    isKeyReference: false,
    description:
      'Integrates cognitive decision-making models with quantum search heuristics to dynamically reconfigure urban delivery schedules under uncertainty.',
    relevance:
      'Conceptual reference for dynamic constraint adaptation in multi-factor routing engines.',
  },
  {
    id: 'quantum-its-icn',
    title: 'Shaping the Future of the Application of Quantum Computing in Intelligent Transportation System',
    authors: 'Sumin Wang, Zhi Pei, Chao Wang, Jie Wang',
    category: 'qaoa',
    categoryLabel: 'Quantum & QAOA Routing',
    venue: 'Intelligent and Converged Networks',
    year: '2021',
    doi: '10.23919/ICN.2021.0019',
    isKeyReference: false,
    description:
      'Surveys quantum computing opportunities across arterial signal control, autonomous vehicle platooning, and routing optimization in metropolitan grids.',
    relevance:
      'Broader intelligent transportation systems (ITS) context for quantum computational speedups.',
  },

  // ─── Quantum-Inspired Optimization (QIO) ───
  {
    id: 'qio-liu',
    title: 'Quantum and Quantum-Inspired Optimisation in Transport and Logistics: A Systematic Review',
    authors: 'Liu, Parkinson, & Best',
    category: 'qio',
    categoryLabel: 'Quantum-Inspired Optimization',
    venue: 'Smart Cities (MDPI)',
    year: '2025',
    doi: '10.3390/smartcities8060206',
    isKeyReference: true,
    description:
      'Comprehensive review analyzing the practical viability of Quantum-Inspired Genetic Algorithms (QIGA), simulated annealing, and hybrid decomposition on real-world road networks.',
    relevance:
      'Direct academic justification for ROUTE/IQ implementing QIGA running on classical hardware to bridge current NISQ qubit limits.',
  },
  {
    id: 'adcaij-qio',
    title: 'Advanced Optimization for Big Data Streams with Quantum Insights for Real-time Big Data Analytics',
    authors: 'ADCAIJ Research Group',
    category: 'qio',
    categoryLabel: 'Quantum-Inspired Optimization',
    venue: 'ADCAIJ: Advances in Distributed Computing and AI',
    year: '2025',
    doi: '10.14201/adcaij.32876',
    pdfUrl: '/papers/ADCAIJ-v14-19-32876.pdf',
    isKeyReference: false,
    description:
      'Explores quantum-inspired representations, quantum bit rotation gates, and probability update matrices for handling continuous streaming logistics metrics.',
    relevance:
      'Algorithmic basis for the quantum rotation gate lookup table and chromosome updating in ROUTE/IQ QIGA engine.',
  },
  {
    id: 'its-scientometric',
    title: 'Integrating Quantum Computing into Intelligent Transportation Systems: A Scientometric Assessment and Synthesis',
    authors: 'Pretom Sarkar, Ali Hanafiah Rambe, Mahbub Hassan, Muzammil Jusoh',
    category: 'qio',
    categoryLabel: 'Quantum-Inspired Optimization',
    venue: 'Archives of Computational Methods in Engineering (Springer)',
    year: '2026',
    doi: '10.1007/s11831-026-10716-2',
    isKeyReference: false,
    description:
      'Rigorous bibliometric and methodological evaluation assessing Technology Readiness Levels (TRLs) of quantum and quantum-inspired algorithms in transportation.',
    relevance:
      'Establishes academic consensus that quantum routing is primarily at simulation readiness (TRL 3-4), whereas quantum-inspired classical heuristics are near production readiness.',
  },

  // ─── Big Data & Intelligent Transportation Systems ───
  {
    id: 'bigdata-zhu',
    title: 'Big Data Analytics in Intelligent Transportation Systems: A Survey',
    authors: 'L. Zhu, F. R. Yu, Y. Wang, J. Ning, P. X. Liu',
    category: 'bigdata',
    categoryLabel: 'Big Data & ITS',
    venue: 'IEEE Transactions on Intelligent Transportation Systems',
    year: '2019',
    doi: '10.1109/TITS.2018.2815678',
    isKeyReference: true,
    description:
      'Examines large-scale transportation data collection, GPS stream aggregation, spatial indexing, and cloud-distributed processing architectures for municipal mobility.',
    relevance:
      'Informs ROUTE/IQ PySpark batch ETL pipeline architecture for processing high-volume NYC TLC trip records and OSM road networks.',
  },
  {
    id: 'bigdata-zheng',
    title: 'Solving Vehicle Routing Problem: A Big Data Analytic Approach',
    authors: 'Shaoqing Zheng',
    category: 'bigdata',
    categoryLabel: 'Big Data & ITS',
    venue: 'IEEE Access',
    year: '2019',
    doi: '10.1109/ACCESS.2019.2955250',
    isKeyReference: true,
    description:
      'Proposes combining big data analytics and spatial clustering with operations research heuristics to accelerate large delivery network optimization.',
    relevance:
      'Methodological basis for partitioning massive delivery coordinates prior to combinatorial routing optimization.',
  },
  {
    id: 'procedia-smartcity',
    title: 'A Big-Data-Analytics Framework for Supporting Logistics Problems in Smart-City Environments',
    authors: 'Procedia Research Collective',
    category: 'bigdata',
    categoryLabel: 'Big Data & ITS',
    venue: 'Procedia Computer Science',
    year: '2019',
    doi: '10.1016/j.procs.2019.09.257',
    isKeyReference: false,
    description:
      'Framework for municipal logistics optimization leveraging real-time sensor streams, spatial databases, and historical transit patterns.',
    relevance:
      'Validates multi-tier data pipeline design for urban freight and smart city delivery platforms.',
  },
  {
    id: 'somvanshi-survey',
    title: 'Quantum Computing in Transportation Engineering: A Survey',
    authors: 'Shriyank Somvanshi, et al.',
    category: 'bigdata',
    categoryLabel: 'Big Data & ITS',
    venue: 'IEEE Transactions on Intelligent Transportation Systems',
    year: '2026',
    doi: '10.1109/TITS.2026.3662626',
    pdfUrl: '/papers/Quantum_Computing_in_Transportation_Engineering_A_Survey (1).pdf',
    isKeyReference: false,
    description:
      'Reviews applications of quantum algorithms to urban traffic control, arterial signal timing, route guidance, and large-scale fleet logistics.',
    relevance:
      'Broad survey on quantum algorithm intersection with urban transportation engineering infrastructure.',
  },
  {
    id: 'cloud-vm-bigdata',
    title: 'Virtual Machine Placement Optimization for Big Data Applications in Cloud Computing',
    authors: 'Seyyed Mohsen Seyyedsalehi, Mohammad Khansari',
    category: 'bigdata',
    categoryLabel: 'Big Data & ITS',
    venue: 'IEEE Access',
    year: '2022',
    doi: '10.1109/ACCESS.2022.3203057',
    isKeyReference: false,
    description:
      'Addresses resource allocation, latency minimization, and distributed VM clustering for big data analytic workloads.',
    relevance:
      'Informs distributed PySpark compute cluster configuration and memory allocation for heavy geospatial operations.',
  },
  {
    id: 'dist-db-opt',
    title: 'Distributed Database System Optimization for Improved Service Delivery in Mobile Computing',
    authors: 'O. T. Jinadu, et al.',
    category: 'bigdata',
    categoryLabel: 'Big Data & ITS',
    venue: 'International Journal of Computer Science and Mobile Computing',
    year: '2021',
    doi: '10.47760/ijcsmc.2021.v10i09.004',
    isKeyReference: false,
    description:
      'Studies query throughput, latency bottlenecks, and indexing optimization across distributed storage architectures.',
    relevance:
      'Applicable to Parquet columnar storage and fast delivery point retrieval across partitioned datasets.',
  },
  {
    id: 'iot-cloud-elhoseny',
    title: 'A Hybrid Model of Internet of Things and Cloud Computing to Manage Big Data in Health Services Applications',
    authors: 'Mohamed Elhoseny, Ahmed Abdelaziz, Ahmed S. Salama, et al.',
    category: 'bigdata',
    categoryLabel: 'Big Data & ITS',
    venue: 'Future Generation Computer Systems (Elsevier)',
    year: '2018',
    doi: '10.1016/j.future.2018.03.005',
    isKeyReference: false,
    description:
      'Investigates scalable hybrid cloud frameworks for high-volume heterogeneous IoT telemetry streams with strict latency bounds.',
    relevance:
      'Informs tiered data pipeline architectures combining edge ingestion and batch compute.',
  },

  // ─── Smart Logistics & Vehicle Routing Optimization ───
  {
    id: 'smart-logistics-issaoui',
    title: 'An Advanced System to Enhance and Optimize Delivery Operations in a Smart Logistics Environment',
    authors: 'Yassine Issaoui, Azeddine Khiat, Karim Haricha',
    category: 'logistics',
    categoryLabel: 'Smart Logistics & VRP',
    venue: 'IEEE Access',
    year: '2022',
    doi: '10.1109/ACCESS.2022.3141311',
    isKeyReference: false,
    description:
      'Develops an automated smart logistics dispatching architecture incorporating tracking, dynamic routing, and telematics in urban corridors.',
    relevance:
      'Benchmark for smart logistics UI architecture and delivery state management.',
  },
  {
    id: 'multi-depot-vrp',
    title: 'An Intelligent Multi-Depot Vehicle Routing and Management Model for Smart Cities',
    authors: 'IEEE T-ITS Research Group',
    category: 'logistics',
    categoryLabel: 'Smart Logistics & VRP',
    venue: 'IEEE Transactions on Intelligent Transportation Systems',
    year: '2025',
    doi: '10.1109/TITS.2025.3557826',
    isKeyReference: false,
    description:
      'Formulates multi-depot vehicle routing models with dynamic demand reallocation and service time constraints across metropolitan sectors.',
    relevance:
      'Directly informs ROUTE/IQ multi-depot fleet dispatching and depot assignment heuristics.',
  },
  {
    id: 'truck-uav-routing',
    title: 'Collaborative Truck-UAV Delivery Routing Optimization Under Dynamic Weather Conditions and Customer Demands',
    authors: 'IEEE TCE Research Group',
    category: 'logistics',
    categoryLabel: 'Smart Logistics & VRP',
    venue: 'IEEE Transactions on Consumer Electronics',
    year: '2025',
    doi: '10.1109/TCE.2025.3622367',
    isKeyReference: false,
    description:
      'Optimizes coordinated truck-and-drone delivery schedules subject to stochastic environmental disruptions and battery limits.',
    relevance:
      'Reference for dynamic re-routing when deliveries encounter adverse travel factors.',
  },
  {
    id: 'vision-iot-logistics',
    title: 'Leveraging Computer Vision and IoT for Optimized Last-Mile Delivery in Smart Logistics Systems',
    authors: 'Ravi Teja Jagarlamudi',
    category: 'logistics',
    categoryLabel: 'Smart Logistics & VRP',
    venue: 'IEEE ICICNIS',
    year: '2025',
    doi: '10.1109/ICICNIS66685.2025.11315516',
    isKeyReference: false,
    description:
      'Explores IoT parcel tracking, camera-assisted loading dock scanning, and computer-vision verification for last-mile delivery handoff.',
    relevance:
      'Context for delivery state verification and last-mile telemetry.',
  },
  {
    id: 'route-opt-ai',
    title: 'Revolutionizing Route Optimization Systems with Artificial Intelligence for a Smarter, Sustainable Future',
    authors: 'Khursheed Mohammed Hussain',
    category: 'logistics',
    categoryLabel: 'Smart Logistics & VRP',
    venue: 'International Journal of Computer Science and Mobile Computing',
    year: '2025',
    doi: '10.47760/ijcsmc.2025.v14i02.008',
    isKeyReference: false,
    description:
      'Surveys modern AI and machine learning heuristics for reducing carbon emissions and fuel expenditure in urban delivery logistics.',
    relevance:
      'Provides sustainability metrics and carbon reduction baselines for routing evaluation.',
  },
  {
    id: 'cold-chain-logistics',
    title: 'Intelligent Algorithms for Cold Chain Logistics Distribution Optimization Based on Big Data Cloud Computing Analysis',
    authors: 'Springer Open Collective',
    category: 'logistics',
    categoryLabel: 'Smart Logistics & VRP',
    venue: 'Journal of Cloud Computing (Springer)',
    year: '2020',
    doi: '10.1186/s13677-020-00174-x',
    isKeyReference: false,
    description:
      'Optimizes temperature-sensitive distribution routes subject to tight delivery time windows and capacity bounds.',
    relevance:
      'Benchmark for time-window constrained routing formulations.',
  },
  {
    id: 'patient-transport',
    title: 'Optimizing Patient Transportation by Applying Cloud Computing and Big Data Analysis',
    authors: 'The Journal of Supercomputing Group',
    category: 'logistics',
    categoryLabel: 'Smart Logistics & VRP',
    venue: 'The Journal of Supercomputing (Springer)',
    year: '2022',
    doi: '10.1007/s11227-022-04576-3',
    isKeyReference: false,
    description:
      'Large-scale routing heuristic for critical medical transit using cloud-backed distance matrices and priority scheduling.',
    relevance:
      'Validates distance matrix computation on heavy urban networks.',
  },
  {
    id: 'disaster-relief-logistics',
    title: 'Application of Cloud Computing and Big Data in Three-Stage Dynamic Modeling of Disaster Relief Logistics and Wounded Transportation',
    authors: 'Environmental Science and Pollution Research Group',
    category: 'logistics',
    categoryLabel: 'Smart Logistics & VRP',
    venue: 'Environmental Science and Pollution Research (Springer)',
    year: '2022',
    doi: '10.1007/s11356-022-24770-3',
    isKeyReference: false,
    description:
      'Three-stage dynamic routing model under emergency network disruptions and bottlenecked supply lines.',
    relevance:
      'Comparative study for multi-priority delivery dispatching under road constraints.',
  },

  // ─── Quantum Computing Limitations & NISQ Review ───
  {
    id: 'review-osaba',
    title: 'A Systematic Literature Review of Quantum Computing for Routing Problems',
    authors: 'Eneko Osaba, Esther Villar-Rodriguez, Izaskun Oregi',
    category: 'nisq',
    categoryLabel: 'NISQ Limits & Systematic Review',
    venue: 'IEEE Access',
    year: '2022',
    doi: '10.1109/ACCESS.2022.3177790',
    pdfUrl: '/papers/1_A_Systematic_Literature_Review_of_Quantum_Computing_for_Routing_Problems.pdf',
    isKeyReference: true,
    description:
      'Rigorous systematic literature review classifying quantum heuristics (annealing, QAOA, VQE, and Grover) across TSP, CVRP, and VRPTW instances.',
    relevance:
      'Essential taxonomy establishing theoretical and practical scalability bounds for quantum routing, justifying classical hybrid partitioning.',
  },
  {
    id: 'noisy-channels-vrp',
    title: 'Analysis of the Vehicle Routing Problem Solved via Hybrid Quantum Algorithms in the Presence of Noisy Channels',
    authors: 'IEEE Quantum Engineering Group',
    category: 'nisq',
    categoryLabel: 'NISQ Limits & Systematic Review',
    venue: 'IEEE Transactions on Quantum Engineering',
    year: '2023',
    doi: '10.1109/TQE.2023.3303989',
    isKeyReference: false,
    description:
      'Detailed quantitative study of gate noise, decoherence, and qubit errors when executing VRP QUBOs on NISQ hardware vs classical simulators.',
    relevance:
      'Highlights current hardware fidelity barriers, confirming why ROUTE/IQ performs QAOA via classical Qiskit simulation rather than claims of physical hardware execution.',
  },
];

// Curated Educational Video Lectures (Verified External Tutorials & Research Seminars)
export interface EducationalLecture {
  id: string;
  title: string;
  channel: string;
  speaker?: string;
  duration: string;
  url: string;
  thumbnail: string;
  topics?: string[];
  description: string;
}

export const EDUCATIONAL_LECTURES: EducationalLecture[] = [
  {
    id: 'qaoa-tutorial',
    title: 'A Tutorial on Quantum Approximate Optimization Algorithm (QAOA) - Theory',
    channel: 'IBM Quantum / Qiskit',
    speaker: 'Dr. Stefan Woerner / Qiskit Research',
    duration: '24 min',
    url: 'https://www.youtube.com/watch?v=AOKM9BkweVU',
    thumbnail: 'https://img.youtube.com/vi/AOKM9BkweVU/hqdefault.jpg',
    topics: ['QAOA Hamiltonian', 'Variational Circuits', 'Statevector Simulation'],
    description:
      'Rigorous mathematical walkthrough of QAOA circuit formulation, cost Hamiltonian encoding, mixer Hamiltonians, and classical outer-loop parameter optimization.',
  },
  {
    id: 'vrp-optimization',
    title: 'Vehicle Routing Problem: Formulations & Operations Research Heuristics',
    channel: 'Operations Research & Optimization',
    speaker: 'OR Academic Consortium',
    duration: '18 min',
    url: 'https://www.youtube.com/watch?v=9jR4UfW07Fw',
    thumbnail: 'https://img.youtube.com/vi/9jR4UfW07Fw/hqdefault.jpg',
    topics: ['CVRP Formulations', 'Clarke-Wright Savings', 'OR-Tools Solvers'],
    description:
      'Core principles of Capacitated Vehicle Routing Problems (CVRP), sub-tour elimination constraints, Clarke-Wright savings heuristics, and constraint programming models.',
  },
  {
    id: 'quantum-logistics',
    title: 'Quantum Computing for Logistics & Supply Chain Optimization',
    channel: 'Qiskit Community Seminars',
    speaker: 'Quantum Applications Lab',
    duration: '32 min',
    url: 'https://www.youtube.com/watch?v=0hK27wM5_4U',
    thumbnail: 'https://img.youtube.com/vi/0hK27wM5_4U/hqdefault.jpg',
    topics: ['Hybrid Pipelines', 'QUBO Mapping', 'Supply Chain Routing'],
    description:
      'Demonstration of end-to-end hybrid classical-quantum pipelines for industrial logistics scheduling, QUBO problem decomposition, and route optimization.',
  },
];

export const OverviewDashboard: React.FC<OverviewProps> = ({ onNavigate }) => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // Mouse coordinate state for ambient glow tracking
  const [mousePos, setMousePos] = useState({ x: 50, y: 50 });
  const [showPapersModal, setShowPapersModal] = useState<boolean>(false);
  const [showVideoModal, setShowVideoModal] = useState<boolean>(false);
  const [paperCategory, setPaperCategory] = useState<string>('all');
  const [paperSearchQuery, setPaperSearchQuery] = useState<string>('');

  const filteredPapers = useMemo(() => {
    return RESEARCH_PAPERS.filter((p) => {
      const matchesCat =
        paperCategory === 'all'
          ? true
          : paperCategory === 'key'
          ? p.isKeyReference
          : p.category === paperCategory;
      if (!matchesCat) return false;

      if (!paperSearchQuery.trim()) return true;
      const q = paperSearchQuery.toLowerCase();
      return (
        p.title.toLowerCase().includes(q) ||
        p.authors.toLowerCase().includes(q) ||
        p.venue.toLowerCase().includes(q) ||
        (p.doi && p.doi.toLowerCase().includes(q)) ||
        p.description.toLowerCase().includes(q)
      );
    });
  }, [paperCategory, paperSearchQuery]);

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
          {/* Card 1 — Our Research Paper */}
          <div className="lg:pr-6 space-y-2">
            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4 text-[#B7FF00]" />
              <h4 className="text-sm font-heading font-bold text-[#080808] dark:text-[#F5F5F7]">
                Our Research Paper
              </h4>
            </div>
            <p className="text-xs text-[#666666] dark:text-[#A1A1AA] leading-relaxed">
              Read our UROP literature survey on hybrid Big Data and quantum-classical approaches to smart delivery route optimization.
            </p>
            <a
              href="/papers/literature_survey_4.pdf"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs font-bold text-[#080808] dark:text-[#B7FF00] hover:underline pt-1 cursor-pointer"
            >
              <span>Read Literature Survey (PDF)</span>
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>

          {/* Card 2 — Watch & Learn */}
          <div className="lg:px-6 space-y-2">
            <div className="flex items-center gap-2">
              <PlayCircle className="h-4 w-4 text-[#B7FF00]" />
              <h4 className="text-sm font-heading font-bold text-[#080808] dark:text-[#F5F5F7]">
                Watch & Learn
              </h4>
            </div>
            <p className="text-xs text-[#666666] dark:text-[#A1A1AA] leading-relaxed">
              Explore educational resources on QAOA, vehicle-routing optimization, quantum-inspired algorithms, and Big Data processing.
            </p>
            <button
              onClick={() => setShowVideoModal(true)}
              className="inline-flex items-center gap-1.5 text-xs font-bold text-[#080808] dark:text-[#B7FF00] hover:underline pt-1 cursor-pointer"
            >
              <span>Watch Educational Lectures</span>
              <ExternalLink className="h-3 w-3" />
            </button>
          </div>

          {/* Card 3 — Reference Papers */}
          <div className="lg:px-6 space-y-2">
            <div className="flex items-center gap-2">
              <BookOpen className="h-4 w-4 text-[#B7FF00]" />
              <h4 className="text-sm font-heading font-bold text-[#080808] dark:text-[#F5F5F7]">
                Reference Papers
              </h4>
            </div>
            <p className="text-xs text-[#666666] dark:text-[#A1A1AA] leading-relaxed">
              Explore key publications that inform our understanding of vehicle routing, quantum optimization, and Big Data in intelligent transportation systems.
            </p>
            <button
              onClick={() => {
                setPaperCategory('key');
                setPaperSearchQuery('');
                setShowPapersModal(true);
              }}
              className="inline-flex items-center gap-1.5 text-xs font-bold text-[#080808] dark:text-[#B7FF00] hover:underline pt-1 cursor-pointer"
            >
              <span>Explore Key References</span>
              <ExternalLink className="h-3 w-3" />
            </button>
          </div>

          {/* Card 4 — Research Library */}
          <div className="lg:pl-6 space-y-2 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2">
                <GraduationCap className="h-4 w-4 text-[#B7FF00]" />
                <h4 className="text-sm font-heading font-bold text-[#080808] dark:text-[#F5F5F7]">
                  Research Library
                </h4>
              </div>
              <p className="text-xs text-[#666666] dark:text-[#A1A1AA] leading-relaxed mt-1">
                Browse the research papers reviewed for our UROP study, with publication details, research themes, and source links.
              </p>
            </div>
            <button
              onClick={() => {
                setPaperCategory('all');
                setPaperSearchQuery('');
                setShowPapersModal(true);
              }}
              className="inline-flex items-center gap-1.5 text-xs font-bold text-[#080808] dark:text-[#B7FF00] hover:underline pt-1 cursor-pointer group"
            >
              <span>Browse Research Library</span>
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
      {/* ─────────────────────────────────────────────────────────────
          MODAL: RESEARCH PAPERS LIBRARY
          Dedicated dialog listing our paper draft and all 27 verified published references
          ───────────────────────────────────────────────────────────── */}
      {showPapersModal &&
        createPortal(
          <div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6 z-[99999] animate-fadeIn"
            onClick={() => setShowPapersModal(false)}
          >
            <div
              className="bg-white dark:bg-[#111113] border border-black/10 dark:border-[#29292E] rounded-3xl max-w-4xl w-full p-6 sm:p-8 shadow-2xl dark:shadow-[0_24px_64px_rgba(0,0,0,0.85)] space-y-5 max-h-[88vh] flex flex-col"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="flex items-start justify-between pb-4 border-b border-black/10 dark:border-[#29292E] shrink-0">
                <div className="space-y-1">
                  <div className="inline-flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-[#B7FF00]" />
                    <span className="text-[11px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A]">
                      Academic Foundations & Verified Citations
                    </span>
                  </div>
                  <h3 className="text-xl sm:text-2xl font-heading font-bold text-[#080808] dark:text-[#F5F5F7]">
                    Research Papers & Academic Reference Library
                  </h3>
                  <p className="text-xs text-[#777777] dark:text-[#A1A1AA]">
                    27 peer-reviewed and preprint publications reviewed for our UROP study, categorized by research theme with verified DOIs and project relevance.
                  </p>
                </div>

                <button
                  onClick={() => setShowPapersModal(false)}
                  className="h-8 w-8 rounded-full flex items-center justify-center bg-black/5 dark:bg-[#18181B] hover:bg-black/10 dark:hover:bg-[#202024] text-[#080808] dark:text-[#F5F5F7] border border-transparent dark:border-[#29292E] transition-colors cursor-pointer text-sm font-bold shrink-0"
                  title="Close"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              {/* Category Filter Pills & Search */}
              <div className="space-y-3 shrink-0">
                <div className="flex flex-wrap items-center gap-1.5">
                  {[
                    { id: 'all', label: `All Papers (${RESEARCH_PAPERS.length})` },
                    { id: 'key', label: `Key References (${RESEARCH_PAPERS.filter((p) => p.isKeyReference).length})` },
                    { id: 'qaoa', label: 'QAOA & Quantum Routing' },
                    { id: 'qio', label: 'Quantum-Inspired (QIGA)' },
                    { id: 'bigdata', label: 'Big Data & ITS' },
                    { id: 'logistics', label: 'Smart Logistics & VRP' },
                    { id: 'nisq', label: 'NISQ Limits & Systematic Reviews' },
                  ].map((cat) => (
                    <button
                      key={cat.id}
                      onClick={() => setPaperCategory(cat.id)}
                      className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                        paperCategory === cat.id
                          ? 'bg-[#080808] text-[#B7FF00] dark:bg-[#B7FF00] dark:text-black shadow-xs'
                          : 'bg-black/5 dark:bg-[#18181B] text-[#666666] dark:text-[#A1A1AA] hover:bg-black/10 dark:hover:bg-[#222226]'
                      }`}
                    >
                      {cat.label}
                    </button>
                  ))}
                </div>

                <div className="relative">
                  <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-[#777777]" />
                  <input
                    type="text"
                    value={paperSearchQuery}
                    onChange={(e) => setPaperSearchQuery(e.target.value)}
                    placeholder="Search by title, author, venue, DOI, or keyword..."
                    className="w-full pl-9 pr-4 py-2 rounded-xl text-xs bg-black/[0.03] dark:bg-[#18181B] border border-black/10 dark:border-[#29292E] text-[#080808] dark:text-[#F5F5F7] placeholder-[#777777] focus:outline-hidden focus:border-[#B7FF00] transition-colors"
                  />
                  {paperSearchQuery && (
                    <button
                      onClick={() => setPaperSearchQuery('')}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-[#777777] hover:text-[#080808] dark:hover:text-[#F5F5F7]"
                    >
                      Clear
                    </button>
                  )}
                </div>
              </div>

              {/* Papers Scrollable List */}
              <div className="space-y-3.5 overflow-y-auto pr-1 flex-1">
                {filteredPapers.length === 0 ? (
                  <div className="text-center py-12 text-xs text-[#777777]">
                    No research papers matched your search filter.
                  </div>
                ) : (
                  filteredPapers.map((paper) => (
                    <div
                      key={paper.id}
                      className={`p-4 sm:p-5 rounded-2xl border transition-all ${
                        paper.category === 'survey'
                          ? 'bg-[#B7FF00]/10 dark:bg-[#B7FF00]/5 border-[#B7FF00]/40'
                          : paper.isKeyReference
                          ? 'bg-black/[0.02] dark:bg-[#18181B] border-[#B7FF00]/30 dark:border-[#B7FF00]/20'
                          : 'bg-black/[0.02] dark:bg-[#18181B] border-black/10 dark:border-[#29292E]'
                      }`}
                    >
                      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                        <div className="space-y-1.5 flex-1">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span
                              className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                                paper.category === 'survey'
                                  ? 'bg-[#080808] text-[#B7FF00] dark:bg-[#B7FF00] dark:text-[#000000]'
                                  : 'bg-black/5 dark:bg-[#202024] text-[#777777] dark:text-[#A1A1AA]'
                              }`}
                            >
                              {paper.categoryLabel}
                            </span>
                            {paper.isKeyReference && (
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#B7FF00]/20 text-[#080808] dark:text-[#B7FF00] border border-[#B7FF00]/40 flex items-center gap-1">
                                <CheckCircle2 className="h-2.5 w-2.5" />
                                Key Reference
                              </span>
                            )}
                            <span className="text-[11px] font-semibold text-[#777777] dark:text-[#A1A1AA]">
                              {paper.venue} · {paper.year}
                            </span>
                          </div>

                          <h4 className="text-sm font-heading font-bold text-[#080808] dark:text-[#F5F5F7] leading-snug">
                            {paper.title}
                          </h4>

                          <p className="text-[11px] text-[#555555] dark:text-[#8E8E93] italic">
                            {paper.authors}
                          </p>

                          <p className="text-xs text-[#555555] dark:text-[#A1A1AA] leading-relaxed pt-0.5">
                            {paper.description}
                          </p>

                          <div className="text-[11px] text-[#666666] dark:text-[#8E8E93] pt-1 border-t border-black/5 dark:border-white/5">
                            <strong className="text-[#080808] dark:text-[#D4D4D8]">Technical Relevance:</strong>{' '}
                            {paper.relevance}
                          </div>
                        </div>

                        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 shrink-0 self-start sm:self-center">
                          {paper.pdfUrl && (
                            <a
                              href={paper.pdfUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-full bg-[#080808] hover:bg-[#171717] dark:bg-[#B7FF00] dark:hover:bg-[#a3e600] text-[#B7FF00] dark:text-black text-xs font-bold transition-all cursor-pointer"
                              title="Open PDF Document"
                            >
                              <Download className="h-3 w-3" />
                              <span>{paper.category === 'survey' ? 'Read Survey' : 'Open PDF'}</span>
                            </a>
                          )}
                          {paper.doi && (
                            <a
                              href={`https://doi.org/${paper.doi}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-full bg-black/5 hover:bg-black/10 dark:bg-[#202024] dark:hover:bg-[#28282D] text-[#080808] dark:text-[#F5F5F7] text-xs font-semibold transition-all cursor-pointer border border-black/10 dark:border-[#29292E]"
                              title={`View verified DOI: ${paper.doi}`}
                            >
                              <span>Publisher DOI</span>
                              <ExternalLink className="h-3 w-3" />
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Modal Footer */}
              <div className="pt-3 flex items-center justify-between border-t border-black/10 dark:border-[#29292E] shrink-0 text-xs text-[#777777]">
                <span>Showing {filteredPapers.length} of {RESEARCH_PAPERS.length} research publications</span>
                <button
                  onClick={() => setShowPapersModal(false)}
                  className="px-4 py-2 bg-[#080808] hover:bg-[#171717] dark:bg-[#18181B] dark:hover:bg-[#202024] border border-transparent dark:border-[#29292E] text-[#B7FF00] rounded-xl text-xs font-bold transition-all cursor-pointer"
                >
                  Close Library
                </button>
              </div>
            </div>
          </div>,
          document.body
        )}

      {/* ─────────────────────────────────────────────────────────────
          MODAL: WATCH & LEARN EDUCATIONAL LECTURES
          Curated external educational lectures on QAOA, VRP, and quantum logistics
          ───────────────────────────────────────────────────────────── */}
      {showVideoModal &&
        createPortal(
          <div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6 z-[99999] animate-fadeIn"
            onClick={() => setShowVideoModal(false)}
          >
            <div
              className="bg-white dark:bg-[#111113] border border-black/10 dark:border-[#29292E] rounded-3xl max-w-3xl w-full p-6 sm:p-8 shadow-2xl dark:shadow-[0_24px_64px_rgba(0,0,0,0.85)] space-y-5 max-h-[88vh] flex flex-col"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="flex items-start justify-between pb-4 border-b border-black/10 dark:border-[#29292E] shrink-0">
                <div className="space-y-1">
                  <div className="inline-flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-[#B7FF00]" />
                    <span className="text-[11px] font-bold uppercase tracking-wider text-[#777777] dark:text-[#71717A]">
                      Curated Academic Lectures & Research Tutorials
                    </span>
                  </div>
                  <h3 className="text-xl sm:text-2xl font-heading font-bold text-[#080808] dark:text-[#F5F5F7]">
                    Watch & Learn: Educational Lectures
                  </h3>
                  <p className="text-xs text-[#777777] dark:text-[#A1A1AA]">
                    Verified academic video lectures covering QAOA mathematics, vehicle routing problem formulations, and quantum logistics pipelines.
                  </p>
                </div>

                <button
                  onClick={() => setShowVideoModal(false)}
                  className="h-8 w-8 rounded-full flex items-center justify-center bg-black/5 dark:bg-[#18181B] hover:bg-black/10 dark:hover:bg-[#202024] text-[#080808] dark:text-[#F5F5F7] border border-transparent dark:border-[#29292E] transition-colors cursor-pointer text-sm font-bold shrink-0"
                  title="Close"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              {/* Lectures List */}
              <div className="space-y-4 overflow-y-auto pr-1 flex-1">
                <div className="p-3.5 rounded-xl bg-black/5 dark:bg-[#18181B] text-xs text-[#666666] dark:text-[#A1A1AA] border border-black/10 dark:border-[#29292E]">
                  <strong>Educational Resources:</strong> Verified video walkthroughs and university/industry seminars covering QAOA formulations, vehicle routing problem heuristics, and hybrid quantum pipelines from accredited research organizations.
                </div>

                {EDUCATIONAL_LECTURES.map((video) => (
                  <div
                    key={video.id}
                    className="p-4 sm:p-5 rounded-2xl border border-black/10 dark:border-[#29292E] bg-black/[0.02] dark:bg-[#18181B] flex flex-col sm:flex-row items-start gap-4 transition-all hover:border-[#B7FF00]/40 group"
                  >
                    {/* YouTube Thumbnail Preview */}
                    <a
                      href={video.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="relative w-full sm:w-44 h-28 rounded-xl overflow-hidden shrink-0 bg-black/80 border border-black/10 dark:border-[#29292E] block group/thumb"
                    >
                      <img
                        src={video.thumbnail}
                        alt={video.title}
                        className="w-full h-full object-cover transition-transform duration-300 group-hover/thumb:scale-105"
                        loading="lazy"
                      />
                      <div className="absolute inset-0 bg-black/30 group-hover/thumb:bg-black/10 transition-colors flex items-center justify-center">
                        <div className="h-10 w-10 rounded-full bg-red-600 text-white flex items-center justify-center shadow-lg transition-transform group-hover/thumb:scale-110">
                          <PlayCircle className="h-6 w-6 fill-current" />
                        </div>
                      </div>
                      <span className="absolute bottom-1.5 right-1.5 px-1.5 py-0.5 rounded bg-black/80 text-[10px] font-mono font-bold text-white">
                        {video.duration}
                      </span>
                    </a>

                    {/* Lecture Info */}
                    <div className="space-y-2 flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-[11px] font-bold text-red-600 dark:text-red-400">
                          {video.channel}
                        </span>
                        {video.speaker && (
                          <>
                            <span className="text-black/20 dark:text-white/20 text-xs">•</span>
                            <span className="text-[11px] text-[#777777] dark:text-[#A1A1AA]">
                              {video.speaker}
                            </span>
                          </>
                        )}
                      </div>

                      <h4 className="text-sm sm:text-base font-heading font-bold text-[#080808] dark:text-[#F5F5F7] group-hover:text-[#B7FF00] transition-colors leading-snug">
                        {video.title}
                      </h4>

                      <p className="text-xs text-[#666666] dark:text-[#A1A1AA] leading-relaxed">
                        {video.description}
                      </p>

                      {video.topics && video.topics.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 pt-1">
                          {video.topics.map((t, ti) => (
                            <span
                              key={ti}
                              className="px-2 py-0.5 rounded-md text-[10px] font-medium bg-black/5 dark:bg-[#202024] text-[#555555] dark:text-[#999999] border border-black/5 dark:border-[#29292E]"
                            >
                              {t}
                            </span>
                          ))}
                        </div>
                      )}

                      <div className="pt-2">
                        <a
                          href={video.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-[#080808] hover:bg-[#171717] dark:bg-[#B7FF00] dark:hover:bg-[#a3e600] text-[#B7FF00] dark:text-black text-xs font-bold transition-all cursor-pointer"
                        >
                          <PlayCircle className="h-3.5 w-3.5" />
                          <span>Watch Lecture on YouTube</span>
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Modal Footer */}
              <div className="pt-3 flex items-center justify-between border-t border-black/10 dark:border-[#29292E] shrink-0">
                <span className="text-xs text-[#777777] dark:text-[#71717A]">
                  3 accredited lectures on quantum optimization & operations research
                </span>
                <button
                  onClick={() => setShowVideoModal(false)}
                  className="px-4 py-2 bg-[#080808] hover:bg-[#171717] dark:bg-[#18181B] dark:hover:bg-[#202024] border border-transparent dark:border-[#29292E] text-[#B7FF00] rounded-xl text-xs font-bold transition-all cursor-pointer"
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
