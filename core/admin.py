from django.contrib import admin
from django.db.models import QuerySet

from .models import Client, PayloadLog, UnimedCredentials


@admin.action(description="Desativar clientes selecionados")
def deactivate_clients(modeladmin, request, queryset: QuerySet):
    updated_count = queryset.update(active=False)
    if updated_count:
        modeladmin.message_user(
            request, f"{updated_count} cliente(s) foram desativados com sucesso."
        )
    else:
        modeladmin.message_user(
            request, "Nenhum cliente foi desativado.", level="warning"
        )


@admin.action(description="Ativar clientes selecionados")
def activate_clients(modeladmin, request, queryset: QuerySet):
    updated_count = queryset.update(active=True)
    if updated_count:
        modeladmin.message_user(
            request, f"{updated_count} cliente(s) foram ativados com sucesso."
        )
    else:
        modeladmin.message_user(request, "Nenhum cliente foi ativado.", level="warning")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    actions = [activate_clients, deactivate_clients]


admin.site.register(UnimedCredentials)
admin.site.register(PayloadLog)
