/** Small-graph Zykov step used by the explorer. The research counts live in Python. */

export type ResearchGraph = { n: number; adj: number[][] };

export type Motif = { name: string; parts: number[] };

export const MOTIFS: Motif[] = [
  { name: "K2,2", parts: [2, 2] },
  { name: "K3,2", parts: [3, 2] },
  { name: "K3,1,1", parts: [3, 1, 1] },
  { name: "K2,1,1,1", parts: [2, 1, 1, 1] },
];

export function emptyGraph(n: number): ResearchGraph {
  return { n, adj: Array.from({ length: n }, () => []) };
}

export function randomGraph(n: number, probability: number, seed: number): ResearchGraph {
  const graph = emptyGraph(n);
  let state = seed >>> 0;
  const random = () => {
    state = (1664525 * state + 1013904223) >>> 0;
    return state / 4294967296;
  };
  for (let u = 0; u < n; u += 1) {
    for (let v = u + 1; v < n; v += 1) {
      if (random() < probability) addEdge(graph, u, v);
    }
  }
  return graph;
}

export function addEdge(graph: ResearchGraph, u: number, v: number) {
  if (!graph.adj[u].includes(v)) graph.adj[u].push(v);
  if (!graph.adj[v].includes(u)) graph.adj[v].push(u);
}

export function degree(graph: ResearchGraph, v: number) {
  return graph.adj[v].length;
}

export function edgeCount(graph: ResearchGraph) {
  return graph.adj.reduce((sum, neigh) => sum + neigh.length, 0) / 2;
}

export function cloneNeighborhood(graph: ResearchGraph, source: number, target: number) {
  const next = new Set(graph.adj[target].filter((v) => v !== source));
  for (const u of graph.adj[source]) {
    graph.adj[u] = graph.adj[u].filter((v) => v !== source);
  }
  graph.adj[source] = [...next];
  for (const u of graph.adj[source]) {
    if (!graph.adj[u].includes(source)) graph.adj[u].push(source);
  }
}

export function nextPair(graph: ResearchGraph): [number, number] | null {
  let best: [number, number, number] | null = null;
  for (let u = 0; u < graph.n; u += 1) {
    for (let v = u + 1; v < graph.n; v += 1) {
      if (graph.adj[u].includes(v)) continue;
      const source = degree(graph, u) <= degree(graph, v) ? u : v;
      const target = source === u ? v : u;
      const same =
        graph.adj[source].length === graph.adj[target].length &&
        graph.adj[source].every((w) => graph.adj[target].includes(w));
      if (same) continue;
      const gap = degree(graph, target) - degree(graph, source);
      if (!best || gap > best[0]) best = [gap, source, target];
    }
  }
  return best ? [best[1], best[2]] : null;
}

export function partLabels(graph: ResearchGraph): number[] {
  const parent = Array.from({ length: graph.n }, (_, i) => i);
  const find = (v: number): number => {
    let x = v;
    while (parent[x] !== x) {
      parent[x] = parent[parent[x]];
      x = parent[x];
    }
    return x;
  };
  const union = (a: number, b: number) => {
    const ra = find(a);
    const rb = find(b);
    if (ra !== rb) parent[rb] = ra;
  };
  for (let u = 0; u < graph.n; u += 1) {
    for (let v = u + 1; v < graph.n; v += 1) {
      if (!graph.adj[u].includes(v)) union(u, v);
    }
  }
  const roots = graph.adj.map((_, index) => find(index));
  const names = new Map<number, number>();
  return roots.map((root) => {
    if (!names.has(root)) names.set(root, names.size);
    return names.get(root) ?? 0;
  });
}

const PART_COLORS = ["#1c1915", "#9a3412", "#1d4e89", "#3f6212", "#7c3aed", "#b45309", "#0f766e", "#9f1239"];

export function partColor(label: number): string {
  return PART_COLORS[label % PART_COLORS.length];
}

export function defect(graph: ResearchGraph): number {
  if (graph.n < 2) return 0;
  const parent = Array.from({ length: graph.n }, (_, i) => i);
  const find = (v: number): number => {
    let x = v;
    while (parent[x] !== x) {
      parent[x] = parent[parent[x]];
      x = parent[x];
    }
    return x;
  };
  const union = (a: number, b: number) => {
    const ra = find(a);
    const rb = find(b);
    if (ra !== rb) parent[rb] = ra;
  };
  for (let u = 0; u < graph.n; u += 1) {
    for (let v = u + 1; v < graph.n; v += 1) {
      if (!graph.adj[u].includes(v)) union(u, v);
    }
  }
  let edits = 0;
  let pairs = 0;
  for (let u = 0; u < graph.n; u += 1) {
    for (let v = u + 1; v < graph.n; v += 1) {
      pairs += 1;
      const same = find(u) === find(v);
      const linked = graph.adj[u].includes(v);
      if (same === linked) edits += 1;
    }
  }
  return edits / pairs;
}

function combinations(n: number, k: number): number[][] {
  const out: number[][] = [];
  const current: number[] = [];
  const walk = (start: number) => {
    if (current.length === k) {
      out.push([...current]);
      return;
    }
    for (let i = start; i < n; i += 1) {
      current.push(i);
      walk(i + 1);
      current.pop();
    }
  };
  walk(0);
  return out;
}

function inducedParts(graph: ResearchGraph, vertices: number[]): number[] | null {
  const index = new Map(vertices.map((v, i) => [v, i]));
  const parent = vertices.map((_, i) => i);
  const find = (i: number): number => {
    let x = i;
    while (parent[x] !== x) {
      parent[x] = parent[parent[x]];
      x = parent[x];
    }
    return x;
  };
  const union = (a: number, b: number) => {
    const ra = find(a);
    const rb = find(b);
    if (ra !== rb) parent[rb] = ra;
  };
  for (let a = 0; a < vertices.length; a += 1) {
    for (let b = a + 1; b < vertices.length; b += 1) {
      if (!graph.adj[vertices[a]].includes(vertices[b])) union(a, b);
    }
  }
  for (let a = 0; a < vertices.length; a += 1) {
    for (let b = a + 1; b < vertices.length; b += 1) {
      const same = find(a) === find(b);
      const linked = graph.adj[vertices[a]].includes(vertices[b]);
      if (same === linked) return null;
    }
  }
  const sizes = new Map<number, number>();
  vertices.forEach((_, i) => {
    const root = find(i);
    sizes.set(root, (sizes.get(root) ?? 0) + 1);
  });
  void index;
  return [...sizes.values()].sort((a, b) => b - a);
}

function sameParts(found: number[] | null, target: number[]) {
  if (!found || found.length !== target.length) return false;
  return found.every((value, i) => value === target[i]);
}

export function exactDensity(graph: ResearchGraph, motif: Motif): number {
  const k = motif.parts.reduce((sum, part) => sum + part, 0);
  const subsets = combinations(graph.n, k);
  if (subsets.length === 0) return 0;
  let hits = 0;
  for (const subset of subsets) {
    if (sameParts(inducedParts(graph, subset), motif.parts)) hits += 1;
  }
  return hits / subsets.length;
}

/** Theorem 1.6 polynomial, evaluated in the browser for the landscape view. */
export function bipartitePolynomial(s: number, t: number, alpha: number): number {
  const one = 1 - alpha;
  const f = alpha ** s * one ** t + alpha ** t * one ** s;
  const binomial = (n: number, k: number) => {
    let value = 1;
    for (let i = 1; i <= k; i += 1) value = (value * (n - k + i)) / i;
    return value;
  };
  return binomial(s + t, s) * (s === t ? 0.5 : 1) * f;
}
