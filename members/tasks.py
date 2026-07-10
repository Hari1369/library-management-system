# from celery import shared_task
# from .cron_management.fine_maintenance import run

# @shared_task(name='members.tasks.run_fine_maintenance')
# def run_fine_maintenance():
#     """Runs every night at midnight to process fines."""
#     try:
#         run()   # calls your existing fine_maintenance logic
#         return "Fine maintenance completed successfully."
#     except Exception as e:
#         return f"Fine maintenance failed: {str(e)}"


from celery import shared_task
from .cron_management.fine_maintenance import run


@shared_task
def run_fine_maintenance():
    print("========== Celery Task Started ==========")

    try:
        run()
        print("========== Celery Task Finished ==========")
    except Exception as e:
        print(e)