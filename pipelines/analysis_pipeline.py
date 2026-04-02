# pipelines/analysis_pipeline.py

from analysis import analyzer, scoring
from core.logger import log


async def run_analysis_pipeline(samples: list):
    """Complete analysis pipeline"""

    results = []

    for sample in samples:
        try:
            sample_hash = sample.get("hash")

            log(f"Analyzing sample: {sample_hash}")

            analysis = await analyzer.analyze(sample_hash)
            score = scoring.score_analysis(analysis)

            results.append({
                "sample": sample,
                "score": score
            })

        except Exception as e:
            log(f"Analysis error: {e}")
            results.append({
                "sample": sample,
                "error": str(e)
            })

    return results
