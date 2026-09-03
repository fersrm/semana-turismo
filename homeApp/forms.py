from django import forms

from MapaApp.models import ConfiguracionMapa, Evento, LogoMapa


class ConfiguracionMapaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionMapa
        fields = [
            "columna_rol",
            "columna_comuna",
            "columna_fecha",
            "escala_mapa",
        ]

        labels = {
            "columna_rol": "Columna de rol",
            "columna_comuna": "Columna de comuna",
            "columna_fecha": "Columna de fecha u hora",
            "escala_mapa": "Escala de colores",
        }

        widgets = {
            "columna_rol": forms.TextInput(attrs={"class": "input-config"}),
            "columna_comuna": forms.TextInput(attrs={"class": "input-config"}),
            "columna_fecha": forms.TextInput(attrs={"class": "input-config"}),
            "escala_mapa": forms.Select(attrs={"class": "input-config"}),
        }


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field

from django import forms

from MapaApp.models import Evento


class EventoForm(forms.ModelForm):

    class Meta:
        model = Evento

        fields = [
            "nombre",
            "fecha_evento",
            "mostrar_desglose_por_tipo",
            "mostrar_solo_dia",
        ]

        labels = {
            "nombre": "Nombre del evento",
            "fecha_evento": "Fecha del evento",
            "mostrar_desglose_por_tipo": (
                "Mostrar emprendedores y asistentes por separado"
            ),
            "mostrar_solo_dia": ("Mostrar solamente el día actual"),
        }

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "placeholder": "Ej.: Ñuble Inspira Acceso",
                    "class": (
                        "w-full rounded-md border border-gray-600 "
                        "bg-gray-700 px-3 py-2 text-white "
                        "placeholder-gray-400 "
                        "focus:border-indigo-500 "
                        "focus:outline-none "
                        "focus:ring-2 "
                        "focus:ring-indigo-500"
                    ),
                }
            ),
            "fecha_evento": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": (
                        "w-full rounded-md border border-gray-600 "
                        "bg-gray-700 px-3 py-2 text-white "
                        "focus:border-indigo-500 "
                        "focus:outline-none "
                        "focus:ring-2 "
                        "focus:ring-indigo-500"
                    ),
                }
            ),
            "mostrar_desglose_por_tipo": forms.CheckboxInput(
                attrs={
                    "class": (
                        "h-4 w-4 rounded border-gray-500 "
                        "bg-gray-700 text-indigo-600 "
                        "focus:ring-indigo-500"
                    ),
                }
            ),
            "mostrar_solo_dia": forms.CheckboxInput(
                attrs={
                    "class": (
                        "h-4 w-4 rounded border-gray-500 "
                        "bg-gray-700 text-indigo-600 "
                        "focus:ring-indigo-500"
                    ),
                }
            ),
        }


class LogoMapaForm(forms.ModelForm):

    class Meta:
        model = LogoMapa

        fields = [
            "nombre",
            "imagen",
        ]

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": (
                        "w-full rounded-lg border border-gray-300 "
                        "px-3 py-2 text-sm text-gray-800 "
                        "focus:border-blue-500 focus:outline-none"
                    ),
                    "placeholder": "Ej: Ñuble Turismo",
                }
            ),
            "imagen": forms.FileInput(
                attrs={
                    "class": (
                        "block w-full text-sm text-gray-700 "
                        "file:mr-4 file:rounded-lg file:border-0 "
                        "file:bg-blue-600 file:px-4 file:py-2 "
                        "file:text-white hover:file:bg-blue-700"
                    ),
                    "accept": "image/png,image/jpeg,image/webp",
                }
            ),
        }

    def clean_imagen(self):
        imagen = self.cleaned_data["imagen"]

        max_size = 5 * 1024 * 1024

        if imagen.size > max_size:
            raise forms.ValidationError("La imagen no puede superar los 5 MB.")

        return imagen
