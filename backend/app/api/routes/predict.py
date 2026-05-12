"""
Beyond 21 – Adaptive Learning AI  |  predict.py
Production endpoint for Railway deployment.

Loads:
  - backend/app/models/dqn_model.h5   (TensorFlow/Keras DQN)
  - backend/app/models/fcm_model.pkl  (pickle — FCM / scaler)

Flow:
  raw student telemetry  →  T-I-F scoring (exact formulas from main.py)
  →  DQN inference  →  Safety Override Layer  →  response
"""

from __future__ import annotations

import logging
import pickle
from functools import lru_cache
from pathlib import Path

import numpy as np
import tensorflow as tf
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

log = logging.getLogger("AdaptiveLearningAPI")

# ─── Router ───────────────────────────────────────────────────────────────────
router = APIRouter(prefix="/api", tags=["predict"])

# ─── Model paths (relative to this file → Railway-safe, no hardcoded roots) ──
BASE_DIR   = Path(__file__).resolve().parents[3]   # → backend/
MODELS_DIR = BASE_DIR / "app" / "models"
DQN_PATH   = MODELS_DIR / "dqn_model.h5"
FCM_PATH   = MODELS_DIR / "fcm_model.pkl"

# ─── Action map (matches main.py exactly) ─────────────────────────────────────
ACTIONS: dict[int, str] = {
    0: "CONTINUE_LEVEL",
    1: "PROVIDE_HINT",
    2: "SENSORY_BREAK",
}

# ─── Lazy model loading (cached — loaded once per process) ────────────────────
@lru_cache(maxsize=1)
def _load_models() -> tuple[tf.keras.Model, object]:
    if not DQN_PATH.exists():
        raise FileNotFoundError(f"DQN model not found: {DQN_PATH}")
    if not FCM_PATH.exists():
        raise FileNotFoundError(f"FCM model not found: {FCM_PATH}")

    dqn = tf.keras.models.load_model(str(DQN_PATH), compile=False)

    with open(FCM_PATH, "rb") as f:
        fcm = pickle.load(f)

    log.info("Models loaded from %s", MODELS_DIR)
    return dqn, fcm


# ─── Pydantic schemas (StudentState fields match main.py exactly) ─────────────
class StudentState(BaseModel):
    response_time:      float
    error_rate:         float
    hesitation_count:   int
    focus_ratio:        float
    frustration_score:  float
    movement_intensity: float
    question_id:        int
    is_answering:       bool


class PredictionResponse(BaseModel):
    action_id:        int
    action_name:      str
    reason:           str
    T:                float
    I:                float
    F:                float
    dqn_action_id:    int
    override_applied: bool
    q_values:         dict
    confidence:       float
    question_id:      int
    is_answering:     bool


# ─── T-I-F scoring (exact formulas from main.py mock_features_to_state) ───────
def features_to_tif(state: StudentState) -> tuple[np.ndarray, float, float, float]:
    """
    Converts raw student telemetry into T, I, F scores in [0, 1].

    Formulas taken verbatim from main.py (mock_features_to_state):

        T = 1 - error_rate - (response_time / 60) - movement_intensity * 0.3
        I = (1 - focus_ratio)*0.5 + movement_intensity*0.3 + hes_norm*0.2
        F = clip(frustration_score, 0, 1)

    All values are clamped so safety-override thresholds do not misfire
    on noisy single frames (documented in original main.py comments).
    """
    mi = float(state.movement_intensity)

    # T: Tranquility — drops with errors, slow responses, and high movement
    T = 1.0 - state.error_rate - (state.response_time / 60.0) - mi * 0.3
    T = float(np.clip(T, 0.0, 1.0))

    # I: Ambiguity — rises with low focus, movement, many hesitations
    hes_norm = min(state.hesitation_count / 15.0, 1.0)   # normalise 0-15 → 0-1
    I = (1.0 - state.focus_ratio) * 0.5 + mi * 0.3 + hes_norm * 0.2
    I = float(np.clip(I, 0.0, 1.0))

    # F: Frustration — clamp so safety overrides do not misfire on bad frames
    F = float(np.clip(state.frustration_score, 0.0, 1.0))

    tif_array = np.array([[T, I, F]], dtype=np.float32)
    return tif_array, T, I, F


# ─── Safety Override Layer (verbatim from main.py get_action) ─────────────────
def get_action(T: float, I: float, F: float, dqn_action: int) -> tuple[int, str]:
    """
    Post-DQN safety override layer.
    Models the 'safe RL' paradigm where a learned policy (DQN) operates
    within hard clinical safety constraints.
    """
    # Override 1: Extreme frustration (F > 0.8) → Must Break
    if F > 0.8:
        return 2, f"Safety override: F={F:.2f} (extreme frustration). DQN suggested {dqn_action}."

    # Override 2: High ambiguity (I > 0.4) but DQN wants to Continue → Escalate to Hint
    if I > 0.4 and dqn_action == 0:
        return 1, f"Safety override: I={I:.2f} (high ambiguity). Escalating to Hint."

    # Override 3: Combined F and I elevation → Sensory Break
    if F > 0.6 and I > 0.5:
        return 2, f"Safety override: F={F:.2f} & I={I:.2f} elevated. Fatigue detected."

    # No override triggered: Trust the DQN
    return dqn_action, "DQN decision — no safety override triggered."


# ─── Endpoint ─────────────────────────────────────────────────────────────────
@router.post("/predict", response_model=PredictionResponse)
async def predict(state: StudentState) -> PredictionResponse:
    """
    Main adaptive-learning inference endpoint.

    1. Convert raw MediaPipe/session telemetry into T, I, F scores.
    2. Feed T-I-F to the real DQN model (.h5).
    3. Apply Safety Override Layer.
    4. Return action + full debug payload (matches QuizSession.jsx shape).
    """
    # ── Load models (cached after first request) ──────────────────────────────
    try:
        dqn, _fcm = _load_models()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    # ── Step 1: T-I-F scoring ─────────────────────────────────────────────────
    tif_array, T, I, F = features_to_tif(state)

    # ── Step 2: DQN inference ─────────────────────────────────────────────────
    # If fcm_model.pkl is a scikit-learn scaler, apply it before inference:
    #   tif_array = _fcm.transform(tif_array)
    try:
        q_vals_raw   = dqn.predict(tif_array, verbose=0)[0]   # shape: (3,)
        dqn_action   = int(np.argmax(q_vals_raw))
        confidence   = float(np.max(q_vals_raw))
        q_values_out = {
            "CONTINUE_LEVEL": round(float(q_vals_raw[0]), 4),
            "PROVIDE_HINT":   round(float(q_vals_raw[1]), 4),
            "SENSORY_BREAK":  round(float(q_vals_raw[2]), 4),
        }
    except Exception as exc:
        log.error("DQN inference failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Model inference failed: {exc}")

    # ── Step 3: Safety Override ───────────────────────────────────────────────
    final_action_id, reason = get_action(T, I, F, dqn_action)
    override_applied        = final_action_id != dqn_action
    action_name             = ACTIONS[final_action_id]

    log.info(
        "Q%s | T:%.2f I:%.2f F:%.2f | DQN:%s → Final:%s%s",
        state.question_id, T, I, F,
        ACTIONS[dqn_action], action_name,
        " [OVERRIDE]" if override_applied else "",
    )

    return PredictionResponse(
        action_id        = final_action_id,
        action_name      = action_name,
        reason           = reason,
        T                = round(T, 3),
        I                = round(I, 3),
        F                = round(F, 3),
        dqn_action_id    = dqn_action,
        override_applied = override_applied,
        q_values         = q_values_out,
        confidence       = round(confidence, 4),
        question_id      = state.question_id,
        is_answering     = state.is_answering,
    )


# ─── Health probe (Railway health check) ──────────────────────────────────────
@router.get("/predict/health")
async def health() -> dict:
    return {"status": "ok", "models_dir": str(MODELS_DIR)}