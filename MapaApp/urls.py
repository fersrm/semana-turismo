from django.urls import path
from MapaApp import views

urlpatterns = [
    path("", views.IndexMapaView.as_view(), name="Mapa"),
    path(
        "mapa_panel/", views.MapaTemplaView.as_view(), name="MapaPanel"
    ),  # carga / panel
    path("mapa_vista/", views.MapaTempla2View.as_view(), name="MapaVista"),
    path("mapa_carga/", views.MapaFormView.as_view(), name="MapaCarga"),
    path("datos/", views.MapaDatosView.as_view(), name="MapaDatos"),
]
