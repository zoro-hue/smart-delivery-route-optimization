# Deliverable 5: Phase Y Apache Spark Multi-Node Cluster Implementation

## 1. Multi-Node Cluster Architecture

To transition from single-machine `local[*]` execution to verified multi-worker scaling, Phase Y implemented a containerized Apache Spark Standalone cluster architecture:

```
[ Spark Driver (ROUTE/IQ Orchestrator) ]
                   │
                   ▼
       [ Spark Master Node: 7077 ]
           │                 │
           ▼                 ▼
[ Worker Node 1: 2 Cores ]  [ Worker Node 2: 2 Cores ]
  (2 GB RAM, Bitnami)         (2 GB RAM, Bitnami)
```

---

## 2. Containerized Cluster Manifests

All configuration files are fully implemented and preserved in `phase_y_breakthrough_engineering/cluster/`:

1. **`docker-compose.yml`**: Defines the `spark-master`, `spark-worker-1`, and `spark-worker-2` services connected over an isolated bridge network (`spark-net`).
2. **`Dockerfile`**: Builds the custom worker image with Python 3.10+, NumPy, Pandas, and PySpark.
3. **`spark-defaults.conf`**: Configures Kryo serialization, executor memory (2G), core allocations (2 per worker), and 8 shuffle partitions.

---

## 3. Host Environment Status & Verification Disclaimer

- **Host Operating System**: Microsoft Windows 11 / Windows Server without Docker Engine installed.
- **Cluster Deployment Status**: **CONFIGURATION COMPLETE; CLUSTER EXECUTION UNVERIFIED DUE TO MISSING DOCKER DAEMON**.
- **Execution Mode**: In the absence of Docker, single-machine multi-threaded parallel execution modes (`local[1]`, `local[2]`, `local[4]`) were benchmarked up to 100,000 delivery stops, preserving scientific transparency.

