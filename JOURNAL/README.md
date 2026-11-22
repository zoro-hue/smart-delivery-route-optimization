# ROUTE/IQ-NextGen Journal Paper Repository

This directory contains the complete IEEE Transactions LaTeX manuscript, figures, tables, and bibliography for:

**ROUTE/IQ-NextGen: An Adaptive, Vehicle-Condition-Aware Cooperative Optimization Engine for Heterogeneous Urban Logistics**

### Authorship and Affiliations
- **Authors:** J. Jayanth, B. Kaivalya, P. Shyam Sai (Undergraduate Research Scholars)
- **Faculty Supervisor:** Dr. Vishnu Prasad Verma
- **Affiliation:** Department of Computer Science and Engineering, SRM University-AP, Amaravati, Andhra Pradesh, India

---

### Structure
- `main.tex`: Master LaTeX document assembling all modular sections.
- `references.bib`: Verified BibTeX entries for all 27 foundational research papers.
- `sections/`: 15 modular LaTeX content sections (01_abstract.tex through 15_conclusion.tex).
- `tables/`: Publication-quality LaTeX tables (Chronology, 27-Paper Review, Benchmark Results, Ablation Study).
- `figures/`: High-resolution (300 DPI) publication diagrams and charts.
- `JOURNAL_PAPER.pdf`: Pre-compiled IEEE Transactions two-column PDF.

---

### Compilation Instructions
To compile the document using standard TeX distributions (TeXLive, MikTeX, or Overleaf):
```bash
pdflatex main
bibtex main
pdflatex main
pdflatex main
```
