from django.db import models


class Evento(models.Model):
    nombre = models.CharField(max_length=150)
    fecha_evento = models.DateField()
    mostrar_desglose_por_tipo = models.BooleanField(
        default=True,
        help_text="Si se desactiva, el mapa mostrará solo el total de asistentes.",
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

    class Meta:
        verbose_name = "Configuración del mapa"
        verbose_name_plural = "Configuración del mapa"

    def __str__(self):
        return "Configuración del mapa"
