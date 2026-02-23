# Desplegar Dispo en Firebase (gratis)

La app se puede publicar en **Firebase Hosting** (HTML estático) + **Cloud Functions** (Python para procesar los Excel). El plan gratuito de Firebase incluye Hosting y un cupo de invocaciones de funciones.

## Requisitos

- Cuenta de [Firebase](https://console.firebase.google.com/)
- [Node.js](https://nodejs.org/) (para la CLI de Firebase)
- [Firebase CLI](https://firebase.google.com/docs/cli): `npm install -g firebase-tools`

**Nota:** Para usar Cloud Functions en producción hace falta el plan **Blaze** (pago por uso). Sigue habiendo [cuota gratuita](https://firebase.google.com/pricing) de invocaciones y GB; solo se paga si se supera.

## Pasos

### 1. Crear proyecto en Firebase

1. Entra en [Firebase Console](https://console.firebase.google.com/).
2. Crea un proyecto nuevo (o elige uno existente).
3. Anota el **ID del proyecto** (ej: `mi-proyecto-dispo`).

### 2. Configurar el proyecto local

En la raíz del repo (carpeta `Dispo AG`):

```bash
# Iniciar sesión en Firebase (abre el navegador)
firebase login

# Usar tu proyecto
firebase use TU_PROJECT_ID
```

Sustituye `TU_PROJECT_ID` por el ID de tu proyecto.  
También puedes editar `.firebaserc` y poner tu ID en `"default": "TU_PROJECT_ID"`.

### 3. Desplegar

```bash
firebase deploy
```

Se desplegarán:

- **Hosting:** la carpeta `public/` (página estática).
- **Functions:** la carpeta `functions/` (función Python `processFiles`).

La primera vez que despliegues funciones puede tardar varios minutos (instalación de dependencias Python).

### 4. URLs

Al terminar, la CLI mostrará algo como:

- **Sitio web:** `https://TU_PROJECT_ID.web.app` (o `https://TU_PROJECT_ID.firebaseapp.com`)
- La ruta `/process` del mismo dominio llama a la Cloud Function gracias al rewrite en `firebase.json`.

Abre la URL del Hosting en el navegador y usa la app como siempre.

## Estructura para Firebase

- `firebase.json` – Configuración de Hosting y Functions (rewrite `/process` → función).
- `.firebaserc` – ID del proyecto (cambiar `TU_PROJECT_ID`).
- `public/index.html` – Página estática que envía los 3 archivos a `/process` por POST y muestra el resultado.
- `functions/main.py` – Cloud Function que recibe los archivos, ejecuta la lógica de `excel_processor` y devuelve JSON (texto + Excel en base64).
- `functions/excel_processor.py` – Misma lógica que en la app Flask local.
- `functions/requirements.txt` – Dependencias Python de la función.

## Solo Hosting (sin funciones)

Si quieres desplegar solo la página estática (sin procesar Excel en la nube):

```bash
firebase deploy --only hosting
```

En ese caso la app no podrá procesar archivos; necesitas desplegar también las funciones para que funcione el “Unir y procesar”.

## Solución de problemas

- **“Permission denied” o “Billing”:** Cloud Functions requiere plan Blaze. Activa facturación en la consola de Google Cloud del proyecto; la cuota gratuita suele ser suficiente para uso personal.
- **Error al desplegar functions:** Comprueba que en la carpeta `functions/` existan `main.py`, `excel_processor.py` y `requirements.txt`, y que tengas Python 3.10–3.12 instalado (la CLI lo usa para empaquetar).
- **CORS:** La función ya envía cabeceras CORS; si usas otro dominio para el front, puede que tengas que ajustar `Access-Control-Allow-Origin` en `functions/main.py`.
