"""
Database Models — Datasets, Experiments, Routes, Results
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime, JSON
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


def gen_uuid():
    return str(uuid.uuid4())


class Dataset(Base):
    """Uploaded dataset record."""
    __tablename__ = "datasets"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)  # e.g. "Customer & Delivery"
    dataset_type = Column(String, nullable=False)  # customer, vehicle, location, traffic, road, weather
    original_filename = Column(String, nullable=False)
    file_size_bytes = Column(Integer, default=0)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)

    # Extraction
    extraction_status = Column(String, default="pending")  # pending, extracted, failed
    extracted_files = Column(JSON, default=list)  # [{"name": "foo.csv", "size": 1234, "type": "csv"}]

    # Validation
    validation_status = Column(String, default="pending")
    record_count = Column(Integer, default=0)
    detected_schema = Column(JSON, default=dict)  # {"columns": [{"name": "x", "dtype": "int64"}]}
    missing_value_pct = Column(Float, default=0.0)
    duplicate_count = Column(Integer, default=0)
    validation_warnings = Column(JSON, default=list)
    validation_errors = Column(JSON, default=list)

    # Column mapping
    column_mapping = Column(JSON, default=dict)  # {"original_col": "canonical_col"}
    mapping_status = Column(String, default="pending")  # pending, mapped, skipped

    # Processing
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    processing_log = Column(Text, default="")
    processed_file_path = Column(String, default="")

    # Data hash for reproducibility
    data_hash = Column(String, default="")


class Experiment(Base):
    """Optimization experiment record."""
    __tablename__ = "experiments"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, default="")
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Configuration
    algorithm = Column(String, nullable=False)  # classical, qaoa, both
    num_customers = Column(Integer, default=0)
    num_vehicles = Column(Integer, default=0)
    depot_lat = Column(Float, default=0.0)
    depot_lon = Column(Float, default=0.0)
    vehicle_capacity = Column(Float, default=0.0)

    # Objective weights
    weight_distance = Column(Float, default=1.0)
    weight_travel_time = Column(Float, default=0.5)
    weight_congestion = Column(Float, default=0.3)
    weight_fuel = Column(Float, default=0.2)
    weight_late_penalty = Column(Float, default=0.5)

    # Traffic/Weather scenario
    traffic_scenario = Column(String, default="normal")  # normal, high_congestion, severe
    weather_scenario = Column(String, default="clear")

    # Classical settings
    classical_time_limit_sec = Column(Integer, default=30)
    classical_solver = Column(String, default="or-tools")

    # Quantum settings
    qaoa_depth = Column(Integer, default=1)
    qaoa_shots = Column(Integer, default=1024)
    qaoa_optimizer = Column(String, default="COBYLA")
    qaoa_penalty = Column(Float, default=10.0)

    # Random seed
    random_seed = Column(Integer, default=42)

    # Dataset references
    dataset_versions = Column(JSON, default=dict)  # {"customer": "hash1", "vehicle": "hash2"}

    # Status
    status = Column(String, default="pending")  # pending, running, completed, failed
    error_message = Column(Text, default="")

    # Results stored in ExperimentResult
    results = relationship("ExperimentResult", back_populates="experiment", lazy="selectin")


class ExperimentResult(Base):
    """Results for one algorithm within an experiment."""
    __tablename__ = "experiment_results"

    id = Column(String, primary_key=True, default=gen_uuid)
    experiment_id = Column(String, ForeignKey("experiments.id"), nullable=False)
    algorithm = Column(String, nullable=False)  # classical, qaoa

    # Core metrics
    total_distance_km = Column(Float, default=0.0)
    total_travel_time_min = Column(Float, default=0.0)
    total_objective_cost = Column(Float, default=0.0)
    execution_time_sec = Column(Float, default=0.0)

    # Feasibility
    is_feasible = Column(Boolean, default=False)
    capacity_violations = Column(Integer, default=0)
    unserved_customers = Column(Integer, default=0)
    constraint_violations = Column(JSON, default=list)

    # Routes
    routes = Column(JSON, default=list)  # [{"vehicle_id": 0, "stops": [...], "distance": 12.3}]
    route_details = Column(JSON, default=dict)

    # Quantum-specific
    qubit_count = Column(Integer, default=0)
    circuit_depth = Column(Integer, default=0)
    qaoa_layers = Column(Integer, default=0)
    measurement_shots = Column(Integer, default=0)
    best_bitstring = Column(String, default="")
    optimizer_iterations = Column(Integer, default=0)
    energy_history = Column(JSON, default=list)

    # Solver log
    solver_log = Column(Text, default="")
    warnings = Column(JSON, default=list)

    experiment = relationship("Experiment", back_populates="results")


class ProcessedData(Base):
    """Cached processed data references."""
    __tablename__ = "processed_data"

    id = Column(String, primary_key=True, default=gen_uuid)
    data_type = Column(String, nullable=False)  # customers, vehicles, locations, etc.
    source_dataset_id = Column(String, default="")
    record_count = Column(Integer, default=0)
    file_path = Column(String, default="")
    data_hash = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON, default=dict)
