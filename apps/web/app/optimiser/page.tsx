import { OptimiserView } from "@/components/OptimiserView";

export default function Page() {
  return (
    <section>
      <h1 className="mb-2 font-serif text-4xl">Multipartite optimiser</h1>
      <p className="mb-6 max-w-3xl text-sm leading-6 text-ink/80">
        Bipartite part ratios for Theorem 1.6. The eight-part and singleton-mass searches from Theorems 1.8 and 1.9
        are the Python runs reported on the paper-results page.
      </p>
      <OptimiserView />
    </section>
  );
}
