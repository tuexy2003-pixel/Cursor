"use client";

import { useEffect, useState } from "react";
import { apiGet } from "../../lib/api";

type Payload = {
  skills: {
    slug: string;
    name: string;
    versions: { version_label: string; status: string; content_hash: string; is_current: boolean }[];
  }[];
  rules: { code: string; scope_level: string; rule_kind: string; title: string; status: string }[];
};

export default function PoliciesPage() {
  const [data, setData] = useState<Payload | null>(null);
  useEffect(() => { apiGet<Payload>("/policies").then(setData).catch(() => setData(null)); }, []);
  return (
    <>
      <h1>Skills and rules</h1>
      <p className="muted">Imported Markdown is the policy. Scope and kind stay visible.</p>
      <table>
        <thead><tr><th>Skill</th><th>Current version</th><th>Status</th><th>Hash</th></tr></thead>
        <tbody>
          {data?.skills.map((skill) => {
            const current = skill.versions.find((version) => version.is_current) ?? skill.versions[0];
            return (
              <tr key={skill.slug}>
                <td><a href={`/policies/${skill.slug}`}>{skill.name}</a></td>
                <td>{current?.version_label}</td>
                <td>{current?.status}</td>
                <td>{current?.content_hash.slice(0, 12)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <h2>Scoped rules</h2>
      <table>
        <thead><tr><th>Code</th><th>Scope</th><th>Kind</th><th>Status</th><th>Text</th></tr></thead>
        <tbody>
          {data?.rules.map((rule) => (
            <tr key={`${rule.code}-${rule.scope_level}-${rule.status}`}>
              <td>{rule.code}</td><td>{rule.scope_level}</td><td>{rule.rule_kind}</td><td>{rule.status}</td><td>{rule.title}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
