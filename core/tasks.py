import json
import os

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer

from core.main import login_and_navigate

from .models import Client


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
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                lines = file.readlines()

            # Process each line
            with open(file_path, "w") as file:
                for line in lines:
                    message = line.strip()
                    if message:
                        send_channel_message(message)
                        print(f"Sent message: {message}")
                    # We don't need to write anything back to the file, effectively removing the line

        else:
            print(f"{file_path} does not exist.")
    except Exception as e:
        print(f"Error processing file: {e}")


def read_from_file(file_path="codigo_beneficiario_list.txt"):
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                return [line.strip() for line in file.readlines()]
        else:
            print(f"{file_path} does not exist.")
            return []
    except Exception as e:
        print(f"Error reading from file: {e}")
        return []


def update_clients(codigo_beneficiarios):
    try:
        for codigo_beneficiario in codigo_beneficiarios:
            Client.objects.filter(codigo_beneficiario=codigo_beneficiario).update(
                active=False
            )
        print("Clients updated successfully.")
    except Exception as e:
        print(f"Error updating clients: {e}")


def clear_file(file_path="codigo_beneficiario_list.txt"):
    try:
        with open(file_path, "w") as file:
            file.truncate()
        print(f"Cleared file: {file_path}")
    except Exception as e:
        print(f"Error clearing file: {e}")


@shared_task()
def executar_guias(payload_json):
    try:
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

        codigo_beneficiarios = read_from_file()
        if codigo_beneficiarios:
            update_clients(codigo_beneficiarios)
            clear_file()
            read_and_process_file()

        return {"success": "Task completed successfully."}

    except Exception as e:
        print(f"Error during task execution: {e}")
        return {"error": str(e)}
