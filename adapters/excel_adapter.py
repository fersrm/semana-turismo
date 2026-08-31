import pandas as pd

from django.db import transaction
from unidecode import unidecode

from MapaApp.models import ConfiguracionMapa, ParticipanteMapa


class ExcelAdapter:
    def __init__(self):
        self.configuracion, _ = ConfiguracionMapa.objects.get_or_create(pk=1)

        self.col_rol = self.configuracion.columna_rol
        self.col_comuna = self.configuracion.columna_comuna
        self.col_fecha = self.configuracion.columna_fecha

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

        columnas_requeridas = [
            self.col_rol,
            self.col_comuna,
        ]

        faltantes = [
            columna for columna in columnas_requeridas if columna not in df.columns
        ]

        if faltantes:
            raise ValueError(
                "El Excel no contiene las columnas configuradas: "
                + ", ".join(faltantes)
            )

        if self.col_fecha not in df.columns:
            df[self.col_fecha] = None

        df = df[
            [
                self.col_rol,
                self.col_comuna,
                self.col_fecha,
            ]
        ].copy()

        df["PART_TCOMUNA"] = df[self.col_comuna].apply(self.clean_text)

        df["TIPO_PARTICIPANTE"] = df[self.col_rol].apply(self.map_tipo_participante)

        df["FECHA_REGISTRO"] = df[self.col_fecha].apply(
            lambda fecha: self.obtener_fecha(
                fecha,
                evento.fecha_evento,
            )
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
            ParticipanteMapa.objects.filter(
                evento=evento,
                origen="EXCEL",
            ).delete()

            ParticipanteMapa.objects.bulk_create(participantes)

        return len(participantes)
