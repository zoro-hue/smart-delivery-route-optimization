# ROUTE/IQ: Master Autonomous Knowledge Package for AI Agents & Researchers
**Document Role:** Universal Autonomous Context Package  
**Target:** AI Coding Agents, New Research Investigators, Independent Evaluators  
**System Designation:** ROUTE/IQ (Smart Delivery Route Optimization)  
**Audit Standard:** Complete Standalone Knowledge Transfer `[VERIFIED]`

---

## 1. System Overview & Core Directives

### 1.1 What ROUTE/IQ Is
ROUTE/IQ is an enterprise-grade, cloud-deployed research platform for urban delivery route optimization. It solves the **Capacitated Vehicle Routing Problem (CVRP)** on a real 54,128-node directed road network of New York City, incorporating Bureau of Public Roads (BPR) volume-delay traffic congestion and NOAA weather modifiers.

### 1.2 Core Architectural Invariant: Proposition 1
Under NO circumstances should candidate solutions degrade the system. The Proposition 1 Monotonic Feasibility Guardrail must always hold:
$$\text{Cost}(S_{\text{final}}) = \min(\text{Cost}(S_{\text{incumbent}}), \text{Cost}(S_{\text{candidate}}))$$
A candidate solution produced by ALNS, QAOA, QIGA, or VND is accepted if and only if it strictly preserves capacity and depot feasibility AND achieves a lower road-network travel distance than the incumbent.

### 1.3 Quantum Simulation Honesty
All quantum algorithms (QAOA, QIGA) execute via **classical CPU statevector simulation** using Qiskit Aer 2.4.1 ($n \le 16$ qubits). NEVER claim physical quantum supremacy on hardware QPUs.

### 1.4 Production Repositories & URLs
- **Repository Path:** `d:\UROP\smart-delivery-route-optimization`
- **Active Research Branch:** `research/next-generation-cooperative-engine` (HEAD `93e8771`)
- **Main Production Branch:** `main` (commit `08a4538`)
- **Live Frontend:** `https://route-iq-frontend-nine.vercel.app`
- **Live Backend:** `https://route-iq-backend.onrender.com`
