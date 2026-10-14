export interface ExtractedFile {
  name: string;
  original_path: string;
  size: number;
  type: string;
  extracted_path: string;
}

export interface Dataset {
  id: string;
  name: string;
  dataset_type: 'customer' | 'vehicle' | 'location' | 'traffic' | 'road' | 'weather';
  original_filename: string;
  file_size_bytes: number;
  upload_timestamp: string;
  extraction_status: 'pending' | 'extracted' | 'failed';
  extracted_files: ExtractedFile[];
  validation_status: 'pending' | 'valid' | 'invalid';
  record_count: number;
  detected_schema: any[];
  missing_value_pct: number;
  duplicate_count: number;
  validation_warnings: string[];
  validation_errors: string[];
  column_mapping: Record<string, string>;
  mapping_status: string;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  data_hash: string;
}

export interface RouteWaypoint {
  lat: number;
  lon: number;
  type: 'depot' | 'customer';
  index: number;
}

export interface VehicleRoute {
  vehicle_id: number;
  stops: number[];
  customer_stops: number[];
  distance_km: number;
  load?: number;
  capacity?: number;
  utilization_pct?: number;
  waypoints?: RouteWaypoint[];
}

export interface SolverValidation {
  is_feasible: boolean;
  capacity_violations: number;
  unserved_count: number;
  served_count: number;
  warnings: string[];
}

export interface SolverResult {
  success: boolean;
  algorithm: string;
  algorithm_name?: string;
  category?: 'classical' | 'quantum_hybrid' | 'quantum_inspired';
  category_label?: string;
  compute_type?: string;
  status?: string;
  execution_time_sec: number;
  routes: VehicleRoute[];
  total_distance_km: number;
  total_travel_time_min: number;
  total_objective_cost: number;
  is_feasible: boolean;
  capacity_violations: number;
  unserved_customers: number;
  served_customers: number;
  num_qubits?: number;
  circuit_depth?: number;
  qaoa_layers?: number;
  measurement_shots?: number;
  best_bitstring?: string;
  best_energy?: number;
  optimizer_iterations?: number;
  energy_history?: number[];
  solver_log?: string;
  warnings?: string[];
  validation?: SolverValidation;
  convergence_info?: Record<string, any>;
  error?: string;
}

export interface AlgorithmInfo {
  id: string;
  name: string;
  category: 'classical' | 'quantum_hybrid' | 'quantum_inspired';
  category_label: string;
  tag: string;
  description: string;
  operational: boolean;
  max_customers: number;
  is_primary: boolean;
  compute_type: string;
}

export interface ComparisonItem {
  id: string;
  name: string;
  category: string;
  category_label: string;
  compute_type: string;
  status: string;
  execution_time_sec: number;
  total_distance_km: number;
  total_travel_time_min: number;
  total_objective_cost: number;
  is_feasible: boolean;
  capacity_violations: number;
  unserved_customers: number;
  served_customers: number;
  vehicles_used: number;
  convergence_info?: Record<string, any>;
  is_best: boolean;
}

export interface ComparisonSummary {
  best_algorithm: string;
  best_algorithm_name: string;
  best_reason: string;
  best_feasible_distance_km: number;
  items: ComparisonItem[];
}

export interface OptimizationResponse {
  experiment_id: string;
  status: string;
  execution_time_sec: number;
  selection_mode?: 'recommended' | 'custom' | 'compare';
  selected_algorithms?: string[];
  primary_algorithm?: string;
  best_feasible_algorithm?: string;
  comparison_summary?: ComparisonSummary;
  problem: {
    num_customers: number;
    num_vehicles: number;
    depot: { lat: number; lon: number };
    traffic_factor: number;
    weather_factor: number;
    locations: Array<{ lat: number; lon: number; demand: number }>;
  };
  results: Record<string, SolverResult> & {
    classical?: SolverResult;
    qaoa?: SolverResult;
    ortools?: SolverResult;
    clarke_wright?: SolverResult;
    two_opt?: SolverResult;
    dijkstra?: SolverResult;
    astar?: SolverResult;
    qiga?: SolverResult;
  };
}

export interface AnalyticsSummary {
  customers: {
    count: number;
    has_coordinates: boolean;
    total_demand: number;
    avg_demand: number;
  } | null;
  vehicles: {
    count: number;
    active_count: number;
    total_capacity: number;
  } | null;
  locations: {
    count: number;
    with_coordinates: number;
  } | null;
  road_network: {
    node_count: number;
    edge_count: number;
  } | null;
  weather: {
    record_count: number;
    date_range_start?: string;
    date_range_end?: string;
  } | null;
  traffic: {
    record_count: number;
    total_vehicles_observed: number;
    avg_segment_volume: number;
  } | null;
  data_readiness: {
    customer?: boolean;
    vehicle?: boolean;
    location?: boolean;
    road?: boolean;
    weather?: boolean;
    traffic?: boolean;
  };
  experiments?: {
    total: number;
    completed: number;
    recent: any[];
  };
}
