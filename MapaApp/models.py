from django.db import models


class ParticipanteMapa(models.Model):
    TIPO_CHOICES = [
        ("ASISTENTE", "Asistente"),
        ("EMPRENDEDOR", "Emprendedor"),
    ]

    ORIGEN_CHOICES = [
        ("EXCEL", "Excel"),
        ("MANUAL", "Manual"),
    ]

    comuna = models.CharField(max_length=100)
    tipo_participante = models.CharField(max_length=20, choices=TIPO_CHOICES)
    fecha = models.DateField(db_index=True)
    origen = models.CharField(
        max_length=10,
        choices=ORIGEN_CHOICES,
        default="EXCEL",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Participante del mapa"
        verbose_name_plural = "Participantes del mapa"
        ordering = ["-fecha", "comuna"]

    def __str__(self):
        return f"{self.comuna} - {self.tipo_participante} - {self.fecha}"
