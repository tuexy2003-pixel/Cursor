"use client";

import { useEffect, useState } from "react";
import { apiGet, apiSend } from "../../lib/api";

type Experiment = { id: string; name: string; hypothesis: string; variable_dimension: string; status: string; variants: { name: string; is_control: boolean }[] };

export default function ExperimentsPage() {
  const [rows, setRows] = useState<Experiment[]>([]);
  const [name, setName] = useState("");
  const [hypothesis, setHypothesis] = useState("");
  const [dimension, setDimension] = useState("floating_hook");
  const [error, setError] = useState<string | null>(null);

  function load() { apiGet<Experiment[]>("/experiments").then(setRows).catch((err: Error) => setError(err.message)); }
  useEffect(() => { load(); }, []);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    await apiSend("/experiments", {
      name,
      hypothesis,
      variable_dimension: dimension,
      control_changes: {},
      variant_changes: { [dimension]: "changed" },
    });
    setName("");
    setHypothesis("");
    load();
  }

  return (
    <>
      <h1>Experiments</h1>
      <p className="muted">Change one dimension. The registry stores what stayed fixed.</p>
      {error && <p className="error">{error}</p>}
      <form onSubmit={submit}>
        <input placeholder="Name" value={name} onChange={(event) => setName(event.target.value)} required />
        <textarea placeholder="Hypothesis" value={hypothesis} onChange={(event) => setHypothesis(event.target.value)} required />
        <input placeholder="Dimension" value={dimension} onChange={(event) => setDimension(event.target.value)} required />
        <button type="submit">Record experiment</button>
      </form>
      {rows.map((row) => (
        <section className="card" key={row.id}>
          <h2>{row.name}</h2>
          <p>{row.hypothesis}</p>
          <p>Dimension: {row.variable_dimension}. Variants: {row.variants.map((variant) => variant.name).join(", ")}</p>
        </section>
      ))}
    </>
  );
}
