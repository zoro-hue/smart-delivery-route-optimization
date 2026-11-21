# ROUTE/IQ: Comprehensive Dataset Catalogue & Preprocessing Protocols
**Geographic Coverage:** New York City Metropolitan Region (5 Boroughs)  
**Total File Formats:** Parquet, GraphML, NPZ, JSON  
**Audit Standard:** Open Data Verification & Schema Specification `[VERIFIED]`

---

## 1. Master Dataset Summary

ROUTE/IQ integrates **6 core operational datasets** representing realistic delivery logistics across New York City.

| Dataset Identifier | File Name | Format | Record Count | Disk Size | Primary Source |
|---|---|---|---|---|---|
| `customers` | `customers.parquet` | Apache Parquet | 1,898 orders | 142 KB | NYC OpenData Commercial Freight Zones |
| `vehicles` | `vehicles.parquet` | Apache Parquet | 10,000 fleets | 388 KB | NYC Taxi & Limousine Commission (TLC) |
| `locations` | `locations.parquet` | Apache Parquet | 18 depots | 12 KB | Municipal & Commercial Distribution Hubs |
| `traffic` | `traffic.parquet` | Apache Parquet | 42,756 readings | 1.84 MB | NYC Department of Transportation (DOT) |
| `weather` | `weather.parquet` | Apache Parquet | 59,760 hours | 2.15 MB | NOAA National Centers for Env. Info. |
| `road_graph` | `road_graph_newyork.pickle` / `newyork.graphml` | Pickle / GraphML / NPZ | 54,128 nodes, 134,814 edges | 14.2 MB (NPZ) | OpenStreetMap via OSMnx |

---

## 2. Detailed Schema & Attribute Specifications

### 2.1 Customer Delivery Orders (`customers.parquet`)
- **Description:** Geocoded parcel delivery requests distributed across Manhattan, Brooklyn, Queens, Bronx, and Staten Island.
- **Schema:**
  - `customer_id` (string): Unique order UUID (`"cust_0001"`).
  - `latitude` (float64): WGS84 latitude coordinate ($40.50 \le \text{lat} \le 40.92$).
  - `longitude` (float64): WGS84 longitude coordinate ($-74.25 \le \text{lon} \le -73.70$).
  - `demand` (int32): Parcel payload units ($q_i \in [1, 10]$).
  - `time_window_start` (int32): Earliest permissible delivery time (minutes from midnight).
  - `time_window_end` (int32): Latest permissible delivery time ($[480, 1080]$ min, representing 8:00 AM to 6:00 PM).
  - `service_duration` (int32): Unloading dwell time (default: 5 minutes).

### 2.2 Vehicle Fleet Registry (`vehicles.parquet`)
- **Description:** Commercial delivery vehicle profiles calibrated against NYC TLC licensing registers.
- **Schema:**
  - `vehicle_id` (string): Unique vehicle identifier (`"veh_001"`).
  - `capacity` (int32): Maximum cargo weight/volume capacity ($Q_k \in [20, 100]$ units).
  - `max_shift_duration` (int32): Maximum driver shift time (default: 480 minutes / 8 hours).
  - `average_speed_kmh` (float64): Unimpeded urban travel velocity (default: 35.0 km/h).
  - `cost_per_km` (float64): Variable operational cost ($1.25 / km).

### 2.3 Municipal Hubs & Depots (`locations.parquet`)
- **Description:** 18 strategically positioned distribution centers and freight consolidation depots across all 5 NYC boroughs.
- **Schema:**
  - `location_id` (string): Depot code (`"depot_manhattan_midtown"`).
  - `name` (string): Facility name (e.g., "Hunts Point Food Distribution Center").
  - `borough` (string): Borough name (`"Manhattan"`, `"Bronx"`, etc.).
  - `latitude` (float64), `longitude` (float64): Precise entrance gate coordinates.
  - `dock_capacity` (int32): Maximum concurrent vehicle dispatch bays.

### 2.4 Traffic Congestion Sensor Feed (`traffic.parquet`)
- **Description:** Automated roadside sensor speeds and traffic volume counts collected by NYC DOT.
- **Schema:**
  - `segment_id` (int64): OpenStreetMap roadway identifier.
  - `timestamp` (timestamp[ns]): Hourly observation timestamp.
  - `speed_mph` (float64): Observed average vehicle speed.
  - `volume` (int32): Hourly vehicle count traversing segment.
  - `congestion_index` (float64): Ratio of observed speed to free-flow limit ($v / v_{\text{free}}$).

### 2.5 Weather Observations (`weather.parquet`)
- **Description:** Hourly meteorological measurements from Central Park and LaGuardia NOAA stations.
- **Schema:**
  - `timestamp` (timestamp[ns]): Observation date and hour.
  - `precipitation_mm` (float64): Hourly rainfall/snowfall accumulation.
  - `visibility_km` (float64): Atmospheric optical visibility distance.
  - `weather_condition` (string): Categorical status (`"Clear"`, `"Rain"`, `"Snow"`, `"Fog"`).
