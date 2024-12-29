from django.contrib import admin
from django.db.models import QuerySet
from .models import PayloadLog, UnimedCredentials, ClientModel


@admin.action(description="Desativar clientes selecionados")
def deactivate_clients(modeladmin, request, queryset: QuerySet):
    updated_count = queryset.update(active=False)
    if updated_count:
        modeladmin.message_user(
            request, f"{updated_count} cliente(s) foram desativados com sucesso."
        )
    else:
        modeladmin.message_user(request, "Nenhum cliente foi desativado.", level="warning")



@admin.action(description="Ativar clientes selecionados")
def activate_clients(modeladmin, request, queryset: QuerySet):
    updated_count = queryset.update(active=True)
    if updated_count:
        modeladmin.message_user(
            request, f"{updated_count} cliente(s) foram ativados com sucesso."
        )
    else:
        modeladmin.message_user(request, "Nenhum cliente foi ativado.", level="warning")


@admin.register(ClientModel)
class ClientModelAdmin(admin.ModelAdmin):
    list_display = ("name", "id_card", "active", "user")
    list_filter = ("active",)
    search_fields = ("id_card", "name")
    actions = [deactivate_clients, activate_clients]



@admin.register(UnimedCredentials)
class UnimedCredentialsAdmin(admin.ModelAdmin):
    list_display = ("user", "username")
    search_fields = ("user__username", "username")


@admin.register(PayloadLog)
class PayloadLogAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "updated_at")
    readonly_fields = ("payload_data", "created_at", "updated_at")
    search_fields = ("payload_data",)
    list_filter = ("created_at",)
