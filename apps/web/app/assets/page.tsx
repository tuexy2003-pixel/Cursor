"use client";

import { useEffect, useState } from "react";
import { apiGet } from "../../lib/api";

type Asset = { id: string; name: string; role: string; rights_status: string; stale: boolean; present_in_snapshot: boolean; original_path: string };

export default function AssetsPage() {
  const [rows, setRows] = useState<Asset[]>([]);
  useEffect(() => { apiGet<Asset[]>("/assets").then(setRows).catch(() => setRows([])); }, []);
  return (
    <>
      <h1>Assets and provenance</h1>
      <p className="muted">Core handoff binaries are absent. Paths are historical provenance, not local files.</p>
      <table>
        <thead><tr><th>Name</th><th>Role</th><th>Rights</th><th>Stale</th><th>In snapshot</th></tr></thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}><td>{row.name}</td><td>{row.role}</td><td>{row.rights_status}</td><td>{row.stale ? "yes" : "no"}</td><td>{row.present_in_snapshot ? "yes" : "no"}</td></tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
