import { useMemo, useState } from 'react';
import type { AnalysisResponse } from '../lib/api';

type ResultCardProps = {
  result: AnalysisResponse;
};

export function ResultCard({ result }: ResultCardProps) {
  const [copied, setCopied] = useState(false);

  const jsonText = useMemo(() => JSON.stringify(result, null, 2), [result]);

  async function handleCopy() {
    await navigator.clipboard.writeText(jsonText);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1200);
  }

  return (
    <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-halo backdrop-blur-xl animate-rise">
      <div className="mb-6 flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.24em] text-brand-200">Structured Output</p>
          <h2 className="mt-2 text-xl font-semibold text-white">Candidate evaluation</h2>
        </div>
        <button
          type="button"
          onClick={handleCopy}
          className="rounded-2xl border border-white/10 bg-slate-900/70 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-brand-300/40 hover:text-white"
        >
          {copied ? 'Copied' : 'Copy JSON'}
        </button>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-3xl border border-white/10 bg-ink-950/60 p-5">
          <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Topics Covered</h3>
          <div className="mt-4 flex flex-wrap gap-2">
            {result.topics_covered.length > 0 ? (
              result.topics_covered.map((topic) => (
                <span key={topic} className="rounded-full border border-brand-400/25 bg-brand-500/10 px-3 py-1 text-sm text-brand-100">
                  {topic}
                </span>
              ))
            ) : (
              <span className="text-sm text-slate-400">Not enough evidence</span>
            )}
          </div>

          <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-4">
            <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Candidate Summary</h3>
            <p className="mt-3 text-sm leading-7 text-slate-200">{result.candidate_summary}</p>
          </div>
        </section>

        <aside className="space-y-4">
          <div className="rounded-3xl border border-brand-400/20 bg-brand-500/10 p-5">
            <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-100">Profile</h3>
            <div className="mt-4 space-y-3">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Role</p>
                <p className="mt-1 text-lg font-semibold text-white">{result.profile.role}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Level</p>
                <p className="mt-1 text-lg font-semibold text-white">{result.profile.level}</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Justification</p>
                <p className="mt-1 text-sm leading-6 text-slate-100">{result.profile.justification}</p>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-5">
            <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Raw JSON</h3>
            <pre className="mt-3 max-h-[300px] overflow-auto text-xs leading-6 text-slate-300">{jsonText}</pre>
          </div>
        </aside>
      </div>
    </div>
  );
}
