# Cloud Function: procesa archivos Excel y devuelve resultado + Excel en base64

import base64
import io
import os
import tempfile
from werkzeug.utils import secure_filename

import functions_framework
from flask import jsonify

from excel_processor import process_three_files, dataframe_to_clipboard_text


def _cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }


@functions_framework.http
def processFiles(request):
    if request.method == "OPTIONS":
        return ("", 204, _cors_headers())

    if request.method != "POST":
        return (jsonify({"success": False, "error": "Método no permitido"}), 405, _cors_headers())

    f1 = request.files.get("file1")
    f2 = request.files.get("file2")
    f3 = request.files.get("file3")
    f4 = request.files.get("file4")
    uploaded = [f for f in (f1, f2, f3, f4) if f and f.filename]

    if not uploaded:
        return (
            jsonify({"success": False, "error": "Debes seleccionar al menos 1 archivo."}),
            400,
            _cors_headers(),
        )

    tmpdir = tempfile.mkdtemp()
    paths = []
    try:
        for i, f in enumerate(uploaded):
            ext = os.path.splitext(secure_filename(f.filename) or "file")[1] or ".xls"
            path = os.path.join(tmpdir, f"upload_{i}{ext}")
            f.save(path)
            paths.append(path)

        df = process_three_files(*paths)
        result_tsv_no_header = dataframe_to_clipboard_text(df, include_header=False)

        buf = io.BytesIO()
        df.to_excel(buf, index=False, engine="openpyxl")
        buf.seek(0)
        excel_base64 = base64.b64encode(buf.getvalue()).decode("ascii")

        return (
            jsonify({
                "success": True,
                "row_count": len(df),
                "result_tsv_no_header": result_tsv_no_header,
                "excel_base64": excel_base64,
            }),
            200,
            _cors_headers(),
        )
    except Exception as e:
        return (
            jsonify({"success": False, "error": str(e)}),
            500,
            _cors_headers(),
        )
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
