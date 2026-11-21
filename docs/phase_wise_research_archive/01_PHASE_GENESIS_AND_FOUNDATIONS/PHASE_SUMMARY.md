# Phase 1 / Foundations: Genesis & Classical Routing Foundations

## 1. Executive Metadata
* **Phase Identifier:** `Phase 1 / Foundations`
* **Archive Directory:** `01_PHASE_GENESIS_AND_FOUNDATIONS/`
* **Time Horizon:** Sept 1 – Sept 20, 2026
* **Git References:** Commits `22589ea` through `5fa3313`
* **Next Phase Connection:** Transitioned to Phase G / Dual-Pillar Architecture to build initial PySpark polar sweep and Qiskit QAOA subproblem formulations.

---

## 2. Research Objective & Motivation
Establish project scope with supervisor Prof. Vishnu Prasad Verma; formulate NYC last-mile delivery problem; extract NYC OSM road networks, NYC OpenData commercial delivery zones, and TLC fleet profiles; implement baseline classical solvers (Dijkstra, A*, Clarke-Wright Savings).

---

## 3. Key Technical Changes & Implementation
OSM graph extraction via OSMnx (54,128 nodes, 134,814 edges); initial FastAPI + React 18 Leaflet map; Dijkstra predecessor shortest path caching; initial CVRP capacity tracking.

---

## 4. Algorithmic Formulations & Innovations
* **Algorithms Evaluated / Built:** Dijkstra, A* Search, Clarke-Wright Savings, Nearest Neighbor, 2-Opt local search.
* **Apache Spark Big Data Contributions:** Initial data ingestion pipeline scripts for 1,898 NYC commercial zones and 10,000 TLC vehicle records.
* **Quantum Computing & QAOA Contributions:** Literature review of Farhi (2014) QAOA and Hadfield (2019) quantum alternating operator ansatz.
* **Cooperative Optimization Engine Developments:** Conceptual foundation: identified that standalone quantum solvers cannot scale to realistic NYC networks without decomposition.

---

## 5. Experimental Configurations & Empirical Results
Benchmarked Clarke-Wright vs nearest neighbor across synthetic Manhattan delivery clusters.

### Key Quantitative Findings:
Clarke-Wright achieved 14.8% savings over nearest neighbor; revealed that raw Dijkstra without graph contraction is too slow for real-time web routing.

---

## 6. Negative Findings, Failed Approaches & Limitations
Zero quantum execution; memory spikes on large OSM networks without edge simplification; homogeneous vehicle capacity assumption.

---

## 7. Archived Documents in this Phase
- [`01_PROJECT_IDENTITY_AND_OBJECTIVES.md`](01_PROJECT_IDENTITY_AND_OBJECTIVES.md)
- [`12_DATASET_CATALOGUE.md`](12_DATASET_CATALOGUE.md)
- [`13_ROAD_NETWORK_DOCUMENTATION.md`](13_ROAD_NETWORK_DOCUMENTATION.md)
- [`15_LITERATURE_REVIEW_AND_RESEARCH_GAP.md`](15_LITERATURE_REVIEW_AND_RESEARCH_GAP.md)
