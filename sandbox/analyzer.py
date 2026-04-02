# sandbox/analyzer.py

from core.logger import log


class SandboxAnalyzer:

    # ─────────────────────────────
    # 🎯 Extract detection score
    # ─────────────────────────────
    def extract_detection(self, result):
        try:
            engines = result.get("engines", {})

            total = len(engines)
            detected = sum(1 for e in engines.values() if e.get("detected"))

            score = detected / total if total > 0 else 1.0

            log(f"Detection score: {score:.2f}")
            return score

        except Exception as e:
            log(f"Detection parsing error: {e}")
            return 1.0

    # ─────────────────────────────
    # 📊 Extract metadata
    # ─────────────────────────────
    def extract_metadata(self, result):
        return {
            "file_type": result.get("file_type"),
            "size": result.get("size"),
            "entropy": result.get("entropy"),
            "imports": result.get("imports", [])
        }

    # ─────────────────────────────
    # 🧠 RL Reward
    # ─────────────────────────────
    def compute_reward(self, detection_score):
        reward = 1.0 - detection_score

        log(f"Reward computed: {reward:.2f}")
        return reward
