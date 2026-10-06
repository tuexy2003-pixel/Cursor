"use client";

import { useEffect, useState } from "react";
import { apiGet } from "../../lib/api";

type Benchmark = { name: string; category: string | null; views: number | null; holdout: boolean; metrics_note: string | null };
type Regression = { code: string; evaluation_mode: string; expected_decision: string };

export default function BenchmarksPage() {
  const [benchmarks, setBenchmarks] = useState<Benchmark[]>([]);
  const [tests, setTests] = useState<Regression[]>([]);
  useEffect(() => {
    apiGet<Benchmark[]>("/benchmarks").then(setBenchmarks).catch(() => setBenchmarks([]));
    apiGet<Regression[]>("/regression-tests").then(setTests).catch(() => setTests([]));
  }, []);
  return (
    <>
      <h1>Benchmarks and regression tests</h1>
      <table>
        <thead><tr><th>Benchmark</th><th>Category</th><th>Views</th><th>Holdout</th></tr></thead>
        <tbody>
          {benchmarks.map((row) => (
            <tr key={row.name}><td>{row.name}</td><td>{row.category ?? "UNKNOWN"}</td><td>{row.views ?? "UNKNOWN"}</td><td>{row.holdout ? "yes" : "no"}</td></tr>
          ))}
        </tbody>
      </table>
      <h2>Regression cases</h2>
      <table>
        <thead><tr><th>Code</th><th>Mode</th><th>Expected</th></tr></thead>
        <tbody>
          {tests.map((row) => (
            <tr key={row.code}><td>{row.code}</td><td>{row.evaluation_mode}</td><td>{row.expected_decision}</td></tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
