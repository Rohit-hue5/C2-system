# pipelines/training_pipeline.py

from models.trainer import Trainer
from models.rl_evasion_trainer import RLEvasionTrainer
from core.logger import log
import threading


def run_training_pipeline(config: dict):
    """Complete ML training pipeline (non-blocking RL)"""

    log(f"[PIPELINE] Starting training | config={config}")

    # ─────────────────────────────
    # STEP 1: BASE TRAINING
    # ─────────────────────────────
    trainer = Trainer()
    task_id = trainer.start_training(config)

    log(f"[PIPELINE] Base training started | task_id={task_id}")

    # ─────────────────────────────
    # STEP 2–4: RUN RL + EVAL IN BACKGROUND
    # ─────────────────────────────
    def rl_job():
        try:
            log("[RL] Evasion training started")

            episodes = config.get("episodes", 1000)

            evasion_trainer = RLEvasionTrainer()

            evasion_model = evasion_trainer.train(episodes)

            # ───────── SAVE MODEL ─────────
            model_path = "models/saved/final_agent.pkl"
            evasion_trainer.save(model_path)

            log(f"[RL] Model saved → {model_path}")

            # ───────── EVALUATION ─────────
            score = evasion_trainer.evaluate(evasion_model)

            log(f"[RL] Evaluation score = {score:.4f}")

            # ───────── STORE STATE ─────────
            try:
                from flask import current_app
                if hasattr(current_app, "state"):
                    current_app.state.set("models:current_score", score)
            except Exception as e:
                log(f"[STATE ERROR] {e}")

            log("[RL] Pipeline complete")

        except Exception as e:
            log(f"[RL ERROR] {e}")

    # Run RL in background
    thread = threading.Thread(target=rl_job)
    thread.start()

    return {
        "status": "started",
        "task_id": task_id,
        "message": "Training pipeline running (RL in background)"
    }
