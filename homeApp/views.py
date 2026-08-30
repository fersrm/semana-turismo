from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from UsuarioApp.models import Profile
from datetime import timedelta
from MapaApp.models import ParticipanteMapa

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
