import { createFileRoute, Link } from "@tanstack/react-router";
import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import confetti from "canvas-confetti";
import { WORDS, type Word } from "@/data/words";
import { Mascot } from "@/components/Mascot";
import { FloatingBackground } from "@/components/FloatingBackground";

export const Route = createFileRoute("/learn/picture")({
  head: () => ({ meta: [{ title: "Show Me a Picture — Beyond 21" }] }),
  component: Picture,
});

type Status = "idle" | "listening" | "processing" | "result" | "fail";

function Picture() {
  const [status, setStatus] = useState<Status>("idle");
  const [recognized, setRecognized] = useState<Word | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  function speak(text: string) {
    if ("speechSynthesis" in window) {
      const u = new SpeechSynthesisUtterance(text);
      u.lang = "ar-TN";
      window.speechSynthesis.speak(u);
    }
  }

  function handleMic() {
    if (timerRef.current) clearTimeout(timerRef.current);
    setStatus("listening");
    setRecognized(null);
    timerRef.current = setTimeout(() => {
      setStatus("processing");
      timerRef.current = setTimeout(() => {
        const ok = Math.random() > 0.15;
        if (ok) {
          const w = WORDS[Math.floor(Math.random() * WORDS.length)];
          setRecognized(w);
          setStatus("result");
          confetti({ particleCount: 60, spread: 70, origin: { y: 0.5 } });
        } else {
          setStatus("fail");
        }
      }, 1200);
    }, 1500);
  }

  return (
    <main className="min-h-screen relative overflow-hidden">
      <FloatingBackground />

      <div className="relative z-10 flex items-center justify-between px-6 py-4">
        <Link to="/learn" className="rounded-full bg-white/80 backdrop-blur w-14 h-14 grid place-items-center text-2xl shadow-soft hover:scale-110 transition" aria-label="Back">⬅️</Link>
        <div className="bg-white/80 backdrop-blur rounded-full px-5 py-2 shadow-soft font-bold flex items-center gap-2">
          <span className="text-2xl">🎨</span><span>Show Me a Picture</span>
        </div>
        <Link to="/" className="rounded-full bg-white/80 backdrop-blur w-14 h-14 grid place-items-center text-2xl shadow-soft hover:scale-110 transition" aria-label="Home">🏠</Link>
      </div>

      <section className="relative z-10 max-w-2xl mx-auto px-6 mt-6 text-center">
        {status === "idle" && (
          <div>
            <Mascot size={140} />
            <div className="mt-6 flex items-center justify-center gap-4 text-5xl">
              <span>👄</span><span className="text-3xl">→</span><span>🎤</span><span className="text-3xl">→</span><span>🖼️</span>
            </div>
            <p className="mt-4 text-2xl font-bold">Say a word! 🎤</p>
          </div>
        )}

        <AnimatePresence mode="wait">
          {status === "result" && recognized && (
            <motion.div
              key={recognized.id}
              initial={{ scale: 0, rotate: -10 }}
              animate={{ scale: 1, rotate: 0 }}
              exit={{ scale: 0 }}
              transition={{ type: "spring", duration: 0.7 }}
              className="rounded-[3rem] bg-white shadow-pop p-8 md:p-12 relative overflow-hidden"
              dir="rtl"
            >
              <div className="absolute inset-0 bg-gradient-celebrate opacity-15" />
              <motion.div animate={{ y: [0, -10, 0] }} transition={{ duration: 3, repeat: Infinity }} className="text-[12rem] leading-none relative">
                {recognized.emoji}
              </motion.div>
              <div className="font-arabic text-6xl font-black mt-2 relative">{recognized.ar}</div>
              <button onClick={() => speak(recognized.ar)} className="mt-4 inline-flex items-center gap-2 rounded-full bg-sky text-white px-6 py-3 shadow-soft hover:scale-110 transition relative" aria-label="Hear">
                <span className="text-2xl">🔊</span>
              </button>
            </motion.div>
          )}

          {status === "fail" && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-white rounded-[3rem] p-10 shadow-pop">
              <div className="text-7xl">🤷</div>
              <p className="mt-4 text-xl font-bold">I missed that! Let's try again 💛</p>
              <button onClick={() => setStatus("idle")} className="mt-4 rounded-full bg-sunny px-8 py-4 text-xl font-bold shadow-soft hover:scale-105 transition">🔄 Try again!</button>
            </motion.div>
          )}

          {status === "processing" && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="py-12">
              <div className="relative inline-block">
                <Mascot mood="thinking" size={140} />
                <motion.div className="absolute -top-4 -right-4 text-5xl" animate={{ scale: [1, 1.3, 1] }} transition={{ duration: 1, repeat: Infinity }}>💡</motion.div>
              </div>
              <p className="mt-4 text-xl font-bold">Thinking… 💭</p>
            </motion.div>
          )}

          {status === "listening" && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="py-12">
              <div className="text-2xl font-bold">I'm listening… 🌈</div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="mt-10 flex justify-center">
          <div className="relative">
            {status === "listening" && (
              <>
                <span className="absolute inset-0 rounded-full bg-bubble animate-ripple" />
                <span className="absolute inset-0 rounded-full bg-mint animate-ripple" style={{ animationDelay: "0.3s" }} />
              </>
            )}
            <button
              onClick={handleMic}
              disabled={status === "listening" || status === "processing"}
              aria-label="Speak"
              className="relative w-32 h-32 rounded-full bg-gradient-celebrate text-white text-5xl shadow-pop grid place-items-center hover:scale-110 active:scale-95 transition animate-breathe disabled:animate-none"
            >
              {status === "processing" ? "🎧" : "🎤"}
            </button>
          </div>
        </div>
      </section>
    </main>
  );
}
