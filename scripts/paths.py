"""
Rutas del proyecto independientes del directorio de trabajo (cwd).

En Google Colab el cwd suele ser /content; si usamos rutas relativas simples
como Path("datos/...") fallan salvo que el usuario haga %cd al root.
Estas funciones siempre resuelven desde la ubicación del repositorio.
"""

from __future__ import annotations

import sys
from pathlib import Path


def project_root() -> Path:
    """Raíz del repo: carpeta que contiene scripts/, datos/ y resultados/."""
    return Path(__file__).resolve().parents[1]


def ensure_project_on_syspath() -> Path:
    """
    Agrega el root al sys.path para imports tipo `scripts.clima...`.

    Necesario al ejecutar `python scripts/main.py` o celdas sueltas en Colab.
    """
    root = project_root()
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    return root


def datos_csv(nombre: str = "clima_datos.csv") -> Path:
    """Ruta al CSV de entrada."""
    return project_root() / "datos" / nombre


def resultados_dir() -> Path:
    """Carpeta de salidas; la crea si no existe."""
    d = project_root() / "resultados"
    d.mkdir(parents=True, exist_ok=True)
    return d
