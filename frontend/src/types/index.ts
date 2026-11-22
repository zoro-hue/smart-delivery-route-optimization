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
  is_cached?: boolean;
  sync_source?: 'backend' | 'cache';
  last_synced_at?: string;
}

export type DatasetSyncStatus = 'CONNECTING' | 'CONNECTED' | 'SYNCING' | 'DEGRADED' | 'DISCONNECTED' | 'ERROR';

export interface RouteWaypoint {
  lat: number;
  lon: number;
  type: 'depot' | 'customer';
  index: number;
}

export interface VehicleProfile {
  id: string;
  name: string;
  vehicle_type: 'car' | 'van' | 'truck' | 'electric_van' | string;
  powertrain: 'diesel' | 'petrol' | 'hybrid' | 'electric';
  capacity_kg: number;
  cargo_volume_m3?: number;
  condition: 'excellent' | 'good' | 'average' | 'poor';
  age_years: number;
  odometer_km: number;
  maintenance_status: 'ok' | 'service_recommended' | 'overdue' | 'critical';
  is_available: boolean;
  battery_capacity_kwh?: number;
  battery_soc_percent?: number;
  battery_soh_percent?: number;
  fuel_tank_capacity_l?: number;
  fuel_level_percent?: number;
  base_consumption_per_100km?: number;
  max_range_km: number;
  average_speed_kmh?: number;
  max_operating_hours?: number;
  cost_per_km_usd?: number;
  cost_per_hour_usd?: number;
  fixed_dispatch_cost_usd?: number;
}

export interface VehicleRoute {
  vehicle_id: number;
  vehicle_profile?: VehicleProfile;
  vehicle_name?: string;
  stops: number[];
  customer_stops: number[];
  distance_km: number;
  total_distance_km?: number;
  driving_time_min?: number;
  service_time_min?: number;
  total_duration_min?: number;
  implied_speed_kmh?: number;
  operational_speed_kmh?: number;
  load?: number;
  capacity?: number;
  utilization_pct?: number;
  usable_range_km?: number;
  is_range_feasible?: boolean;
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
  category?: 'classical' | 'quantum_hybrid' | 'quantum_inspired' | 'cooperative' | string;
  category_label?: string;
  compute_type?: string;
  status?: string;
  execution_time_sec: number;
  routes: VehicleRoute[];
  total_distance_km: number;
  total_travel_time_min: number;
  driving_duration_min?: number;
  service_duration_min?: number;
  total_duration_min?: number;
  implied_speed_kmh?: number;
  operational_speed_kmh?: number;
  speed_model?: {
    base_speed_kmh?: number;
    traffic_factor?: number;
    weather_factor?: number;
    effective_speed_kmh?: number;
    service_time_per_stop_min?: number;
    model_description?: string;
    includes_service_time?: boolean;
  };
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
  execution_id?: string;
  solution_origin?: string;
  resource_metrics?: {
    runtime_ms?: number;
    cpu_time_ms?: number;
    cpu_utilization_percent?: number;
    cpu_core_ratio_percent?: number;
    memory_used_mb?: number;
    peak_memory_mb?: number;
    heap_allocated_mb?: number;
    heap_peak_mb?: number;
    process_rss_mb?: number;
    time_complexity?: string;
    space_complexity?: string;
    measurement_available?: boolean;
    measurement_method?: string;
  };
  error?: string;
  energy_metrics?: AlgorithmEnergyProfile;
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
  driving_duration_min?: number;
  service_duration_min?: number;
  total_duration_min?: number;
  implied_speed_kmh?: number;
  operational_speed_kmh?: number;
  speed_model?: {
    base_speed_kmh?: number;
    traffic_factor?: number;
    weather_factor?: number;
    effective_speed_kmh?: number;
    service_time_per_stop_min?: number;
    model_description?: string;
    includes_service_time?: boolean;
  };
  total_objective_cost: number;
  is_feasible: boolean;
  capacity_violations: number;
  unserved_customers: number;
  served_customers: number;
  vehicles_used: number;
  convergence_info?: Record<string, any>;
  cpu_utilization_percent?: number;
  cpu_core_ratio_percent?: number;
  memory_used_mb?: number;
  peak_memory_mb?: number;
  heap_allocated_mb?: number;
  heap_peak_mb?: number;
  process_rss_mb?: number;
  time_complexity?: string;
  space_complexity?: string;
  resource_metrics?: Record<string, any>;
  is_best: boolean;
  error?: string;
  energy_metrics?: AlgorithmEnergyProfile;
  energy_comparison?: EnergyComparison;
}

export type VehiclePropulsionType = 'diesel' | 'petrol' | 'hybrid' | 'electric';

export interface VehicleRouteEnergy {
  vehicle_id: number;
  vehicle_profile?: VehicleProfile;
  propulsion_type?: string;
  distance_km: number;
  duration_min: number;
  stops_count: number;
  load: number;
  capacity: number;
  utilization_pct: number;
  load_factor: number;
  traffic_factor: number;
  fuel_consumption_litres: number;
  energy_consumption_kwh: number;
  direct_tailpipe_co2_kg: number;
  indirect_grid_co2_kg: number;
  upstream_well_to_tank_co2_kg: number;
  total_co2_kg: number;
  fuel_energy_cost_usd?: number;
  maintenance_wear_cost_usd?: number;
  driver_labor_cost_usd?: number;
  dispatch_cost_usd?: number;
  operational_cost_usd: number;
  remaining_soc_pct?: number | null;
  remaining_fuel_pct?: number | null;
  remaining_range_km?: number;
  is_range_feasible?: boolean;
  is_shift_feasible?: boolean;
  is_all_feasible?: boolean;
  unit_label: string;
}

export interface AlgorithmEnergyProfile {
  algorithm_id: string;
  algorithm_name: string;
  category: string;
  is_feasible: boolean;
  propulsion_type: VehiclePropulsionType;
  propulsion_name: string;
  unit_label: string;
  total_distance_km: number;
  total_duration_min: number;
  vehicles_count: number;
  fuel_consumption_litres: number;
  energy_consumption_kwh: number;
  direct_tailpipe_co2_kg: number;
  indirect_grid_co2_kg: number;
  upstream_well_to_tank_co2_kg: number;
  total_co2_kg: number;
  fuel_energy_cost_usd?: number;
  maintenance_wear_cost_usd?: number;
  driver_labor_cost_usd?: number;
  dispatch_cost_usd?: number;
  operational_cost_usd: number;
  vehicle_breakdowns: VehicleRouteEnergy[];
  data_tags?: Record<string, 'MEASURED' | 'COMPUTED' | 'ESTIMATED' | 'ASSUMED' | 'SIMULATED' | 'UNAVAILABLE' | 'INVALID'>;
}

export interface EnergyComparison {
  target_algorithm: string;
  baseline_algorithm: string;
  propulsion_type: VehiclePropulsionType;
  delta_distance_km: number;
  delta_fuel_litres: number;
  delta_energy_kwh: number;
  delta_co2_kg: number;
  delta_cost_usd: number;
  co2_abatement_kg?: number;
  fleet_cost_saved_usd?: number;
  pct_distance_savings: number;
  pct_fuel_savings: number;
  pct_energy_savings: number;
  pct_co2_savings: number;
  pct_cost_savings: number;
  is_saving: boolean;
  is_identical: boolean;
  status_label: 'RESOURCE_SAVING' | 'RESOURCE_DEFICIT' | 'IDENTICAL_TO_BASELINE' | 'MIXED_OUTCOME';
  impact_summary: string;
}

export interface FullEnergyAnalysis {
  active_propulsion: VehiclePropulsionType;
  baseline_algorithm: string;
  best_eco_algorithm?: string;
  propulsion_models: Record<string, any>;
  profiles: Record<string, AlgorithmEnergyProfile>;
  profiles_by_propulsion: Record<VehiclePropulsionType, Record<string, AlgorithmEnergyProfile>>;
  comparisons: Record<string, EnergyComparison>;
  flagship_comparison?: EnergyComparison;
  methodology?: {
    title: string;
    standards: string[];
    data_tags: Record<string, string>;
    fuel_prices_source: string;
  };
}

export interface RouteIdentityDiagnostics {
  execution_id_coop: string;
  execution_id_ortools: string;
  is_separate_memory_objects: boolean;
  distance_coop_km: number;
  distance_ortools_km: number;
  distance_delta_km: number;
  distance_delta_pct: number;
  directed_edge_overlap_pct: number;
  undirected_edge_overlap_pct: number;
  vehicle_allocation_similarity_pct: number;
  shared_directed_edges_count: number;
  total_coop_directed_edges: number;
  total_ortools_directed_edges: number;
  relationship_code:
    | 'SUPREMACY_IMPROVED'
    | 'INDEPENDENT_ALTERNATIVE_OPTIMUM'
    | 'INDEPENDENT_IDENTICAL_CONVERGENCE'
    | 'PROVEN_OPTIMAL_INCUMBENT_RETAINED';
  relationship_label: string;
  explanation: string;
  is_identical_route: boolean;
  is_same_distance: boolean;
}

export interface ComparisonSummary {
  best_algorithm?: string | null;
  best_algorithm_name?: string | null;
  best_reason: string;
  best_feasible_distance_km?: number | null;
  has_feasible_solution?: boolean;
  items: ComparisonItem[];
  route_identity_diagnostics?: RouteIdentityDiagnostics;
  energy_analysis?: FullEnergyAnalysis;
}

export interface OptimizationResponse {
  experiment_id: string;
  job_id?: string;
  status: string;
  execution_time_sec: number;
  selection_mode?: 'recommended' | 'custom' | 'compare';
  selected_algorithms?: string[];
  primary_algorithm?: string;
  best_feasible_algorithm?: string;
  completed_algorithms?: number;
  total_algorithms?: number;
  solver_statuses?: Record<string, string>;
  comparison_summary?: ComparisonSummary;
  problem: {
    num_customers: number;
    num_vehicles: number;
    vehicle_capacity?: number;
    vehicle_profiles?: VehicleProfile[];
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
    tabu_search?: SolverResult;
    kernighan_lin?: SolverResult;
    vnd?: SolverResult;
    qiga?: SolverResult;
    routeiq_cooperative?: SolverResult;
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
