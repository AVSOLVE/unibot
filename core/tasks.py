import fcntl
import json
import logging
import os

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer

from core.main import login_and_navigate

from .models import Client

logger = logging.getLogger(__name__)


def send_channel_message(message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "live_data",
        {
            "type": "live_data_message",
            "message": message,
        },
    )


def read_and_process_file(file_path="processed_clients.json"):
    if not os.path.exists(file_path):
        logger.warning(f"{file_path} does not exist.")
        return

    try:
        with open(file_path, "r+") as file:
            fcntl.flock(file, fcntl.LOCK_EX)  # Lock the file
            lines = file.readlines()
            unique_lines = list(set(line.strip() for line in lines if line.strip()))

            for line in unique_lines:
                send_channel_message(line)
                logger.info(f"Sent message: {line}")
                codigo_beneficiario, nome_beneficiario, status = line.split(";")
                if status == "false":
                    Client.objects.filter(
                        codigo_beneficiario=codigo_beneficiario
                    ).update(active=True)

            file.seek(0)
            file.truncate()  # Clear the file content
            logger.info(f"File {file_path} cleaned after processing.")

    except Exception as e:
        logger.error(f"Error processing file: {e}")
    finally:
        fcntl.flock(file, fcntl.LOCK_UN)  # Unlock the file


@shared_task(bind=True)
def executar_guias(self, **kwargs):
    try:
        payload_json = kwargs.get("payload_json")

        if not payload_json:
            raise ValueError("No payload_json provided.")

        payload = json.loads(payload_json)
        credentials = payload["credentials"]
        clients = payload["clients"]

        if not credentials["login"] or not credentials["password"]:
            raise ValueError("Invalid credentials provided.")

        if not clients:
            print("No active clients found to process.")
            return

        print("Starting process...")
        login_and_navigate(credentials, clients)
        read_and_process_file()

        return {"success": "Task completed successfully."}

    except Exception as e:
        print(f"Error during task execution: {e}")
        return {"error": str(e)}
