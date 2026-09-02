from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from UsuarioApp.models import Profile


class PermitsPositionMixin(LoginRequiredMixin):
    """
    Permite acceso al módulo solo a usuarios activos
    con cargo ADMIN o MANAGER.
    """

    login_url = "account_login"
    redirect_url = reverse_lazy("Home")

    permisos_docente = ("ADMIN", "MANAGER")

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return self.handle_no_permission()

        if not user.is_active:
            return redirect(self.redirect_url)

        if user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        try:
            perfil = user.profile
        except Profile.DoesNotExist:
            return redirect(self.redirect_url)

        permiso = perfil.position_FK.permission_code if perfil.position_FK else None

        if permiso not in self.permisos_docente:
            return redirect(self.redirect_url)

        return super().dispatch(request, *args, **kwargs)
