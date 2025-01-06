from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TypeChoices(models.TextChoices):
    ATENDIMENTO_DOMICILIAR = "6", _("Atendimento Domiciliar")
    CONSULTA = "4", _("Consulta")
    EXAME = "23", _("Exame")
    EXAME_AMBULATORIAL = "5", _("Exame Ambulatorial")
    INTERNACAO = "7", _("Internação (SADT internado)")
    OUTRAS_TERAPIAS = "3", _("Outras Terapias")
    PEQUENA_CIRURGIA = "2", _("Pequena Cirurgia")
    PEQUENO_ATENDIMENTO = "13", _("Pequeno Atendimento (sutura, gesso e outros)")
    PRONTO_SOCORRO = "11", _("Pronto Socorro")
    QUIMIOTERAPIA = "8", _("Quimioterapia")
    RADIOTERAPIA = "9", _("Radioterapia")
    REMOCAO = "1", _("Remoção")
    SAUDE_OCUPACIONAL_ADMISSIONAL = "14", _("Saúde Ocupacional - Admissional")
    SAUDE_OCUPACIONAL_ASSISTENCIA_DEMITIDOS = "21", _(
        "Saúde Ocupacional - Assistência a Demitidos"
    )
    SAUDE_OCUPACIONAL_BENEFICIARIO_NOVO = "20", _(
        "Saúde Ocupacional - Beneficiário Novo"
    )
    SAUDE_OCUPACIONAL_DEMISSIONAL = "15", _("Saúde Ocupacional - Demissional")
    SAUDE_OCUPACIONAL_MUDANCA_FUNCAO = "18", _("Saúde Ocupacional - Mudança de Função")
    SAUDE_OCUPACIONAL_PERIODICO = "16", _("Saúde Ocupacional - Periódico")
    SAUDE_OCUPACIONAL_PROMOCAO_SAUDE = "19", _("Saúde Ocupacional - Promoção à Saúde")
    SAUDE_OCUPACIONAL_RETORNO_TRABALHO = "17", _(
        "Saúde Ocupacional - Retorno ao Trabalho"
    )
    TELESSAUDE = "22", _("Telessaúde")
    TERAPIA_RENAL_SUBSTITUTIVA = "10", _("Terapia Renal Substitutiva (TRS)")


class UnimedCredentials(TimeStamped):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    login = models.CharField(max_length=255, verbose_name="Unimed Login")
    password = models.CharField(max_length=255, verbose_name="Unimed Password")

    def __str__(self):
        return f"Unimed Credentials for {self.user.username}"


class Client(TimeStamped):
    nome_beneficiario = models.CharField(
        max_length=255, verbose_name=_("Nome do Beneficiário")
    )
    codigo_beneficiario = models.CharField(
        max_length=17,
        verbose_name=_("Carteirinha"),
        unique=True,
        validators=[
            RegexValidator(
                r"^\d{17}$", _("A carteirinha deve conter exatos 17 dígitos.")
            )
        ],
    )
    tipo_atendimento = models.CharField(
        max_length=2, choices=TypeChoices.choices, verbose_name=_("Tipo de Atendimento")
    )
    quantidade = models.PositiveIntegerField(
        verbose_name=_("Quantidade a Executar"),
        validators=[MinValueValidator(1)],
    )
    active = models.BooleanField(default=True, verbose_name=_("Ativo"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Usuário"))

    def __str__(self):
        return f"{self.nome_beneficiario} ({self.codigo_beneficiario}) - {self.get_tipo_atendimento_display()}"


class PayloadLog(TimeStamped):
    payload_data = models.JSONField(verbose_name=_("Dados do Payload"))

    def __str__(self):
        return f"PayloadLog {self.id} for {self.created_at.date()}"
