"use client";

import { useEffect, useState } from "react";
import { apiGet } from "../../lib/api";

type Payload = {
  skills: { slug: string; name: string; versions: { status: string; content_hash: string; source_path: string }[] }[];
  rules: { code: string; scope_level: string; rule_kind: string; title: string }[];
};

export default function PoliciesPage() {
  const [data, setData] = useState<Payload | null>(null);
  useEffect(() => { apiGet<Payload>("/policies").then(setData).catch(() => setData(null)); }, []);
  return (
    <>
      <h1>Skills and rules</h1>
      <p className="muted">Imported Markdown is the policy. Scope and kind stay visible.</p>
      <table>
        <thead><tr><th>Skill</th><th>Status</th><th>Hash</th></tr></thead>
        <tbody>
          {data?.skills.map((skill) => (
            <tr key={skill.slug}>
              <td><a href={`/policies/${skill.slug}`}>{skill.name}</a></td>
              <td>{skill.versions[0]?.status}</td>
              <td>{skill.versions[0]?.content_hash.slice(0, 12)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <h2>Scoped rules</h2>
      <table>
        <thead><tr><th>Code</th><th>Scope</th><th>Kind</th><th>Text</th></tr></thead>
        <tbody>
          {data?.rules.map((rule) => (
            <tr key={rule.code}><td>{rule.code}</td><td>{rule.scope_level}</td><td>{rule.rule_kind}</td><td>{rule.title}</td></tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
