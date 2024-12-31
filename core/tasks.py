import os
import json
from celery import shared_task
from core.main import login_and_navigate
from .models import Client


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


@shared_task(bind=True, max_retries=3)
def executar_guias(self, payload_json):
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

        # Read from file, update clients, and clear the file
        codigo_beneficiarios = read_from_file()
        if codigo_beneficiarios:
            update_clients(codigo_beneficiarios)
            clear_file()

        return {"success": "Task completed successfully."}

    except Exception as e:
        print(f"Error during task execution: {e}")
        return {"error": str(e)}
