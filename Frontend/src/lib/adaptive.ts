// Adaptive Learning Controller — shared store for child exercise sessions
// and the parent dashboard "AI Adaptation" tab.

import { useEffect, useState } from "react";

export type LogEntry = { ts: number; icon: string; text: string };

export type AdaptiveState = {
  // Live sensor features (0–100)
  focus: number;
  movement: number;
  frustration: number;
  errorRate: number;
  // Session stats
  hesitations: number;
  avgResponseMs: number;
  // Neutrosophic logic scores (0–1)
  T: number;
  I: number;
  F: number;
  // Current AI decision
  decision: { text: string; icon: string };
  // Rolling log
  log: LogEntry[];
};

const initial: AdaptiveState = {
  focus: 78,
  movement: 32,
  frustration: 22,
  errorRate: 18,
  hesitations: 3,
  avgResponseMs: 2400,
  T: 0.72,
  I: 0.18,
  F: 0.1,
  decision: { text: "Monitoring session", icon: "👀" },
  log: [
    { ts: Date.now() - 60_000, icon: "🚀", text: "Session started" },
    { ts: Date.now() - 45_000, icon: "✅", text: "Correct answer — moving to next word" },
    { ts: Date.now() - 30_000, icon: "👀", text: "Focus lost — providing visual cue" },
    { ts: Date.now() - 15_000, icon: "💡", text: "Hint provided — showing reference image" },
  ],
};

let state: AdaptiveState = initial;
const subs = new Set<(s: AdaptiveState) => void>();

function set(next: Partial<AdaptiveState>) {
  state = { ...state, ...next };
  subs.forEach((fn) => fn(state));
}

function pushLog(icon: string, text: string) {
  const entry: LogEntry = { ts: Date.now(), icon, text };
  set({ log: [entry, ...state.log].slice(0, 30) });
}

function decideFromFeatures(): { text: string; icon: string } {
  const { frustration, errorRate, focus } = state;
  if (frustration > 70) return { text: "Sensory Break triggered", icon: "😴" };
  if (errorRate > 60 && focus > 50) return { text: "Hint provided", icon: "💡" };
  if (focus < 40) return { text: "Visual cue sent", icon: "👀" };
  if (errorRate < 20 && focus > 70) return { text: "Increasing difficulty", icon: "⬆️" };
  return { text: "Monitoring session", icon: "👀" };
}

function recomputeTIF() {
  // Simple mapping: T from focus & inverse-error, F from frustration & error,
  // I from movement variability + hesitations
  const T = Math.max(0, Math.min(1, (state.focus / 100) * 0.6 + (1 - state.errorRate / 100) * 0.4));
  const F = Math.max(0, Math.min(1, (state.frustration / 100) * 0.6 + (state.errorRate / 100) * 0.4));
  const I = Math.max(0, Math.min(1, (state.movement / 100) * 0.5 + Math.min(state.hesitations, 10) / 20));
  set({ T: +T.toFixed(2), I: +I.toFixed(2), F: +F.toFixed(2), decision: decideFromFeatures() });
}

export const adaptive = {
  get: () => state,
  subscribe(fn: (s: AdaptiveState) => void) {
    subs.add(fn);
    return () => { subs.delete(fn); };
  },
  recordCorrect(responseMs: number) {
    const focus = Math.min(100, state.focus + 3);
    const errorRate = Math.max(0, state.errorRate - 5);
    const frustration = Math.max(0, state.frustration - 4);
    const avg = Math.round((state.avgResponseMs + responseMs) / 2);
    set({ focus, errorRate, frustration, avgResponseMs: avg });
    pushLog("✅", "Correct answer — moving to next word");
    recomputeTIF();
  },
  recordWrong(responseMs: number) {
    const errorRate = Math.min(100, state.errorRate + 8);
    const frustration = Math.min(100, state.frustration + 6);
    const avg = Math.round((state.avgResponseMs + responseMs) / 2);
    set({ errorRate, frustration, avgResponseMs: avg });
    pushLog("❌", "Incorrect — adjusting difficulty");
    recomputeTIF();
  },
  recordHesitation() {
    set({ hesitations: state.hesitations + 1, focus: Math.max(0, state.focus - 4) });
    pushLog("⏳", "Hesitation detected — sending visual cue");
    recomputeTIF();
  },
  recordBreak() {
    set({ frustration: Math.max(0, state.frustration - 30), movement: Math.max(0, state.movement - 20) });
    pushLog("😴", "Sensory break started — 30 seconds");
    recomputeTIF();
  },
  recordStreak(n: number) {
    pushLog("⬆️", `${n} correct streak — increasing difficulty`);
    recomputeTIF();
  },
  recordHint() {
    pushLog("💡", "Hint provided — showing reference image");
    recomputeTIF();
  },
  recordCompletion(score: string) {
    pushLog("🎉", `Exercise completed — ${score}`);
    recomputeTIF();
  },
};

// Background drift so the parent dashboard always feels alive.
if (typeof window !== "undefined") {
  setInterval(() => {
    const jitter = (v: number, amt = 4) =>
      Math.max(0, Math.min(100, v + (Math.random() - 0.5) * amt));
    set({
      focus: jitter(state.focus),
      movement: jitter(state.movement, 6),
      frustration: jitter(state.frustration, 3),
      errorRate: jitter(state.errorRate, 2),
    });
    recomputeTIF();
  }, 2000);
}

export function useAdaptive() {
  const [s, setS] = useState<AdaptiveState>(state);
  useEffect(() => {
    const unsub = adaptive.subscribe(setS);
    return () => { unsub; };
  }, []);
  return s;
}

export function colorForScore(value: number, invert = false) {
  // invert=true means HIGH is BAD (frustration, errorRate, movement)
  const v = invert ? 100 - value : value;
  if (v >= 75) return "var(--happy)";
  if (v >= 50) return "var(--sunny)";
  if (v >= 25) return "var(--peach)";
  return "#ef4444";
}
