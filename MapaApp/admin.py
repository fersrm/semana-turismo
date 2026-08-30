from django.contrib import admin

from .models import Evento, ParticipanteMapa


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "fecha_evento",
        "mostrar_desglose_por_tipo",
    )
    search_fields = ("nombre",)
    list_filter = ("fecha_evento",)


@admin.register(ParticipanteMapa)
class ParticipanteMapaAdmin(admin.ModelAdmin):
    list_display = (
        "evento",
        "comuna",
        "tipo_participante",
        "fecha",
        "origen",
    )
    list_filter = (
        "evento",
        "tipo_participante",
        "origen",
        "fecha",
    )
