from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, TemplateView, View

from adapters.excel_adapter import ExcelAdapter

from .forms import MapaForm
from .models import Evento, ParticipanteMapa, ConfiguracionMapa


def obtener_evento_activo():
    return Evento.objects.order_by(
        "-fecha_evento",
        "-id",
    ).first()


class MapaFormView(LoginRequiredMixin, FormView):

    form_class = MapaForm
    template_name = "pages/mapa/components/carga_excel.html"
    success_url = reverse_lazy("MapaPanel")
    login_url = reverse_lazy("account_login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["evento_predeterminado"] = obtener_evento_activo()

        return context

    def form_valid(self, form):
        document = form.cleaned_data["document"]

        evento = obtener_evento_activo()

        if not evento:
            messages.error(self.request, "Debe crear un evento antes de cargar datos.")
            return redirect("MapaPanel")

        try:
            adapter = ExcelAdapter()

            total_registros = adapter.process_excel_file(
                document,
                evento,
            )

            messages.success(
                self.request,
                f"Archivo cargado con éxito. "
                f"Se guardaron {total_registros} registros "
                f"en «{evento.nombre}».",
            )

        except Exception as error:
            messages.error(self.request, f"Error al procesar el archivo: {error}")

            return redirect("MapaPanel")

        return super().form_valid(form)

    def form_invalid(self, form):

        for _, errors in form.errors.items():
            for error in errors:
                messages.error(
                    self.request,
                    error,
                )

        return redirect("MapaPanel")


class MapaDatosView(View):

    def get(self, request, *args, **kwargs):
        evento_id = request.GET.get("evento")

        if not evento_id:
            return JsonResponse(
                {"error": "Debe seleccionar un evento."},
                status=400,
            )

        evento = get_object_or_404(Evento, pk=evento_id)

        dias = request.GET.get("dias", "todo")

        queryset = ParticipanteMapa.objects.filter(evento=evento)

        if dias != "todo":
            try:
                dias = int(dias)
            except ValueError:
                dias = 7

            if dias not in [1, 7]:
                dias = 7

            fecha_inicio = timezone.localdate() - timedelta(days=dias - 1)

            queryset = queryset.filter(fecha__gte=fecha_inicio)

        resumen_qs = queryset.values(
            "comuna",
            "tipo_participante",
        ).annotate(cantidad=Count("id"))

        resumen_dict = {}

        for item in resumen_qs:
            comuna = item["comuna"]

            if comuna not in resumen_dict:
                resumen_dict[comuna] = {
                    "PART_TCOMUNA": comuna,
                    "EMPRENDEDOR": 0,
                    "ASISTENTE": 0,
                    "TOTAL": 0,
                }

            resumen_dict[comuna][item["tipo_participante"]] = item["cantidad"]

        for comuna in resumen_dict.values():
            comuna["TOTAL"] = comuna["EMPRENDEDOR"] + comuna["ASISTENTE"]

        detalle = [
            {
                "PART_TCOMUNA": item["comuna"],
                "TIPO": item["tipo_participante"],
                "FECHA": (item["fecha"].isoformat() if item["fecha"] else None),
            }
            for item in queryset.values(
                "comuna",
                "tipo_participante",
                "fecha",
            )
        ]

        configuracion, _ = ConfiguracionMapa.objects.get_or_create(pk=1)

        return JsonResponse(
            {
                "evento": {
                    "id": evento.id,
                    "nombre": evento.nombre,
                },
                "config": {
                    "mostrar_desglose_por_tipo": (evento.mostrar_desglose_por_tipo),
                    "escala_mapa": configuracion.escala_mapa,
                },
                "resumen": list(resumen_dict.values()),
                "detalle": detalle,
            }
        )


class MapaTemplaView(LoginRequiredMixin, TemplateView):

    template_name = "pages/mapa/carga_mapa.html"
    login_url = reverse_lazy("account_login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        eventos = Evento.objects.order_by(
            "-fecha_evento",
            "-id",
        )

        evento_predeterminado = eventos.first()

        evento_id = self.request.GET.get("evento")

        evento_visualizado = None

        if evento_id:
            evento_visualizado = eventos.filter(pk=evento_id).first()

        if not evento_visualizado:
            evento_visualizado = evento_predeterminado

        context["eventos"] = eventos

        # Evento oficialmente activo
        context["evento_predeterminado"] = evento_predeterminado

        # Evento que estamos mirando
        context["evento_activo"] = evento_visualizado

        context["dias_filtro"] = self.request.GET.get(
            "dias",
            "todo",
        )

        return context


class MapaTempla2View(TemplateView):

    template_name = "pages/mapa/vista_mapa.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        eventos = Evento.objects.order_by(
            "-fecha_evento",
            "-id",
        )

        evento_activo = eventos.first()

        configuracion, _ = ConfiguracionMapa.objects.get_or_create(pk=1)

        context["logo_mapa"] = configuracion.logo_activo
        context["eventos"] = eventos
        context["evento_activo"] = evento_activo

        # Vista pública:
        # evento diario -> solo hoy
        # evento acumulativo -> todo
        if evento_activo and evento_activo.mostrar_solo_dia:
            context["dias_filtro"] = "1"
        else:
            context["dias_filtro"] = "todo"

        return context


class IndexMapaView(LoginRequiredMixin, TemplateView):
    template_name = "pages/mapa/mapa.html"
    login_url = reverse_lazy("account_login")
