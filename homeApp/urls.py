from django.urls import path
from .views import HomeView, MapaConfiguracionView

urlpatterns = [
    path("", HomeView.as_view(), name="Home"),
    path(
        "configuracion/mapa/",
        MapaConfiguracionView.as_view(),
        name="MapaConfiguracion",
    ),
]
