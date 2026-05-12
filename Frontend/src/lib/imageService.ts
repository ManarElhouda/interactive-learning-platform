/**
 * imageService.ts
 * ───────────────
 * Appels au backend FastAPI pour le pipeline Speech-to-Vision.
 * À placer dans : src/lib/imageService.ts
 */

import { getApiUrl } from "./api";

const HEADERS = { "ngrok-skip-browser-warning": "true" };

// ── Types ──────────────────────────────────────────────────────────────────────

export interface FullPipelineResponse {
  transcription: string;   // texte arabe tunisien (Whisper)
  french: string;          // traduction intermédiaire FR
  english: string;         // traduction finale EN
  prompt: string;          // prompt SDXL enrichi
  negative_prompt: string;
  image_b64: string;       // image PNG en base64
  image_url: string;       // URL Pollinations (debug)
  latency_translation: number;
  latency_prompt: number;
  latency_image: number;
  latency_total: number;
  status: string;
}

export interface FeedbackRequest {
  child_id: string;
  transcription: string;
  translation: string;
  prompt: string;
  feedback: "positive" | "neutral" | "negative";
  feedback_note?: string;
}

// ── Pipeline complet : transcription → traduction → image ─────────────────────

export async function runFullPipeline(
  transcription: string,
  childId: string = "child_001"
): Promise<FullPipelineResponse> {
  const base = getApiUrl();
  if (!base) throw new Error("API URL non configurée — va dans Parent Dashboard > Settings");

  const res = await fetch(`${base}/api/pipeline/full`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...HEADERS,
    },
    body: JSON.stringify({
      transcription,
      child_id: childId,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Pipeline échoué : ${res.status}`);
  }

  return res.json();
}

// ── Feedback utilisateur ──────────────────────────────────────────────────────

export async function sendFeedback(feedback: FeedbackRequest): Promise<void> {
  const base = getApiUrl();
  if (!base) return;

  await fetch(`${base}/api/pipeline/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...HEADERS },
    body: JSON.stringify(feedback),
  }).catch(() => {});   // feedback non bloquant
}

// ── Utilitaire ────────────────────────────────────────────────────────────────

export function base64ToImageSrc(base64: string): string {
  return `data:image/png;base64,${base64}`;
}
