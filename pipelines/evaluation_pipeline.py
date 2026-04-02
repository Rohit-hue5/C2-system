# pipelines/evaluation_pipeline.py

from models.rl_evasion_trainer import RLEvasionTrainer
from core.logger import log


def run_evaluation(config: dict = None):
    """Evaluate trained RL model"""

    log("[EVAL] Starting evaluation pipeline")

    try:
        trainer = RLEvasionTrainer()

        episodes = 100
        if config and "episodes" in config:
            episodes = config["episodes"]

        score = trainer.evaluate(episodes=episodes)

        log(f"[EVAL] Completed | score={score:.4f}")

        return {
            "score": score,
            "episodes": episodes
        }

    except Exception as e:
        log(f"[EVAL ERROR] {e}")

        return {
            "error": str(e),
            "score": 0
        }
