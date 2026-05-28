from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.paths import datos_csv, ensure_project_on_syspath, resultados_dir  # noqa: E402

ensure_project_on_syspath()

from scripts.clima.importacion import leer_csv_clima, solo_columnas  # noqa: E402


def main() -> int:
    """
    CLI de utilidad para validar la importación.

    Este script sirve para:
    - comprobar que el CSV se lee bien
    - ver una muestra rápida (preview)
    - opcionalmente exportar las columnas extraídas a JSON
    """
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Importa datos climáticos desde un CSV.")
    parser.add_argument(
        "-i",
        "--input",
        default="",
        help="Ruta del CSV de entrada (por defecto: datos/clima_datos.csv en el repo)",
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
        help="Nombre o ruta del JSON de salida (relativo a resultados/ si no es absoluta)",
    )

    args = parser.parse_args()

    out_dir = resultados_dir()

    csv_path = datos_csv() if not args.input else Path(args.input)
    if not csv_path.exists():
        print(f"Error: no se encontró el archivo: {csv_path}")
        return 1

    records = leer_csv_clima(csv_path, encoding=args.encoding)
    cols = solo_columnas(records)

    print(f"Archivo: {csv_path}")
    print(f"Registros: {len(records)}")
    print(f"Columnas extraídas: {', '.join([k for k, v in cols.items() if len(v) > 0])}")
    print("")
    print("Preview (primeras filas):")
    for r in records[: max(args.preview, 0)]:
        print(r)

    if args.to_json:
        out = Path(args.to_json)
        if not out.is_absolute():
            out = out_dir / out.name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(cols, ensure_ascii=False, indent=2), encoding="utf-8")
        print("")
        print(f"JSON guardado en: {out}")

    print("")
    print("Análisis completado correctamente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
