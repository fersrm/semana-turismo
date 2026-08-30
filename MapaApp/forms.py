from django import forms
from .models import Evento


class MapaForm(forms.Form):
    evento = forms.ModelChoiceField(
        queryset=Evento.objects.all(),
        empty_label="Seleccione un evento",
        label="Evento",
    )

    document = forms.FileField(
        label="Archivo Excel",
    )

    def clean_document(self):
        document = self.cleaned_data["document"]

        if not document.name.lower().endswith(".xlsx"):
            raise forms.ValidationError("El archivo debe ser de formato Excel (.xlsx).")

        max_size = 50 * 1024 * 1024  # 50 MB

        if document.size > max_size:
            raise forms.ValidationError(
                "El tamaño del archivo no puede ser mayor a 50 MB."
            )

        return document
