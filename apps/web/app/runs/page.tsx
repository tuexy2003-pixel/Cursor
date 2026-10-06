"use client";

import { useEffect, useState } from "react";
import { apiGet, apiSend } from "../../lib/api";

type ProviderChoice = { name: string; available: boolean; status: string };
type BundleChoice = {
  id: string;
  stage: string;
  payload_hash: string;
  expected_output_type: string | null;
  instruction: string;
};
type Evaluation = {
  id: string;
  origin: string;
  provider_name: string;
  model_name: string;
  stage: string;
  rubric_score: string;
  packet_hash: string;
  notes: string | null;
  run_timestamp: string;
};
type Diversity = { level: string | null; report: { reason?: string } | null; status: string };
type RunView = {
  id: string;
  status: string;
  error: string | null;
  provider_model_name: string | null;
  latency_ms: number | null;
  cost: string | null;
  cost_currency: string | null;
  input_tokens: number | null;
  output_tokens: number | null;
  cached_tokens: number | null;
  context_bundle_hash: string | null;
  execution_origin: string | null;
  parse_error: string | null;
  parsed_output: unknown;
  diversity: Diversity | null;
  story_audit: { record_status: string; overall_status: string; diagnosis: string } | null;
};
type Payload = {
  text_reasoning_providers: ProviderChoice[];
  allowed_stages: string[];
  disabled_capabilities: string[];
  context_bundles: BundleChoice[];
  manual_evaluations: Evaluation[];
  model_runs: RunView[];
};

function money(run: RunView) {
  if (run.cost == null) return "UNKNOWN";
  return `${run.cost} ${run.cost_currency ?? ""}`.trim();
}

function tokens(value: number | null) {
  return value == null ? "UNKNOWN" : String(value);
}

export default function RunsPage() {
  const [data, setData] = useState<Payload | null>(null);
  const [bundleId, setBundleId] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [compared, setCompared] = useState<RunView[] | null>(null);
  const [message, setMessage] = useState("");

  function load() {
    apiGet<Payload>("/runs").then((payload) => {
      setData(payload);
      setBundleId((current) => current || payload.context_bundles[0]?.id || "");
      setSelected((current) => current.length ? current : payload.text_reasoning_providers.map((row) => row.name));
    }).catch(() => setData(null));
  }

  useEffect(() => { load(); }, []);

  function toggle(name: string) {
    setSelected((current) => current.includes(name) ? current.filter((item) => item !== name) : [...current, name]);
  }

  async function compare() {
    setMessage("");
    setCompared(null);
    try {
      const result = await apiSend<{ runs: RunView[] }>("/runs/compare", {
        context_bundle_id: bundleId,
        providers: selected,
      });
      setCompared(result.runs);
      load();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "comparison failed");
    }
  }

  const shown = compared ?? [];

  return (
    <>
      <h1>Model transfer / provider comparison</h1>
      <p className="muted">
        Text creative reasoning only. A provider reads one frozen context bundle and returns a proposal or a diagnosis.
        Research, image, and posting execution stay disabled. The holdout rubric is not applied here.
      </p>
      <p>Allowed stages: {data?.allowed_stages.join(", ") || "loading"}</p>
      <p>Disabled: {data?.disabled_capabilities.join(", ") || "loading"}</p>

      <h2>Manual transfer evaluations</h2>
      <p className="muted">These scores were recorded outside Creative OS. They are not provider executions.</p>
      <table>
        <thead>
          <tr>
            <th>Origin</th>
            <th>Provider</th>
            <th>Model</th>
            <th>Stage</th>
            <th>Score</th>
            <th>Packet hash</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          {data?.manual_evaluations.map((row) => (
            <tr key={row.id}>
              <td>{row.origin}</td>
              <td>{row.provider_name}</td>
              <td>{row.model_name}</td>
              <td>{row.stage}</td>
              <td>{row.rubric_score}</td>
              <td>{row.packet_hash.slice(0, 12)}</td>
              <td>{row.notes}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Run the same bundle</h2>
      <form onSubmit={(event) => { event.preventDefault(); void compare(); }}>
        <label>
          Context bundle
          <select value={bundleId} onChange={(event) => setBundleId(event.target.value)}>
            {(data?.context_bundles ?? []).map((bundle) => (
              <option key={bundle.id} value={bundle.id}>
                {bundle.stage} · {bundle.payload_hash.slice(0, 12)} · {bundle.instruction}
              </option>
            ))}
          </select>
        </label>
        {(data?.text_reasoning_providers ?? []).map((provider) => (
          <label className="choice" key={provider.name}>
            <input
              type="checkbox"
              checked={selected.includes(provider.name)}
              onChange={() => toggle(provider.name)}
            />
            {provider.name} · {provider.status}
          </label>
        ))}
        <button type="submit" disabled={!bundleId || selected.length === 0}>Run comparison</button>
      </form>
      {message ? <p className="error">{message}</p> : null}
      <p className="muted">Manual packet export remains available with creative-os export-context-bundle.</p>

      <div className="columns">
        {shown.map((run) => (
          <article className="card" key={run.id}>
            <h3>{run.provider_model_name} · {run.status}</h3>
            <p>Origin: {run.execution_origin}</p>
            <p>Bundle hash: {run.context_bundle_hash}</p>
            <p>Latency: {run.latency_ms ?? "UNKNOWN"} ms</p>
            <p>Cost: {money(run)}</p>
            <p>Tokens in/out/cached: {tokens(run.input_tokens)} / {tokens(run.output_tokens)} / {tokens(run.cached_tokens)}</p>
            {run.diversity ? <p>Batch diversity: {run.diversity.level} — {run.diversity.report?.reason}</p> : null}
            {run.story_audit ? <p>Audit record: {run.story_audit.record_status} · {run.story_audit.overall_status}</p> : null}
            {run.parse_error ? <p className="error">{run.parse_error}</p> : null}
            {run.error && run.error !== run.parse_error ? <p className="error">{run.error}</p> : null}
            <pre className="output">{JSON.stringify(run.parsed_output ?? run.story_audit ?? { status: run.status }, null, 2)}</pre>
          </article>
        ))}
      </div>
    </>
  );
}
