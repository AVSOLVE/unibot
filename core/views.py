from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .serializers import PayloadSerializer
from .tasks import executar_guias
from .form import ClientForm
from celery import group
from .models import Client, PayloadLog, UnimedCredentials
from rest_framework.exceptions import ValidationError
from rest_framework.renderers import JSONRenderer


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


def chunk_list(lst, chunk_size):
    """Utility function to divide a list into chunks of given size."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


@login_required
def run_script(request):
    # Fetch active clients and credentials
    client_list = list(
        Client.objects.filter(user=request.user, active=True).order_by("-created_at")
    )
    credentials = UnimedCredentials.objects.filter(user=request.user).first()

    if not credentials:
        return JsonResponse(
            {"status": "error", "message": "No credentials found."}, status=400
        )

    # Divide clients into chunks of 10
    chunk_size = 5
    client_chunks = list(chunk_list(client_list, chunk_size))

    # Prepare tasks for each chunk
    celery_tasks = []
    for chunk in client_chunks:
        payload_data = PayloadSerializer.from_models(chunk, credentials)
        serializer = PayloadSerializer(data=payload_data)
        try:
            serializer.is_valid(raise_exception=True)
            payload_json = (
                JSONRenderer().render(serializer.validated_data).decode("utf-8")
            )

            # Save the payload log
            PayloadLog.objects.create(payload_data=serializer.validated_data)

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
        workflow = group(celery_tasks)
        result = workflow.apply_async()
        print("Workflow Task ID:", result.id)
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
def client_list_view(request):
    client_list = Client.objects.filter(user=request.user).order_by("nome_beneficiario")
    active_clients = client_list.filter(active=True).count
    return render(
        request,
        "index.html",
        {
            "client_list": client_list,
            "active_clients": active_clients,
        },
    )


def client_create_view(request):
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
