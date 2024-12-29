from django import forms
from django.forms import ModelForm
from core.models import ClientModel


class ClientForm(ModelForm):
    class Meta:
        model = ClientModel
        fields = "__all__"  # You can customize the fields here if needed
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "id_card": forms.TextInput(attrs={"class": "form-control"}),
            "type": forms.Select(attrs={"class": "form-control"}),
            "qtd": forms.TextInput(attrs={"class": "form-control"}),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "user": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "name": "Nome do Beneficiário",
            "id_card": "Carteirinha",
            "type": "Tipo de Atendimento",
            "qtd": "Quantidade a Executar",
            "active": "Ativo",
            "user": "Usuário",
        }
        help_texts = {
            "name": "Digite o nome do beneficiário",
            "id_card": "Digite o número da carteirinha",
            "type": "Selecione o tipo de atendimento",
            "qtd": "Digite a quantidade a executar",
            "active": "Marque se o beneficiário está ativo",
            "user": "Selecione o usuário",
        }
        error_messages = {
            "name": {"required": "Este campo é obrigatório"},
            "id_card": {"required": "Este campo é obrigatório"},
            "type": {"required": "Este campo é obrigatório"},
            "qtd": {"required": "Este campo é obrigatório"},
            "active": {"required": "Este campo é obrigatório"},
            "user": {"required": "Este campo é obrigatório"},
        }
