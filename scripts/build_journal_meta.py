import os
import shutil
import subprocess

def write_main_tex():
    main_tex = r'''\documentclass[journal,10pt]{IEEEtran}

\usepackage{amsmath,amssymb,amsfonts,amsthm}
\usepackage{algorithmic}
\usepackage{algorithm}
\usepackage{graphicx}
\usepackage{textcomp}
\usepackage{xcolor}
\usepackage{booktabs}
\usepackage{cite}
\usepackage{url}
\usepackage{hyperref}
\usepackage{multirow}
\usepackage{array}

\newtheorem{proposition}{Proposition}
\newtheorem{theorem}{Theorem}
\newtheorem{definition}{Definition}
\newtheorem{lemma}{Lemma}
\newtheorem{corollary}{Corollary}

\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,      
    urlcolor=cyan,
    citecolor=blue,
}

\begin{document}

\title{ROUTE/IQ-NextGen: An Adaptive, Vehicle-Condition-Aware Cooperative Optimization Engine for Heterogeneous Urban Logistics}

\author{J.~Jayanth, 
        B.~Kaivalya, 
        and~P.~Shyam~Sai%
\thanks{Manuscript updated November 21, 2026. This research was conducted under the academic supervision of Dr.~Vishnu~Prasad~Verma in the Department of Computer Science and Engineering, SRM University-AP, Amaravati, Andhra Pradesh 522240, India.}%
\thanks{J. Jayanth, B. Kaivalya, and P. Shyam Sai are undergraduate research scholars in the Department of Computer Science and Engineering, SRM University-AP, Amaravati, Andhra Pradesh 522240, India.}%
\thanks{Faculty Supervisor: Dr.~Vishnu~Prasad~Verma, Department of Computer Science and Engineering, SRM University-AP, Amaravati, Andhra Pradesh 522240, India.}%
\thanks{Open-source code, reproducibility scripts, raw benchmark records, and audit artifacts are available at: \url{https://github.com/zoro-hue/smart-delivery-route-optimization}.}}

\markboth{IEEE Transactions on Intelligent Transportation Systems,~Vol.~X, No.~X,~November~2026}%
{Jayanth \MakeLowercase{\textit{et al.}}: ROUTE/IQ-NextGen: Adaptive Vehicle-Condition-Aware Cooperative Optimization}

\maketitle

\input{sections/01_abstract.tex}
\input{sections/02_introduction.tex}
\input{tables/table1_chronology.tex}
\input{sections/03_related_work.tex}
\input{tables/table2_literature_review_27_papers.tex}
\input{sections/04_problem_formulation.tex}
\input{sections/05_system_architecture.tex}
\input{sections/06_big_data_processing.tex}
\input{sections/07_quantum_classical_methods.tex}
\input{sections/08_cooperative_engine.tex}
\input{sections/09_vehicle_aware_optimization.tex}
\input{sections/10_mathematical_formulation.tex}
\input{sections/11_experimental_methodology.tex}
\input{tables/table3_benchmark_results.tex}
\input{sections/12_results_and_discussion.tex}
\input{tables/table4_ablation_study.tex}
\input{sections/13_novelty_and_contributions.tex}
\input{sections/14_limitations.tex}
\input{sections/15_conclusion.tex}

\section*{Acknowledgment}
The authors express their deepest gratitude to their faculty research supervisor, Dr.~Vishnu~Prasad~Verma, Department of Computer Science and Engineering, SRM University-AP, for his invaluable guidance, technical reviews, and sustained mentorship throughout the inception and development of the ROUTE/IQ project.

\bibliographystyle{IEEEtran}
\bibliography{references}

\end{document}
'''
    with open('JOURNAL/main.tex', 'w', encoding='utf-8') as f:
        f.write(main_tex)
    print("JOURNAL/main.tex created successfully!")

def write_readme():
    readme = r'''# ROUTE/IQ-NextGen Journal Paper Repository

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
'''
    with open('JOURNAL/README.md', 'w', encoding='utf-8') as f:
        f.write(readme)
    print("JOURNAL/README.md created successfully!")

if __name__ == '__main__':
    write_main_tex()
    write_readme()
