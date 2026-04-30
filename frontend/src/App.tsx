import { useMemo, useState } from 'react';
import { InputBox } from './components/InputBox';
import { Loader } from './components/Loader';
import { ResultCard } from './components/ResultCard';
import { analyzeTranscript, type AnalysisResponse } from './lib/api';

const sampleHint = 'Upload a transcript or paste one of the sample interview files to see the structured summary.';

export default function App() {
  const [transcript, setTranscript] = useState('');
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const wordCount = useMemo(() => transcript.trim().split(/\s+/).filter(Boolean).length, [transcript]);

  async function handleFileUpload(file: File | null) {
    if (!file) {
      return;
    }

    const text = await file.text();
    setTranscript(text);
    setError('');
    setResult(null);
  }

  async function handleAnalyze() {
    if (!transcript.trim()) {
      setError('Please paste or upload a transcript first.');
      return;
    }

    setError('');
    setIsLoading(true);
    setResult(null);

    try {
      const analysis = await analyzeTranscript(transcript);
      setResult(analysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unexpected error while analyzing transcript.');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.26),_transparent_30%),linear-gradient(180deg,#07111f_0%,#0b1730_55%,#060c18_100%)] text-white">
      <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-4 py-8 sm:px-6 lg:px-8">
        <header className="mb-8 grid gap-4 rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-halo backdrop-blur-xl lg:grid-cols-[1.2fr_0.8fr] lg:items-end">
          <div>
            <p className="text-sm font-medium uppercase tracking-[0.28em] text-brand-200">AI Interview Analyzer</p>
            <h1 className="mt-3 text-4xl font-semibold tracking-tight sm:text-5xl">Structured transcript summaries for interview debriefs</h1>
            <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-300 sm:text-base">
              Paste a transcript, upload a text file, and get a grounded evaluation with topics covered, profile fit, and a concise candidate summary.
            </p>
          </div>

          <div className="grid gap-3 rounded-3xl border border-brand-400/20 bg-brand-500/10 p-5 text-sm text-slate-200">
            <div className="flex items-center justify-between gap-3">
              <span className="text-slate-400">Transcript length</span>
              <span className="font-semibold text-white">{wordCount} words</span>
            </div>
            <div className="flex items-center justify-between gap-3">
              <span className="text-slate-400">Backend</span>
              <span className="font-semibold text-white">FastAPI + LLM provider switch</span>
            </div>
            <div className="flex items-center justify-between gap-3">
              <span className="text-slate-400">Mode</span>
              <span className="font-semibold text-white">JSON-first structured output</span>
            </div>
          </div>
        </header>

        <section className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
          <div className="space-y-4">
            <InputBox
              transcript={transcript}
              setTranscript={(value) => {
                setTranscript(value);
                setError('');
              }}
              onAnalyze={handleAnalyze}
              onFileUpload={handleFileUpload}
              isLoading={isLoading}
            />

            {error ? (
              <div className="rounded-3xl border border-rose-400/20 bg-rose-500/10 p-4 text-sm text-rose-100">
                {error}
              </div>
            ) : null}

            <div className="rounded-3xl border border-white/10 bg-white/5 p-5 text-sm leading-7 text-slate-300">
              <p className="font-semibold text-white">What this does</p>
              <p className="mt-2">{sampleHint}</p>
            </div>
          </div>

          <div>{isLoading ? <Loader /> : result ? <ResultCard result={result} /> : <EmptyState />}</div>
        </section>
      </div>
    </main>
  );
}

function EmptyState() {
  return (
    <div className="rounded-3xl border border-dashed border-white/15 bg-white/5 p-10 text-center shadow-halo">
      <div className="mx-auto max-w-md">
        <div className="mx-auto mb-4 h-14 w-14 rounded-2xl bg-brand-500/15 ring-1 ring-brand-300/20" />
        <h2 className="text-xl font-semibold text-white">Results appear here</h2>
        <p className="mt-3 text-sm leading-7 text-slate-300">
          Once you analyze a transcript, this panel will show the topic list, candidate profile, summary paragraph, and raw JSON.
        </p>
      </div>
    </div>
  );
}
