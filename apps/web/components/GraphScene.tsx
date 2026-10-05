"use client";

import { Line } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { degree, partColor, partLabels, type ResearchGraph } from "@/lib/researchGraph";

function positions(graph: ResearchGraph): [number, number, number][] {
  return Array.from({ length: graph.n }, (_, index) => {
    const angle = (2 * Math.PI * index) / graph.n;
    const radius = 1.6;
    return [radius * Math.cos(angle), 0.15 * degree(graph, index), radius * Math.sin(angle)] as [
      number,
      number,
      number,
    ];
  });
}

export function GraphScene({ graph, selected }: { graph: ResearchGraph; selected: [number, number] | null }) {
  const points = positions(graph);
  const labels = partLabels(graph);
  const edges: [number, number][] = [];
  for (let u = 0; u < graph.n; u += 1) {
    for (const v of graph.adj[u]) {
      if (u < v) edges.push([u, v]);
    }
  }
  return (
    <Canvas camera={{ position: [0, 2.4, 4.2], fov: 45 }} aria-label="Graph drawing">
      <color attach="background" args={["#f4f0e6"]} />
      <ambientLight intensity={0.7} />
      <directionalLight position={[3, 4, 2]} intensity={0.8} />
      {edges.map(([u, v]) => (
        <Line key={`${u}-${v}`} points={[points[u], points[v]]} color="#1c1915" lineWidth={1} />
      ))}
      {points.map((position, index) => {
        const chosen = selected?.includes(index) ?? false;
        return (
          <mesh key={index} position={position}>
            <sphereGeometry args={[chosen ? 0.12 : 0.08, 20, 20]} />
            <meshStandardMaterial color={chosen ? "#c2410c" : partColor(labels[index])} />
          </mesh>
        );
      })}
    </Canvas>
  );
}
