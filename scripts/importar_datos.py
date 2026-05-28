from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Permite ejecutar el script directo: `python scripts/importar_datos.py`
# (en ese caso, el root del proyecto no queda automáticamente en sys.path).
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.clima.importacion import leer_csv_clima, solo_columnas  # noqa: E402


def main() -> int:
    """
    CLI de utilidad para validar la importación.

    Este script sirve para:
    - comprobar que el CSV se lee bien
    - ver una muestra rápida (preview)
    - opcionalmente exportar las columnas extraídas a JSON
    """
    # Evita caracteres raros en Windows al imprimir acentos (si la terminal lo permite).
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Importa datos climáticos desde un CSV.")
    parser.add_argument(
        "-i",
        "--input",
        default=str(Path("datos") / "clima_datos.csv"),
        help="Ruta del CSV de entrada (por defecto: datos/clima_datos.csv)",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Encoding del archivo CSV (por defecto: utf-8)",
    )
    parser.add_argument(
        "--preview",
        type=int,
        default=5,
        help="Cantidad de filas a mostrar como preview (por defecto: 5)",
    )
    parser.add_argument(
        "--to-json",
        default="",
        help="Si se setea, guarda un JSON con columnas extraídas en esta ruta.",
    )
    parser.add_argument(
        "--resultados-dir",
        default="resultados",
        help="Directorio donde se guardan salidas (por defecto: resultados/)",
    )

    args = parser.parse_args()

    # Estandarizamos una carpeta de salida (útil para local y Colab).
    resultados_dir = Path(args.resultados_dir)
    resultados_dir.mkdir(parents=True, exist_ok=True)

    # Importación: leer y tipar (todavía sin cálculos de indicadores).
    records = leer_csv_clima(args.input, encoding=args.encoding)

    # Estructura alternativa (columnas como listas) para facilitar análisis posterior.
    cols = solo_columnas(records)

    print(f"Archivo: {args.input}")
    print(f"Registros: {len(records)}")
    print(f"Columnas extraídas: {', '.join([k for k, v in cols.items() if len(v) > 0])}")
    print("")
    print("Preview (primeras filas):")
    for r in records[: max(args.preview, 0)]:
        print(r)

    if args.to_json:
        out = Path(args.to_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(cols, ensure_ascii=False, indent=2), encoding="utf-8")
        print("")
        print(f"JSON guardado en: {out}")

    print("")
    print("Análisis completado correctamente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

