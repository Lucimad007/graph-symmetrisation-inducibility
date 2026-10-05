"use client";

import { GraphScene } from "@/components/GraphScene";
import { Button } from "@/components/ui/button";
import {
  cloneNeighborhood,
  defect,
  edgeCount,
  exactDensity,
  MOTIFS,
  nextPair,
  randomGraph,
  type ResearchGraph,
} from "@/lib/researchGraph";
import { useEffect, useMemo, useState } from "react";

const N = 8;

export function Explorer() {
  const [seed, setSeed] = useState(1);
  const [graph, setGraph] = useState<ResearchGraph>(() => randomGraph(N, 0.35, 1));
  const [iteration, setIteration] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [history, setHistory] = useState<number[]>([0]);
  const [motifName, setMotifName] = useState(MOTIFS[0].name);
  const motif = MOTIFS.find((item) => item.name === motifName) ?? MOTIFS[0];
  const pair = useMemo(() => nextPair(graph), [graph]);
  const density = useMemo(() => exactDensity(graph, motif), [graph, motif]);
  const distance = useMemo(() => defect(graph), [graph]);

  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(() => {
      setGraph((current) => {
        const chosen = nextPair(current);
        if (!chosen) {
          setPlaying(false);
          return current;
        }
        const next = structuredClone(current);
        cloneNeighborhood(next, chosen[0], chosen[1]);
        return next;
      });
      setIteration((value) => value + 1);
    }, 700);
    return () => window.clearInterval(timer);
  }, [playing]);

  useEffect(() => {
    setHistory((values) => [...values, density]);
  }, [density]);

  function step(times: number) {
    setGraph((current) => {
      const next = structuredClone(current);
      let done = 0;
      while (done < times) {
        const chosen = nextPair(next);
        if (!chosen) break;
        cloneNeighborhood(next, chosen[0], chosen[1]);
        done += 1;
      }
      setIteration((value) => value + done);
      return next;
    });
  }

  function reset(nextSeed: number) {
    setPlaying(false);
    setSeed(nextSeed);
    setIteration(0);
    const fresh = randomGraph(N, 0.35, nextSeed);
    setGraph(fresh);
    setHistory([exactDensity(fresh, motif)]);
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1.4fr)_minmax(18rem,0.8fr)]">
      <div className="h-[28rem] border border-rule bg-paper">
        <GraphScene graph={graph} selected={pair} />
      </div>
      <div className="space-y-4">
        <p className="text-sm leading-6 text-ink/80">
          Each step replaces the lower-degree endpoint of a non-edge by a clone of the higher-degree endpoint.
          Colour groups vertices that the non-edge relation has already joined; on a complete multipartite graph those
          colours are the parts. The highlighted pair is the next clone. Densities are exact counts on this {N}-vertex graph.
        </p>
        <div className="flex flex-wrap gap-2">
          <Button onClick={() => step(1)}>One step</Button>
          <Button variant="outline" onClick={() => step(5)}>
            Five steps
          </Button>
          <Button variant="outline" onClick={() => setPlaying((value) => !value)}>
            {playing ? "Pause" : "Play"}
          </Button>
          <Button variant="outline" onClick={() => reset(seed + 1)}>
            New graph
          </Button>
        </div>
        <label className="block text-sm">
          Motif
          <select
            className="mt-1 w-full border border-rule bg-paper px-2 py-1"
            value={motifName}
            onChange={(event) => {
              setMotifName(event.target.value);
              setHistory([]);
            }}
          >
            {MOTIFS.map((item) => (
              <option key={item.name}>{item.name}</option>
            ))}
          </select>
        </label>
        <dl className="grid grid-cols-2 gap-3 text-sm">
          <Stat label="Iteration" value={String(iteration)} />
          <Stat label="Edges" value={String(edgeCount(graph))} />
          <Stat label="Induced density" value={density.toFixed(4)} />
          <Stat label="Multipartite distance" value={distance.toFixed(4)} />
        </dl>
        <p className="text-xs leading-5 text-ink/70">
          Pair {pair ? `${pair[0]} ← clone of ${pair[1]}` : "none: every non-adjacent pair is already a twin"}. Seed {seed}.
        </p>
        <DensityTrace values={history.slice(-24)} />
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="border border-rule px-3 py-2">
      <dt className="text-xs uppercase tracking-wide text-ink/60">{label}</dt>
      <dd className="font-serif text-2xl">{value}</dd>
    </div>
  );
}

function DensityTrace({ values }: { values: number[] }) {
  const width = 280;
  const height = 72;
  if (values.length < 2) return <p className="text-xs text-ink/60">Objective history appears after the next measurement.</p>;
  const max = Math.max(...values, 0.01);
  const path = values
    .map((value, index) => {
      const x = (index / (values.length - 1)) * width;
      const y = height - (value / max) * (height - 4) - 2;
      return `${index === 0 ? "M" : "L"}${x.toFixed(1)} ${y.toFixed(1)}`;
    })
    .join(" ");
  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full border border-rule" role="img" aria-label="Induced density history">
      <path d={path} fill="none" stroke="#9a3412" strokeWidth="1.5" />
    </svg>
  );
}
