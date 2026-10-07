"use client";

import { useEffect, useState } from "react";
import { apiGet } from "../../lib/api";

type Payload = { doors: { id: string; kind: string; text: string }[]; clusters: { label: string; size: number; unexpected: boolean }[]; mappings: { relationship: string }[] };

export default function CommentsPage() {
  const [data, setData] = useState<Payload | null>(null);
  useEffect(() => { apiGet<Payload>("/comments").then(setData).catch(() => setData(null)); }, []);
  return (
    <>
      <h1>Comment doors</h1>
      <p className="muted">Predicted doors come from the story lock. Actual comments were not in the core archive.</p>
      <ul>{data?.doors.map((door) => <li key={door.id}>{door.kind}: {door.text}</li>)}</ul>
      <h2>Clusters</h2>
      {data && data.clusters.length === 0 && <p>No clusters yet.</p>}
    </>
  );
}
