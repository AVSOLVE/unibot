from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .serializers import PayloadSerializer
from .tasks import executar_guias
from .form import ClientForm
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


@login_required
def run_script(request):

    client_list = Client.objects.filter(user=request.user, active=True).order_by("-created_at")
    credentials = UnimedCredentials.objects.filter(user=request.user).first()

    payload_data = PayloadSerializer.from_models(client_list, credentials)

    serializer = PayloadSerializer(data=payload_data)
    try:
        serializer.is_valid(raise_exception=True)
    except ValidationError as e:
        print("Payload Validation Error:", e.detail)
        return JsonResponse({"status": "error", "message": e.detail}, status=400)

    # Save the payload log
    try:
        PayloadLog.objects.create(payload_data=serializer.validated_data)
    except Exception as e:
        print("Error Saving Payload Log:", str(e))
        return JsonResponse(
            {"status": "error", "message": "Failed to save payload log."}, status=500
        )

    try:
        payload_json = JSONRenderer().render(serializer.validated_data).decode("utf-8")
        print("Serialized Payload JSON:", payload_json)

        result = executar_guias.delay(payload_json)
        print("Task Result:", result.result)
    except Exception as e:
        print("Script Execution Error:", str(e))
        return JsonResponse(
            {"status": "error", "message": f"Script execution failed: {str(e)}"},
            status=500,
        )

    return redirect("client_list")



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
