import { Explorer } from "@/components/Explorer";

export default function Page() {
  return (
    <section>
      <h1 className="mb-2 font-serif text-4xl">Graph symmetrisation</h1>
      <p className="mb-6 max-w-3xl text-sm leading-6 text-muted-foreground">
        A finite illustration of Zykov&apos;s clone step. The selection rule is the degree rule from the introduction
        of the paper. It keeps the number of edges from falling. It does not, by itself, prove that an induced-density
        objective is symmetrisable.
      </p>
      <Explorer />
    </section>
  );
}
