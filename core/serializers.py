from core.models import Client, UnimedCredentials
from rest_framework import serializers


class ClientSerializer(serializers.ModelSerializer):
    nome_beneficiario = serializers.CharField()
    codigo_beneficiario = serializers.CharField()
    tipo_atendimento = serializers.CharField()
    quantidade = serializers.IntegerField()

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
        serialized_clients = [
            ClientSerializer.from_client_model(client) for client in client_list
        ]
        serialized_credentials = (
            CredentialsSerializer.from_credentials_model(credentials)
            if credentials
            else {"login": None, "password": None}
        )
        return {"clients": serialized_clients, "credentials": serialized_credentials}
