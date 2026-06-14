from celery import shared_task
from .cron_management.fine_maintenance import run

@shared_task(name='members.tasks.run_fine_maintenance')
def run_fine_maintenance():
    """Runs every night at midnight to process fines."""
    try:
        run()   # calls your existing fine_maintenance logic
        return "Fine maintenance completed successfully."
    except Exception as e:
        return f"Fine maintenance failed: {str(e)}"