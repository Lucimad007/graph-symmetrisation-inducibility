import { StabilityChart } from "@/components/StabilityChart";
import { readFileSync } from "node:fs";
import path from "node:path";

type OneEdge = {
  host: string;
  motif: string;
  n: number;
  copies_lost_adding_an_edge_inside_the_largest_part: number | null;
  copies_lost_deleting_a_cross_edge: number | null;
};

type Payload = {
  seed: number;
  operation: string;
  density_is: string;
  one_edge: OneEdge[];
  rows: {
    motif: string;
    toggles: number;
    density: number;
    density_drop: number;
    defect: number;
    clean_density: number;
    n: number;
  }[];
};

export default function Page() {
  const file = path.join(process.cwd(), "..", "..", "experiments", "results", "near_extremal.json");
  let payload: Payload | null = null;
  try {
    payload = JSON.parse(readFileSync(file, "utf8")) as Payload;
  } catch {
    payload = null;
  }
  if (!payload) {
    return (
      <section>
        <h1 className="font-serif text-4xl">Near-extremal edits</h1>
        <p className="mt-3 text-sm">Run python -m experiments.near_extremal to generate the figure data.</p>
      </section>
    );
  }
  return (
    <section>
      <h1 className="mb-2 font-serif text-4xl">Near-extremal edits</h1>
      <p className="mb-6 max-w-3xl text-sm leading-6 text-muted-foreground">
        Each point starts from a complete multipartite host with a high induced density, then toggles a random set of
        pairs. Densities are exact. Seed {payload.seed}. {payload.operation}. This is the shape suggested by perfect
        stability; it is not a proof of Theorem 1.4.
      </p>
      <StabilityChart rows={payload.rows} />
      <div className="mt-8 grid gap-4 md:grid-cols-2">
        {payload.one_edge.map((item) => (
          <article key={item.motif} className="border border p-4 text-sm">
            <h2 className="font-serif text-2xl">{item.motif}</h2>
            <p className="mt-1 text-muted-foreground">
              {item.host}, n = {item.n}. Copies lost by one edit, Theorem 1.4 (i) as a finite count.
            </p>
            <dl className="mt-3 grid grid-cols-2 gap-3">
              <div>
                <dt className="text-xs uppercase tracking-wide text-muted-foreground">Edge inside the large part</dt>
                <dd className="font-serif text-3xl">{item.copies_lost_adding_an_edge_inside_the_largest_part}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-muted-foreground">Cross edge deleted</dt>
                <dd className="font-serif text-3xl">{item.copies_lost_deleting_a_cross_edge}</dd>
              </div>
            </dl>
          </article>
        ))}
      </div>
    </section>
  );
}
