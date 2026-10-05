"use client";

import { bipartitePolynomial } from "@/lib/researchGraph";
import { useMemo, useState } from "react";

const CASES = [
  { name: "K2,2", s: 2, t: 2 },
  { name: "K3,1", s: 3, t: 1 },
  { name: "K3,2", s: 3, t: 2 },
  { name: "K4,1", s: 4, t: 1 },
];

export function OptimiserView() {
  const [name, setName] = useState(CASES[0].name);
  const selected = CASES.find((item) => item.name === name) ?? CASES[0];
  const samples = useMemo(() => {
    const points = [];
    for (let i = 0; i <= 80; i += 1) {
      const alpha = 0.5 + (0.5 * i) / 80;
      points.push({ alpha, value: bipartitePolynomial(selected.s, selected.t, alpha) });
    }
    return points;
  }, [selected]);
  const best = samples.reduce((champion, point) => (point.value > champion.value ? point : champion));
  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,1.2fr)_20rem]">
      <div>
        <p className="mb-4 max-w-2xl text-sm leading-6 text-ink/80">
          The curve is the Theorem 1.6 formula for a complete bipartite host, computed at 81 ratios in [1/2, 1].
          The marked point is the maximum on that grid, not a certified unique maximiser.
        </p>
        <Landscape samples={samples} bestAlpha={best.alpha} />
      </div>
      <div className="space-y-4">
        <label className="block text-sm">
          Target
          <select className="mt-1 w-full border border-rule bg-paper px-2 py-1" value={name} onChange={(event) => setName(event.target.value)}>
            {CASES.map((item) => (
              <option key={item.name}>{item.name}</option>
            ))}
          </select>
        </label>
        <dl className="space-y-2 text-sm">
          <div className="border border-rule px-3 py-2">
            <dt className="text-xs uppercase tracking-wide text-ink/60">Best grid ratio</dt>
            <dd className="font-serif text-2xl">{best.alpha.toFixed(4)} / {(1 - best.alpha).toFixed(4)}</dd>
          </div>
          <div className="border border-rule px-3 py-2">
            <dt className="text-xs uppercase tracking-wide text-ink/60">Objective on the grid</dt>
            <dd className="font-serif text-2xl">{best.value.toFixed(6)}</dd>
          </div>
          <div className="border border-rule px-3 py-2">
            <dt className="text-xs uppercase tracking-wide text-ink/60">Parts</dt>
            <dd className="font-serif text-2xl">2</dd>
          </div>
        </dl>
      </div>
    </div>
  );
}

function Landscape({ samples, bestAlpha }: { samples: { alpha: number; value: number }[]; bestAlpha: number }) {
  const width = 640;
  const height = 280;
  const max = Math.max(...samples.map((point) => point.value));
  const path = samples
    .map((point, index) => {
      const x = 32 + ((point.alpha - 0.5) / 0.5) * (width - 48);
      const y = height - 28 - (point.value / max) * (height - 56);
      return `${index === 0 ? "M" : "L"}${x.toFixed(1)} ${y.toFixed(1)}`;
    })
    .join(" ");
  const markerX = 32 + ((bestAlpha - 0.5) / 0.5) * (width - 48);
  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full border border-rule bg-paper" role="img" aria-label="Bipartite inducibility landscape">
      <path d={path} fill="none" stroke="#1c1915" strokeWidth="1.6" />
      <line x1={markerX} y1={16} x2={markerX} y2={height - 28} stroke="#9a3412" strokeDasharray="3 3" />
      <text x={32} y={height - 8} fontSize="12" fill="#1c1915">
        1/2
      </text>
      <text x={width - 28} y={height - 8} fontSize="12" fill="#1c1915">
        1
      </text>
    </svg>
  );
}
