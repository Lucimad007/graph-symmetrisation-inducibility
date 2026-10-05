# Paper analysis

Source: Hong Liu, Oleg Pikhurko, Maryam Sharifzadeh, Katherine Staden, *Stability from graph symmetrisation arguments with applications to inducibility*, arXiv:2012.10731v3 (4 October 2023).

This note separates what the paper proves from what this repository computes. Nothing here is a formal verification of those proofs.

## What the paper proves

The paper gives a sufficient condition for **perfect stability** of graph parameters that can be maximised by Zykov symmetrisation.

A parameter is built from a function \(\gamma\) on \(k\)-vertex graphs by averaging:

\[
\lambda(G) = \binom{n}{k}^{-1} \sum_{X \in \binom{V}{k}} \gamma(G[X]).
\]

**Symmetrisability** (Definition 1.1) asks that, for large \(n\), one can reach a complete partite graph by edits that do not decrease \(\lambda\), with each step changing only a small fraction of the pairs, and that a vertex added to an already complete partite graph can be moved until it is complete or empty to each part.

**Perfect stability** (Definition 1.2) asks for a constant \(C\) such that every large graph \(G\) is within edit distance

\[
\hat\delta_1(G, H) \le C\bigl(\lambda(n) - \lambda(G)\bigr)
\]

of some complete partite \(H\).

**Theorem 1.4** (finite form) and **Theorem 3.5** (limit form) say that a symmetrisable \(\lambda\) with finitely many maximisers in the partite limit space \(\mathcal{P}\) is perfectly stable if those maximisers are strict: toggling one edge in the realisation drops \(\lambda\) by \(\Omega(n^{-2})\), and a new vertex that is complete or empty to each part is close to a clone whenever its marginal \(\lambda(G_v, v)\) is close to \(\lambda(G)\).

**Lemma 1.5** (Schelp–Thomason) says that \(\lambda(G) = \sum_F c_F\, p(F, G)\) is symmetrisable when every \(F\) is complete partite and \(c_F \ge 0\) whenever \(F\) is not a clique. Inducibility of one complete partite graph is the case of a single coefficient \(1\).

Section 6 then identifies the maximisers for several inducibility problems and checks strictness:

| Result | Statement used by the experiments |
| --- | --- |
| Theorem 1.6 | For \(st \ge 2\), \(p(K_{s,t},\cdot)\) is perfectly stable. The unique maximiser is bipartite, with part ratio \(\alpha \in [1/2, 1]\) maximising \(f_{s,t}(\alpha) = \alpha^s(1-\alpha)^t + \alpha^t(1-\alpha)^s\). |
| Theorem 1.7 | For \(t > 1 + \log r\), the unique maximiser of \(p(K_r(t), \cdot)\) is \(r\) equal parts. |
| Theorem 1.8 | \(i(K_{2,1,1,1}) = 525/1024\), unique maximiser \((1/8,\ldots,1/8)\) (eight parts). |
| Theorem 1.9 | \(i(K_{3,1,1}) = 216/625\), unique maximiser \((3/5, 0, \ldots)\), i.e. one part of mass \(3/5\) and singleton mass \(2/5\). |

The proofs of Theorems 1.8 and 1.9 reduce the maximiser search to polynomial identities (a Buchberger elimination in the balanced case, a sum-of-squares certificate for Claim 6.1). Those certificates are not recomputed here.

## What is implemented

| Component | Paper anchor | What the code does |
| --- | --- | --- |
| Explicit graphs and cloning | §1, Zykov’s move: replace \(x\) by a clone of a non-adjacent \(y\) | Adjacency-set graphs, neighbourhood replacement, edge and degree queries |
| Symmetrisation loop | Definition 1.1, the edge-form used for Turán’s theorem in the introduction | Repeated cloning, with the objective recorded before and after each step. Monotonicity is measured, not assumed |
| Induced density \(p(F, G)\) | §1.2 | Exact enumeration of \(k\)-subsets on small graphs; Monte Carlo sampling labelled as approximate |
| Limit density on \(\mathcal{P}\) | §2, \(\lambda(x) = \lim \lambda(G_{n,x})\) | Exact multinomial expansion for a complete partite target in a complete partite host |
| Realisation \(G_{n,x}\) | Definition 1.3 | Integer part sizes from a ratio vector, including a singleton pool when the masses sum to less than 1 |
| Distance to a complete partite graph | \(\hat\Delta_1\), Definition 1.2 | A documented candidate: parts = connected components of the non-edge graph; edits = pairs that violate the complete partite rule for those parts. This is not proved to be the minimum over all \(H\) |
| Numerical maximisation of \(\lambda(x)\) | The “polynomial optimisation” left open in §1.1, and the concrete maxima in §6 | Grid search and SLSQP on the simplex. The returned vector is whatever the solver finds |

## What is only experimental

- Whether a random graph’s induced density rises, falls, or stays flat under cloning. Definition 1.1 requires some sequence of symmetrisations that does not decrease \(\lambda\); an arbitrary choice of pair need not be monotone.
- Whether graphs with large induced density are close, in the candidate edit metric, to a complete partite graph. That is the shape of perfect stability, not a proof of it.
- Finite-\(n\) densities of \(G_{n,x}\) as a check that they approach the limit polynomial.

## What is not implemented and must not be described as implemented

- The proof of Theorem 3.5 (Sections 3–5): compactness of \((\mathcal{P}, \delta_{\mathrm{edit}})\), strictness in the limit, and the removal of exceptional vertices.
- Symmetrisability in the sense of Definition 1.1 for a general coefficient vector \((c_F)\). The code can evaluate objectives; it does not prove that a non-decreasing edit sequence exists.
- The Buchberger elimination and the sum-of-squares identity in the proofs of Theorems 1.8 and 1.9.
- Uniqueness of the maximiser. A numerical search can find the value on a grid or at a local optimum. It does not prove no other point of \(\mathcal{P}\) is higher.
- Flag algebras, graphons beyond the complete partite graphon used to evaluate \(\lambda(x)\), and inducibility of non-complete-partite graphs (the paper explicitly sets these aside).

## Licensing of the paper PDF

The arXiv abstract page and the PDF header identify the work as arXiv:2012.10731. They do not grant a licence to redistribute the PDF inside a third-party repository. This repository links to https://arxiv.org/abs/2012.10731 and does not vendor the PDF.
