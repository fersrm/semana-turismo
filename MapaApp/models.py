import os
import uuid

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver


def logo_mapa_path(instance, filename):
    extension = os.path.splitext(filename)[1].lower()
    random_filename = uuid.uuid4()

    return f"logos/mapa/{random_filename}{extension}"


class Evento(models.Model):
    nombre = models.CharField(max_length=150)
    fecha_evento = models.DateField()
    mostrar_desglose_por_tipo = models.BooleanField(
        default=True,
        help_text="Si se desactiva, el mapa mostrará solo el total de asistentes.",
    )
    mostrar_solo_dia = models.BooleanField(
        default=False,
        help_text=("Si se desactiva, el mapa mostrará todo el evento."),
    )

    class Meta:
        ordering = ["-fecha_evento", "nombre"]

    def __str__(self):
        return self.nombre


class ParticipanteMapa(models.Model):
    TIPO_CHOICES = [
        ("ASISTENTE", "Asistente"),
        ("EMPRENDEDOR", "Emprendedor"),
    ]

    ORIGEN_CHOICES = [
        ("EXCEL", "Excel"),
    ]

    evento = models.ForeignKey(
        Evento,
        on_delete=models.PROTECT,
        related_name="participantes",
        null=True,
        blank=True,
    )
    comuna = models.CharField(max_length=100)
    tipo_participante = models.CharField(max_length=20, choices=TIPO_CHOICES)
    fecha = models.DateField(db_index=True)
    origen = models.CharField(
        max_length=10,
        choices=ORIGEN_CHOICES,
        default="EXCEL",
    )
    fecha_hora_registro = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "comuna"]

    def __str__(self):
        return f"{self.comuna} - {self.tipo_participante} - {self.fecha}"


class ConfiguracionMapa(models.Model):
    ESCALA_CHOICES = [
        ("LOG", "Logarítmica (recomendada)"),
        ("LINEAL", "Lineal"),
    ]

    columna_rol = models.CharField(
        max_length=255,
        default="Indique que tipo de participante es:",
    )

    columna_comuna = models.CharField(
        max_length=255,
        default="Comuna",
    )

    columna_fecha = models.CharField(
        max_length=255,
        default="Hora de inicio",
    )

    escala_mapa = models.CharField(
        max_length=10,
        choices=ESCALA_CHOICES,
        default="LOG",
    )
    logo_activo = models.ForeignKey(
        "LogoMapa",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        verbose_name = "Configuración del mapa"
        verbose_name_plural = "Configuración del mapa"

    def __str__(self):
        return "Configuración del mapa"


class LogoMapa(models.Model):
    nombre = models.CharField(
        max_length=100,
        unique=True,
    )

    imagen = models.ImageField(
        upload_to=logo_mapa_path,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Logo del mapa"
        verbose_name_plural = "Logos del mapa"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


@receiver(post_delete, sender=LogoMapa)
def eliminar_archivo_logo(sender, instance, **kwargs):
    """
    Elimina físicamente el archivo al eliminar el registro.
    Funciona también si más adelante cambias el storage.
    """
    if instance.imagen:
        instance.imagen.delete(save=False)
