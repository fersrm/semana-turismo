import pandas as pd

from unidecode import unidecode
from django.db import transaction

from MapaApp.models import ParticipanteMapa


class ExcelAdapter:
    COL_ROL = "Indique que tipo de participante es:"
    COL_COMUNA = "Comuna"
    COL_FECHA = "Hora de inicio"

    def clean_text(self, value):
        if pd.isna(value):
            return ""

        if isinstance(value, str):
            return unidecode(value.upper().strip())

        return str(value).strip()

    def map_tipo_participante(self, rol):
        rol_limpio = self.clean_text(rol)

        if rol_limpio in {
            "EMPRENDEDOR/EMPRESA",
            "EMPRENDEDOR",
            "EMPRESA",
        }:
            return "EMPRENDEDOR"

        return "ASISTENTE"

    def obtener_fecha(self, valor_fecha, fecha_evento):
        if pd.isna(valor_fecha) or valor_fecha == "":
            return fecha_evento

        fecha = pd.to_datetime(valor_fecha, errors="coerce")

        if pd.isna(fecha):
            return fecha_evento

        return fecha.date()

    def process_excel_file(self, document, evento):
        df = pd.read_excel(document)

        columnas_requeridas = [self.COL_ROL, self.COL_COMUNA]
        faltantes = [
            columna for columna in columnas_requeridas if columna not in df.columns
        ]

        if faltantes:
            raise ValueError(
                "El Excel no contiene las columnas requeridas: " + ", ".join(faltantes)
            )

        if self.COL_FECHA not in df.columns:
            df[self.COL_FECHA] = None

        df = df[
            [
                self.COL_ROL,
                self.COL_COMUNA,
                self.COL_FECHA,
            ]
        ].copy()

        df["PART_TCOMUNA"] = df[self.COL_COMUNA].apply(self.clean_text)
        df["TIPO_PARTICIPANTE"] = df[self.COL_ROL].apply(self.map_tipo_participante)
        df["FECHA_REGISTRO"] = df[self.COL_FECHA].apply(
            lambda fecha: self.obtener_fecha(fecha, evento.fecha_evento)
        )

        df = df[df["PART_TCOMUNA"] != ""]

        participantes = [
            ParticipanteMapa(
                evento=evento,
                comuna=row["PART_TCOMUNA"],
                tipo_participante=row["TIPO_PARTICIPANTE"],
                fecha=row["FECHA_REGISTRO"],
                origen="EXCEL",
            )
            for _, row in df.iterrows()
        ]

        with transaction.atomic():
            # Solo reemplaza la carga Excel del evento seleccionado.
            # No toca otros eventos ni registros manuales.
            ParticipanteMapa.objects.filter(
                evento=evento,
                origen="EXCEL",
            ).delete()

            ParticipanteMapa.objects.bulk_create(participantes)

        return len(participantes)
