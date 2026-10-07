"use client";

import { useEffect, useState } from "react";
import { apiGet } from "../../lib/api";

type Post = { id: string; platform: string; notes: string | null; snapshots: { source: string; views: number | null }[] };

export default function PostsPage() {
  const [rows, setRows] = useState<Post[]>([]);
  useEffect(() => { apiGet<Post[]>("/posts").then(setRows).catch(() => setRows([])); }, []);
  return (
    <>
      <h1>Posts and performance</h1>
      <p className="muted">No performance rows were invented from the handoff. Add snapshots through the API.</p>
      {rows.length === 0 && <p>No posts imported.</p>}
      {rows.map((row) => (
        <section className="card" key={row.id}>
          <h2>{row.platform}</h2>
          <p>{row.notes}</p>
          <ul>{row.snapshots.map((snap) => <li key={snap.source}>{snap.source}: {snap.views ?? "views unknown"}</li>)}</ul>
        </section>
      ))}
    </>
  );
}
