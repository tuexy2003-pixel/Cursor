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
  const [stage, setStage] = useState("STORY_DEVELOPMENT");
  const [asOf, setAsOf] = useState("");
  const [bundle, setBundle] = useState<Record<string, unknown> | null>(null);
  const [openSkill, setOpenSkill] = useState<string | null>(null);

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

  async function compileBundle(event: React.FormEvent) {
    event.preventDefault();
    setMessage(null);
    try {
      const result = await apiSend<Record<string, unknown>>(`/creatives/${params.id}/context-bundles`, {
        stage,
        as_of: asOf ? new Date(asOf).toISOString() : null,
      });
      setBundle(result);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "context bundle failed");
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
        <h2>Context bundle</h2>
        <p className="muted">This freezes the exact package a future model would receive. Provider execution is NOT_IMPLEMENTED.</p>
        <form onSubmit={compileBundle}>
          <label>Stage
            <select value={stage} onChange={(event) => setStage(event.target.value)}>
              <option>RESEARCH</option>
              <option>CONCEPT_GENERATION</option>
              <option>STORY_DEVELOPMENT</option>
              <option>PRODUCTION_ROUTING</option>
              <option>PRODUCTION_QA</option>
              <option>PERFORMANCE_INTERPRETATION</option>
            </select>
          </label>
          <label>As of<input type="datetime-local" value={asOf} onChange={(event) => setAsOf(event.target.value)} /></label>
          <button type="submit">Compile context bundle</button>
        </form>
        {bundle && (
          <>
            <ul>
              <li>Bundle id: {String(bundle.id)}</li>
              <li>Bundle hash: {String(bundle.payload_hash)}</li>
              <li>Creative: {String(bundle.creative_id)}</li>
              <li>Account: {String(bundle.account_id ?? "none")}</li>
              <li>Campaign: {String(bundle.campaign_id ?? "none")}</li>
              <li>Story lock: {String(bundle.story_lock_version_id)}</li>
              <li>Account DNA: {String(bundle.account_dna_profile_id ?? "none")}</li>
              <li>Genome: {String(bundle.creative_genome_id ?? "none")}</li>
              <li>Stage: {String(bundle.requested_stage)}</li>
              <li>As of: {String(bundle.as_of)}</li>
              <li>Global invariants: {Array.isArray(bundle.global_invariants) ? bundle.global_invariants.length : 0}</li>
              <li>Program rules: {Array.isArray(bundle.program_policies) ? bundle.program_policies.length : 0}</li>
              <li>Account rules: {Array.isArray(bundle.account_policies) ? bundle.account_policies.length : 0}</li>
              <li>Campaign rules: {Array.isArray(bundle.campaign_policies) ? bundle.campaign_policies.length : 0}</li>
              <li>Creative locks: {Array.isArray(bundle.creative_locks) ? bundle.creative_locks.length : 0}</li>
              <li>Skills: {Array.isArray(bundle.skill_versions) ? bundle.skill_versions.length : 0}</li>
              <li>Benchmarks: {Array.isArray(bundle.benchmarks) ? bundle.benchmarks.length : 0}</li>
              <li>Comment doors: {Array.isArray(bundle.comment_doors) ? bundle.comment_doors.length : 0}</li>
              <li>Continuity: {Array.isArray(bundle.continuity) ? bundle.continuity.length : 0}</li>
              <li>Mechanic history as of: {String((bundle.mechanic_context as { as_of?: string } | null)?.as_of ?? bundle.as_of)}</li>
              <li>References: {Array.isArray(bundle.references) ? bundle.references.length : 0}</li>
              <li>Excluded: {Array.isArray(bundle.excluded_for_token_budget) ? bundle.excluded_for_token_budget.length : 0}</li>
              <li>Characters: {String(bundle.size_estimate)}. Token estimate: {String(bundle.token_estimate)}</li>
              <li>Provider execution: {String(bundle.provider_execution)}</li>
            </ul>
            {Array.isArray(bundle.excluded_for_token_budget) && bundle.excluded_for_token_budget.length > 0 && (
              <ul>
                {bundle.excluded_for_token_budget.map((item) => {
                  const row = item as { code?: string; slug?: string; name?: string; reason_excluded?: string };
                  return <li key={`${row.code ?? row.slug ?? row.name}`}>{row.code ?? row.slug ?? row.name}: {row.reason_excluded}</li>;
                })}
              </ul>
            )}
            {Array.isArray(bundle.skill_versions) && bundle.skill_versions.map((skill) => {
              const row = skill as { slug: string; version: string; content?: string; reason_included: string; authority: string };
              return (
                <div key={row.slug}>
                  <button type="button" onClick={() => setOpenSkill(openSkill === row.slug ? null : row.slug)}>
                    {row.slug} {row.version}
                  </button>
                  {openSkill === row.slug && <pre>{row.content}</pre>}
                  <p className="muted">{row.reason_included}. {row.authority}.</p>
                </div>
              );
            })}
          </>
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
