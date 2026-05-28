from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.clima.importacion import ClimaRecord


@dataclass(frozen=True)
class IndicadoresAnio:
    """Indicadores climáticos calculados para un año."""

    year: int
    temperatura_promedio: float
    temperatura_maxima: float
    temperatura_minima: float
    precipitacion_promedio: float


def indicadores_para_anio(records: Iterable[ClimaRecord], year: int) -> IndicadoresAnio:
    """
    Calcula indicadores para un año específico.

    Importante: en el CSV actual hay 1 fila por año y las columnas son:
    - min_temp
    - max_temp
    - precipitacion

    Por eso:
    - temperatura_promedio = (min_temp + max_temp) / 2
    - temperatura_maxima = max_temp
    - temperatura_minima = min_temp
    - precipitacion_promedio = precipitacion
    """
    # En el CSV actual hay una fila por año, así que buscamos ese registro.
    row = next((r for r in records if r.year == year), None)
    if row is None:
        raise ValueError(f"No hay datos para el año {year}.")

    # Validaciones mínimas para evitar cálculos con valores faltantes.
    if row.min_temp is None or row.max_temp is None:
        raise ValueError(f"Faltan datos de temperatura para el año {year}.")
    if row.precipitacion is None:
        raise ValueError(f"Faltan datos de precipitación para el año {year}.")

    # Definición del promedio según el esquema disponible (min/max por año).
    temp_prom = (row.min_temp + row.max_temp) / 2
    return IndicadoresAnio(
        year=year,
        temperatura_promedio=temp_prom,
        temperatura_maxima=row.max_temp,
        temperatura_minima=row.min_temp,
        precipitacion_promedio=row.precipitacion,
    )


def indicadores_a_texto(ind: IndicadoresAnio) -> str:
    """
    Formatea indicadores para mostrar/guardar.

    La idea es reutilizar exactamente el mismo texto tanto para imprimirlo por pantalla
    como para guardarlo en `resultados/indicadores_<año>.txt`.
    """
    return "\n".join(
        [
            f"Año: {ind.year}",
            f"Temperatura promedio: {ind.temperatura_promedio:.3f}",
            f"Temperatura máxima: {ind.temperatura_maxima:.3f}",
            f"Temperatura mínima: {ind.temperatura_minima:.3f}",
            f"Promedio precipitaciones: {ind.precipitacion_promedio:.3f}",
        ]
    )

