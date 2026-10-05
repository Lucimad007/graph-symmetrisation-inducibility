"use client";

import { GraphScene } from "@/components/GraphScene";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
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
import { Pause, Play, RotateCcw, StepForward } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

const N = 8;

export function Explorer() {
  const [seed, setSeed] = useState(1);
  const [graph, setGraph] = useState<ResearchGraph>(() => randomGraph(N, 0.35, 1));
  const [iteration, setIteration] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [motifName, setMotifName] = useState(MOTIFS[0].name);
  const motif = MOTIFS.find((item) => item.name === motifName) ?? MOTIFS[0];
  const pair = useMemo(() => nextPair(graph), [graph]);
  const density = useMemo(() => exactDensity(graph, motif), [graph, motif]);
  const distance = useMemo(() => defect(graph), [graph]);
  const [history, setHistory] = useState<number[]>(() => [exactDensity(randomGraph(N, 0.35, 1), MOTIFS[0])]);
  const [lastEdgeDelta, setLastEdgeDelta] = useState(0);
  const densities = useMemo(() => MOTIFS.map((item) => ({ name: item.name, value: exactDensity(graph, item) })), [graph]);

  function applySteps(times: number) {
    const next = structuredClone(graph);
    const edgesBefore = edgeCount(graph);
    let done = 0;
    while (done < times) {
      const chosen = nextPair(next);
      if (!chosen) break;
      cloneNeighborhood(next, chosen[0], chosen[1]);
      done += 1;
    }
    if (done === 0) {
      setPlaying(false);
      return;
    }
    setGraph(next);
    setIteration((value) => value + done);
    setLastEdgeDelta(edgeCount(next) - edgesBefore);
    setHistory((values) => [...values, exactDensity(next, motif)].slice(-40));
  }

  useEffect(() => {
    if (!playing) return;
    const timer = window.setTimeout(() => applySteps(1), 700);
    return () => window.clearTimeout(timer);
  }, [playing, graph, motif]);

  function reset(nextSeed: number) {
    setPlaying(false);
    setSeed(nextSeed);
    setIteration(0);
    const fresh = randomGraph(N, 0.35, nextSeed);
    setGraph(fresh);
    setLastEdgeDelta(0);
    setHistory([exactDensity(fresh, motif)]);
  }

  function changeMotif(name: string) {
    const nextMotif = MOTIFS.find((item) => item.name === name) ?? MOTIFS[0];
    setMotifName(name);
    setHistory([exactDensity(graph, nextMotif)]);
  }

  return (
    <div className="grid items-start gap-4 xl:grid-cols-[minmax(0,1.3fr)_22rem]">
      <Card className="overflow-hidden">
        <CardHeader className="pb-3">
          <CardTitle>Current graph</CardTitle>
          <CardDescription>
            Colour is the non-edge component. On a complete multipartite graph those colours are the parts. The larger
            vertices are the next clone pair.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[26rem] overflow-hidden rounded-md border bg-background">
            <GraphScene graph={graph} selected={pair} />
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle>Symmetrisation</CardTitle>
            <CardDescription>
              Clone the lower-degree end of a non-edge onto the higher-degree end. Densities are exact on {N} vertices.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3">
            <div className="flex flex-wrap gap-2">
              <Button onClick={() => applySteps(1)} disabled={!pair}>
                <StepForward className="h-4 w-4" />
                One step
              </Button>
              <Button variant="outline" onClick={() => setPlaying((value) => !value)} disabled={!pair && !playing}>
                {playing ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                {playing ? "Pause" : "Play"}
              </Button>
              <Button variant="outline" onClick={() => reset(seed + 1)}>
                <RotateCcw className="h-4 w-4" />
                New graph
              </Button>
            </div>
            <Select value={motifName} onValueChange={changeMotif}>
              <SelectTrigger aria-label="Motif">
                <SelectValue placeholder="Motif" />
              </SelectTrigger>
              <SelectContent>
                {MOTIFS.map((item) => (
                  <SelectItem key={item.name} value={item.name}>
                    {item.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
              <Badge variant={pair ? "default" : "secondary"}>{pair ? `Clone ${pair[0]} from ${pair[1]}` : "Fully symmetrised"}</Badge>
              <span>Seed {seed}</span>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-2 gap-3">
          <Stat label="Iteration" value={String(iteration)} />
          <Stat label="Edges" value={String(edgeCount(graph))} />
          <Stat label="Induced density" value={density.toFixed(4)} />
          <Stat label="Multipartite distance" value={distance.toFixed(4)} />
          <Stat label="Last edge change" value={lastEdgeDelta > 0 ? `+${lastEdgeDelta}` : String(lastEdgeDelta)} />
        </div>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">All motifs</CardTitle>
            <CardDescription>Exact induced density of each complete partite motif on this graph.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-2">
            {densities.map((item) => (
              <div key={item.name} className="flex items-center justify-between text-sm">
                <span className={item.name === motifName ? "font-medium" : "text-muted-foreground"}>{item.name}</span>
                <span className="tabular-nums">{item.value.toFixed(4)}</span>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Induced density</CardTitle>
            <CardDescription>One point per successful clone step for the selected motif.</CardDescription>
          </CardHeader>
          <CardContent>
            <DensityTrace values={history} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <Card>
      <CardHeader className="p-4 pb-1">
        <CardDescription>{label}</CardDescription>
      </CardHeader>
      <CardContent className="p-4 pt-0">
        <p className="font-serif text-2xl tabular-nums">{value}</p>
      </CardContent>
    </Card>
  );
}

function DensityTrace({ values }: { values: number[] }) {
  const width = 320;
  const height = 140;
  const pad = 16;
  if (values.length < 2) {
    return <p className="text-sm text-muted-foreground">Take a step to draw the history.</p>;
  }
  const max = Math.max(...values, 0.01);
  const min = Math.min(...values, 0);
  const span = Math.max(max - min, 0.01);
  const path = values
    .map((value, index) => {
      const x = pad + (index / (values.length - 1)) * (width - pad * 2);
      const y = height - pad - ((value - min) / span) * (height - pad * 2);
      return `${index === 0 ? "M" : "L"}${x.toFixed(1)} ${y.toFixed(1)}`;
    })
    .join(" ");
  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="h-36 w-full" role="img" aria-label="Induced density history">
      <path d={path} fill="none" stroke="hsl(17 76% 34%)" strokeWidth="2" strokeLinejoin="round" />
    </svg>
  );
}
