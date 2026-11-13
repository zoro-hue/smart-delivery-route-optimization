# ROUTE/IQ — PHASE P: COMPLETE MATHEMATICAL FORMULATION
**Rigorous Analytical Specifications, Objective Hamiltonians, and Proposition 1 Proof**

---

## 1. Global Optimization Problem Formulation

Let \(\mathcal{G} = (\mathcal{V}, \mathcal{E})\) be the directed street network of New York City, where \(\mathcal{V} = \{0, 1, \dots, N\}\) represents the node set (depot \(0\) and \(N\) customer delivery locations), and \(\mathcal{E} \subseteq \mathcal{V} \times \mathcal{V}\) represents the drivable road segments.

### 1.1 Decision Variables
For a homogeneous fleet of \(M\) vehicles, each with load capacity \(Q\):
\[
x_{ijk} \in \{0, 1\} = \begin{cases}
1, & \text{if vehicle } k \text{ traverses arc } (i, j) \in \mathcal{E} \\
0, & \text{otherwise}
\end{cases}
\]
\[
u_{ik} \ge 0 = \text{cumulative delivery load carried by vehicle } k \text{ after visiting customer } i
\]

### 1.2 Generalized Road Impedance Objective
Rather than minimizing straight-line Euclidean distance, ROUTE/IQ minimizes the authentic road-network dynamic impedance:
\[
\min \quad \mathcal{F}(\mathbf{x}) = \sum_{k=1}^M \sum_{i=0}^N \sum_{j=0}^N \Big( w_d \cdot D_{ij} + w_t \cdot t_{ij}(\mathbf{v}, \mathbf{c}) + \mu \cdot \mathcal{X}(r_k) \Big) x_{ijk}
\]
where:
- \(D_{ij}\): Shortest physical road distance between nodes \(i\) and \(j\) computed via Dijkstra on the NYC road graph.
- \(t_{ij}(\mathbf{v}, \mathbf{c})\): Dynamic travel time given by the Bureau of Public Roads (BPR) function:
  \[
  t_{ij} = \frac{D_{ij}}{v^0_{ij}} \left[ 1 + \alpha \left( \frac{v_{ij}}{c_{ij}} \right)^\beta \right] \cdot W_{\text{weather}}
  \]
  with standard highway calibration parameters \(\alpha = 0.15\), \(\beta = 4.0\), traffic volume \(v_{ij}\), segment capacity \(c_{ij}\), and weather impairment factor \(W_{\text{weather}} \ge 1.0\).
- \(\mathcal{X}(r_k)\): Planar edge crossing regularizer for route \(k\).
- \(w_d, w_t, \mu\): User-configurable objective weighting parameters.

### 1.3 Feasibility Constraints
1. **Customer Visit Uniqueness:**
   \[
   \sum_{k=1}^M \sum_{j=0, j \neq i}^N x_{ijk} = 1 \quad \forall i \in \{1, \dots, N\}
   \]
2. **Depot Flow Balance:**
   \[
   \sum_{j=1}^N x_{0jk} = \sum_{j=1}^N x_{j0k} \le 1 \quad \forall k \in \{1, \dots, M\}
   \]
3. **Route Continuity:**
   \[
   \sum_{i=0, i \neq p}^N x_{ipk} - \sum_{j=0, j \neq p}^N x_{pjk} = 0 \quad \forall p \in \{1, \dots, N\}, \forall k \in \{1, \dots, M\}
   \]
4. **Capacity Restriction:**
   \[
   \sum_{i=1}^N d_i \sum_{j=0, j \neq i}^N x_{ijk} \le Q \quad \forall k \in \{1, \dots, M\}
   \]
5. **Sub-tour Elimination (Miller-Tucker-Zemlin):**
   \[
   u_{ik} - u_{jk} + Q x_{ijk} \le Q - d_j \quad \forall i, j \in \{1, \dots, N\}, i \neq j, \forall k \in \{1, \dots, M\}
   \]

---

## 2. Pillar 1: Distributed Big Data Polar Sweep Partitioning

To scale to large delivery volumes, Apache Spark executes distributed capacity-aware polar partitioning:

1. **Coordinate Transformation:**
   For each customer location \((lat_i, lon_i)\) relative to depot \((lat_0, lon_0)\):
   \[
   \Delta x_i = (lon_i - lon_0) \cos\left(\frac{lat_0 \pi}{180}\right) \cdot R_{\text{earth}}, \quad \Delta y_i = (lat_i - lat_0) \cdot R_{\text{earth}}
   \]
   \[
   \theta_i = \text{atan2}(\Delta y_i, \Delta x_i) \in [-\pi, \pi]
   \]
2. **Distributed Sorting & Prefix Accumulation:**
   In PySpark, records are sorted by \(\theta_i\). Cumulative demand prefix sums \(S_i = \sum_{j \le i} d_j\) are evaluated via window functions.
3. **Partition Boundary Allocation:**
   Cluster index \(m(i) = \lfloor S_i / Q \rfloor + 1\). If \(m(i) > M\), the angular sweep wraps to balance utilization:
   \[
   \mathcal{S}_m = \{ i \in \{1, \dots, N\} \mid m(i) = m \}
   \]

---

## 3. Pillar 2: QAOA Micro-Cluster ATSP Formulation

For an extracted micro-subproblem \(\mathcal{S}_{\text{sub}}\) of \(K \le 4\) customer nodes with entry node \(u_{\text{in}}\) and exit node \(u_{\text{out}}\):

### 3.1 Binary One-Hot Encoding
Define binary decision variable \(y_{it} \in \{0, 1\}\) for customer \(i \in \{1, \dots, K\}\) at sequence position \(t \in \{1, \dots, K\}\).
Total logical qubits required: \(N_q = K^2 = 16\) qubits for \(K=4\).

### 3.2 Problem Cost Hamiltonian (\(H_C\))
\[
H_C = H_{\text{distance}} + \lambda_{\text{penalty}} \Big( H_{\text{row}} + H_{\text{col}} \Big)
\]
Where:
\[
H_{\text{distance}} = \sum_{t=1}^{K-1} \sum_{i=1}^K \sum_{j \neq i}^K D_{ij} y_{it} y_{j, t+1} + \sum_{i=1}^K D_{u_{\text{in}}, i} y_{i, 1} + \sum_{i=1}^K D_{i, u_{\text{out}}} y_{i, K}
\]
\[
H_{\text{row}} = \sum_{i=1}^K \left( \sum_{t=1}^K y_{it} - 1 \right)^2, \quad H_{\text{col}} = \sum_{t=1}^K \left( \sum_{i=1}^K y_{it} - 1 \right)^2
\]

Expressed in spin-\(1/2\) Pauli operators via \(y_{it} = \frac{I - \sigma^z_{it}}{2}\):
\[
\left( \sum_{t=1}^K y_{it} - 1 \right)^2 = \left( \sum_{t=1}^K \frac{I - \sigma^z_{it}}{2} - 1 \right)^2 = \text{const} + \sum_{t < t'} \frac{1}{2} \sigma^z_{it} \sigma^z_{it'} + \frac{K - 2}{2} \sum_{t=1}^K \sigma^z_{it}
\]

### 3.3 XY Mixer Hamiltonian (\(H_M\))
To restrict state evolution strictly to the valid permutation subspace:
\[
H_M = \frac{1}{2} \sum_{i=1}^K \sum_{t=1}^{K-1} \Big( \sigma^x_{it} \sigma^x_{i, t+1} + \sigma^y_{it} \sigma^y_{i, t+1} \Big)
\]

### 3.4 Variational Unitary & Energy Expectation
The \(p\)-layer ansatz evaluates:
\[
|\psi(\boldsymbol{\gamma}, \boldsymbol{\beta})\rangle = \prod_{l=1}^p \left( e^{-i \beta_l H_M} e^{-i \gamma_l H_C} \right) |\pi_{\text{classical}}\rangle
\]
The classical optimizer searches for:
\[
(\boldsymbol{\gamma}^*, \boldsymbol{\beta}^*) = \arg\min_{\boldsymbol{\gamma}, \boldsymbol{\beta}} \langle \psi(\boldsymbol{\gamma}, \boldsymbol{\beta}) | H_C | \psi(\boldsymbol{\gamma}, \boldsymbol{\beta})\rangle
\]

---

## 4. Planar Edge Crossing Regularizer Formulation

A persistent issue in heuristic routing is "topological tangling" (edges that cross in 2D Euclidean space).

### 4.1 Geometric Orientation Predicate
For two directed edges \(e_1 = (A, B)\) and \(e_2 = (C, D)\) with 2D coordinates:
\[
\text{ccw}(P, Q, R) = (Q_x - P_x)(R_y - P_y) - (Q_y - P_y)(R_x - P_x)
\]
Edges \(e_1\) and \(e_2\) intersect if and only if:
\[
\Big( \text{ccw}(A, B, C) \cdot \text{ccw}(A, B, D) < 0 \Big) \quad \land \quad \Big( \text{ccw}(C, D, A) \cdot \text{ccw}(C, D, B) < 0 \Big)
\]

### 4.2 Route Crossing Penalty
\[
\mathcal{X}(r) = \sum_{i=1}^{|r|-2} \sum_{j=i+2}^{|r|-1} \mathbb{I}\Big[ \text{intersect}\Big( (r[i], r[i+1]), (r[j], r[j+1]) \Big) \Big]
\]
This penalty is incorporated directly into candidate scoring during QGAR assembly.

---

## 5. Proposition 1: Monotonic Non-Degradation Guardrail

### 5.1 Theorem Statement
Let \(R_{\text{incumbent}}\) be a structurally feasible initial solution produced by classical optimization (e.g. OR-Tools or Clarke–Wright) with total cost \(C(R_{\text{incumbent}})\). Let \(R_{\text{hybrid}}\) be the candidate solution generated by the cooperative hybrid optimization pipeline. Under the Unified Incumbent Management Policy:
\[
R_{\text{final}} = \begin{cases}
R_{\text{hybrid}}, & \text{if } C(R_{\text{hybrid}}) \le C(R_{\text{incumbent}}) \text{ and } \text{IsFeasible}(R_{\text{hybrid}}) \\
R_{\text{incumbent}}, & \text{otherwise}
\end{cases}
\]
Then for every problem instance \(\mathcal{P}\), the final solution strictly satisfies:
\[
C(R_{\text{final}}) \le C(R_{\text{incumbent}})
\]

### 5.2 Proof Sketch
1. **Feasibility Preservation:** \(R_{\text{incumbent}}\) is pre-validated: \(\sum_{i \in r_k} d_i \le Q\), all customers visited once, starting/ending at depot.
2. **Deterministic Evaluation:** Both \(R_{\text{hybrid}}\) and \(R_{\text{incumbent}}\) are evaluated using the identical objective function \(\mathcal{F}(\mathbf{x})\) over the exact same physical distance matrix \(\mathbf{D}\) and impedance matrix \(\mathbf{T}\).
3. **Monotonic Acceptance:** If the quantum-assisted candidate yields \(C(R_{\text{hybrid}}) > C(R_{\text{incumbent}})\), or if \(R_{\text{hybrid}}\) violates any capacity or assignment constraint, the rejection branch triggers with certainty.
4. **Conclusion:** The cost of \(R_{\text{final}}\) is bounded above by \(\min(C(R_{\text{hybrid}}), C(R_{\text{incumbent}}))\). Hence, \(C(R_{\text{final}}) \le C(R_{\text{incumbent}})\) holds monotonically. \(\blacksquare\)

---

## 6. Verification Verdict

The mathematical formulation provides closed-form equations for every component of the cooperative pipeline. The Hamiltonian maps directly to Pauli matrices; the XY mixer guarantees permutation invariance; and Proposition 1 establishes a deterministic mathematical safety barrier against quantum degradation.

