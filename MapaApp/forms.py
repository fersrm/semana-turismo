from django import forms
from django.utils import timezone
from .models import ParticipanteMapa


class MapaForm(forms.Form):
    document = forms.FileField()

    def clean_document(self):
        document = self.cleaned_data["document"]

        if not document.name.endswith((".xlsx",)):
            raise forms.ValidationError("El archivo debe ser de formato Excel (xlsx)")

        max_size = 50 * 1024 * 1024
        if document.size > max_size:
            raise forms.ValidationError(
                "El tamaño del archivo no puede ser mayor a 50 megabytes."
            )

        return document


class ParticipanteManualForm(forms.Form):
    COMUNAS_CHOICES = [
        ("SAN FABIAN", "San Fabián"),
        ("COIHUECO", "Coihueco"),
        ("PINTO", "Pinto"),
        ("SAN CARLOS", "San Carlos"),
        ("YUNGAY", "Yungay"),
        ("EL CARMEN", "El Carmen"),
        ("COBQUECURA", "Cobquecura"),
        ("QUIRIHUE", "Quirihue"),
        ("PEMUCO", "Pemuco"),
        ("SAN NICOLAS", "San Nicolás"),
        ("NIQUEN", "Ñiquén"),
        ("CHILLAN", "Chillán"),
        ("BULNES", "Bulnes"),
        ("QUILLON", "Quillón"),
        ("NINHUE", "Ninhue"),
        ("COELEMU", "Coelemu"),
        ("SAN IGNACIO", "San Ignacio"),
        ("TREHUACO", "Trehuaco"),
        ("CHILLAN VIEJO", "Chillán Viejo"),
        ("PORTEZUELO", "Portezuelo"),
        ("RANQUIL", "Ránquil"),
    ]

    ROL_CHOICES = [
        ("", "Seleccione un rol"),
        ("ESTUDIANTE INACAP", "Estudiante INACAP"),
        ("DOCENTE INACAP", "Docente INACAP"),
        ("ADMINISTRATIVO INACAP", "Administrativo INACAP"),
        ("EXALUMNO INACAP", "Exalumno INACAP"),
        ("EMPRENDEDOR/EMPRESA", "Emprendedor/Empresa"),
        ("OTRO", "Otro"),
    ]

    comuna = forms.ChoiceField(
        label="Comuna",
        choices=[("", "Seleccione una comuna")] + COMUNAS_CHOICES,
    )

    rol = forms.ChoiceField(
        label="Rol",
        choices=ROL_CHOICES,
    )

    fecha = forms.DateField(
        label="Fecha",
        initial=timezone.localdate,
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={
                "type": "date",
                "max": timezone.localdate().isoformat(),
            },
        ),
        input_formats=["%Y-%m-%d"],
    )

    def clean_fecha(self):
        fecha = self.cleaned_data["fecha"]

        if fecha > timezone.localdate():
            raise forms.ValidationError(
                "La fecha no puede ser mayor a la fecha actual."
            )

        return fecha

    def save(self):
        rol = self.cleaned_data["rol"]

        tipo_participante = (
            "EMPRENDEDOR" if rol == "EMPRENDEDOR/EMPRESA" else "ASISTENTE"
        )

        return ParticipanteMapa.objects.create(
            comuna=self.cleaned_data["comuna"],
            tipo_participante=tipo_participante,
            fecha=self.cleaned_data["fecha"],
            origen="MANUAL",
        )
