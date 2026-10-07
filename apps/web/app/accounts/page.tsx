"use client";

import { useEffect, useState } from "react";
import { apiGet } from "../../lib/api";

type Observation = { field_name: string; value: string; evidence_kind: string; sample_size: number | null; notes: string | null };
type Account = { id: string; name: string; notes: string | null; dna: Observation[] };

export default function AccountsPage() {
  const [rows, setRows] = useState<Account[]>([]);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    apiGet<Account[]>("/accounts").then(setRows).catch((err: Error) => setError(err.message));
  }, []);
  return (
    <>
      <h1>Accounts</h1>
      <p className="muted">Lanes are human-set constraints. View counts are single historical observations.</p>
      {error && <p className="error">{error}</p>}
      {rows.map((row) => (
        <section className="card" key={row.id}>
          <h2>{row.name}</h2>
          <p>{row.notes}</p>
          <table>
            <thead>
              <tr><th>Field</th><th>Value</th><th>Kind</th><th>Sample</th></tr>
            </thead>
            <tbody>
              {row.dna.map((item) => (
                <tr key={item.field_name}>
                  <td>{item.field_name}</td>
                  <td>{item.value}</td>
                  <td>{item.evidence_kind}</td>
                  <td>{item.sample_size ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ))}
    </>
  );
}
