import json
from celery import shared_task
from core.main import login_and_navigate
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True)
def executar_guias(self, payload_json):
    logger.info(f"Task {self.request.id} received payload: {payload_json}")
    try:
        payload = json.loads(payload_json)
        clients = payload["clients"]
        credentials = payload["credentials"]

        if not credentials["login"] or not credentials["password"]:
            raise ValueError("Invalid credentials provided.")

        if not clients:
            print("No active clients found to process.")
            return

        print("Starting login_and_navigate...")
        login_and_navigate(
            credentials, clients
        )  # Ensure this is the actual method you're calling
        print("Finished login_and_navigate.")
        return {"success": "Task completed successfully."}

    except Exception as e:
        print(f"Error during task execution: {e}")
        return {"error": str(e)}
