"use client";

type Row = {
  motif: string;
  toggles: number;
  density: number;
  density_drop: number;
  defect: number;
  clean_density: number;
};

const COLORS: Record<string, string> = { K22: "#9a3412", K311: "#1d4e89" };

export function StabilityChart({ rows }: { rows: Row[] }) {
  const motifs = [...new Set(rows.map((row) => row.motif))];
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Scatter rows={rows} motifs={motifs} />
      <Means rows={rows} motifs={motifs} />
    </div>
  );
}

function Scatter({ rows, motifs }: { rows: Row[]; motifs: string[] }) {
  const width = 520;
  const height = 320;
  const pad = 36;
  const maxD = Math.max(...rows.map((row) => row.density), 0.01);
  const maxX = Math.max(...rows.map((row) => row.toggles), 1);
  return (
    <figure>
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full border border-rule bg-paper" role="img" aria-label="Density against edit fraction">
        {rows.map((row, index) => {
          const x = pad + (row.toggles / maxX) * (width - pad - 12);
          const y = height - pad - (row.density / maxD) * (height - pad - 16);
          return <circle key={index} cx={x} cy={y} r={3.2} fill={COLORS[row.motif] ?? "#1c1915"} />;
        })}
        <text x={pad} y={16} fontSize="12" fill="#1c1915">
          exact induced density
        </text>
        <text x={width - 150} y={height - 10} fontSize="12" fill="#1c1915">
          pairs toggled
        </text>
      </svg>
      <Legend motifs={motifs} />
    </figure>
  );
}

function Means({ rows, motifs }: { rows: Row[]; motifs: string[] }) {
  const width = 520;
  const height = 320;
  const pad = 36;
  const maxDrop = Math.max(...rows.map((row) => row.density_drop), 0.01);
  const maxT = Math.max(...rows.map((row) => row.toggles), 1);
  return (
    <figure>
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full border border-rule bg-paper" role="img" aria-label="Mean density drop against pairs toggled">
        {motifs.map((motif) => {
          const budgets = [...new Set(rows.filter((row) => row.motif === motif).map((row) => row.toggles))].sort((a, b) => a - b);
          const path = budgets
            .map((budget, index) => {
              const sample = rows.filter((row) => row.motif === motif && row.toggles === budget);
              const mean = sample.reduce((sum, row) => sum + row.density_drop, 0) / sample.length;
              const x = pad + (budget / maxT) * (width - pad - 12);
              const y = height - pad - (mean / maxDrop) * (height - pad - 16);
              return `${index === 0 ? "M" : "L"}${x.toFixed(1)} ${y.toFixed(1)}`;
            })
            .join(" ");
          return <path key={motif} d={path} fill="none" stroke={COLORS[motif] ?? "#1c1915"} strokeWidth="1.8" />;
        })}
        <text x={pad} y={16} fontSize="12" fill="#1c1915">
          mean density drop
        </text>
        <text x={width - 120} y={height - 10} fontSize="12" fill="#1c1915">
          pairs toggled
        </text>
      </svg>
      <Legend motifs={motifs} />
    </figure>
  );
}

function Legend({ motifs }: { motifs: string[] }) {
  return (
    <figcaption className="mt-2 flex gap-4 text-xs text-ink/70">
      {motifs.map((motif) => (
        <span key={motif}>
          <span className="mr-1 inline-block h-2 w-2" style={{ background: COLORS[motif] ?? "#1c1915" }} />
          {motif}
        </span>
      ))}
    </figcaption>
  );
}
