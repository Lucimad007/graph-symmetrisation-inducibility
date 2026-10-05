# Graph Symmetrisation & Inducibility

Computational exploration of graph symmetrisation, inducibility, and extremal graph structures inspired by recent research in extremal combinatorics.

This repository is a computational research companion to the paper. It does not constitute a formal verification or implementation of all theoretical proofs.

## Overview

The companion follows Liu, Pikhurko, Sharifzadeh, and Staden, *Stability from graph symmetrisation arguments with applications to inducibility* ([arXiv:2012.10731](https://arxiv.org/abs/2012.10731)). It computes induced densities, runs Zykov clone steps, and numerically maximises those densities over part ratios in the partite limit space. The mapping from paper statements to code, and the list of results that are not implemented, is in [`docs/paper-analysis.md`](docs/paper-analysis.md).

## Research Question

For a complete partite motif \(F\), which part-ratio vectors make the induced density of \(F\) large, and what happens to that density and to the distance from a complete multipartite graph when a finite graph is symmetrised one clone at a time?

## Mathematical Background

A \(k\)-vertex motif contributes to \(\lambda(G)\) through the fraction of \(k\)-subsets that induce it (Section 1.2). Zykov symmetrisation replaces a vertex \(x\) by a clone of a non-adjacent vertex \(y\) (introduction). Complete partite graphs are encoded by non-increasing masses \(x_1 \ge x_2 \ge \cdots\) with residual singleton mass \(x_0 = 1 - \sum x_i\) (Definition 1.3 and Section 2). Perfect stability (Definition 1.2) is a theorem under the hypotheses of Theorem 1.4. The experiments measure a candidate edit fraction; they do not prove that inequality.

The limit density of a complete partite motif in a complete partite host is the multinomial probability that \(k\) i.i.d. samples induce that part type. On the two constructions in Theorems 1.8 and 1.9 this polynomial evaluates to \(525/1024\) and \(216/625\).

## Computational Components

| Piece | Role |
| --- | --- |
| `python/graph` | Adjacency-set graphs, cloning, complete multipartite realisations, candidate edit fraction |
| `python/inducibility` | Motifs, exact \(k\)-subset counts, Monte Carlo estimates (labelled as such), limit polynomial |
| `python/optimisation` | Budgeted grid and SLSQP on the ordered simplex |
| `python/experiments` | Section 6 comparison, clone trajectories, and edits of an extremal host |
| `apps/web` | Explorer, bipartite landscape, display of the Section 6 JSON |

The candidate distance is the fraction of pairs that violate the complete multipartite graph whose parts are the connected components of the non-edge graph. It is zero exactly on complete multipartite graphs. It is not the minimum of \(\hat\Delta_1\) over every complete partite graph.

## Architecture

```
python/graph            explicit graphs and symmetrisation
python/inducibility     motif densities
python/optimisation     part-ratio search
python/experiments      reproducible scripts
python/tests            unit tests
experiments/results     JSON
experiments/figures     PNG
apps/web                Next.js explorer
docs/paper-analysis.md  what is and is not implemented
```

## Experiments

From the repository root, with `PYTHONPATH=python`:

```bash
python -m experiments.run_all
```

Individual scripts: `python -m experiments.section6`, `python -m experiments.symmetrisation_run`, `python -m experiments.stability_scan`.

Seeds, \(n\), and the selection rule are stored in the JSON. Symmetrisation figures use the first seed. Induced densities in these scripts are exact enumerations. The Section 6 objective is the limit polynomial in float64.

## Reproduced Results

A fresh run of `experiments.section6` (seed 0, at most 8 parts, SLSQP from a budgeted grid and random starts) produced:

| Statement | Computed | Stated in the paper | Absolute error | Ratios found |
| --- | --- | --- | --- | --- |
| Theorem 1.8, \(K_{2,1,1,1}\) | 0.5126953125 | \(525/1024\) | 0 | eight parts of \(1/8\) |
| Theorem 1.9, \(K_{3,1,1}\) | 0.34559999999995517 | \(216/625\) | \(4.5 \times 10^{-14}\) | one part of mass \(0.6\), singleton mass \(0.4\) |

The paper values are used only to compute the error column. The optimiser does not return them in place of an evaluation. Agreement on these two points is not a proof of uniqueness or of perfect stability.

## Interactive Visualisation

The web app has three views.

* **Symmetrisation.** An 8-vertex graph, one clone step or a run of steps, exact induced density, edge count, candidate distance, and a short history.
* **Optimiser.** The Theorem 1.6 bipartite polynomial on a grid in \([1/2, 1]\).
* **Paper results.** The JSON written by the Section 6 script, with links to the arXiv version.

## Reproducibility

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m experiments.run_all
```

On Windows, set `PYTHONPATH=python` if the package is not installed. The web app reads `experiments/results/section6.json`, so run the Section 6 script before building the results page.

```bash
cd apps/web
npm install
npm run dev
```

## Limitations

* Definition 1.1 is not proved for a general objective. The flagship loop uses the degree rule, which is monotone for the number of edges, and it records whether each motif density rose or fell.
* The edit fraction is a candidate, not \(\min_H \hat\Delta_1(G, H)\).
* The grid in more than three coordinates is replaced by balanced vectors plus SLSQP. A maximiser with many unequal parts can be missed.
* SLSQP reports local success. Coordinates smaller than \(10^{-5}\) are dropped as solver dust before the vector is written down.
* Monte Carlo densities are estimates. Exact inducibility numbers in the JSON are either full enumerations or evaluations of the limit polynomial.
* The Buchberger and sum-of-squares arguments in Section 6 are not rerun.
* The PDF is not vendored. The arXiv record does not clearly permit redistributing it.

## Relation to the Paper

Read [`docs/paper-analysis.md`](docs/paper-analysis.md) before treating any number in this repository as a theorem. Theorems 1.4, 1.6, 1.7, 1.8, and 1.9 remain results of the paper. This code checks specialisations that can be evaluated directly: the limit polynomial on the stated constructions, numerical search nearby, and finite clone trajectories.

## Citation

Liu, Pikhurko, Sharifzadeh, and Staden, *Stability from graph symmetrisation arguments with applications to inducibility*, arXiv:2012.10731v3, 2023.

```bibtex
@article{liu2023symmetrisation,
  title={Stability from graph symmetrisation arguments with applications to inducibility},
  author={Liu, Hong and Pikhurko, Oleg and Sharifzadeh, Maryam and Staden, Katherine},
  journal={arXiv preprint arXiv:2012.10731},
  year={2023}
}
```
