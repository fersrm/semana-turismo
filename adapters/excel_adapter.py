import pandas as pd
from unidecode import unidecode
from django.conf import settings
import os
import json


class ExcelAdapter:
    # Nombres reales de columnas en el Excel
    COL_ROL = "¿Desde qué rol nos acompañas hoy?"
    COL_COMUNA = "Indique comuna de la organización o empresa que representa"

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

    def process_excel_file(self, document):
        df = pd.read_excel(document)

        # Dejar solo las columnas necesarias
        df = df[
            [
                self.COL_ROL,
                self.COL_COMUNA,
            ]
        ].copy()

        # Limpiar comuna y rol
        df["PART_TCOMUNA"] = df[self.COL_COMUNA].apply(self.clean_text)
        df["TIPO_PARTICIPANTE"] = df[self.COL_ROL].apply(self.map_tipo_participante)

        # Quitar filas sin comuna
        df = df[df["PART_TCOMUNA"] != ""]

        # Resumen por comuna y tipo
        resumen = (
            df.groupby(["PART_TCOMUNA", "TIPO_PARTICIPANTE"])
            .size()
            .unstack(fill_value=0)
            .reset_index()
        )

        if "EMPRENDEDOR" not in resumen.columns:
            resumen["EMPRENDEDOR"] = 0
        if "ASISTENTE" not in resumen.columns:
            resumen["ASISTENTE"] = 0

        resumen["TOTAL"] = resumen["EMPRENDEDOR"] + resumen["ASISTENTE"]

        # Detalle simple
        detalle = df[
            ["PART_TCOMUNA", "TIPO_PARTICIPANTE"]
        ].rename(columns={"TIPO_PARTICIPANTE": "TIPO"})

        data = {
            "resumen": resumen.to_dict(orient="records"),
            "detalle": detalle.to_dict(orient="records"),
        }

        json_path = os.path.join(settings.MEDIA_ROOT, "json", "data.json")
        os.makedirs(os.path.dirname(json_path), exist_ok=True)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return json_path