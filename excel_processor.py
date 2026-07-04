# excel_processor.py - Lógica de unión y transformación de los Excel

import re
import pandas as pd
from pathlib import Path


def _normalize_column_name(name):
    """Normaliza nombre de columna para búsqueda."""
    if pd.isna(name):
        return ""
    return str(name).strip().lower()


def _find_column(df, *candidates):
    """Busca una columna por varios nombres posibles."""
    normalized = {_normalize_column_name(c): c for c in candidates}
    for col in df.columns:
        nc = _normalize_column_name(col)
        if nc in normalized or any(cand in nc for cand in [c.lower() for c in candidates]):
            return col
    return None


def load_excel(path: str) -> pd.DataFrame:
    """Carga un archivo .xls o .xlsx en un DataFrame.

    Se leen todas las columnas disponibles y más adelante se recorta
    a un máximo de 9 (A–I) para evitar errores cuando alguna hoja
    tiene menos columnas.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")
    df = pd.read_excel(path, engine="xlrd" if path.suffix.lower() == ".xls" else "openpyxl")
    return df


def _normalize_species(name) -> str:
    """Clave única por especie (sin distinguir mayúsculas)."""
    if pd.isna(name):
        return ""
    return str(name).strip().upper()


def _largo_numeric(val) -> int:
    """Extrae número de largo para ordenar (50, 60, 70…)."""
    if pd.isna(val):
        return 0
    m = re.search(r"\d+", str(val))
    return int(m.group()) if m else 0


def _order_tipo(tipo_norm: str):
    if tipo_norm == "ROSAS":
        return (0, tipo_norm)
    return (1, tipo_norm)


def process_three_files(*paths: str) -> pd.DataFrame:
    """
    Une los archivos Excel y aplica las reglas:
    - Unir en una hoja
    - Eliminar columnas C, E, G, I
    - Cap # Cajas a máximo 6
    - Ordenar por Variedad y Largo dentro de cada especie
    - Agrupar por Tipo flor (especie única) con fila vacía y título en A entre grupos
    - Eliminar columna Tipo flor
    """
    dfs = []
    for path in paths:
        df = load_excel(path)
        dfs.append(df)

    # 1. Unir todos los archivos
    consolidated = pd.concat(dfs, ignore_index=True)

    # Asegurar que tenemos al menos 9 columnas (A-I); si hay más, tomar las primeras 9
    if len(consolidated.columns) > 9:
        consolidated = consolidated.iloc[:, :9]
    elif len(consolidated.columns) < 9:
        # Rellenar con columnas vacías si vinieran menos
        for i in range(len(consolidated.columns), 9):
            consolidated.insert(i, f"Col_{i}", None)

    # 2. Eliminar columnas C, E, G, I (índices 2, 4, 6, 8 en 0-based)
    cols_to_drop = [2, 4, 6, 8]
    names_to_drop = [consolidated.columns[i] for i in cols_to_drop if i < len(consolidated.columns)]
    consolidated = consolidated.drop(columns=names_to_drop)

    # 3. Columna "# Cajas": máximo 6 por registro
    cajas_col = _find_column(consolidated, "# cajas", "cajas", "Cajas", "# Cajas")
    if cajas_col is not None:
        consolidated[cajas_col] = pd.to_numeric(consolidated[cajas_col], errors="coerce").fillna(0).astype(int)
        consolidated[cajas_col] = consolidated[cajas_col].clip(upper=6)

    # 4. Columnas de orden y agrupación
    tipo_col = _find_column(consolidated, "tipo flor", "Tipo flor", "Tipo Flor")
    variedad_col = _find_column(consolidated, "variedad", "Variedad")
    largo_col = _find_column(consolidated, "largo", "longitud", "cm", "Largo")

    if tipo_col is None:
        return consolidated

    consolidated["_tipo_norm"] = consolidated[tipo_col].apply(_normalize_species)

    result_rows = []
    first_col_name = consolidated.columns[0]
    groups = list(consolidated.groupby("_tipo_norm", sort=False))
    groups.sort(key=lambda g: _order_tipo(g[0]))
    n_groups = len(groups)

    for i, (tipo_norm, group) in enumerate(groups):
        group = group.copy()
        sort_cols = []
        if variedad_col:
            sort_cols.append(variedad_col)
        if largo_col:
            group["_largo_num"] = group[largo_col].apply(_largo_numeric)
            sort_cols.append("_largo_num")
        if sort_cols:
            group = group.sort_values(by=sort_cols, na_position="last")
        group = group.drop(columns=["_tipo_norm", "_largo_num"], errors="ignore")

        display_tipo = tipo_norm or (
            str(group[tipo_col].iloc[0]).strip() if len(group) else ""
        )
        title_row = {first_col_name: display_tipo}
        for c in consolidated.columns:
            if c.startswith("_") or c == first_col_name:
                continue
            title_row[c] = ""
        result_rows.append(pd.DataFrame([title_row]))
        result_rows.append(group.drop(columns=["_tipo_norm"], errors="ignore"))
        if i < n_groups - 1:
            empty_row = {c: "" for c in consolidated.columns if not str(c).startswith("_")}
            result_rows.append(pd.DataFrame([empty_row]))

    if not result_rows:
        return consolidated

    result = pd.concat(result_rows, ignore_index=True)

    # 6. Eliminar completamente la columna "Tipo flor"
    if tipo_col in result.columns:
        result = result.drop(columns=[tipo_col])

    return result


def export_to_excel(df: pd.DataFrame, path: str) -> None:
    """Exporta el DataFrame a un archivo .xlsx."""
    path = Path(path)
    df.to_excel(path, index=False, engine="openpyxl")


def dataframe_to_clipboard_text(df: pd.DataFrame, include_header: bool = True) -> str:
    """Convierte el DataFrame a texto tabular para portapapeles (TSV)."""
    return df.to_csv(sep="\t", index=False, header=include_header, encoding="utf-8")
