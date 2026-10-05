# graph-symmetrisation-inducibility

Computational exploration of graph symmetrisation, inducibility, and extremal graph theory, following Liu, Pikhurko, Sharifzadeh, and Staden, *Stability from graph symmetrisation arguments with applications to inducibility* (arXiv:2012.10731).

The paper shows that a symmetrisable graph parameter is maximised by a complete partite graph, and that perfect stability follows once the finitely many maximisers in the partite limit space satisfy two strictness inequalities. For the inducibility of a complete partite graph those maximisers are points \(x = (x_1 \ge x_2 \ge \cdots)\) with \(\sum x_i \le 1\), and the induced density is a polynomial in the part masses.

## What is implemented

* The partite limit space and the finite realisation \(G_{n,x}\) (Definition 1.3).
* Exact and asymptotic induced densities of a complete partite graph in a complete partite host. The asymptotic density is the probability that \(k\) i.i.d. samples induce the target.
* The bipartite polynomial \(f_{s,t}\) of Theorem 1.6, and a grid search over part ratios.
* The change in the number of induced copies when a single pair of an extremal complete partite graph is edited (the finite form of condition (i) in Theorem 1.4).
* Zykov symmetrisation: repeatedly replace a vertex by a clone of a non-adjacent vertex of larger degree, which does not decrease the number of edges and ends at a complete partite graph.

## Known values recovered

| Target | Maximiser | Induced density |
| --- | --- | --- |
| \(K_{2,2}\) | \((1/2, 1/2)\) | \(3/8\) |
| \(K_{3,1,1}\) | \((3/5)\) with singleton mass \(2/5\) | \(216/625\) |
| \(K_{2,1,1,1}\) | eight parts of mass \(1/8\) | \(525/1024\) |

## Usage

```python
from syminduc import PartiteVector, limit_induced_density, maximise_bipartite

print(limit_induced_density((2, 1, 1, 1), PartiteVector.balanced(8)))
print(maximise_bipartite(4, 1))
```

```bash
pip install -e ".[dev]"
pytest
python -m syminduc.cli
```
