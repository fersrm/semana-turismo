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


class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = [
            "nombre",
            "fecha_evento",
            "mostrar_desglose_por_tipo",
        ]

        labels = {
            "nombre": "Nombre del evento",
            "fecha_evento": "Fecha del evento",
            "mostrar_desglose_por_tipo": (
                "Mostrar emprendedores y asistentes por separado"
            ),
        }

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "input-config",
                    "placeholder": "Ej.: Ñuble Inspira Acceso",
                }
            ),
            "fecha_evento": forms.DateInput(
                attrs={
                    "class": "input-config",
                    "type": "date",
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
