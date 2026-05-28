from __future__ import annotations

from pathlib import Path
from typing import Iterable

from scripts.clima.importacion import ClimaRecord


def generar_grafico_variacion_temperatura(
    records: Iterable[ClimaRecord], 
    year_inicio: int,
    output_path: str | Path | None = None
) -> Path:
    """
    Genera un gráfico de variación de temperatura desde year_inicio hasta el final del dataset.
    
    Args:
        records: Lista de registros climáticos
        year_inicio: Año de inicio para el gráfico
        output_path: Ruta donde guardar el gráfico. Si es None, se genera automáticamente.
        
    Returns:
        Path al archivo del gráfico generado
        
    Raises:
        ValueError: Si year_inicio no está en el dataset
        ImportError: Si matplotlib no está disponible
    """
    try:
        import matplotlib
        import matplotlib.pyplot as plt
        # Usar backend no interactivo para compatibilidad con diferentes entornos
        matplotlib.use('Agg')
    except ImportError:
        raise ImportError(
            "matplotlib es requerido para generar gráficos. "
            "En Google Colab está disponible por defecto. "
            "En local, instálalo con: pip install matplotlib"
        )
    
    # Filtrar y ordenar registros desde year_inicio
    records_filtrados = [
        r for r in records 
        if r.year is not None and r.year >= year_inicio
        and r.min_temp is not None and r.max_temp is not None
    ]
    
    if not records_filtrados:
        raise ValueError(f"No hay datos disponibles desde el año {year_inicio}")
    
    # Ordenar por año
    records_filtrados.sort(key=lambda r: r.year)
    
    # Verificar que year_inicio está en el dataset
    years_disponibles = {r.year for r in records_filtrados}
    if year_inicio not in years_disponibles:
        raise ValueError(f"El año {year_inicio} no existe en el dataset")
    
    # Extraer datos para el gráfico
    years = [r.year for r in records_filtrados]
    temp_min = [r.min_temp for r in records_filtrados]
    temp_max = [r.max_temp for r in records_filtrados]
    temp_promedio = [(r.min_temp + r.max_temp) / 2 for r in records_filtrados]
    
    # Configurar el gráfico
    plt.figure(figsize=(12, 8))
    
    # Plotear las temperaturas
    plt.plot(years, temp_min, label='Temperatura Mínima', color='blue', linewidth=2, marker='o', markersize=3)
    plt.plot(years, temp_max, label='Temperatura Máxima', color='red', linewidth=2, marker='o', markersize=3)
    plt.plot(years, temp_promedio, label='Temperatura Promedio', color='green', linewidth=2, marker='o', markersize=3)
    
    # Rellenar el área entre min y max
    plt.fill_between(years, temp_min, temp_max, alpha=0.2, color='gray', label='Rango de Temperatura')
    
    # Configurar títulos y etiquetas
    plt.title(f'Variación de Temperatura desde {year_inicio} hasta {max(years)}', fontsize=16, fontweight='bold')
    plt.xlabel('Año', fontsize=12)
    plt.ylabel('Temperatura (°C)', fontsize=12)
    
    # Configurar la leyenda
    plt.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
    
    # Configurar la grilla
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Mejorar la visualización de los años en el eje x
    if len(years) > 20:
        # Si hay muchos años, mostrar solo algunos
        step = max(1, len(years) // 10)
        plt.xticks(years[::step], rotation=45)
    else:
        plt.xticks(years, rotation=45)
    
    # Ajustar el layout para evitar que se corten las etiquetas
    plt.tight_layout()
    
    # Determinar la ruta de salida
    if output_path is None:
        from scripts.paths import resultados_dir
        output_dir = resultados_dir()
        output_path = output_dir / f"variacion_temperatura_{year_inicio}_{max(years)}.png"
    else:
        output_path = Path(output_path)
    
    # Crear directorio si no existe
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Guardar el gráfico
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()  # Liberar memoria
    
    return output_path


def obtener_rango_anos(records: Iterable[ClimaRecord]) -> tuple[int, int]:
    """
    Obtiene el rango de años disponible en el dataset.
    
    Returns:
        Tupla (año_mínimo, año_máximo)
        
    Raises:
        ValueError: Si no hay datos válidos
    """
    years = [r.year for r in records if r.year is not None]
    
    if not years:
        raise ValueError("No hay datos de años válidos en el dataset")
    
    return min(years), max(years)


def validar_ano_en_dataset(records: Iterable[ClimaRecord], year: int) -> bool:
    """
    Valida si un año específico existe en el dataset.
    
    Args:
        records: Lista de registros climáticos
        year: Año a validar
        
    Returns:
        True si el año existe, False en caso contrario
    """
    return any(r.year == year for r in records if r.year is not None)