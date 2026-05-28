from __future__ import annotations

import sys
from pathlib import Path

# Bootstrap mínimo: permite `python scripts/main.py` desde cualquier cwd (Colab/local).
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.paths import datos_csv, ensure_project_on_syspath, resultados_dir  # noqa: E402

ensure_project_on_syspath()

from scripts.clima.importacion import leer_csv_clima  # noqa: E402
from scripts.clima.indicadores import indicadores_a_texto, indicadores_para_anio  # noqa: E402
from scripts.clima.graficos import generar_grafico_variacion_temperatura, obtener_rango_anos, validar_ano_en_dataset  # noqa: E402


def _pedir_opcion() -> str:
    """Lee la opción del menú elegida por el usuario."""
    return input("Elegí una opción: ").strip()


def _pedir_anio(*, min_year: int = 1940, max_year: int = 2025) -> int:
    """
    Solicita un año y valida que sea un entero dentro del rango permitido.

    Se repite hasta obtener un valor válido.
    """
    while True:
        raw = input(f"Ingresá un año ({min_year}-{max_year}): ").strip()
        try:
            year = int(raw)
        except ValueError:
            print("Año inválido. Ingresá un número entero.")
            continue

        if year < min_year or year > max_year:
            print(f"Año fuera de rango. Debe estar entre {min_year} y {max_year}.")
            continue

        return year


def _pedir_anio_validado(records, *, prompt: str = "Ingresá un año de inicio") -> int:
    """
    Solicita un año y valida que exista en el dataset.
    
    Args:
        records: Lista de registros para validación
        prompt: Mensaje personalizado para solicitar el año
    """
    try:
        min_year, max_year = obtener_rango_anos(records)
    except ValueError as e:
        raise ValueError(f"Error al obtener rango de años: {e}")
    
    while True:
        raw = input(f"{prompt} ({min_year}-{max_year}): ").strip()
        try:
            year = int(raw)
        except ValueError:
            print("Año inválido. Ingresá un número entero.")
            continue
        
        if not validar_ano_en_dataset(records, year):
            print(f"El año {year} no existe en el dataset. Disponible: {min_year}-{max_year}")
            continue
            
        return year


def main() -> int:
    """
    Punto de entrada del menú.

    Por simplicidad cargamos el CSV una sola vez y reusamos los registros en memoria.
    """
    # Evita caracteres raros en Windows al imprimir acentos (si la terminal lo permite).
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass

    out_dir = resultados_dir()

    # Rutas absolutas respecto al repo (compatible con Colab sin depender del cwd).
    csv_path = datos_csv()
    if not csv_path.exists():
        print(f"Error: no se encontró el archivo de datos: {csv_path}")
        print("Verificá que exista datos/clima_datos.csv en el proyecto.")
        return 1

    records = leer_csv_clima(csv_path)

    while True:
        print("")
        print("=== Menú - Análisis Climático ===")
        print("1) Obtener indicadores para un año")
        print("2) Generar gráfico de variación de temperatura")
        print("3) Salir")
        print("")

        opcion = _pedir_opcion()

        if opcion == "1":
            year = _pedir_anio()
            try:
                ind = indicadores_para_anio(records, year)
            except ValueError as e:
                print(f"Error: {e}")
                continue

            contenido = indicadores_a_texto(ind)
            print("")
            print(contenido)

            # Guardamos el mismo contenido mostrado por pantalla para trazabilidad.
            out_path = out_dir / f"indicadores_{year}.txt"
            out_path.write_text(contenido + "\n", encoding="utf-8")
            print(f"\nArchivo generado: {out_path}")

        elif opcion == "2":
            print("\n--- Generar Gráfico de Variación de Temperatura ---")
            try:
                year_inicio = _pedir_anio_validado(
                    records, 
                    prompt="Ingresá el año de inicio para el gráfico"
                )
                
                print(f"\nGenerando gráfico desde {year_inicio} hasta el final del dataset...")
                
                grafico_path = generar_grafico_variacion_temperatura(records, year_inicio)
                
                print(f"✓ Gráfico generado exitosamente!")
                print(f"📊 Archivo: {grafico_path}")
                print(f"📁 Ubicación: {grafico_path.resolve()}")
                
            except ValueError as e:
                print(f"Error: {e}")
                continue
            except ImportError as e:
                print(f"Error: {e}")
                print("\nNota: En Google Colab, matplotlib está disponible por defecto.")
                print("En entorno local, instálalo con: pip install matplotlib")
                continue
            except Exception as e:
                print(f"Error inesperado al generar el gráfico: {e}")
                continue

        elif opcion == "3":
            print("Saliendo...")
            return 0
        else:
            print("Opción inválida. Probá nuevamente.")


if __name__ == "__main__":
    raise SystemExit(main())
