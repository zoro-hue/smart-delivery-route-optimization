# Reproducibility Guide and Verification Protocol

**Project:** ROUTE/IQ: Intelligent Delivery Route Optimization Using Hybrid Big Data, Quantum Computing, and Cooperative Vehicle Fleet Optimization  
**Institutional Affiliation:** Department of Computer Science and Engineering, SRM University-AP, Amaravati, Andhra Pradesh, India  
**Authors:** J. Jayanth, B. Kaivalya, P. Shyam Sai (Undergraduate Research Scholars)  
**Faculty Research Supervisor:** Dr. Vishnu Prasad Verma  
**Date:** November 21, 2026  

---

## 1. System Requirements

### Hardware Environment
- Processor: x86-64 multi-core CPU (Intel Core i5/i7 or AMD Ryzen 5/7/9, $\ge 4$ physical cores).
- RAM: Minimum 8 GB (16 GB recommended for PySpark and Qiskit Aer simulation).
- Disk: $\ge 2$ GB free space.
- Operating System: Windows 10/11, Ubuntu 20.04+, or macOS 12+.

### Software Dependencies
- Python 3.10 or 3.11
- Apache Spark 3.5+ or 4.2+ (with PySpark)
- Java OpenJDK 11 or 17 (required for PySpark)
- Google OR-Tools 9.9+
- Qiskit 1.0+ and Qiskit-Aer 0.14+
- NumPy, SciPy, Matplotlib, ReportLab, python-docx

---

## 2. Installation and Environment Setup

```bash
# Clone the repository
git clone https://github.com/zoro-hue/smart-delivery-route-optimization.git
cd smart-delivery-route-optimization

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scriptsctivate
# Linux/macOS:
source venv/bin/activate

# Install required Python packages
pip install ortools qiskit qiskit-aer pyspark numpy scipy matplotlib python-docx reportlab pymupdf
```

---

## 3. Step-by-Step Reproduction of Benchmark Suite

To reproduce the complete 9-configuration empirical benchmark suite reported in the journal paper:

```bash
# Execute the comprehensive automated benchmark suite
python scripts/benchmark_nextgen_cooperative_suite.py
```

### Verification Checklist:
1. The script will execute all 9 configurations across NYC delivery instances ($N \in [12, 30]$).
2. Raw JSON benchmark metrics are saved to `scripts/benchmark_nextgen_results.json`.
3. Verify the final benchmark output matches:
   - Google OR-Tools Mean Distance: $pprox 181.57	ext{ km}$
   - Next-Gen Cooperative Engine Mean Distance: $pprox 179.31	ext{ km}$ ($-1.24\%$ reduction)
   - $N=30$ Node Instance Distance: $pprox 250.76	ext{ km}$ ($-3.16\%$ reduction vs OR-Tools $258.95	ext{ km}$)
   - Mean Latency: $pprox 1219.2	ext{ ms}$ ($24.0\%$ speedup vs legacy $1604.0	ext{ ms}$)
   - Feasibility Rate: $100.0\%$
   - Guardrail Assertions: `assert final_distance <= ortools_distance + 1e-4` passed for 100% of runs.

---

## 4. Rebuilding LaTeX and Compilation of PDF

```bash
# Generate LaTeX sections and figures
python scripts/build_latex_sections.py
python scripts/build_journal_meta.py

# Compile master LaTeX document (in JOURNAL/ directory)
cd JOURNAL
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```
