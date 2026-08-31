from django import forms

from MapaApp.models import ConfiguracionMapa, Evento


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
