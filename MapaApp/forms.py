from django import forms


class MapaForm(forms.Form):
    document = forms.FileField(label="Archivo Excel")

    def clean_document(self):
        document = self.cleaned_data["document"]

        if not document.name.lower().endswith(".xlsx"):
            raise forms.ValidationError("El archivo debe ser de formato Excel (.xlsx).")

        max_size = 50 * 1024 * 1024

        if document.size > max_size:
            raise forms.ValidationError(
                "El tamaño del archivo no puede superar los 50 MB."
            )

        return document
