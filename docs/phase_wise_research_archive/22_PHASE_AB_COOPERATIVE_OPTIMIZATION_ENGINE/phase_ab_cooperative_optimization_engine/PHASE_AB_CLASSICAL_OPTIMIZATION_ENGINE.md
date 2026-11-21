# PHASE AB DELIVERABLE 5: CLASSICAL OPTIMIZATION FOUNDATION

## Project: ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing
**Institution:** SRM University-AP | **Supervisor:** Dr. Vishnu Prasad Verma

---

## 1. Role of Classical Optimization in ROUTE/IQ

Classical algorithms provide the foundational bedrock of ROUTE/IQ. No quantum circuit can solve a delivery logistics routing problem in isolation:
1. **Initial Incumbent Creation:** Solves baseline vehicle routing using Google OR-Tools constraint programming.
2. **Metaheuristic Partition Exploration:** Provides high-speed, diverse bipartition exploration using Kernighan-Lin, Tabu Search, and Uniform Random Feasible sampling.
3. **Tour Construction:** Converts discrete set partitions into sequenced Hamiltonian paths using greedy insertion.
4. **Algorithmic Local Search (VND):** Optimizes the resulting routes across multiple deterministic topological neighborhoods.

---

## 2. Metaheuristic Partition Solvers

Implemented in [`ClassicalOptimizationEngine`](file:///d:/UROP/smart-delivery-route-optimization/phase_ab_cooperative_optimization_engine/engine/classical_engine.py) and [`candidate_generators.py`](file:///d:/UROP/smart-delivery-route-optimization/phase_ab_cooperative_optimization_engine/engine/candidate_generators.py):

### 1. Single-Pass Kernighan-Lin (KL)
- **Mechanism:** Computes the net gain $g_{ab} = D_a + D_b - 2 c_{ab}$ for exchanging customer $a \in A$ with $b \in B$.
- **Complexity:** $O(N^2)$ per pass.
- **Latency:** $\approx 4.1\text{ ms}$.
- **Performance:** Fleet distance **603.72 km** (accepted 40.0%).

### 2. Multistart Kernighan-Lin (MS-KL)
- **Mechanism:** Initiates multiple KL trajectories from randomized initial feasible seeds, perturbing assignments to escape shallow local minima.
- **Latency:** $\approx 22.4\text{ ms}$.
- **Performance:** Fleet distance **598.14 km** (accepted 53.3%).

### 3. Tabu Search
- **Mechanism:** Employs a short-term recency memory tenure matrix preventing recent swaps from being reversed for $T$ iterations ($T = 7$). Incorporates aspiration criteria that override tabu status if a global incumbent improvement is found.
- **Latency:** $\approx 33.85\text{ ms}$.
- **Performance:** Fleet distance **595.45 km** (accepted **60.0%**, highest acceptance rate of any standalone generator).

### 4. Uniform Random Feasible Sampling
- **Mechanism:** Generates random uniform bitstrings filtered strictly by capacity limits.
- **Latency:** $\approx 53.0\text{ ms}$ for 512 samples.
- **Performance:** Fleet distance **602.90 km** (accepted 46.7%).

---

## 3. Algorithmic Variable Neighborhood Descent (VND)

Algorithmic VND operates deterministically across four hierarchical neighborhoods:
1. **Intra-Route 2-Opt:** Reverses subpaths within the same route to eliminate crossed edges.
2. **Inter-Route Relocate:** Transfers a customer from Route $A$ to Route $B$ if capacity permits and distance decreases.
3. **Inter-Route Swap:** Exchanges two customer positions between Route $A$ and Route $B$.
4. **Inter-Route Cross-Exchange:** Swaps and optionally reverses two segments of length up to 2 between Route $A$ and Route $B$.

Whenever a neighborhood produces a strictly improving move, VND restarts from Neighborhood 1. The search terminates at a local optimum across all 4 neighborhoods.

### Impact of Initial VND on Greedy Routing
- Raw OR-Tools Incumbent: **1,307.16 km**
- OR-Tools + VND: **621.45 km**
- **Immediate Improvement:** **685.71 km cut (52.46% reduction)** in just $8.27\text{ ms}$ average runtime.
