# excel_processor.py - Lógica de unión y transformación de los 3 Excel

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


def process_three_files(path1: str, path2: str, path3: str) -> pd.DataFrame:
    """
    Une los 3 archivos Excel y aplica las reglas:
    - Unir en una hoja
    - Eliminar columnas C, E, G, I
    - Cap # Cajas a máximo 6
    - Ordenar por Tipo flor y Variedad
    - Agrupar por Tipo flor con fila vacía y título en A entre grupos
    - Eliminar columna Tipo flor
    """
    dfs = []
    for path in (path1, path2, path3):
        df = load_excel(path)
        dfs.append(df)

    # 1. Unir los 3 archivos
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

    # 4. Ordenar por "Tipo flor" y luego "Variedad"
    tipo_col = _find_column(consolidated, "tipo flor", "Tipo flor", "Tipo Flor")
    variedad_col = _find_column(consolidated, "variedad", "Variedad")

    if tipo_col is not None and variedad_col is not None:
        consolidated = consolidated.sort_values(by=[tipo_col, variedad_col], na_position="last")
    elif tipo_col is not None:
        consolidated = consolidated.sort_values(by=[tipo_col], na_position="last")

    # 5. Separar cada grupo de "Tipo flor": primero ROSAS, luego el resto en orden alfabético
    if tipo_col is None:
        return consolidated

    result_rows = []
    first_col_name = consolidated.columns[0]
    groups = list(consolidated.groupby(tipo_col, sort=False))

    def _order_tipo(t):
        name = str(t).strip().upper() if pd.notna(t) else ""
        if name == "ROSAS":
            return (0, name)
        return (1, name)

    groups.sort(key=lambda g: _order_tipo(g[0]))
    n_groups = len(groups)

    for i, (tipo, group) in enumerate(groups):
        # Título del tipo de flor en la celda A (primera columna) antes de cada grupo
        title_row = {first_col_name: str(tipo).strip() if pd.notna(tipo) else ""}
        for c in consolidated.columns:
            if c != first_col_name:
                title_row[c] = ""
        result_rows.append(pd.DataFrame([title_row]))
        result_rows.append(group)
        # 1 fila vacía entre cada tipo (no después del último)
        if i < n_groups - 1:
            empty_row = {c: "" for c in consolidated.columns}
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
