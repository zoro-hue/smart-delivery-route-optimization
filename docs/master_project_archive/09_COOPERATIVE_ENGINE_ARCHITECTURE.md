# ROUTE/IQ: Cooperative Optimization Engine — Deep Algorithmic Architecture
**Primary Engine Designation:** ROUTE/IQ Next-Generation Cooperative Optimization Engine (`routeiq_cooperative`)  
**Implementation Source:** `backend/app/core/nextgen_cooperative_engine.py`  
**Core Components:** Multi-Armed Bandit (UCB1), ALNS Ruin-and-Recreate, Regret-3 Insertion, VND, Proposition 1 Guardrail  
**Audit Standard:** Advanced Algorithmic Systems Forensic Specification `[VERIFIED]`

---

## 1. Engine Mission & Design Philosophy

The ROUTE/IQ Cooperative Optimization Engine is engineered to produce the highest quality feasible vehicle routes by orchestrating multiple complementary optimization paradigms. Rather than relying on a single static algorithm, the Cooperative Engine operates as an **adaptive multi-metaheuristic cooperation pool**.

### 1.1 The Five Structural Stages
```
+-------------------------------------------------------------------------------+
| STAGE 1: INCUMBENT HARVESTING & FEASIBLE INITIALIZATION                       |
| Generate high-quality initial solution via OR-Tools / Clarke-Wright Savings   |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
| STAGE 2: MULTI-ARMED BANDIT (UCB1) HYPER-HEURISTIC ORCHESTRATOR               |
| Dynamically select operator arm based on online reward ratios & time budget   |
+-------------------------------------------------------------------------------+
                                       |
         +-----------------------------+-----------------------------+
         v                                                           v
+----------------------------------+          +---------------------------------+
| OPERATOR POOL A: ALNS RUIN & REC |          | OPERATOR POOL B: QUANTUM & VND  |
| - Shaw Relatedness Removal       |          | - Simulated QAOA Boundary Swap  |
| - Worst-Cost Edge Removal        |          | - QIGA Qubit Rotation           |
| - Random Perturbation Removal    |          | - Variable Neighborhood Descent |
| - Regret-3 Opportunity Insertion |          |   (2-opt, Relocate, Exchange)   |
+----------------------------------+          +---------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
| STAGE 3: FEASIBILITY REPAIR & SUBTOUR VALIDATION                              |
| Strict check of capacity Q_k, depot returns, and directed road connectivity   |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
| STAGE 4: PROPOSITION 1 MONOTONIC ACCEPTANCE GUARDRAIL                         |
| Cost(Candidate) < Cost(Incumbent) -> Accept new Incumbent                     |
| Otherwise -> Reject Candidate, Preserve Incumbent                             |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
| STAGE 5: ROAD-NETWORK RECONSTRUCTION & GEOMETRY SERIALIZATION                 |
| Trace exact directed road-network edges & compute BPR congestion delays       |
+-------------------------------------------------------------------------------+
```

---

## 2. Deep Dive: Adaptive Large Neighborhood Search (ALNS)

ALNS is the primary diversification and intensification engine within Stage 2. It systematically destroys portions of the incumbent solution and rebuilds them using intelligent heuristics.

### 2.1 Removal Operators (Ruin)
1. **Shaw Relatedness Removal:**
   Selects a seed customer $r$ and removes $q$ related customers based on a relatedness measure $R(i, j)$:
   $$R(i, j) = \phi_1 \frac{d(i, j)}{\max d} + \phi_2 \frac{|q_i - q_j|}{\max q} + \phi_3 \left( 1 - \frac{|\text{TW}_i \cap \text{TW}_j|}{\max \text{TW}} \right)$$
   Where $d(i, j)$ is road distance, $q$ is parcel demand, and $\text{TW}$ is delivery time window overlap. Customers with small $R(i, j)$ are strongly related and removed together to allow meaningful neighborhood restructuring.
2. **Worst-Cost Removal:**
   Computes the cost reduction achieved by removing each customer $i$ from its current route:
   $$\text{cost}(i) = \text{dist}(\text{prev}(i), i) + \text{dist}(i, \text{next}(i)) - \text{dist}(\text{prev}(i), \text{next}(i))$$
   Sorts customers in descending order of cost and probabilistically removes the most expensive stops using a randomized exponent $y^{p_{\text{worst}}}$.
3. **Random Removal:**
   Removes $q$ customers uniformly at random to break out of deep local attractors and inject search entropy.

### 2.2 Insertion Operators (Recreate): Regret-3 Insertion
Unlike simple greedy insertion (which places customers into their cheapest immediate position), **Regret-3 Insertion** prevents shortsighted decisions by considering the opportunity cost of not inserting a customer into its best route:
For each unassigned customer $u$, compute the insertion cost into its best route ($c_{u, 1}$), second-best route ($c_{u, 2}$), and third-best route ($c_{u, 3}$).
The regret value is:
$$\text{Regret}_3(u) = (c_{u, 2} - c_{u, 1}) + (c_{u, 3} - c_{u, 1})$$
The customer with the **maximum regret** is inserted first into its optimal position. This prioritizes customers that have few good placement options, dramatically improving final route efficiency.

---

## 3. Proposition 1 Monotonic Feasibility Guardrail

### 3.1 Formal Mathematical Definition
Let $S_{\text{incumbent}}$ denote the incumbent feasible CVRP solution, and let $S_{\text{candidate}}$ denote a newly constructed candidate solution produced by ALNS, QAOA, QIGA, or VND.
The Proposition 1 Acceptance Guardrail is defined as:

$$S_{\text{next}} = \begin{cases} 
S_{\text{candidate}} & \text{if } \text{Feasible}(S_{\text{candidate}}) \land \text{Cost}(S_{\text{candidate}}) < \text{Cost}(S_{\text{incumbent}}) \\
S_{\text{incumbent}} & \text{otherwise}
\end{cases}$$

### 3.2 Inductive Proof of Non-Degradation
- **Base Case:** At iteration $t = 0$, $S_0$ is initialized via OR-Tools or Clarke-Wright. Since the initial heuristic is strictly feasible, $\text{Feasible}(S_0) = \text{True}$.
- **Inductive Step:** Assume $S_t$ is feasible and $\text{Cost}(S_t) \le \text{Cost}(S_0)$. At iteration $t+1$:
  - If $S_{\text{candidate}}$ is accepted, then by definition $\text{Feasible}(S_{\text{candidate}}) = \text{True}$ and $\text{Cost}(S_{\text{candidate}}) < \text{Cost}(S_t)$. Therefore $\text{Cost}(S_{t+1}) < \text{Cost}(S_t) \le \text{Cost}(S_0)$.
  - If $S_{\text{candidate}}$ is rejected, $S_{t+1} = S_t$. Therefore $\text{Cost}(S_{t+1}) = \text{Cost}(S_t) \le \text{Cost}(S_0)$.
- **Conclusion:** By mathematical induction, for all iterations $T \ge 0$, $\text{Cost}(S_T) \le \text{Cost}(S_0)$ and $\text{Feasible}(S_T) = \text{True}$.
**The Cooperative Engine cannot degrade below the quality of its initial incumbent.**
