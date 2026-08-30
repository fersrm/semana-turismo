import pandas as pd
from unidecode import unidecode
from django.utils import timezone
from MapaApp.models import ParticipanteMapa


class ExcelAdapter:
    # Nombres reales de columnas en el Excel
    COL_ROL = "¿Desde qué rol nos acompañas hoy?"
    COL_COMUNA = "Indique comuna de la organización o empresa que representa"

    # Ajustar al nombre real de la columna fecha del Excel
    COL_FECHA = "Fecha"

    def clean_text(self, x):
        if pd.isna(x):
            return ""
        if isinstance(x, str):
            return unidecode(x.upper().strip())
        return x

    def map_tipo_participante(self, rol):
        rol_limpio = self.clean_text(rol)

        roles_asistente = {
            "ESTUDIANTE INACAP",
            "DOCENTE INACAP",
            "ADMINISTRATIVO INACAP",
            "EXALUMNO INACAP",
            "OTRO",
        }

        if rol_limpio in roles_asistente:
            return "ASISTENTE"

        if rol_limpio == "EMPRENDEDOR/EMPRESA":
            return "EMPRENDEDOR"

        return "ASISTENTE"

    def obtener_fecha(self, valor_fecha):
        """
        Si el Excel trae una fecha válida, la usa.
        Si no trae fecha o viene vacía, usa la fecha local actual.
        """
        if pd.isna(valor_fecha) or valor_fecha == "":
            return timezone.localdate()

        fecha = pd.to_datetime(valor_fecha, errors="coerce")

        if pd.isna(fecha):
            return timezone.localdate()

        return fecha.date()

    def process_excel_file(self, document):
        df = pd.read_excel(document)

        # Si la columna fecha no existe en el Excel, se crea vacía
        if self.COL_FECHA not in df.columns:
            df[self.COL_FECHA] = None

        # Dejar solo las columnas necesarias
        df = df[
            [
                self.COL_ROL,
                self.COL_COMUNA,
                self.COL_FECHA,
            ]
        ].copy()

        # Limpiar datos
        df["PART_TCOMUNA"] = df[self.COL_COMUNA].apply(self.clean_text)
        df["TIPO_PARTICIPANTE"] = df[self.COL_ROL].apply(self.map_tipo_participante)
        df["FECHA_REGISTRO"] = df[self.COL_FECHA].apply(self.obtener_fecha)

        # Quitar filas sin comuna
        df = df[df["PART_TCOMUNA"] != ""]

        # Crear objetos para guardar en BD
        participantes = [
            ParticipanteMapa(
                comuna=row["PART_TCOMUNA"],
                tipo_participante=row["TIPO_PARTICIPANTE"],
                fecha=row["FECHA_REGISTRO"],
                origen="EXCEL",
            )
            for _, row in df.iterrows()
        ]

        # Eliminado masivo
        ParticipanteMapa.objects.filter(origen="EXCEL").delete()
        # Guardado masivo
        ParticipanteMapa.objects.bulk_create(participantes)

        return len(participantes)
