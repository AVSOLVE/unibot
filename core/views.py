import json
from django.conf import settings
from django.utils.timezone import now
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.tasks import run_playwright_executar_guias
from core.form import ClientForm
from .models import ClientModel, PayloadLog, UnimedCredentials
import asyncio


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
def run_script(request):
    client_list = ClientModel.objects.filter(user=request.user, active=True).order_by(
        "-created_at"
    )
    credentials = UnimedCredentials.objects.filter(user=request.user).first()

    # Serialize client data
    serialized_clients = [
        {
            "nome_beneficiario": client.name,
            "codigo_beneficiario": client.id_card,
            "tipo_atendimento": client.type,
            "quantidade": client.qtd,
        }
        for client in client_list
    ]

    # Serialize credentials
    serialized_credentials = {
        "login": credentials.username if credentials else None,
        "password": credentials.password if credentials else None,
    }

    # Create the payload to send
    payload = {
        "clients": serialized_clients,
        "credentials": serialized_credentials,
    }

    # Check if the payload has already been used today
    today = now().date()
    # if PayloadLog.objects.filter(created_at__date=today, payload_data=payload).exists():
    #     return JsonResponse(
    #         {"status": "error", "message": "Payload already used today."}, status=400
    #     )

    # Validate required keys
    required_keys = {
        "nome_beneficiario",
        "codigo_beneficiario",
        "tipo_atendimento",
        "quantidade",
    }
    for idx, client in enumerate(serialized_clients, start=1):
        if not required_keys.issubset(client.keys()):
            return JsonResponse(
                {"status": "error", "message": f"Payload mismatch for client #{idx}."},
                status=400,
            )

    # Save the payload log
    PayloadLog.objects.create(payload_data=payload)

    # Call the external script
    try:
        payload_json = json.dumps(payload)
        result = run_playwright_executar_guias.delay(payload_json)
        print(result.result)
        # run_playwright_executar_guias.apply_async(
        #     args=[payload_json],
        #     queue=settings.ENVIRONMENT,
        # )
    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": f"Script execution failed: {str(e)}"},
            status=500,
        )

    return redirect("client_list")


@login_required
def client_list_view(request):
    client_list = ClientModel.objects.filter(user=request.user).order_by("name")
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
    client = get_object_or_404(ClientModel, id=client_id)

    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect("client_list")
    else:
        form = ClientForm(instance=client)

    return render(request, "client_edit.html", {"form": form, "client": client})
