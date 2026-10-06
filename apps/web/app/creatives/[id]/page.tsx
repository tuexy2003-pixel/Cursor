"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiGet, apiSend } from "../../../lib/api";

type Detail = {
  name: string;
  status: string;
  notes: string | null;
  story_lock: { version_number: number; approved_by: string | null; change_reason: string; content: Record<string, unknown> } | null;
  versions: { id: string; version_number: number; change_reason: string; approved_by: string | null; content_hash: string }[];
  line_items: { position: number; title: string; unit_price: string | null; model: string | null }[];
  comment_doors: { kind: string; text: string }[];
  assets: { name: string; role: string; rights_status: string; stale: boolean; staleness_state?: string }[];
  approvals: { status: string; actor: string; notes: string | null }[];
  genome: { dimension: string; value: string; assignment: string }[];
  diff_from_previous: { path: string; from: unknown; to: unknown }[] | null;
  context_preview: {
    provider_execution: string;
    requested_stage: string;
    global_invariants: { code: string; reason_included: string; authority: string; scope: string; version: string }[];
    program_policies: unknown[];
    account_policies: unknown[];
    campaign_policies: unknown[];
    creative_locks: unknown[];
    skill_versions: unknown[];
    excluded_for_token_budget: unknown[];
    current_story_lock_version: { version_number: number; document_hash: string | null } | null;
    account_dna: { version: string } | null;
    creative_genome: { version: string } | null;
  } | null;
};

export default function CreativeDetailPage() {
  const params = useParams<{ id: string }>();
  const [detail, setDetail] = useState<Detail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [hook, setHook] = useState("");
  const [reason, setReason] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  function load() {
    apiGet<Detail>(`/creatives/${params.id}`).then(setDetail).catch((err: Error) => setError(err.message));
  }
  useEffect(() => { load(); }, [params.id]);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setMessage(null);
    try {
      const result = await apiSend<{ version_number: number }>(`/creatives/${params.id}/story-lock/corrections`, {
        changes: { floating_hook: hook },
        actor: "operator",
        reason,
      });
      setMessage(`Approved version ${result.version_number}. Previous version kept. Only affected deliverables were marked stale.`);
      setHook("");
      setReason("");
      load();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "correction failed");
    }
  }

  if (error) return <p className="error">{error}</p>;
  if (!detail) return <p>Loading…</p>;
  const content = detail.story_lock?.content ?? {};
  return (
    <>
      <h1>{detail.name}</h1>
      <p className="muted">{detail.status}. {detail.notes}</p>
      <section className="card">
        <h2>Current story lock v{detail.story_lock?.version_number ?? "—"}</h2>
        <p>Hook: {String(content.hook ?? "—")}</p>
        <p>Floating hook: {String(content.floating_hook ?? "—")}</p>
        <p>Approved by {detail.story_lock?.approved_by}. {detail.story_lock?.change_reason}</p>
      </section>
      <section className="card">
        <h2>Economics and items</h2>
        <pre>{JSON.stringify(content.economics ?? null, null, 2)}</pre>
        <table>
          <tbody>
            {detail.line_items.map((item) => (
              <tr key={item.position}><td>{item.position}</td><td>{item.title}</td><td>{item.unit_price}</td><td>{item.model}</td></tr>
            ))}
          </tbody>
        </table>
      </section>
      <section className="card">
        <h2>Comment doors</h2>
        <ul>{detail.comment_doors.map((door) => <li key={door.text}>{door.kind}: {door.text}</li>)}</ul>
      </section>
      <section className="card">
        <h2>Genome</h2>
        <ul>{detail.genome.map((facet) => <li key={facet.dimension}>{facet.dimension}: {facet.value} ({facet.assignment})</li>)}</ul>
      </section>
      <section className="card">
        <h2>Diff from previous version</h2>
        {detail.diff_from_previous ? (
          <pre>{JSON.stringify(detail.diff_from_previous, null, 2)}</pre>
        ) : (
          <p className="muted">No previous approved version.</p>
        )}
      </section>
      <section className="card">
        <h2>Versions</h2>
        <table>
          <tbody>
            {detail.versions.map((version) => (
              <tr key={version.id}><td>v{version.version_number}</td><td>{version.approved_by}</td><td>{version.change_reason}</td><td>{version.content_hash.slice(0, 12)}</td></tr>
            ))}
          </tbody>
        </table>
      </section>
      <section className="card">
        <h2>Assets</h2>
        <table>
          <tbody>
            {detail.assets.map((asset) => (
              <tr key={asset.name}><td>{asset.name}</td><td>{asset.role}</td><td>{asset.rights_status}</td><td>{asset.staleness_state ?? (asset.stale ? "stale" : "current")}</td></tr>
            ))}
          </tbody>
        </table>
      </section>
      <section className="card">
        <h2>Context preview</h2>
        <p className="muted">Dry run only. Provider execution is {detail.context_preview?.provider_execution ?? "NOT_IMPLEMENTED"}.</p>
        {detail.context_preview && (
          <ul>
            <li>Stage: {detail.context_preview.requested_stage}</li>
            <li>Story lock v{detail.context_preview.current_story_lock_version?.version_number ?? "—"}</li>
            <li>Global invariants: {detail.context_preview.global_invariants.length}</li>
            <li>Program policies: {detail.context_preview.program_policies.length}</li>
            <li>Account policies: {detail.context_preview.account_policies.length}</li>
            <li>Campaign policies: {detail.context_preview.campaign_policies.length}</li>
            <li>Creative locks: {detail.context_preview.creative_locks.length}</li>
            <li>Skill versions: {detail.context_preview.skill_versions.length}</li>
            <li>Account DNA: {detail.context_preview.account_dna?.version ?? "none"}</li>
            <li>Genome: {detail.context_preview.creative_genome?.version ?? "none"}</li>
            <li>Excluded for token budget: {detail.context_preview.excluded_for_token_budget.length}</li>
          </ul>
        )}
        {detail.context_preview?.global_invariants[0] && (
          <p>
            Example invariant {detail.context_preview.global_invariants[0].code}: {detail.context_preview.global_invariants[0].reason_included}. Scope {detail.context_preview.global_invariants[0].scope}. Authority {detail.context_preview.global_invariants[0].authority}.
          </p>
        )}
      </section>
      <section className="card">
        <h2>Human correction</h2>
        <p className="muted">The server records the configured operator. A provider proposal cannot approve itself. Only affected deliverables go stale.</p>
        <form onSubmit={submit}>
          <label>New floating hook<input value={hook} onChange={(event) => setHook(event.target.value)} required /></label>
          <label>Reason<textarea value={reason} onChange={(event) => setReason(event.target.value)} required /></label>
          <button type="submit">Approve new version</button>
        </form>
        {message && <p>{message}</p>}
      </section>
    </>
  );
}
