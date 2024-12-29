from core.models import Client, UnimedCredentials
from rest_framework import serializers


class ClientSerializer(serializers.ModelSerializer):
    nome_beneficiario = serializers.CharField(source="name")
    codigo_beneficiario = serializers.CharField(source="id_card")
    tipo_atendimento = serializers.CharField(source="type")
    quantidade = serializers.IntegerField(source="qtd")

    class Meta:
        model = Client
        fields = [
            "nome_beneficiario",
            "codigo_beneficiario",
            "tipo_atendimento",
            "quantidade",
        ]

    @staticmethod
    def from_client_model(client):
        return ClientSerializer(client).data


class CredentialsSerializer(serializers.ModelSerializer):
    login = serializers.CharField(source="username")
    password = serializers.CharField()

    class Meta:
        model = UnimedCredentials
        fields = ["login", "password"]

    @staticmethod
    def from_credentials_model(credentials):
        return CredentialsSerializer(credentials).data


class PayloadSerializer(serializers.Serializer):
    clients = ClientSerializer(many=True)
    credentials = CredentialsSerializer()

    @staticmethod
    def from_models(client_list, credentials):
        serialized_clients = ClientSerializer(client_list, many=True).data
        serialized_credentials = (
            CredentialsSerializer(credentials).data
            if credentials
            else {
                "login": None,
                "password": None,
            }
        )
        return {"clients": serialized_clients, "credentials": serialized_credentials}
