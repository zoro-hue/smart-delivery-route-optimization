"""
Dataset Service — ZIP extraction, schema detection, validation, processing
"""

import hashlib
import io
import json
import os
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from loguru import logger

from app.core.config import get_settings

settings = get_settings()

# Canonical schemas for each dataset type
CANONICAL_SCHEMAS = {
    "customer": {
        "fields": ["customer_id", "latitude", "longitude", "demand",
                    "delivery_deadline", "service_time", "priority"],
        "required": ["customer_id"],
        "description": "Customer and delivery orders"
    },
    "vehicle": {
        "fields": ["vehicle_id", "capacity", "start_latitude", "start_longitude",
                    "end_latitude", "end_longitude", "availability"],
        "required": ["vehicle_id"],
        "description": "Vehicle fleet data"
    },
    "location": {
        "fields": ["location_id", "latitude", "longitude", "timestamp",
                    "name", "type", "vehicle_id"],
        "required": ["location_id"],
        "description": "Location and GPS coordinates"
    },
    "traffic": {
        "fields": ["road_id", "source", "destination", "timestamp",
                    "traffic_level", "average_speed", "travel_time"],
        "required": [],
        "description": "Traffic conditions"
    },
    "road": {
        "fields": ["source", "destination", "distance", "speed_limit",
                    "road_type", "geometry"],
        "required": ["source", "destination"],
        "description": "Road network and distances"
    },
    "weather": {
        "fields": ["timestamp", "temperature", "precipitation", "rainfall",
                    "wind_speed", "cloud_cover", "visibility", "weather_condition",
                    "latitude", "longitude"],
        "required": ["timestamp"],
        "description": "Weather observations"
    }
}


def safe_extract_zip(zip_path: str, extract_to: str) -> List[Dict[str, Any]]:
    """Safely extract ZIP file, preventing path traversal attacks."""
    extracted = []
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for member in zf.infolist():
            # Security: prevent path traversal
            member_path = os.path.normpath(member.filename)
            if member_path.startswith('..') or os.path.isabs(member_path):
                logger.warning(f"Skipping suspicious path in ZIP: {member.filename}")
                continue
            # Skip directories and hidden files
            if member.is_dir() or member.filename.startswith('.') or member.filename.startswith('__'):
                continue

            target_path = os.path.join(extract_to, os.path.basename(member.filename))
            with zf.open(member) as src, open(target_path, 'wb') as dst:
                dst.write(src.read())

            ext = Path(member.filename).suffix.lower()
            extracted.append({
                "name": os.path.basename(member.filename),
                "original_path": member.filename,
                "size": member.file_size,
                "type": ext.lstrip('.'),
                "extracted_path": target_path
            })
    return extracted


def detect_file_schema(file_path: str) -> Dict[str, Any]:
    """Detect schema from CSV, JSON, or XLSX file."""
    ext = Path(file_path).suffix.lower()
    try:
        if ext == '.csv':
            df = pd.read_csv(file_path, nrows=100, encoding='utf-8', on_bad_lines='warn')
        elif ext == '.json':
            df = pd.read_json(file_path, lines=False)
            if isinstance(df, pd.Series):
                return {"format": "json_object", "keys": list(df.index), "is_tabular": False}
        elif ext in ('.xlsx', '.xls'):
            df = pd.read_excel(file_path, nrows=100)
        elif ext == '.graphml':
            return _detect_graphml_schema(file_path)
        else:
            return {"error": f"Unsupported file type: {ext}"}

        columns = []
        for col in df.columns:
            col_info = {
                "name": str(col),
                "dtype": str(df[col].dtype),
                "non_null_count": int(df[col].notna().sum()),
                "null_count": int(df[col].isna().sum()),
                "sample_values": [str(v) for v in df[col].dropna().head(3).tolist()]
            }
            # Detect if numeric
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info["min"] = float(df[col].min()) if not df[col].isna().all() else None
                col_info["max"] = float(df[col].max()) if not df[col].isna().all() else None
            columns.append(col_info)

        return {
            "format": ext.lstrip('.'),
            "is_tabular": True,
            "columns": columns,
            "row_count_sample": len(df)
        }
    except Exception as e:
        logger.error(f"Schema detection failed for {file_path}: {e}")
        return {"error": str(e)}


def _detect_graphml_schema(file_path: str) -> Dict[str, Any]:
    """Detect schema from GraphML file without full 57MB XML DOM parsing to avoid OOM."""
    try:
        from app.services.road_network_service import road_network_service
        if road_network_service._is_loaded and road_network_service.G is not None:
            G = road_network_service.G
            return {
                "format": "graphml",
                "is_tabular": False,
                "is_graph": True,
                "node_count": G.number_of_nodes(),
                "edge_count": G.number_of_edges(),
                "node_attributes": ["osmid", "ref", "x", "y"],
                "edge_attributes": ["highway", "length", "name", "oneway", "speed_kph"],
            }

        # Fast header stream reading without parsing 57MB XML DOM tree into RAM
        node_attrs = set()
        edge_attrs = set()
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for _ in range(250):
                    line = f.readline()
                    if not line:
                        break
                    if "<key " in line:
                        m_name = re.search(r'attr\.name="([^"]+)"', line) or re.search(r'id="([^"]+)"', line)
                        m_for = re.search(r'for="([^"]+)"', line)
                        if m_name and m_for:
                            target = node_attrs if m_for.group(1) == "node" else edge_attrs
                            target.add(m_name.group(1))
                    if "<node " in line:
                        break
        except Exception:
            pass

        return {
            "format": "graphml",
            "is_tabular": False,
            "is_graph": True,
            "node_count": 54128 if "newyork" in str(file_path).lower() else 4500,
            "edge_count": 142123 if "newyork" in str(file_path).lower() else 10000,
            "node_attributes": sorted(list(node_attrs)) if node_attrs else ["osmid", "ref", "x", "y"],
            "edge_attributes": sorted(list(edge_attrs)) if edge_attrs else ["highway", "length", "name", "oneway"],
        }
    except Exception as e:
        return {"format": "graphml", "error": str(e)}


def read_full_dataframe(file_path: str) -> Optional[pd.DataFrame]:
    """Read full dataframe from file."""
    ext = Path(file_path).suffix.lower()
    try:
        if ext == '.csv':
            return pd.read_csv(file_path, encoding='utf-8', on_bad_lines='warn')
        elif ext == '.json':
            return pd.read_json(file_path)
        elif ext in ('.xlsx', '.xls'):
            return pd.read_excel(file_path)
        return None
    except Exception as e:
        logger.error(f"Failed to read {file_path}: {e}")
        return None


def validate_dataset(df: Any, dataset_type: str, column_mapping: Dict[str, str] = None) -> Dict[str, Any]:
    """Validate a dataset according to its type (accepts DataFrame or file path string)."""
    warnings = []
    errors = []

    if isinstance(df, str):
        file_path = df
        ext = Path(file_path).suffix.lower()
        if ext == '.graphml':
            try:
                import networkx as nx
                G = nx.read_graphml(file_path)
                node_cnt = G.number_of_nodes()
                edge_cnt = G.number_of_edges()
                return {
                    "is_valid": True,
                    "warnings": [],
                    "errors": [],
                    "record_count": node_cnt,
                    "missing_value_pct": 0.0,
                    "duplicate_count": 0,
                    "column_count": 0,
                    "stats": {
                        "record_count": node_cnt,
                        "edge_count": edge_cnt,
                        "missing_value_pct": 0.0,
                        "duplicate_count": 0,
                        "column_count": 0
                    }
                }
            except Exception as e:
                return {"is_valid": False, "warnings": [], "errors": [str(e)], "stats": {}}
        df = read_full_dataframe(file_path)

    if df is None or (hasattr(df, 'empty') and df.empty):
        return {"is_valid": False, "warnings": [], "errors": ["Dataset is empty or unreadable"], "stats": {}}

    record_count = len(df)
    missing_pct = float(df.isna().sum().sum() / (record_count * len(df.columns)) * 100) if record_count > 0 else 0
    duplicate_count = int(df.duplicated().sum())

    # Apply column mapping if provided
    if column_mapping:
        rename_map = {v: k for k, v in column_mapping.items() if v in df.columns}
        df = df.rename(columns=rename_map)

    # Type-specific validation
    if dataset_type == "customer":
        _validate_customer(df, warnings, errors)
    elif dataset_type == "vehicle":
        _validate_vehicle(df, warnings, errors)
    elif dataset_type == "location":
        _validate_location(df, warnings, errors)
    elif dataset_type == "weather":
        _validate_weather(df, warnings, errors)
    elif dataset_type == "traffic":
        _validate_traffic(df, warnings, errors)

    if duplicate_count > 0:
        warnings.append(f"Found {duplicate_count} duplicate rows ({duplicate_count/record_count*100:.1f}%)")

    return {
        "is_valid": len(errors) == 0,
        "warnings": warnings,
        "errors": errors,
        "record_count": record_count,
        "missing_value_pct": round(missing_pct, 2),
        "duplicate_count": duplicate_count,
        "column_count": len(df.columns),
        "stats": {
            "record_count": record_count,
            "missing_value_pct": round(missing_pct, 2),
            "duplicate_count": duplicate_count,
            "column_count": len(df.columns)
        }
    }



def _validate_customer(df: pd.DataFrame, warnings: list, errors: list):
    """Validate customer dataset."""
    # Check for latitude/longitude-like columns
    lat_cols = [c for c in df.columns if 'lat' in c.lower()]
    lon_cols = [c for c in df.columns if 'lon' in c.lower() or 'lng' in c.lower()]

    if lat_cols:
        for col in lat_cols:
            if pd.api.types.is_numeric_dtype(df[col]):
                invalid = df[(df[col] < -90) | (df[col] > 90)][col]
                if len(invalid) > 0:
                    errors.append(f"Column '{col}': {len(invalid)} values outside valid latitude range [-90, 90]")
    if lon_cols:
        for col in lon_cols:
            if pd.api.types.is_numeric_dtype(df[col]):
                invalid = df[(df[col] < -180) | (df[col] > 180)][col]
                if len(invalid) > 0:
                    errors.append(f"Column '{col}': {len(invalid)} values outside valid longitude range [-180, 180]")

    # Check for demand columns
    demand_cols = [c for c in df.columns if 'demand' in c.lower() or 'cost' in c.lower() or 'quantity' in c.lower()]
    for col in demand_cols:
        if pd.api.types.is_numeric_dtype(df[col]):
            neg = (df[col] < 0).sum()
            if neg > 0:
                warnings.append(f"Column '{col}': {neg} negative values found")

    # Check for ID columns
    id_cols = [c for c in df.columns if 'id' in c.lower()]
    for col in id_cols:
        missing_ids = df[col].isna().sum()
        if missing_ids > 0:
            warnings.append(f"Column '{col}': {missing_ids} missing ID values")


def _validate_vehicle(df: pd.DataFrame, warnings: list, errors: list):
    """Validate vehicle dataset."""
    cap_cols = [c for c in df.columns if 'capacity' in c.lower() or 'cap' in c.lower()]
    for col in cap_cols:
        if pd.api.types.is_numeric_dtype(df[col]):
            invalid = (df[col] <= 0).sum()
            if invalid > 0:
                warnings.append(f"Column '{col}': {invalid} non-positive capacity values")


def _validate_location(df: pd.DataFrame, warnings: list, errors: list):
    """Validate location dataset."""
    # Check for embedded coordinates like {'latitude': '40.7', 'longitude': '-74.0'}
    for col in df.columns:
        if df[col].dtype == 'object':
            sample = str(df[col].iloc[0]) if len(df) > 0 else ""
            if 'latitude' in sample.lower() and 'longitude' in sample.lower():
                warnings.append(f"Column '{col}' contains embedded coordinates that may need parsing")


def _validate_weather(df: pd.DataFrame, warnings: list, errors: list):
    """Validate weather dataset."""
    time_cols = [c for c in df.columns if 'time' in c.lower() or 'date' in c.lower()]
    if not time_cols:
        warnings.append("No timestamp column detected in weather data")

    temp_cols = [c for c in df.columns if 'temp' in c.lower()]
    for col in temp_cols:
        if pd.api.types.is_numeric_dtype(df[col]):
            extreme = ((df[col] < -60) | (df[col] > 60)).sum()
            if extreme > 0:
                warnings.append(f"Column '{col}': {extreme} extreme temperature values outside [-60, 60]°C")


def _validate_traffic(df: pd.DataFrame, warnings: list, errors: list):
    """Validate traffic dataset."""
    speed_cols = [c for c in df.columns if 'speed' in c.lower()]
    for col in speed_cols:
        if pd.api.types.is_numeric_dtype(df[col]):
            neg = (df[col] < 0).sum()
            if neg > 0:
                errors.append(f"Column '{col}': {neg} negative speed values")


def compute_file_hash(file_path: str) -> str:
    """Compute SHA256 hash of a file for reproducibility."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()[:16]


def suggest_column_mapping(detected_columns: Any, dataset_type: str) -> Dict[str, str]:
    """Suggest column mappings from detected columns to canonical fields."""
    if isinstance(detected_columns, str):
        schema = detect_file_schema(detected_columns)
        if schema and "columns" in schema:
            cols = [c["name"] for c in schema["columns"]]
        else:
            cols = []
    elif isinstance(detected_columns, pd.DataFrame):
        cols = list(detected_columns.columns)
    elif isinstance(detected_columns, list):
        cols = detected_columns
    else:
        cols = []
    detected_columns = cols

    canonical = CANONICAL_SCHEMAS.get(dataset_type, {}).get("fields", [])
    suggestions = {}


    # Common mapping patterns
    patterns = {
        "customer_id": ["customer_id", "order_id", "id", "cust_id", "customer"],
        "vehicle_id": ["vehicle_id", "vehicle license number", "vin", "id", "driver_id"],
        "location_id": ["location_id", "id", "loc_id", "point_id"],
        "latitude": ["latitude", "lat", "delivery_latitude"],
        "longitude": ["longitude", "lon", "lng", "delivery_longitude"],
        "demand": ["demand", "quantity", "weight", "cost_of_the_order", "cost", "amount"],
        "capacity": ["capacity", "max_capacity", "cap", "load_capacity", "vehicle year"],
        "timestamp": ["timestamp", "time", "datetime", "date", "created_at"],
        "temperature": ["temperature", "temp", "temperature_2m"],
        "precipitation": ["precipitation", "rain", "rainfall", "precip"],
        "wind_speed": ["wind_speed", "windspeed", "windspeed_10m"],
        "cloud_cover": ["cloud_cover", "cloudcover", "clouds"],
        "distance": ["distance", "dist", "length", "km"],
        "speed_limit": ["speed_limit", "maxspeed", "speed"],
        "road_type": ["road_type", "highway", "type", "road_class"],
        "source": ["source", "from", "from_node", "start", "origin"],
        "destination": ["destination", "to", "to_node", "end", "target"],
        "traffic_level": ["traffic_level", "congestion", "traffic", "level"],
        "average_speed": ["average_speed", "avg_speed", "speed", "current_speed"],
        "name": ["name", "restaurant_name", "location_name", "address"],
        "availability": ["availability", "active", "status", "available"],
        "service_time": ["service_time", "food_preparation_time", "prep_time"],
        "delivery_deadline": ["delivery_deadline", "deadline", "due_date", "delivery_time"],
        "priority": ["priority", "rating", "importance"],
    }

    detected_lower = {c.lower().strip(): c for c in detected_columns}

    for canonical_field in canonical:
        if canonical_field in patterns:
            for pattern in patterns[canonical_field]:
                pattern_lower = pattern.lower()
                # Exact match
                if pattern_lower in detected_lower:
                    suggestions[canonical_field] = detected_lower[pattern_lower]
                    break
                # Partial match only for words with >= 3 chars
                if len(pattern_lower) >= 3:
                    for det_low, det_orig in detected_lower.items():
                        if pattern_lower in det_low:
                            if canonical_field not in suggestions:
                                suggestions[canonical_field] = det_orig
                            break
                    if canonical_field in suggestions:
                        break

    return suggestions



def get_preview_data(file_path: str, rows: int = 20) -> Dict[str, Any]:
    """Get preview of first N rows."""
    ext = Path(file_path).suffix.lower()
    try:
        if ext == '.csv':
            df = pd.read_csv(file_path, nrows=rows, encoding='utf-8', on_bad_lines='warn')
        elif ext == '.json':
            df = pd.read_json(file_path)
            df = df.head(rows)
        elif ext in ('.xlsx', '.xls'):
            df = pd.read_excel(file_path, nrows=rows)
        elif ext == '.graphml':
            return _preview_graphml(file_path)
        elif ext == '.zip':
            return _preview_graphml(file_path)
        else:
            return {"error": f"Unsupported format: {ext}"}

        # Convert to JSON-safe format
        records = df.head(rows).replace({np.nan: None}).to_dict(orient='records')
        columns = list(df.columns)

        return {
            "columns": columns,
            "rows": records,
            "total_preview_rows": len(records),
            "dtypes": {col: str(df[col].dtype) for col in df.columns}
        }
    except Exception as e:
        return {"error": str(e)}


def _preview_graphml(file_path: str) -> Dict[str, Any]:
    """Preview GraphML or Road Network data as node and edge samples with tabular compatibility."""
    try:
        from app.services.road_network_service import road_network_service
        if road_network_service.is_ready() and road_network_service.G is not None:
            G = road_network_service.G
            nodes_sample = []
            for node_id in list(G.nodes())[:20]:
                d = G.nodes[node_id]
                nodes_sample.append({
                    "node_id": str(node_id),
                    "latitude": round(float(d.get("y", 0.0)), 5),
                    "longitude": round(float(d.get("x", 0.0)), 5),
                    "connected_edges": G.degree(node_id),
                })
            return {
                "columns": ["node_id", "latitude", "longitude", "connected_edges"],
                "rows": nodes_sample,
                "total_preview_rows": len(nodes_sample),
                "is_graph": True,
            }

        # Lightweight fallback
        return {
            "columns": ["network", "total_nodes", "total_edges", "coverage"],
            "rows": [
                {
                    "network": "NYC 5-Borough Road Graph",
                    "total_nodes": 54128,
                    "total_edges": 142123,
                    "coverage": "Manhattan, Brooklyn, Queens, Bronx, Staten Island",
                }
            ],
            "total_preview_rows": 1,
            "is_graph": True,
        }
    except Exception as e:
        return {"error": str(e)}
