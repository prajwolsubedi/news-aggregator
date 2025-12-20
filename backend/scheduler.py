import logging
import os
from typing import Optional

from apscheduler.schedulers.blocking import BlockingScheduler


def _run_pipeline() -> None:
    """Entry point for the scheduled job.

    This function lazily imports and executes the pipeline runner to avoid
    hard import failures if `run_pipeline.py` has not been created yet.
    """
    try:
        import run_pipeline  # type: ignore[import]
    except ImportError:
        logging.error(
            "run_pipeline module not found. Ensure `run_pipeline.py` exists "
            "with a callable `main()` before running the scheduler."
        )
        return

    if hasattr(run_pipeline, "main") and callable(getattr(run_pipeline, "main")):
        logging.info("Starting daily pipeline run...")
        try:
            run_pipeline.main()
            logging.info("Daily pipeline run completed successfully.")
        except Exception as exc:  # noqa: BLE001
            logging.exception("Daily pipeline run failed: %s", exc)
    else:
        logging.error(
            "`run_pipeline` module does not expose a callable `main()` function."
        )


def _create_scheduler(timezone: Optional[str] = None) -> BlockingScheduler:
    """Create and configure the APScheduler instance.

    By default, the scheduler uses the server's local timezone. A specific
    timezone (e.g. \"UTC\") can be provided if desired.
    """
    scheduler = BlockingScheduler(timezone=timezone)

    # Run every day at 9am Nepal time (3:15am UTC)
    # Nepal Standard Time is UTC+5:45
    scheduler.add_job(
        _run_pipeline,
        "cron",
        hour=3,
        minute=15,
        id="daily_pipeline",
        replace_existing=True,
    )

    return scheduler


def main() -> None:
    """Initialize logging and start the scheduler."""
    log_level = os.getenv("SCHEDULER_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )

    tz = os.getenv("SCHEDULER_TIMEZONE") or None

    scheduler = _create_scheduler(timezone=tz)

    logging.info("Starting APScheduler for daily pipeline at 9am Nepal time (3:15am UTC)...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler received shutdown signal, stopping...")
        scheduler.shutdown(wait=True)
        logging.info("Scheduler stopped cleanly.")


if __name__ == "__main__":
    main()


