# ROUTE/IQ: Project Implementation vs. Literature Survey Approach Differences

**Document Purpose:** Comprehensive audit comparing the theoretical framework and literature review in `LITERATURE_SURVEY (4).pdf` against the actual codebase implementation of the **ROUTE/IQ** platform (`smart-delivery-route-optimization`).

* **Institution:** Department of Computer Science and Engineering, SRM University-AP, Amaravati, Andhra Pradesh, India
* **Research Program:** Undergraduate Research Opportunity Program (UROP)
* **Faculty Supervisor:** Dr. Vishnu Prasad Verma
* **Student Researchers:** J. Jayanth, B. Kaivalya, P. Shyam Sai
* **Primary Survey Reference:** `LITERATURE_SURVEY (4).pdf` (8 pages, 20 reviewed papers, 5 primary categories)
* **Implementation Ground Truth:** Active source code in `backend/` and `frontend/`

---

## 1. Executive Summary of Audit Findings

The literature survey (`LITERATURE_SURVEY (4).pdf`) articulates an academic motivation for bridging Big Data transportation analytics and Quantum Computing (specifically QAOA) for vehicle routing. When comparing the paper's narrative against the actual software implementation, the core conceptual pipeline (`Transportation Data → Big Data Processing → Route Optimization → QUBO → QAOA`) is genuinely implemented. 

However, several notable differences exist between the broad academic review and the engineering realities of the software:

1. **Big Data Execution Model:** The survey paper mentions "real-time traffic information", "continuous data updates", and "streaming IoT/GPS feeds" (citing Chen [1], Zheng [2], and Jagarlamudi [18]). In contrast, ROUTE/IQ genuinely implements **offline batch ETL via Apache Spark 4.2.0** generating curated Parquet datasets. There is no active Apache Kafka or live sensor streaming in the codebase.
2. **Quantum Hardware vs. Classical Simulation:** The survey paper discusses quantum processing and hardware limitations broadly (citing Azad [7], Yarkoni [8], Sarkar [9]). ROUTE/IQ executes QAOA entirely via **classical CPU statevector simulation** (`qiskit.primitives.StatevectorSampler` on Qiskit 2.4.1), strictly limited to small instances ($N \le 20$ decision qubits) to prevent exponential RAM exhaustion.
3. **Absence of QIGA in the Survey Paper:** While ROUTE/IQ implements a functioning **Quantum-Inspired Genetic Algorithm (QIGA)** solver using qubit probability amplitudes $(\alpha, \beta)$ and rotation gate updates on classical hardware (`qiga_solver.py`), **QIGA is not mentioned anywhere in `LITERATURE_SURVEY (4).pdf`**. The survey focuses solely on QAOA and quantum annealing.
4. **Integration Mechanism:** In ROUTE/IQ, Big Data and Quantum Computing are integrated through an **enriched road-network cost matrix**: Spark processes historical speeds and weather slowdown factors into Parquet tables; at request-time, the API uses these curated factors to scale A* travel costs across the OpenStreetMap road graph before the cost matrix is passed to the classical or quantum/quantum-inspired solvers.
5. **Geographic Grounding:** The survey paper treats VRP as an abstract mathematical graph problem. ROUTE/IQ specifically grounds routing on **New York City's OpenStreetMap road network** (54,128 nodes, 142,123 edges) with strict ray-casting boundary validation.

---

## 2. Comprehensive Discrepancy & Alignment Matrix

| Topic | What our survey paper says (`LITERATURE_SURVEY (4).pdf`) | What ROUTE/IQ actually implements (`smart-delivery-route-optimization`) | Difference type | Recommended action for the survey |
|---|---|---|---|---|
| **Big Data Architecture & Processing Model** | Mentions "real-time traffic data", "continuous data updates" (Fig. 2), and dynamic streams from GPS/IoT sensors (Sections 1, 4, 5, 6, citing Chen [1], Zheng [2], Zhu [3]). | Implements an **offline batch ETL pipeline** using Apache Spark 4.2.0 (`backend/app/services/bigdata_pipeline.py`). Ingests static raw CSVs and outputs curated Parquet files. No streaming engine (Kafka/Flink) is implemented. | **Major technical mismatch** | Clarify in Sections 4 & 5 that the companion prototype uses batch Apache Spark ETL to construct curated traffic/weather baseline profiles, leaving low-latency streaming ingestion as a future extension. |
| **Dataset Sources & Data Preparation** | Broadly lists GPS, traffic information, customer requirements, vehicle information, weather, and road conditions (Section 4, Page 2). | Specifically ingests 5 heterogeneous datasets totaling 114,642 verified records: NYC TLC Yellow Taxi, NYC DOT traffic volume counts, NOAA Central Park weather observations, synthetic customer orders, and municipal vehicle fleets. Stores results in `backend/data/processed/spark_output/*.parquet`. | **Missing implementation detail in the survey** | Expand Section 4 to explicitly name the real-world NYC datasets and Parquet schema curation implemented in the companion system. |
| **Quantum Optimization Formulation (QAOA)** | Formulates delivery problem as binary decision variables transformed into QUBO, solved by QAOA (Sections 4, 9, 19, 21; Eq. 1 & 2). | Accurately implements binary decision variables $x_{i,t}$, maps constraints via penalty weights $\lambda_1, \lambda_2$ to an Ising Hamiltonian ($Z_i Z_j$ couplings), and solves using a 2-layer parameterized QAOA ansatz optimized via COBYLA (`backend/app/services/optimization/quantum_solver.py`). | **Consistent — no change needed** | Retain existing mathematical formulations in Sections 4 and 9. |
| **Quantum Hardware vs. Simulation** | Refers to "Quantum Optimization Layer: QAOA and Quantum Processing" (Fig. 2) and discusses "limitations of current quantum hardware" (Section 20.D, citing [7], [9]). | Strictly runs via **classical CPU simulation** using Qiskit 2.4.1 `StatevectorSampler`. Does not connect to IBM Quantum or D-Wave physical QPUs. Memory constraints restrict problems to $\le 20$ qubits (e.g., 3-4 stops). | **Terminology or framing mismatch** | Explicitly state in Sections 4, 9, and 20.D that experimental evaluation was conducted using classical statevector circuit simulation rather than physical QPU execution. |
| **Quantum-Inspired Genetic Algorithm (QIGA)** | **Not discussed in the survey paper.** The survey reviews only QAOA and quantum annealing ([7], [8], [11], [12]). | Genuinely implemented in `backend/app/services/optimization/qiga_solver.py`. Represents chromosome permutations using probability amplitudes $[\cos(\theta), \sin(\theta)]$, updates states via quantum rotation gates $\Delta \theta$, and runs efficiently on classical CPUs for larger stop counts. | **Missing implementation detail in the survey** | Add a subsection to Section 9 or Section 21 introducing Quantum-Inspired Genetic Algorithms (QIGA) as a bridge between classical heuristics and NISQ-limited QAOA. |
| **Big Data + QC Integration Mechanism** | Conceptual workflow: `Transportation Data → Big Data Processing → Route Optimization → QUBO → QAOA` (Sections 4, 19, 21). | Concrete data flow: Spark batch ETL aggregates traffic speeds and weather conditions into Parquet. At runtime, the API extracts hourly speed and weather multiplier floats to scale shortest-path road costs. The resulting enriched cost matrix is then supplied to QAOA/QIGA. | **Missing implementation detail in the survey** | Detail the exact cost-enrichment integration mechanism in Section 4, explaining how Big Data outputs calibrate the cost matrix fed to QUBO/QAOA. |
| **Classical Optimization Baselines** | Mentions classical processing for data preparation, constraint handling, and route reconstruction (Section 4, Page 2). | Implements 3 production classical routing solvers for direct benchmarking: Google OR-Tools (Guided Local Search), Clarke–Wright Savings, and 2-opt, alongside Dijkstra and A* road search (`backend/app/services/optimization/classical_solver.py`). | **Missing implementation detail in the survey** | Mention Google OR-Tools and Clarke–Wright savings in Section 4 as essential classical baselines for benchmarking quantum routing quality. |
| **Geographic Road-Network Validation & Snapping** | Abstract graph formulation; treats distances as edge weights without discussing GIS or map networks. | Implements dual-layer geographic validation (5-borough polygon ray-casting and Long Island exclusion) and snaps GPS stops to the nearest node on a 54,128-node OpenStreetMap Manhattan/Bronx road graph (`road_network_service.py`). | **Missing implementation detail in the survey** | Highlight in Section 4 or Section 20 that realistic road-network graph topology is necessary to avoid inaccurate Euclidean assumptions. |
| **Dynamic Route Re-Optimization** | Discusses dynamic re-optimization as a critical need when traffic or demand changes during delivery (Section 20.E, Section 22). | ROUTE/IQ allows users to adjust interactive scenario sliders (traffic congestion factor, weather severity factor) in the UI to dynamically re-trigger route optimization. However, it does not autonomously re-route in-transit vehicles. | **Terminology or framing mismatch** | Clarify that dynamic re-optimization in the companion tool is user-driven scenario simulation rather than automated telemetry re-routing. |
| **Performance Claims & Quantum Speedup** | Avoids claiming quantum supremacy; notes that quantum routing is evaluated on limited problem sizes due to hardware limits (Section 20.A, 20.D). | Consistent with implementation reality. QAOA takes 5.46s for 3 stops on CPU simulator, whereas OR-Tools takes 0.008s and achieves equal or superior tour length. No quantum speedup claim is made. | **Consistent — no change needed** | Maintain this honest, academically rigorous tone. |

---

## 3. Recommended Text Revisions for the Survey Paper

To harmonize `LITERATURE_SURVEY (4).pdf` with the companion software implementation in future revisions, the following replacement text is recommended:

### A. Clarifying Big Data Processing (Section 4, Page 2)
* **Current Survey Text:**
  > *"Transportation information can be collected from GPS devices, traffic information, customer requirements, vehicle information, weather conditions, and road conditions. The collected information can be processed using Big Data techniques to obtain transportation information required for route optimization."*
* **Recommended Replacement Text:**
  > *"Transportation information is gathered across heterogeneous datasets, including municipal vehicle fleet specifications, customer order coordinates, historical road-segment traffic counts, and multi-year weather observations. In our companion implementation (ROUTE/IQ), this information is processed via an Apache Spark 4.2.0 batch ETL pipeline to construct curated Parquet tables with median imputation and standardized roadway taxonomy. While live IoT/GPS streaming represents an ideal target architecture, batch Parquet curation provides a robust, reproducible foundation for calibrating route cost models."*

### B. Incorporating Quantum Simulation and QIGA (Section 9, Page 3)
* **Current Survey Text:**
  > *"The Quantum Approximate Optimization Algorithm is a hybrid quantum-classical algorithm that can be applied to combinatorial optimization problems... Azad et al. [7] investigated QAOA for the Vehicle Routing Problem..."*
* **Recommended Replacement Text:**
  > *"The Quantum Approximate Optimization Algorithm (QAOA) is a hybrid quantum-classical algorithm designed for combinatorial optimization problems. In experimental routing implementations, CVRP instances are mapped to Quadratic Unconstrained Binary Optimization (QUBO) formulations and converted to Ising Hamiltonians. Given the qubit and decoherence constraints of current physical quantum processors, routing circuits are primarily evaluated using classical statevector simulators (e.g., Qiskit StatevectorSampler), which encounter severe memory scaling limits beyond 20 qubits. To address this computational bottleneck on classical architectures, Quantum-Inspired Genetic Algorithms (QIGA)—which utilize qubit probability amplitude vectors and quantum rotation gates without requiring quantum hardware—can serve as an intermediate, scalable bridge for medium-scale routing instances."*

### C. Detailing the Integration Mechanism (Section 19, Page 6)
* **Current Survey Text:**
  > *"The proposed project can therefore be represented as: Transportation Data → Big Data Processing → Route Optimization → QUBO → QAOA"*
* **Recommended Replacement Text:**
  > *"The integrated hybrid framework operates via cost-matrix enrichment: Large-scale transportation datasets are cleaned and aggregated offline using Apache Spark to yield hourly speed profiles and weather friction coefficients. At optimization request-time, these curated Big Data metrics scale the edge traversal costs across an OpenStreetMap street graph. The resulting cost matrix is then supplied to the selected solver—whether classical baselines (Google OR-Tools, Clarke-Wright, 2-opt), quantum-inspired heuristics (QIGA), or a QUBO/QAOA quantum circuit formulation."*

---

## 4. Summary of Impact on Research Contributions

1. **Does the discrepancy diminish the paper's contribution?**  
   **No.** The survey paper's primary contribution is a structured 20-paper taxonomy, timeline distribution, and conceptual framework across Big Data and Quantum Computing. Describing the companion software accurately as an offline batch ETL pipeline with classical statevector QAOA simulation and QIGA heuristics strengthens academic credibility by demonstrating rigorous awareness of current NISQ limitations.
2. **Key Enhancement:**  
   Explicitly introducing QIGA into future revisions of the survey paper directly answers the scalability gap (Section 20.A), as QIGA provides a quantum-inspired alternative capable of handling 20+ stops where QAOA statevector simulation exhausts classical CPU RAM.
