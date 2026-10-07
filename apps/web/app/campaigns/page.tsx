"use client";

import { useEffect, useState } from "react";
import { apiGet } from "../../lib/api";

export default function CampaignsPage() {
  const [rows, setRows] = useState<{ id: string; name: string; notes: string | null }[]>([]);
  useEffect(() => {
    apiGet<typeof rows>("/campaigns").then(setRows).catch(() => setRows([]));
  }, []);
  return (
    <>
      <h1>Campaigns</h1>
      {rows.map((row) => (
        <section className="card" key={row.id}>
          <h2>{row.name}</h2>
          <p>{row.notes}</p>
        </section>
      ))}
    </>
  );
}
