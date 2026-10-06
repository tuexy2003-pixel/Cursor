"use client";

import { useEffect, useState } from "react";
import { apiGet } from "../lib/api";

export default function HomePage() {
  const [summary, setSummary] = useState<Record<string, number> | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    apiGet<Record<string, number>>("/summary").then(setSummary).catch((err: Error) => setError(err.message));
  }, []);
  return (
    <>
      <h1>Creative OS</h1>
      <p className="muted">
        The current approved story lock wins for creative values. Active skills govern behavior.
        Reference evidence governs native visual structure.
      </p>
      {error && <p className="error">{error}. Start the API, then import the handoff.</p>}
      {summary && (
        <table>
          <tbody>
            {Object.entries(summary).map(([key, value]) => (
              <tr key={key}>
                <th>{key}</th>
                <td>{value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}
