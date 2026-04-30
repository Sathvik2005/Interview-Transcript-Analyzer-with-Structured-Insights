type InputBoxProps = {
  transcript: string;
  setTranscript: (value: string) => void;
  onAnalyze: () => void;
  onFileUpload: (file: File | null) => void;
  isLoading: boolean;
};

export function InputBox({ transcript, setTranscript, onAnalyze, onFileUpload, isLoading }: InputBoxProps) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-halo backdrop-blur-xl">
      <div className="mb-5 flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.24em] text-brand-200">Transcript Input</p>
          <h2 className="mt-2 text-xl font-semibold text-white">Paste text or upload a `.txt` file</h2>
        </div>
        <label className="cursor-pointer rounded-2xl border border-brand-400/30 bg-brand-500/10 px-4 py-2 text-sm font-medium text-brand-100 transition hover:border-brand-300/60 hover:bg-brand-500/20">
          Upload
          <input
            type="file"
            accept=".txt,text/plain"
            className="hidden"
            onChange={(event) => onFileUpload(event.target.files?.[0] ?? null)}
          />
        </label>
      </div>

      <textarea
        value={transcript}
        onChange={(event) => setTranscript(event.target.value)}
        placeholder="Paste an interview transcript here..."
        className="min-h-[320px] w-full rounded-3xl border border-white/10 bg-ink-950/60 p-5 text-sm leading-6 text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-brand-300/50 focus:ring-2 focus:ring-brand-500/20"
      />

      <div className="mt-5 flex items-center justify-between gap-4">
        <p className="text-xs text-slate-400">The backend returns strict JSON and falls back to “Not enough evidence” when needed.</p>
        <button
          type="button"
          onClick={onAnalyze}
          disabled={isLoading || transcript.trim().length === 0}
          className="inline-flex items-center justify-center rounded-2xl bg-brand-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-brand-600/30 transition hover:bg-brand-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isLoading ? 'Analyzing...' : 'Analyze transcript'}
        </button>
      </div>
    </div>
  );
}
