import { readFileSync } from "node:fs";
import path from "node:path";

type Row = {
  theorem: string;
  paper_value: number;
  absolute_error: number;
  computed: {
    motif: string;
    value: number;
    ratios: number[];
    parts_used: number;
    singleton_mass: number;
    method: string;
    evaluations: number;
    success: boolean;
  };
};

export default function Page() {
  const file = path.join(process.cwd(), "..", "..", "experiments", "results", "section6.json");
  const payload = JSON.parse(readFileSync(file, "utf8")) as { claim: string; rows: Row[] };
  return (
    <section>
      <h1 className="mb-2 font-serif text-4xl">Paper results</h1>
      <p className="mb-6 max-w-3xl text-sm leading-6 text-muted-foreground">{payload.claim}</p>
      <div className="space-y-6">
        {payload.rows.map((row) => (
          <article key={row.theorem} className="border border p-4">
            <h2 className="font-serif text-2xl">{row.theorem}</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              <a className="underline" href="https://arxiv.org/abs/2012.10731">
                arXiv:2012.10731
              </a>
              , Section 6. Motif {row.computed.motif}. Method {row.computed.method}, {row.computed.evaluations} evaluations.
            </p>
            <dl className="mt-4 grid gap-3 sm:grid-cols-3 text-sm">
              <Field label="Computed" value={row.computed.value.toPrecision(12)} />
              <Field label="Stated in the paper" value={row.paper_value.toPrecision(12)} />
              <Field label="Absolute error" value={row.absolute_error.toExponential(2)} />
            </dl>
            <RatioBar ratios={row.computed.ratios} singletonMass={row.computed.singleton_mass} />
            <p className="mt-3 text-sm">
              Parts {row.computed.parts_used}, singleton mass {row.computed.singleton_mass.toFixed(6)}. Solver success:{" "}
              {row.computed.success ? "yes" : "no"}.
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}

function RatioBar({ ratios, singletonMass }: { ratios: number[]; singletonMass: number }) {
  const pieces = [...ratios.map((value) => ({ value, label: "part" })), { value: singletonMass, label: "singletons" }];
  return (
    <div className="mt-4" aria-label="Part masses">
      <div className="flex h-8 overflow-hidden border border">
        {pieces.filter((piece) => piece.value > 0.001).map((piece, index) => (
          <div
            key={`${piece.label}-${index}`}
            style={{ width: `${piece.value * 100}%`, background: piece.label === "singletons" ? "#e7e5e4" : index % 2 === 0 ? "#1c1915" : "#9a3412" }}
            title={`${piece.label} ${piece.value.toFixed(4)}`}
          />
        ))}
      </div>
      <p className="mt-1 text-xs text-muted-foreground">Dark blocks are parts. The pale block is singleton mass.</p>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wide text-muted-foreground">{label}</dt>
      <dd className="font-serif text-xl">{value}</dd>
    </div>
  );
}
