from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from UsuarioApp.models import Profile
from datetime import timedelta
from MapaApp.models import ParticipanteMapa
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from MapaApp.models import (
    ConfiguracionMapa,
    Evento,
    ParticipanteMapa,
    LogoMapa,
)

from .forms import (
    ConfiguracionMapaForm,
    EventoForm,
    LogoMapaForm,
)

# Create your views here.


class HomeView(LoginRequiredMixin, ListView):
    model = User
    template_name = "pages/index.html"

    def get_queryset(self):
        return (
            User.objects.filter(Q(last_login__isnull=False))
            .select_related("profile__position_FK")
            .order_by("-last_login")[:5]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        recent_activity_cutoff = timezone.now() - timedelta(minutes=2)

        active_users = Profile.objects.filter(
            last_activity__gte=recent_activity_cutoff
        ).values_list("user_FK_id", flat=True)

        context["active_users"] = active_users

        # Lunes de la semana actual.
        hoy = timezone.localdate()
        lunes = hoy - timedelta(days=hoy.weekday())
        viernes = lunes + timedelta(days=4)

        registros_por_dia = dict(
            ParticipanteMapa.objects.filter(fecha__range=(lunes, viernes))
            .values("fecha")
            .annotate(total=Count("id"))
            .values_list("fecha", "total")
        )

        dias_semana = [
            ("Lun", lunes),
            ("Mar", lunes + timedelta(days=1)),
            ("Mié", lunes + timedelta(days=2)),
            ("Jue", lunes + timedelta(days=3)),
            ("Vie", viernes),
        ]

        context["grafico_semana"] = {
            "labels": [nombre for nombre, _ in dias_semana],
            "values": [registros_por_dia.get(fecha, 0) for _, fecha in dias_semana],
        }

        return context


class MapaConfiguracionView(LoginRequiredMixin, TemplateView):
    template_name = "pages/configuracion/mapa_configuracion.html"
    login_url = reverse_lazy("account_login")

    def get_configuracion(self):
        configuracion, _ = ConfiguracionMapa.objects.get_or_create(pk=1)
        return configuracion

    def get_context_data(
        self,
        configuracion_form=None,
        evento_form=None,
        logo_form=None,
        **kwargs,
    ):
        context = super().get_context_data(**kwargs)

        configuracion = self.get_configuracion()

        context["configuracion_form"] = configuracion_form or ConfiguracionMapaForm(
            instance=configuracion
        )

        eventos = Evento.objects.annotate(
            total_participantes=Count("participantes")
        ).order_by(
            "-fecha_evento",
            "-id",
        )

        context["evento_form"] = evento_form or EventoForm()
        context["evento_activo"] = eventos.first()
        context["eventos"] = eventos
        context["logo_form"] = logo_form or LogoMapaForm()
        context["logos"] = LogoMapa.objects.all()
        context["logo_activo"] = configuracion.logo_activo

        return context

    def post(self, request, *args, **kwargs):
        accion = request.POST.get("accion")

        if accion == "guardar_configuracion":
            configuracion = self.get_configuracion()

            form = ConfiguracionMapaForm(
                request.POST,
                instance=configuracion,
            )

            if form.is_valid():
                form.save()

                messages.success(
                    request,
                    "Configuración del Excel y mapa actualizada.",
                )

                return redirect("MapaConfiguracion")

            return self.render_to_response(
                self.get_context_data(configuracion_form=form)
            )

        if accion == "crear_evento":
            form = EventoForm(request.POST)

            if form.is_valid():
                evento = form.save()

                messages.success(
                    request,
                    f"Evento «{evento.nombre}» creado correctamente.",
                )

                return redirect("MapaConfiguracion")

            return self.render_to_response(self.get_context_data(evento_form=form))

        if accion == "eliminar_evento":
            evento_id = request.POST.get("evento_id")

            evento = get_object_or_404(Evento, pk=evento_id)

            total = ParticipanteMapa.objects.filter(evento=evento).count()

            with transaction.atomic():
                ParticipanteMapa.objects.filter(evento=evento).delete()

                evento.delete()

            messages.success(
                request,
                f"Evento eliminado. También se eliminaron "
                f"{total} registros asociados.",
            )

            return redirect("MapaConfiguracion")

        if accion == "crear_logo":
            form = LogoMapaForm(
                request.POST,
                request.FILES,
            )

            if form.is_valid():
                logo = form.save()

                configuracion = self.get_configuracion()

                # Si es el primer logo, usarlo automáticamente.
                if not configuracion.logo_activo:
                    configuracion.logo_activo = logo
                    configuracion.save(update_fields=["logo_activo"])

                messages.success(
                    request,
                    f"Logo «{logo.nombre}» agregado correctamente.",
                )

                return redirect("MapaConfiguracion")

            return self.render_to_response(self.get_context_data(logo_form=form))

        if accion == "seleccionar_logo":
            logo_id = request.POST.get("logo_id")

            logo = get_object_or_404(
                LogoMapa,
                pk=logo_id,
            )

            configuracion = self.get_configuracion()

            configuracion.logo_activo = logo

            configuracion.save(update_fields=["logo_activo"])

            messages.success(
                request,
                f"Ahora se está utilizando el logo «{logo.nombre}».",
            )

            return redirect("MapaConfiguracion")

        if accion == "eliminar_logo":
            logo_id = request.POST.get("logo_id")

            logo = get_object_or_404(
                LogoMapa,
                pk=logo_id,
            )

            nombre = logo.nombre

            configuracion = self.get_configuracion()

            if configuracion.logo_activo_id == logo.id:
                configuracion.logo_activo = None
                configuracion.save(update_fields=["logo_activo"])

            logo.delete()

            messages.success(
                request,
                f"Logo «{nombre}» eliminado correctamente.",
            )

            return redirect("MapaConfiguracion")

        messages.error(request, "Acción no válida.")

        return redirect("MapaConfiguracion")
