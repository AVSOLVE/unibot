import time

from asgiref.sync import async_to_sync
from celery import group
from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.exceptions import ValidationError
from rest_framework.renderers import JSONRenderer
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from core.main import get_beneficiario_data

from .form import ClientForm
from .models import Client, PayloadLog, UnimedCredentials
from .serializers import CredentialsSerializer, PayloadSerializer
from .tasks import executar_guias


class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        """Called when the observed file is modified."""
        if event.src_path.endswith("processed_clients.json"):
            print(f"File modified: {event.src_path}")
            self.send_channel_message()

    def send_channel_message(self):
        """Send a message to the WebSocket channel."""
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "live_data",  # Replace with the name of your channel group
            {
                "type": "live_data_message",  # The method in your consumer
                "message": "File has been updated with new client data.",
            },
        )


def observe_file(file_path):
    """Observe changes in the file."""
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=file_path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)  # Keep the program running to watch the file
    except KeyboardInterrupt:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    observe_file("./processed_clients.json")


def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully logged in!")
            return redirect("client_list")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "login.html")


def user_logout(request):
    logout(request)
    return redirect("login")


@login_required
def home_view(request):
    return render(request, "index.html")


def chunk_list(client_list, chunk_size):
    for i in range(0, len(client_list), chunk_size):
        yield client_list[i : i + chunk_size]


@login_required
def run_script(request):
    client_list = list(
        Client.objects.filter(user=request.user, active=True).order_by("-created_at")
    )
    credentials = UnimedCredentials.objects.filter(user=request.user).first()

    if not credentials:
        return JsonResponse(
            {"status": "error", "message": "No credentials found."}, status=400
        )

    # Divide clients into chunks of 12
    chunk_size = 12
    client_chunks = list(chunk_list(client_list, chunk_size))

    # Prepare tasks for each chunk
    celery_tasks = []
    seen_chunks = []  # List to store serialized chunks for comparison

    for chunk in client_chunks:
        # Serialize the chunk for comparison
        payload_data = PayloadSerializer.from_models(chunk, credentials)
        serializer = PayloadSerializer(data=payload_data)
        try:
            serializer.is_valid(raise_exception=True)
            payload_json = (
                JSONRenderer().render(serializer.validated_data).decode("utf-8")
            )

            # Check if this chunk is already in the seen chunks
            if payload_json in seen_chunks:
                print("Duplicate chunk found, skipping...")
                continue

            # Save the payload log
            PayloadLog.objects.create(payload_data=serializer.validated_data)

            # Add the serialized chunk to the seen chunks for future comparisons
            seen_chunks.append(payload_json)

            # Create a Celery task for this chunk
            celery_tasks.append(executar_guias.s(payload_json))

        except ValidationError as e:
            print("Payload Validation Error for chunk:", e.detail)
            return JsonResponse({"status": "error", "message": e.detail}, status=400)
        except Exception as e:
            print("Error Saving Payload Log:", str(e))
            return JsonResponse(
                {"status": "error", "message": "Failed to save payload log."},
                status=500,
            )

    # Execute all tasks in parallel
    try:
        if celery_tasks:
            workflow = group(celery_tasks)
            result = workflow.apply_async()
            print("Workflow Task ID:", result.id)
        else:
            print("No tasks to dispatch.")
    except Exception as e:
        print("Error Dispatching Celery Tasks:", str(e))
        return JsonResponse(
            {"status": "error", "message": f"Task dispatch failed: {str(e)}"},
            status=500,
        )

    return JsonResponse(
        {"status": "success", "message": "Tasks dispatched successfully."}
    )


@login_required
def run_script2(request):
    credentials = UnimedCredentials.objects.filter(user=request.user).first()
    if not credentials:
        return JsonResponse(
            {"status": "error", "message": "No credentials found."}, status=400
        )

    # Serialize and validate credentials
    serializer = CredentialsSerializer.from_credentials_model(credentials)
    payload_json = JSONRenderer().render(serializer).decode("utf-8")
    print("Payload JSON:", payload_json)
    get_beneficiario_data(payload_json, "02220607001617033")


@login_required
def client_list(request):
    client_list = Client.objects.filter(user=request.user).order_by("nome_beneficiario")
    active_clients = client_list.filter(active=True).count()
    inactive_clients = client_list.count() - active_clients
    return render(
        request,
        "client_list.html",
        {
            "client_list": client_list,
            "active_clients": active_clients,
            "inactive_clients": inactive_clients,
        },
    )


@login_required
def client_create(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.user = request.user
            client.save()
            return redirect("client_list")
    else:
        form = ClientForm()
    return render(request, "client_create.html", {"form": form})


@login_required
def client_edit(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect("client_list")
    else:
        form = ClientForm(instance=client)

    return render(request, "client_edit.html", {"form": form, "client": client})


@login_required
def client_update_active(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    client.active = not client.active
    client.save()

    return redirect("client_list")
