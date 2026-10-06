"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiGet } from "../../../lib/api";

export default function SkillPage() {
  const params = useParams<{ slug: string }>();
  const [body, setBody] = useState<{ status: string; content: string; content_hash: string } | null>(null);
  useEffect(() => {
    apiGet<{ status: string; content: string; content_hash: string }>(`/policies/skills/${params.slug}`).then(setBody);
  }, [params.slug]);
  if (!body) return <p>Loading…</p>;
  return (
    <>
      <h1>{params.slug}</h1>
      <p className="muted">{body.status}. {body.content_hash}</p>
      <pre style={{ whiteSpace: "pre-wrap" }}>{body.content}</pre>
    </>
  );
}
