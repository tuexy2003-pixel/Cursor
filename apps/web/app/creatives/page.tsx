"use client";

import { useEffect, useState } from "react";
import { apiGet } from "../../lib/api";

type Creative = { id: string; name: string; status: string; holdout: boolean; slug: string };

export default function CreativesPage() {
  const [rows, setRows] = useState<Creative[]>([]);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    apiGet<Creative[]>("/creatives").then(setRows).catch((err: Error) => setError(err.message));
  }, []);
  return (
    <>
      <h1>Creatives</h1>
      {error && <p className="error">{error}</p>}
      <table>
        <thead><tr><th>Name</th><th>Status</th><th>Holdout</th></tr></thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              <td><a href={`/creatives/${row.id}`}>{row.name}</a></td>
              <td>{row.status}</td>
              <td>{row.holdout ? "yes" : "no"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
