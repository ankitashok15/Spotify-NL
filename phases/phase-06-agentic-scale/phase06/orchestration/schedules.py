from celery.schedules import crontab

beat_schedule = {
    "daily-incremental-scrape": {
        "task": "phase06.orchestration.tasks.scrape.scrape_incremental",
        "schedule": crontab(hour=2, minute=0),
        "kwargs": {"limit": None},
    },
    "daily-pipeline-after-scrape": {
        "task": "phase06.orchestration.tasks.pipeline.run_incremental_pipeline",
        "schedule": crontab(hour=3, minute=30),
        "kwargs": {"extract_limit": 500, "embed_limit": 500, "assign_limit": 500},
    },
    "weekly-cluster-and-insights": {
        "task": "phase06.orchestration.tasks.pipeline.run_weekly_insights",
        "schedule": crontab(hour=4, minute=0, day_of_week=1),
        "kwargs": {},
    },
}
