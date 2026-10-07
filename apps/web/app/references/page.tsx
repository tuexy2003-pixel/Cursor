"use client";

import { useEffect, useState } from "react";
import { apiGet } from "../../lib/api";

export default function ReferencesPage() {
  const [rows, setRows] = useState<{ id: string; name: string; original_path: string; notes: string | null }[]>([]);
  useEffect(() => { apiGet<typeof rows>("/references").then(setRows).catch(() => setRows([])); }, []);
  return (
    <>
      <h1>Reference banks</h1>
      {rows.map((row) => (
        <section className="card" key={row.id}>
          <h2>{row.name}</h2>
          <p>{row.original_path}</p>
          <p>{row.notes}</p>
        </section>
      ))}
    </>
  );
}
