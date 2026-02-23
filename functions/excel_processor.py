# excel_processor.py - Lógica de unión y transformación de los 3 Excel

import pandas as pd
from pathlib import Path


def _normalize_column_name(name):
    if pd.isna(name):
        return ""
    return str(name).strip().lower()


def _find_column(df, *candidates):
    normalized = {_normalize_column_name(c): c for c in candidates}
    for col in df.columns:
        nc = _normalize_column_name(col)
        if nc in normalized or any(cand in nc for cand in [c.lower() for c in candidates]):
            return col
    return None


def load_excel(path: str) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")
    df = pd.read_excel(path, usecols="A:I", engine="xlrd" if path.suffix.lower() == ".xls" else "openpyxl")
    return df


def process_three_files(path1: str, path2: str, path3: str) -> pd.DataFrame:
    dfs = []
    for path in (path1, path2, path3):
        df = load_excel(path)
        dfs.append(df)

    consolidated = pd.concat(dfs, ignore_index=True)

    if len(consolidated.columns) > 9:
        consolidated = consolidated.iloc[:, :9]
    elif len(consolidated.columns) < 9:
        for i in range(len(consolidated.columns), 9):
            consolidated.insert(i, f"Col_{i}", None)

    cols_to_drop = [2, 4, 6, 8]
    names_to_drop = [consolidated.columns[i] for i in cols_to_drop if i < len(consolidated.columns)]
    consolidated = consolidated.drop(columns=names_to_drop)

    cajas_col = _find_column(consolidated, "# cajas", "cajas", "Cajas", "# Cajas")
    if cajas_col is not None:
        consolidated[cajas_col] = pd.to_numeric(consolidated[cajas_col], errors="coerce").fillna(0).astype(int)
        consolidated[cajas_col] = consolidated[cajas_col].clip(upper=6)

    tipo_col = _find_column(consolidated, "tipo flor", "Tipo flor", "Tipo Flor")
    variedad_col = _find_column(consolidated, "variedad", "Variedad")

    if tipo_col is not None and variedad_col is not None:
        consolidated = consolidated.sort_values(by=[tipo_col, variedad_col], na_position="last")
    elif tipo_col is not None:
        consolidated = consolidated.sort_values(by=[tipo_col], na_position="last")

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
        title_row = {first_col_name: str(tipo).strip() if pd.notna(tipo) else ""}
        for c in consolidated.columns:
            if c != first_col_name:
                title_row[c] = ""
        result_rows.append(pd.DataFrame([title_row]))
        result_rows.append(group)
        if i < n_groups - 1:
            empty_row = {c: "" for c in consolidated.columns}
            result_rows.append(pd.DataFrame([empty_row]))

    if not result_rows:
        return consolidated

    result = pd.concat(result_rows, ignore_index=True)
    if tipo_col in result.columns:
        result = result.drop(columns=[tipo_col])
    return result


def dataframe_to_clipboard_text(df: pd.DataFrame, include_header: bool = True) -> str:
    return df.to_csv(sep="\t", index=False, header=include_header, encoding="utf-8")
