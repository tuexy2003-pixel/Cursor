"use client";

import { useEffect, useState } from "react";
import { apiGet, apiSend } from "../../lib/api";

type ProviderChoice = {
  name: string;
  available: boolean;
  explicit_model: string | null;
  status: string;
};
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
type Diversity = {
  level: string | null;
  report: { reason?: string; assessment_method?: string; coverage?: { known_count: number; total_count: number } } | null;
  status: string;
};
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
  execution_state: string | null;
  provider_request_id: string | null;
  parse_error: string | null;
  parsed_output: unknown;
  diversity: Diversity | null;
  story_audit: { record_status: string; overall_status: string; diagnosis: string } | null;
};
type UsageRow = {
  provider_model: string;
  run_count: number;
  input_tokens: number;
  output_tokens: number;
  cached_tokens: number;
  known_cost: number | null;
  unknown_cost_runs: number;
  provider_errors: number;
  parse_failures: number;
};
type Gate = {
  live_text_reasoning_enabled: boolean;
  daily_run_limit: number;
  daily_network_attempts: number;
  max_providers: number;
  estimated_cost_status: string;
};
type Preflight = {
  execution_status: string;
  provider: string;
  model: string | null;
  stage: string;
  task_instruction: string;
  context_bundle_id: string;
  context_bundle_hash: string;
  character_count: number;
  estimated_tokens: number;
  max_attempts: number;
  max_output_tokens: number;
  daily_network_attempts: number;
  daily_run_limit: number;
  estimated_cost_status: string;
  warning: string;
};
type Payload = {
  text_reasoning_providers: ProviderChoice[];
  allowed_stages: string[];
  disabled_capabilities: string[];
  context_bundles: BundleChoice[];
  manual_evaluations: Evaluation[];
  model_runs: RunView[];
  execution_gate: Gate;
  usage: { today: UsageRow[]; last_7_days: UsageRow[]; lifetime: UsageRow[] };
};

function money(run: RunView) {
  if (run.cost == null) return "UNKNOWN";
  return `${run.cost} ${run.cost_currency ?? ""}`.trim();
}

function tokens(value: number | null) {
  return value == null ? "UNKNOWN" : String(value);
}

function usageTable(title: string, rows: UsageRow[]) {
  return (
    <>
      <h3>{title}</h3>
      <table>
        <thead>
          <tr>
            <th>Provider / model</th>
            <th>Runs</th>
            <th>In</th>
            <th>Out</th>
            <th>Cached</th>
            <th>Known cost</th>
            <th>Unknown cost</th>
            <th>Provider errors</th>
            <th>Parse failures</th>
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr><td colSpan={9}>No recorded runs</td></tr>
          ) : rows.map((row) => (
            <tr key={row.provider_model}>
              <td>{row.provider_model}</td>
              <td>{row.run_count}</td>
              <td>{row.input_tokens}</td>
              <td>{row.output_tokens}</td>
              <td>{row.cached_tokens}</td>
              <td>{row.known_cost == null ? "UNKNOWN" : row.known_cost}</td>
              <td>{row.unknown_cost_runs}</td>
              <td>{row.provider_errors}</td>
              <td>{row.parse_failures}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}

export default function RunsPage() {
  const [data, setData] = useState<Payload | null>(null);
  const [bundleId, setBundleId] = useState("");
  const [providerName, setProviderName] = useState("");
  const [preflight, setPreflight] = useState<Preflight | null>(null);
  const [idempotencyKey, setIdempotencyKey] = useState("");
  const [result, setResult] = useState<RunView | null>(null);
  const [message, setMessage] = useState("");
  const [compareNames, setCompareNames] = useState<string[]>([]);
  const [compareMessage, setCompareMessage] = useState("");

  function load() {
    apiGet<Payload>("/runs").then(setData).catch(() => setData(null));
  }

  useEffect(() => { load(); }, []);

  useEffect(() => {
    if (!bundleId || !providerName) {
      setPreflight(null);
      setIdempotencyKey("");
      return;
    }
    setIdempotencyKey(crypto.randomUUID());
    setResult(null);
    apiGet<Preflight>(`/runs/preflight?context_bundle_id=${encodeURIComponent(bundleId)}&provider=${encodeURIComponent(providerName)}`)
      .then(setPreflight)
      .catch((error: Error) => {
        setPreflight(null);
        setMessage(error.message);
      });
  }, [bundleId, providerName]);

  async function authorizeOnce() {
    if (!bundleId || !providerName || !idempotencyKey) return;
    setMessage("");
    try {
      const response = await apiSend<{ run: RunView }>("/runs/authorize-once", {
        context_bundle_id: bundleId,
        provider: providerName,
        idempotency_key: idempotencyKey,
      });
      setResult(response.run);
      load();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "authorization failed");
    }
  }

  function toggleCompare(name: string) {
    setCompareNames((current) => {
      if (current.includes(name)) return current.filter((item) => item !== name);
      if (current.length >= 2) return current;
      return [...current, name];
    });
  }

  async function compare() {
    setCompareMessage("");
    try {
      await apiSend("/runs/compare", { context_bundle_id: bundleId, providers: compareNames });
      setCompareMessage("comparison returned without a named authorization");
    } catch (error) {
      setCompareMessage(error instanceof Error ? error.message : "comparison rejected");
    }
  }

  const gate = data?.execution_gate;

  return (
    <>
      <h1>Safe live text reasoning</h1>
      <p className="muted">
        A configured API key is not permission to spend. Live text reasoning stays off until the operator enables it
        and authorizes one frozen context bundle.
      </p>
      <p>Allowed stages: {data?.allowed_stages.join(", ") || "loading"}</p>
      <p>Disabled: {data?.disabled_capabilities.join(", ") || "loading"}</p>
      <p>
        Live flag: {gate ? String(gate.live_text_reasoning_enabled) : "loading"}
        {" · "}
        Daily network attempts: {gate ? `${gate.daily_network_attempts} / ${gate.daily_run_limit}` : "loading"}
        {" · "}
        Comparison cap: {gate?.max_providers ?? "loading"}
        {" · "}
        Estimated cost source: {gate?.estimated_cost_status ?? "UNKNOWN"}
      </p>

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

      <h2>Safe live smoke test</h2>
      <p className="muted">
        One provider. One frozen bundle. One network attempt. No provider is pre-selected.
      </p>
      <form onSubmit={(event) => { event.preventDefault(); void authorizeOnce(); }}>
        <label>
          Context bundle
          <select value={bundleId} onChange={(event) => setBundleId(event.target.value)}>
            <option value="">Select a frozen bundle</option>
            {(data?.context_bundles ?? []).map((bundle) => (
              <option key={bundle.id} value={bundle.id}>
                {bundle.expected_output_type || bundle.stage} · {bundle.payload_hash.slice(0, 12)} · {bundle.instruction}
              </option>
            ))}
          </select>
        </label>
        <fieldset>
          <legend>One provider</legend>
          {(data?.text_reasoning_providers ?? []).map((provider) => (
            <label className="choice" key={provider.name}>
              <input
                type="radio"
                name="provider"
                checked={providerName === provider.name}
                onChange={() => setProviderName(provider.name)}
              />
              {provider.name} · key {provider.available ? "configured" : "missing"} · {provider.status}
              {provider.explicit_model ? ` · ${provider.explicit_model}` : " · model not set"}
            </label>
          ))}
        </fieldset>
        {preflight ? (
          <div className="warning">
            <p><strong>{preflight.warning}</strong></p>
            <dl className="confirm">
              <dt>PROVIDER</dt><dd>{preflight.provider}</dd>
              <dt>MODEL</dt><dd>{preflight.model ?? "NOT CONFIGURED"}</dd>
              <dt>STAGE</dt><dd>{preflight.stage}</dd>
              <dt>TASK</dt><dd>{preflight.task_instruction}</dd>
              <dt>CONTEXT BUNDLE ID</dt><dd>{preflight.context_bundle_id}</dd>
              <dt>CONTEXT HASH</dt><dd>{preflight.context_bundle_hash}</dd>
              <dt>CONTEXT SIZE</dt><dd>{preflight.character_count} characters · {preflight.estimated_tokens} estimated tokens</dd>
              <dt>MAX ATTEMPTS</dt><dd>{preflight.max_attempts}</dd>
              <dt>MAX OUTPUT TOKENS</dt><dd>{preflight.max_output_tokens}</dd>
              <dt>DAILY RUN COUNT / LIMIT</dt><dd>{preflight.daily_network_attempts} / {preflight.daily_run_limit}</dd>
              <dt>ESTIMATED COST</dt><dd>{preflight.estimated_cost_status}</dd>
              <dt>EXECUTION STATUS</dt><dd>{preflight.execution_status}</dd>
            </dl>
          </div>
        ) : null}
        <button type="submit" disabled={!preflight || !idempotencyKey}>AUTHORIZE & RUN ONCE</button>
      </form>
      {message ? <p className="error">{message}</p> : null}
      {result ? (
        <article className="card">
          <h3>{result.provider_model_name} · {result.status}</h3>
          <p>Execution state: {result.execution_state}</p>
          <p>Provider request id: {result.provider_request_id ?? "not returned"}</p>
          <p>Bundle hash: {result.context_bundle_hash}</p>
          <p>Cost: {money(result)}</p>
          <p>Tokens in/out/cached: {tokens(result.input_tokens)} / {tokens(result.output_tokens)} / {tokens(result.cached_tokens)}</p>
          {result.diversity ? (
            <p>
              Diversity heuristic: {result.diversity.level}
              {" "}
              ({result.diversity.report?.assessment_method ?? "DETERMINISTIC_HEURISTIC"}
              {result.diversity.report?.coverage
                ? `, coverage ${result.diversity.report.coverage.known_count}/${result.diversity.report.coverage.total_count}`
                : ""}
              )
            </p>
          ) : null}
          {result.story_audit ? <p>Audit record: {result.story_audit.record_status} · {result.story_audit.overall_status}</p> : null}
          {result.parse_error ? <p className="error">{result.parse_error}</p> : null}
          {result.error && result.error !== result.parse_error ? <p className="error">{result.error}</p> : null}
        </article>
      ) : null}
      <p className="muted">Manual packet export remains available with creative-os export-context-bundle.</p>

      <h2>Recorded usage</h2>
      <p className="muted">Counts come from stored model runs. This view does not call a billing API.</p>
      {data ? (
        <>
          {usageTable("Today", data.usage.today)}
          {usageTable("Last 7 days", data.usage.last_7_days)}
          {usageTable("Lifetime", data.usage.lifetime)}
        </>
      ) : null}

      <h2>Provider comparison</h2>
      <p className="muted">
        Comparison is capped at 2 named providers and is not the first live action. No provider starts selected.
        A paid comparison requires an authorization that names those providers.
      </p>
      {(data?.text_reasoning_providers ?? []).map((provider) => (
        <label className="choice" key={`compare-${provider.name}`}>
          <input
            type="checkbox"
            checked={compareNames.includes(provider.name)}
            onChange={() => toggleCompare(provider.name)}
          />
          {provider.name}
        </label>
      ))}
      <button type="button" disabled={!bundleId || compareNames.length === 0} onClick={() => void compare()}>
        Request named comparison
      </button>
      {compareMessage ? <p className="error">{compareMessage}</p> : null}

      <h2>Recent runs</h2>
      <div className="columns">
        {(data?.model_runs ?? []).slice(0, 6).map((run) => (
          <article className="card" key={run.id}>
            <h3>{run.provider_model_name} · {run.status}</h3>
            <p>State: {run.execution_state}</p>
            <p>Cost: {money(run)}</p>
            <p>Tokens in/out/cached: {tokens(run.input_tokens)} / {tokens(run.output_tokens)} / {tokens(run.cached_tokens)}</p>
          </article>
        ))}
      </div>
    </>
  );
}
