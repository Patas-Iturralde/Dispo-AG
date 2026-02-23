#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App web local para unir 3 archivos Excel en uno siguiendo las reglas de negocio.
No requiere tkinter; se abre en el navegador.
"""

import io
import os
import tempfile
from pathlib import Path

from flask import Flask, request, render_template, send_file, flash, redirect, url_for

from excel_processor import process_three_files, dataframe_to_clipboard_text

app = Flask(__name__)
app.secret_key = "dispo-ag-secret"

# Resultado del último procesamiento (en memoria para esta sesión)
_result_df = None
_result_tsv = None
_result_tsv_no_header = None  # para copiar/editar sin cabecera


@app.route("/")
def index():
    global _result_df, _result_tsv, _result_tsv_no_header
    result_ready = _result_df is not None
    row_count = len(_result_df) if _result_df is not None else 0
    return render_template(
        "index.html",
        result_ready=result_ready,
        row_count=row_count,
        result_tsv_no_header=_result_tsv_no_header or "",
    )


@app.route("/process", methods=["POST"])
def process():
    global _result_df, _result_tsv, _result_tsv_no_header
    f1 = request.files.get("file1")
    f2 = request.files.get("file2")
    f3 = request.files.get("file3")
    if not all([f1, f2, f3]) or not all([f1.filename, f2.filename, f3.filename]):
        flash("Debes seleccionar los 3 archivos.", "error")
        return redirect(url_for("index"))

    # Guardar temporales para que el procesador los lea por ruta
    tmpdir = tempfile.mkdtemp()
    paths = []
    try:
        for i, f in enumerate([f1, f2, f3]):
            ext = Path(f.filename).suffix or ".xls"
            path = os.path.join(tmpdir, f"upload_{i}{ext}")
            f.save(path)
            paths.append(path)
        _result_df = process_three_files(paths[0], paths[1], paths[2])
        _result_tsv = dataframe_to_clipboard_text(_result_df, include_header=True)
        _result_tsv_no_header = dataframe_to_clipboard_text(_result_df, include_header=False)
        flash(f"Procesado correctamente: {len(_result_df)} filas.", "success")
    except FileNotFoundError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        for p in paths:
            try:
                os.unlink(p)
            except OSError:
                pass
        try:
            os.rmdir(tmpdir)
        except OSError:
            pass
    return redirect(url_for("index"))


@app.route("/reset")
def reset():
    """Limpia el resultado en memoria y vuelve al inicio."""
    global _result_df, _result_tsv, _result_tsv_no_header
    _result_df = None
    _result_tsv = None
    _result_tsv_no_header = None
    return redirect(url_for("index"))


@app.route("/download")
def download_excel():
    global _result_df
    if _result_df is None:
        flash("No hay datos para exportar. Procesa los 3 archivos primero.", "error")
        return redirect(url_for("index"))
    buf = io.BytesIO()
    _result_df.to_excel(buf, index=False, engine="openpyxl")
    buf.seek(0)
    return send_file(
        buf,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="dispo_consolidado.xlsx",
    )


if __name__ == "__main__":
    print("Abre en el navegador: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
