# core/schedular.py

from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from typing import Callable, Dict, Any


class SchedulerManager:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.jobs = {}

    # ───────── INIT ─────────
    def init_app(self, app):
        """Initialize scheduler with Flask app"""

        self.scheduler.start()

        # Attach safely to app (NO current_app misuse)
        app.scheduler = self

        # Pause initially (your original logic)
        self.scheduler.pause()

        # Graceful shutdown
        atexit.register(self.shutdown)

    # ───────── JOB MANAGEMENT ─────────
    def add_job(self, job_id: str, func: Callable, **kwargs):
        """Add scheduled job"""

        if job_id in self.jobs:
            self.remove_job(job_id)

        job = self.scheduler.add_job(
            func,
            id=job_id,
            **kwargs
        )

        self.jobs[job_id] = job
        return job

    def remove_job(self, job_id: str):
        """Remove scheduled job"""

        if job_id in self.jobs:
            try:
                self.scheduler.remove_job(job_id)
            except Exception:
                pass
            del self.jobs[job_id]

    # ───────── CONTROL ─────────
    def start(self):
        """Start scheduler"""
        self.scheduler.resume()

    def pause(self):
        """Pause scheduler"""
        self.scheduler.pause()

    # ───────── STATUS ─────────
    def get_jobs(self) -> Dict[str, Any]:
        """Get all job info"""

        result = {}

        for job_id, job in self.jobs.items():
            result[job_id] = {
                "next_run_time": str(job.next_run_time),
                "trigger": str(job.trigger)
            }

        return result

    # ───────── SHUTDOWN ─────────
    def shutdown(self):
        """Shutdown scheduler safely"""

        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=False)
        except Exception:
            pass
