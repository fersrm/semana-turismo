from django.views.generic import FormView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import MapaForm, ParticipanteManualForm
from django.contrib import messages
from django.urls import reverse_lazy
from adapters.excel_adapter import ExcelAdapter
from django.shortcuts import redirect
from datetime import timedelta
from django.http import JsonResponse
from django.db.models import Count
from django.utils import timezone
from .models import ParticipanteMapa


class ParticipanteManualCreateView(LoginRequiredMixin, FormView):
    form_class = ParticipanteManualForm
    template_name = "pages/mapa/components/carga_manual.html"
    success_url = reverse_lazy("MapaPanel")
    login_url = reverse_lazy("account_login")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Registro agregado correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        for _, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)

        return redirect("MapaPanel")


class MapaFormView(LoginRequiredMixin, FormView):
    form_class = MapaForm
    template_name = "pages/mapa/components/carga_excel.html"
    success_url = reverse_lazy("MapaPanel")
    login_url = reverse_lazy("account_login")

    def form_valid(self, form):
        document = form.cleaned_data["document"]

        try:
            adapter = ExcelAdapter()
            total_registros = adapter.process_excel_file(document)

            messages.success(
                self.request,
                f"Archivo cargado con éxito. Se guardaron {total_registros} registros.",
            )

        except Exception as e:
            form.add_error(None, f"Error al procesar el archivo: {str(e)}")
            return self.form_invalid(form)

        return super().form_valid(form)

    def form_invalid(self, form):
        for _, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{error}")

        return redirect("MapaPanel")


class MapaTemplaView(LoginRequiredMixin, TemplateView):
    template_name = "pages/mapa/carga_mapa.html"
    login_url = reverse_lazy("account_login")


# Vista que entregue los datos al mapa según filtro
class MapaDatosView(LoginRequiredMixin, View):

    login_url = reverse_lazy("account_login")

    def get(self, request, *args, **kwargs):
        dias = request.GET.get("dias", "7")

        try:
            dias = int(dias)
        except ValueError:
            dias = 7

        # Solo permitimos 7 o 30 por ahora
        if dias not in [7, 30]:
            dias = 7

        fecha_inicio = timezone.localdate() - timedelta(days=dias - 1)

        queryset = ParticipanteMapa.objects.filter(fecha__gte=fecha_inicio)

        resumen_qs = queryset.values("comuna", "tipo_participante").annotate(
            cantidad=Count("id")
        )

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

        detalle = list(
            queryset.values(
                "comuna",
                "tipo_participante",
                "fecha",
            )
        )

        detalle_formateado = [
            {
                "PART_TCOMUNA": item["comuna"],
                "TIPO": item["tipo_participante"],
                "FECHA": item["fecha"].isoformat(),
            }
            for item in detalle
        ]

        data = {
            "resumen": list(resumen_dict.values()),
            "detalle": detalle_formateado,
        }

        return JsonResponse(data)


# Vistas Principales
class MapaTemplaView(LoginRequiredMixin, TemplateView):
    template_name = "pages/mapa/carga_mapa.html"
    login_url = reverse_lazy("account_login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dias_filtro"] = self.request.GET.get("dias", "7")
        return context


class MapaTempla2View(LoginRequiredMixin, TemplateView):
    template_name = "pages/mapa/vista_mapa.html"
    login_url = reverse_lazy("account_login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dias_filtro"] = self.request.GET.get("dias", "7")
        return context


class IndexMapaView(LoginRequiredMixin, TemplateView):
    template_name = "pages/mapa/mapa.html"
    login_url = reverse_lazy("account_login")
