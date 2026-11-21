# Limitations and Threats to Validity Document

**Project:** ROUTE/IQ: Intelligent Delivery Route Optimization Using Hybrid Big Data, Quantum Computing, and Cooperative Vehicle Fleet Optimization  
**Institutional Affiliation:** Department of Computer Science and Engineering, SRM University-AP, Amaravati, Andhra Pradesh, India  
**Authors:** J. Jayanth, B. Kaivalya, P. Shyam Sai (Undergraduate Research Scholars)  
**Faculty Research Supervisor:** Dr. Vishnu Prasad Verma  
**Date:** November 21, 2026  

---

## 1. Explicit Scientific Disclosures and Boundaries

In strict adherence to academic integrity and empirical research standards, we document the precise boundaries and negative findings of our research:

### 1. Classical Simulation of Quantum Circuits
- **Disclosure:** All QAOA circuits were simulated classically using the Qiskit Aer statevector simulator on a multi-core x86-64 CPU.
- **Scientific Boundary:** No experiments were conducted on physical quantum hardware (e.g., IBM Quantum Eagle/Heron QPUs). We make **zero claims of quantum supremacy or physical quantum speedup**.
- **Practical Implication:** In current computational environments, classical statevector simulation of QAOA incurs exponential memory and time complexity $O(2^n)$. On classical hardware, QAOA functions purely as a novel stochastic combinatorial diversification operator.

### 2. Classical Heuristic Dominance at Small Scales ($N \le 15$)
- **Empirical Finding:** On small instances with $N \le 15$ delivery stops, Google OR-Tools alone discovers the optimal routing permutation in less than $150	ext{ ms}$.
- **Boundary:** Cooperative co-evolution, quantum boundary cuts, and genetic mutation introduce unnecessary computational overhead on small instances. The cooperative architecture is practically beneficial only when graph scale exceeds $N \ge 20$ stops.

### 3. Apache Spark Local JVM Overhead
- **Empirical Finding:** Initializing a local PySpark context (`local[*]`) incurs $1.5	ext{--}2.5	ext{ s}$ of JVM bootstrap latency.
- **Boundary:** PySpark is unsuited for interactive, sub-second single-query dispatching. In ROUTE/IQ, Spark is deployed exclusively for offline batch transformations of large historical datasets ($>10,000$ points), while real-time routing utilizes vectorized NumPy/SciPy execution.

### 4. Static Traffic and Deterministic Range Assumptions
- **Boundary:** Congestion travel times are computed using deterministic BPR formulas based on static arc volumes, rather than microscopic dynamic traffic simulations. Similarly, battery consumption is modeled using linear average discharge rates rather than continuous elevation, temperature, and acceleration profiles.

---

## 2. Threats to Validity

### Threats to Internal Validity
- **Parameter Sensitivity:** The Contextual MAB reward weights ($w_1=0.50, w_2=0.25, w_3=0.20, w_4=0.05$) and exploration parameter $c=1.414$ were calibrated empirically. Altering these weights could shift operator selection preferences.
- **Simulation Stochastics:** Quantum statevector simulation and QIGA rotation gates rely on pseudorandom number generators. To mitigate stochastic bias, all experimental configurations were evaluated under identical seeds.

### Threats to External Validity
- **Geographic Generalizability:** Benchmark instances were generated from New York City delivery coordinates (Manhattan, Brooklyn, Queens). While NYC features dense urban grids and bridge bottlenecks, results may differ in sprawling suburban networks or regions with sparse road topologies.
- **Fleet Composition:** Evaluated fleets comprised up to 5 vehicles with 3 powertrain categories. Fleet scales with hundreds of vehicles will require multi-tier spatial clustering before cooperative optimization.
