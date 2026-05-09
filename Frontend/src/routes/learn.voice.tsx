import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { motion } from "framer-motion";
import confetti from "canvas-confetti";
import { WORDS } from "@/data/words";
import { Mascot } from "@/components/Mascot";
import { FloatingBackground } from "@/components/FloatingBackground";

export const Route = createFileRoute("/learn/voice")({
  head: () => ({ meta: [{ title: "My Voice — Beyond 21" }] }),
  component: Voice,
});

const TARGET = 20;

function speak(t: string) {
  if ("speechSynthesis" in window) {
    const u = new SpeechSynthesisUtterance(t);
    u.lang = "ar-TN";
    window.speechSynthesis.speak(u);
  }
}

function Voice() {
  const items = WORDS.concat(WORDS).concat(WORDS).slice(0, TARGET);
  const [recorded, setRecorded] = useState<Set<string>>(new Set());
  const [recordingId, setRecordingId] = useState<string | null>(null);

  function startRec(uid: string) {
    setRecordingId(uid);
    setTimeout(() => {
      setRecorded((s) => new Set(s).add(uid));
      setRecordingId(null);
      if (recorded.size + 1 >= TARGET) confetti({ particleCount: 200, spread: 100 });
    }, 1500);
  }

  const done = recorded.size >= TARGET;

  return (
    <main className="min-h-screen relative overflow-hidden">
      <FloatingBackground />

      <div className="relative z-10 flex items-center justify-between px-6 py-4">
        <Link to="/learn" className="rounded-full bg-white/80 backdrop-blur w-14 h-14 grid place-items-center text-2xl shadow-soft hover:scale-110 transition" aria-label="Back">⬅️</Link>
        <div className="bg-white/80 backdrop-blur rounded-full px-5 py-2 shadow-soft font-bold flex items-center gap-2">
          <span className="text-2xl">🎙️</span><span>My Voice</span>
        </div>
        <Link to="/" className="rounded-full bg-white/80 backdrop-blur w-14 h-14 grid place-items-center text-2xl shadow-soft hover:scale-110 transition" aria-label="Home">🏠</Link>
      </div>

      <section className="relative z-10 max-w-3xl mx-auto px-6 mt-4 pb-16">
        {done ? (
          <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} className="bg-white rounded-[3rem] p-12 text-center shadow-pop">
            <div className="text-8xl">🎉</div>
            <h1 className="text-4xl font-bold mt-4">Your voice is ready! 🌟</h1>
            <p className="text-muted-foreground mt-2">Beyond 21 knows your voice now!</p>
            <button onClick={() => setRecorded(new Set())} className="mt-6 rounded-full bg-primary text-primary-foreground px-6 py-3 font-bold">Record again</button>
          </motion.div>
        ) : (
          <>
            <div className="text-center mb-6">
              <div className="inline-flex items-center gap-3 bg-white rounded-full px-5 py-3 shadow-soft">
                <Mascot size={60} />
                <div className="text-left">
                  <div className="font-bold">Let's teach me your voice!</div>
                  <div className="text-xs text-muted-foreground">Tap 🔴 and say each word</div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-3xl p-4 shadow-soft mb-4">
              <div className="flex items-center justify-between text-sm font-semibold mb-2">
                <span>{recorded.size} / {TARGET} words recorded ✅</span>
                <span>{Math.round((recorded.size / TARGET) * 100)}%</span>
              </div>
              <div className="h-4 rounded-full bg-muted overflow-hidden relative">
                <motion.div className="h-full bg-gradient-celebrate" animate={{ width: `${(recorded.size / TARGET) * 100}%` }} />
                <span className="absolute right-2 top-1/2 -translate-y-1/2 text-lg">⭐</span>
              </div>
            </div>

            <div className="grid sm:grid-cols-2 gap-3" dir="rtl">
              {items.map((w, i) => {
                const uid = `${w.id}-${i}`;
                const isDone = recorded.has(uid);
                const isRec = recordingId === uid;
                return (
                  <div key={uid} className={`bg-white rounded-2xl p-4 shadow-soft flex items-center gap-3 ${isDone ? "ring-2 ring-happy" : ""}`}>
                    <div className="text-5xl">{w.emoji}</div>
                    <div className="flex-1">
                      <div className="font-arabic text-2xl font-bold">{w.ar}</div>
                    </div>
                    <button onClick={() => speak(w.ar)} className="w-10 h-10 rounded-full bg-sky text-white grid place-items-center" aria-label="Listen">🔊</button>
                    {isDone ? (
                      <button onClick={() => { const n = new Set(recorded); n.delete(uid); setRecorded(n); }} className="w-10 h-10 rounded-full bg-happy grid place-items-center text-xl" aria-label="Re-record">✅</button>
                    ) : (
                      <button onClick={() => startRec(uid)} disabled={!!recordingId} className={`w-10 h-10 rounded-full grid place-items-center text-xl ${isRec ? "bg-destructive animate-breathe" : "bg-destructive/80 hover:scale-110"}`} aria-label="Record">
                        {isRec ? "⏺️" : "🔴"}
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </>
        )}
      </section>
    </main>
  );
}
