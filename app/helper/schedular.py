from apscheduler.schedulers.background import BackgroundScheduler
from app.helper.remainder_job import reminder_job

scheduler = BackgroundScheduler()

scheduler.add_job(
    reminder_job,
    "interval",
    day=1,
)

scheduler.start()