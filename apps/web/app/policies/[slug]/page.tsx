"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiGet } from "../../../lib/api";

export default function SkillPage() {
  const params = useParams<{ slug: string }>();
  const [body, setBody] = useState<{
    status: string;
    version_label: string;
    approval_state: string;
    content: string;
    content_hash: string;
  } | null>(null);
  useEffect(() => {
    apiGet<{
      status: string;
      version_label: string;
      approval_state: string;
      content: string;
      content_hash: string;
    }>(`/policies/skills/${params.slug}`).then(setBody);
  }, [params.slug]);
  if (!body) return <p>Loading…</p>;
  return (
    <>
      <h1>{params.slug}</h1>
      <p className="muted">{body.version_label}. {body.approval_state}. {body.status}. {body.content_hash}</p>
      <pre style={{ whiteSpace: "pre-wrap" }}>{body.content}</pre>
    </>
  );
}
