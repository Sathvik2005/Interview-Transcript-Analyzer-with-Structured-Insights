export function Loader() {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-halo backdrop-blur-xl">
      <div className="space-y-4">
        <div className="h-4 w-40 rounded-full bg-gradient-to-r from-slate-700 via-slate-500 to-slate-700 bg-[length:200%_100%] animate-shimmer" />
        <div className="h-28 rounded-2xl bg-gradient-to-r from-slate-800 via-slate-700 to-slate-800 bg-[length:200%_100%] animate-shimmer" />
        <div className="grid gap-3 md:grid-cols-2">
          <div className="h-20 rounded-2xl bg-gradient-to-r from-slate-800 via-slate-700 to-slate-800 bg-[length:200%_100%] animate-shimmer" />
          <div className="h-20 rounded-2xl bg-gradient-to-r from-slate-800 via-slate-700 to-slate-800 bg-[length:200%_100%] animate-shimmer" />
        </div>
      </div>
    </div>
  );
}
