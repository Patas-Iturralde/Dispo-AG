# Unir 3 Excel → Dispo

Aplicación web local en Python que une 3 archivos Excel en uno solo aplicando las reglas de negocio (columnas A–I, eliminar C/E/G/I, máximo 6 cajas, orden por Tipo flor y Variedad, títulos y separaciones entre grupos, eliminar columna Tipo flor). **No usa tkinter**: se abre en el navegador.

## Requisitos

- Python 3.8+
- Dependencias: `pandas`, `openpyxl`, `xlrd`, `flask`

## Instalación

En la carpeta del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate   # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución

```bash
python app.py
```

Luego abre en el navegador: **http://127.0.0.1:5000**

## Uso

1. Elige los 3 archivos Excel (por ejemplo `fileXLS.xls`, `fileXLS (1).xls`, `fileXLS (2).xls`).
2. Pulsa **Unir y procesar**. Se unen los 3 archivos y se aplican las reglas.
3. **Exportar a Excel**: descarga el archivo `.xlsx`.
4. **Copiar al portapapeles**: selecciona todo el texto de la caja que aparece y cópialo (Cmd+C / Ctrl+C); luego pega en Excel.

El resultado sigue el mismo criterio que el archivo de ejemplo `dispo 23.01.xlsx`.

---

## Publicar en Firebase (hosting gratis)

Puedes desplegar la app en **Firebase Hosting** + **Cloud Functions** (Python) para usarla desde una URL pública. Ver **[DEPLOY_FIREBASE.md](DEPLOY_FIREBASE.md)** para los pasos (crear proyecto, `firebase use`, `firebase deploy`).  
La carpeta `public/` y `functions/` ya están preparadas para el despliegue.

## Hosting gratis (app Flask completa)

Para tener la app actual (Flask + Excel) en la nube **sin pagar** y sin depender de Firebase Blaze: **[DEPLOY_HOSTING_GRATIS.md](DEPLOY_HOSTING_GRATIS.md)**. Incluye pasos para **Render**, **Railway** y **PythonAnywhere**. El proyecto ya incluye `Procfile` y `gunicorn` para desplegar.
