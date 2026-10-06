"use client";

import { useEffect, useState } from "react";
import { apiGet, apiSend } from "../../lib/api";

type Payload = {
  providers: { name: string; capability: string; model_version: string | null }[];
  model_runs: { id: string; status: string; error: string | null }[];
};

export default function RunsPage() {
  const [data, setData] = useState<Payload | null>(null);
  function load() { apiGet<Payload>("/runs").then(setData).catch(() => setData(null)); }
  useEffect(() => { load(); }, []);
  return (
    <>
      <h1>Model and validation runs</h1>
      <p className="muted">Providers are recorded. Execution returns NOT_IMPLEMENTED.</p>
      <button type="button" onClick={() => apiSend("/runs/stub", {}).then(load)}>Record a stub run</button>
      <ul>{data?.providers.map((row) => <li key={row.name + row.capability}>{row.name} / {row.capability} / {row.model_version}</li>)}</ul>
      <ul>{data?.model_runs.map((row) => <li key={row.id}>{row.status}: {row.error}</li>)}</ul>
    </>
  );
}
