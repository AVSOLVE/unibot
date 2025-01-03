from django import forms
from django.forms import ModelForm

from core.models import Client


class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = "__all__"  # You can customize the fields here if needed
        widgets = {
            "nome_beneficiario": forms.TextInput(attrs={"class": "form-control"}),
            "codigo_beneficiario": forms.NumberInput(
                attrs={"class": "form-control", "maxlength": "17"}
            ),
            "tipo_atendimento": forms.Select(attrs={"class": "form-control"}),
            "quantidade": forms.NumberInput(attrs={"class": "form-control"}),
            "user": forms.Select(attrs={"class": "form-control"}),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "nome_beneficiario": "Nome do Beneficiário",
            "codigo_beneficiario": "Carteirinha",
            "tipo_atendimento": "Tipo de Atendimento",
            "quantidade": "Quantidade a Executar",
            "user": "Usuário",
            "active": "Ativo",
        }
        help_texts = {
            "nome_beneficiario": "Digite o nome do beneficiário",
            "codigo_beneficiario": "Digite o número da carteirinha",
            "tipo_atendimento": "Selecione o tipo de atendimento",
            "quantidade": "Digite a quantidade a executar",
            "user": "Selecione o usuário",
            "active": "Marque se o beneficiário está ativo",
        }
        error_messages = {
            "nome_beneficiario": {"required": "Este campo é obrigatório"},
            "codigo_beneficiario": {"required": "Este campo é obrigatório"},
            "tipo_atendimento": {"required": "Este campo é obrigatório"},
            "quantidade": {"required": "Este campo é obrigatório"},
            "user": {"required": "Este campo é obrigatório"},
            "active": {"required": "Este campo é obrigatório"},
        }

    def clean_codigo_beneficiario(self):
        codigo_beneficiario = self.cleaned_data["codigo_beneficiario"]
        if len(str(codigo_beneficiario)) != 17:
            raise forms.ValidationError(
                "A carteirinha deve conter exatamente 17 dígitos."
            )
        return codigo_beneficiario
