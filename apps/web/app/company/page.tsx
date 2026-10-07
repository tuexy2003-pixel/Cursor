"use client";

import { type FormEvent, useCallback, useEffect, useState } from "react";
import { apiGet, apiSend } from "../../lib/api";

type Status = {
  running: Array<{ id: string; goal: string; status: string }>;
  blocked: Array<{ id: string; goal: string; status: string }>;
  waiting_on_human: Array<{ id: string; approval_type: string; subject_id: string; status: string }>;
  waiting_on_specialist: Array<{ id: string; specialist_role: string; transport: string; status: string }>;
  missing_references: Array<{ workflow_run_id: string; gaps: Array<Record<string, string | null>> }>;
  completed_recently: Array<{ id: string; goal: string; status: string }>;
  recommended_next_action: { action: string; subject_id: string; reason: string };
};

type Queue = {
  work_orders: Array<{ id: string; goal: string; status: string; priority: string; task_ids: string[] }>;
  programs: Array<{ id: string; slug: string; name: string }>;
};

type RunRow = { id: string; work_order_id: string; status: string };
type RunDetail = {
  id: string;
  status: string;
  graph_hash: string | null;
  steps: Array<{ id: string; node_id: string; node_kind: string; status: string; error_code: string | null }>;
};
type Assignment = {
  id: string;
  specialist_role: string;
  transport: string;
  status: string;
  validation_status: string;
  api_verified: boolean;
  contract_name: string;
};
type Packet = { wrapper: string; bundle_id: string; bundle_hash: string; transport: string; api_verified: boolean };

export default function CompanyPage() {
  const [status, setStatus] = useState<Status | null>(null);
  const [queue, setQueue] = useState<Queue | null>(null);
  const [runs, setRuns] = useState<RunRow[]>([]);
  const [detail, setDetail] = useState<RunDetail | null>(null);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [packet, setPacket] = useState<Packet | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [goal, setGoal] = useState("");
  const [programId, setProgramId] = useState("");
  const [workOrderId, setWorkOrderId] = useState("");
  const [assignmentId, setAssignmentId] = useState("");
  const [provider, setProvider] = useState("grok");
  const [model, setModel] = useState("grok-4");
  const [raw, setRaw] = useState("");
  const [approvalId, setApprovalId] = useState("");
  const [conceptId, setConceptId] = useState("");
  const [decision, setDecision] = useState("APPROVED");

  const load = useCallback(() => {
    setError(null);
    Promise.all([
      apiGet<Status>("/company/status"),
      apiGet<Queue>("/company/queue"),
      apiGet<RunRow[]>("/company/workflow-runs"),
      apiGet<Assignment[]>("/company/assignments"),
    ])
      .then(([nextStatus, nextQueue, nextRuns, nextAssignments]) => {
        setStatus(nextStatus);
        setQueue(nextQueue);
        setRuns(nextRuns);
        setAssignments(nextAssignments);
        if (!programId && nextQueue.programs[0]) setProgramId(nextQueue.programs[0].id);
      })
      .catch((err: Error) => setError(err.message));
  }, [programId]);

  useEffect(() => {
    load();
  }, [load]);

  async function createOrder(event: FormEvent) {
    event.preventDefault();
    try {
      await apiSend("/company/work-orders", { goal, program_id: programId, priority: "NORMAL" });
      setGoal("");
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create the work order");
    }
  }

  async function startRun(event: FormEvent) {
    event.preventDefault();
    try {
      const created = await apiSend<{ id: string }>("/company/workflow-runs", { work_order_id: workOrderId });
      setDetail(await apiGet<RunDetail>(`/company/workflow-runs/${created.id}`));
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not start the workflow");
    }
  }

  async function openRun(id: string) {
    setDetail(await apiGet<RunDetail>(`/company/workflow-runs/${id}`));
  }

  async function loadPacket(id: string) {
    setAssignmentId(id);
    setPacket(await apiGet<Packet>(`/company/assignments/${id}/packet`));
  }

  async function copyWrapper() {
    if (packet) await navigator.clipboard.writeText(packet.wrapper);
  }

  async function importResponse(event: FormEvent) {
    event.preventDefault();
    try {
      await apiSend(`/company/assignments/${assignmentId}/import`, {
        raw_response: raw,
        provider_name: provider,
        model_name: model,
      });
      setRaw("");
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not import the response");
    }
  }

  async function decide(event: FormEvent) {
    event.preventDefault();
    try {
      await apiSend(`/company/approvals/${approvalId}/decide`, {
        decision,
        concept_id: conceptId || null,
      });
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not record the decision");
    }
  }

  return (
    <>
      <h1>Company</h1>
      <p className="muted">
        Creative OS calculates this queue. A specialist proposal does not approve itself, and a reported
        execution is not a verified outcome.
      </p>
      {error && <p className="error">{error}</p>}
      {status && (
        <section className="card" id="today">
          <h2>Today</h2>
          <p>
            <strong>{status.recommended_next_action.action}</strong> {status.recommended_next_action.reason}
          </p>
          <div className="columns">
            <Count label="Running" value={status.running.length} />
            <Count label="Blocked" value={status.blocked.length} />
            <Count label="Waiting on you" value={status.waiting_on_human.length} />
            <Count label="Waiting on a specialist" value={status.waiting_on_specialist.length} />
          </div>
        </section>
      )}

      <section id="work-orders">
        <h2>Work orders</h2>
        <form onSubmit={createOrder}>
          <label>
            Goal
            <input value={goal} onChange={(event) => setGoal(event.target.value)} required />
          </label>
          <label>
            Program
            <select value={programId} onChange={(event) => setProgramId(event.target.value)}>
              {(queue?.programs ?? []).map((program) => (
                <option key={program.id} value={program.id}>
                  {program.slug}
                </option>
              ))}
            </select>
          </label>
          <button type="submit">Create work order</button>
        </form>
        <table>
          <thead>
            <tr>
              <th>Goal</th>
              <th>Status</th>
              <th>Priority</th>
              <th>Tasks</th>
            </tr>
          </thead>
          <tbody>
            {(queue?.work_orders ?? []).map((order) => (
              <tr key={order.id}>
                <td>{order.goal}</td>
                <td>{order.status}</td>
                <td>{order.priority}</td>
                <td>{order.task_ids.length}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <form onSubmit={startRun}>
          <label>
            Start NEW_CREATIVE_V1
            <select value={workOrderId} onChange={(event) => setWorkOrderId(event.target.value)}>
              <option value="">Choose a work order</option>
              {(queue?.work_orders ?? []).map((order) => (
                <option key={order.id} value={order.id}>
                  {order.goal}
                </option>
              ))}
            </select>
          </label>
          <button type="submit">Start workflow</button>
        </form>
      </section>

      <section id="workflow-run">
        <h2>Workflow runs</h2>
        <table>
          <thead>
            <tr>
              <th>Run</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => (
              <tr key={run.id}>
                <td>{run.id}</td>
                <td>{run.status}</td>
                <td>
                  <button type="button" onClick={() => openRun(run.id)}>
                    Open
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {detail && (
          <div className="card">
            <p className="muted">Graph {detail.graph_hash}</p>
            <table>
              <thead>
                <tr>
                  <th>Node</th>
                  <th>Kind</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {detail.steps.map((step) => (
                  <tr key={step.id}>
                    <td>{step.node_id}</td>
                    <td>{step.node_kind}</td>
                    <td>{step.error_code ? `${step.status} ${step.error_code}` : step.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section id="waiting">
        <h2>Waiting for me</h2>
        <table>
          <thead>
            <tr>
              <th>Request</th>
              <th>Type</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {(status?.waiting_on_human ?? []).map((row) => (
              <tr key={row.id}>
                <td>{row.id}</td>
                <td>{row.approval_type}</td>
                <td>{row.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <form onSubmit={decide}>
          <label>
            Approval id
            <input value={approvalId} onChange={(event) => setApprovalId(event.target.value)} required />
          </label>
          <label>
            Concept id
            <input value={conceptId} onChange={(event) => setConceptId(event.target.value)} />
          </label>
          <label>
            Decision
            <select value={decision} onChange={(event) => setDecision(event.target.value)}>
              <option>APPROVED</option>
              <option>REJECTED</option>
              <option>NEEDS_CHANGES</option>
            </select>
          </label>
          <button type="submit">Record human decision</button>
        </form>
      </section>

      <section id="assignments">
        <h2>Specialist assignments</h2>
        <table>
          <thead>
            <tr>
              <th>Role</th>
              <th>Transport</th>
              <th>Status</th>
              <th>Validation</th>
              <th>API verified</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {assignments.map((row) => (
              <tr key={row.id}>
                <td>{row.specialist_role}</td>
                <td>{row.transport}</td>
                <td>{row.status}</td>
                <td>{row.validation_status}</td>
                <td>{row.api_verified ? "yes" : "no"}</td>
                <td>
                  <button type="button" onClick={() => loadPacket(row.id)}>
                    Export packet
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {packet && (
          <div className="card">
            <p className="muted">
              Bundle {packet.bundle_id} {packet.bundle_hash} · {packet.transport} · api_verified false
            </p>
            <button type="button" onClick={copyWrapper}>
              Copy wrapper
            </button>
            <pre className="output">{packet.wrapper}</pre>
            <form onSubmit={importResponse}>
              <label>
                Provider
                <input value={provider} onChange={(event) => setProvider(event.target.value)} />
              </label>
              <label>
                Model
                <input value={model} onChange={(event) => setModel(event.target.value)} />
              </label>
              <label>
                Import response
                <textarea value={raw} onChange={(event) => setRaw(event.target.value)} rows={8} required />
              </label>
              <button type="submit">Import response</button>
            </form>
          </div>
        )}
      </section>

      <section id="references">
        <h2>Reference blockers</h2>
        {(status?.missing_references ?? []).length === 0 && <p className="muted">No declared reference gaps.</p>}
        {(status?.missing_references ?? []).map((row) => (
          <div className="card" key={row.workflow_run_id}>
            <p>Run {row.workflow_run_id}</p>
            <ul>
              {row.gaps.map((gap, index) => (
                <li key={`${row.workflow_run_id}-${index}`}>
                  {gap.ecosystem} {gap.surface_type} {gap.state} {gap.mode} {gap.product} {gap.required_role}:{" "}
                  {gap.reason}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </section>
    </>
  );
}

function Count({ label, value }: { label: string; value: number }) {
  return (
    <div className="card">
      <p className="muted">{label}</p>
      <strong>{value}</strong>
    </div>
  );
}
