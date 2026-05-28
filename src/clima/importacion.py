from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class ClimaRecord:
    """
    Representa una fila del dataset ya importada y tipada.

    Nota: mantenemos campos "genéricos" (fecha/temperatura) además de los del CSV actual
    (year/min_temp/max_temp/precipitacion) para que el importador soporte distintos esquemas
    sin romper el resto del proyecto.
    """

    year: int | None
    fecha: str | None
    temperatura: float | None
    min_temp: float | None
    max_temp: float | None
    precipitacion: float | None

    # Diccionario original del CSV (útil para debug/columnas extra)
    raw: dict[str, Any]


def _to_int(value: Any) -> int | None:
    """Convierte a int; devuelve None si viene vacío."""
    if value is None:
        return None
    s = str(value).strip()
    if s == "":
        return None
    # Acepta "1940.0" o "1940" sin fallar.
    return int(float(s))


def _to_float(value: Any) -> float | None:
    """Convierte a float; devuelve None si viene vacío."""
    if value is None:
        return None
    s = str(value).strip()
    if s == "":
        return None
    return float(s)


def leer_csv_clima(path: str | Path, *, encoding: str = "utf-8") -> list[ClimaRecord]:
    """
    Lee un CSV de clima y devuelve registros tipados (sin calcular indicadores).

    Soporta (al menos) estos esquemas:
    - year,min_temp,max_temp,precipitacion
    - fecha,temperatura,precipitacion
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"No existe el archivo: {p}")

    with p.open("r", encoding=encoding, newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV sin encabezados (header).")

        records: list[ClimaRecord] = []
        for row in reader:
            # Normalizamos keys/values para tolerar headers con espacios.
            row_norm = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items() if k is not None}

            # Mapeo flexible de posibles nombres de columna.
            year = _to_int(row_norm.get("year"))
            fecha = row_norm.get("fecha") or row_norm.get("date")

            temperatura = _to_float(row_norm.get("temperatura") or row_norm.get("temp") or row_norm.get("temperature"))
            min_temp = _to_float(row_norm.get("min_temp") or row_norm.get("tmin") or row_norm.get("temp_min"))
            max_temp = _to_float(row_norm.get("max_temp") or row_norm.get("tmax") or row_norm.get("temp_max"))
            precipitacion = _to_float(
                row_norm.get("precipitacion") or row_norm.get("precip") or row_norm.get("precipitation")
            )

            records.append(
                ClimaRecord(
                    year=year,
                    fecha=fecha,
                    temperatura=temperatura,
                    min_temp=min_temp,
                    max_temp=max_temp,
                    precipitacion=precipitacion,
                    raw=row_norm,
                )
            )

    return records


def solo_columnas(records: Iterable[ClimaRecord]) -> dict[str, list[Any]]:
    """
    Devuelve listas por columna para facilitar el trabajo posterior.
    No calcula indicadores, solo extrae/acomoda datos.
    """
    years: list[int] = []
    fechas: list[str] = []
    temperaturas: list[float] = []
    min_temps: list[float] = []
    max_temps: list[float] = []
    precipitaciones: list[float] = []

    for r in records:
        if r.year is not None:
            years.append(r.year)
        if r.fecha is not None:
            fechas.append(r.fecha)
        if r.temperatura is not None:
            temperaturas.append(r.temperatura)
        if r.min_temp is not None:
            min_temps.append(r.min_temp)
        if r.max_temp is not None:
            max_temps.append(r.max_temp)
        if r.precipitacion is not None:
            precipitaciones.append(r.precipitacion)

    return {
        "year": years,
        "fecha": fechas,
        "temperatura": temperaturas,
        "min_temp": min_temps,
        "max_temp": max_temps,
        "precipitacion": precipitaciones,
    }

