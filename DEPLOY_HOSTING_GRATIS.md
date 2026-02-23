# Hosting gratis para la app Dispo (Flask)

Tu app actual (Flask + Python + pandas + Excel) puede desplegarse en varios hostings con plan gratuito. La app debe estar en **GitHub** (o GitLab) para conectar y desplegar.

---

## 1. Render (recomendado)

**Ventajas:** Fácil, 750 h/mes gratis, soporta Flask y pandas. No pide tarjeta para el tier gratis.  
**Desventaja:** El servicio “duerme” tras ~15 min sin uso; la primera petición tras dormir tarda 30–60 s en responder.

### Pasos

1. **Sube el proyecto a GitHub** (solo la app Flask, no hace falta la carpeta `firebase/` ni `public/` si no usas Firebase):
   - Crea un repo en GitHub y sube: `app.py`, `excel_processor.py`, `requirements.txt`, `Procfile`, carpeta `templates/`.

2. Entra en [render.com](https://render.com) e inicia sesión con GitHub.

3. **New → Web Service**.

4. Conecta el repositorio donde está la app y configura:
   - **Name:** `dispo` (o el que quieras).
   - **Runtime:** Python 3.
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT app:app`  
     (o deja que use el `Procfile` si Render lo detecta).
   - **Plan:** Free.

5. **Create Web Service**. Render construye y despliega; al terminar te da una URL tipo `https://dispo-xxxx.onrender.com`.

6. Abre esa URL: es tu app funcionando (subir 3 Excel, procesar, exportar, copiar, WhatsApp).

**Importante:** En el tier gratis, el servicio se duerme con la inactividad. La primera vez que alguien entre después de un rato puede tardar medio minuto en cargar.

---

## 2. Railway

**Ventajas:** Muy fácil desde GitHub, entorno moderno.  
**Desventaja:** El plan gratuito suele dar créditos limitados al mes (ej. 5 USD); si te pasas, pide tarjeta o se para.

1. Entra en [railway.app](https://railway.app) y inicia sesión con GitHub.
2. **New Project → Deploy from GitHub repo** y elige el repo de la app.
3. Railway detecta Python; si no, en **Settings** pon:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn --bind 0.0.0.0:$PORT app:app`
4. En **Settings → Networking** genera un dominio público.
5. Despliega; tu app quedará en una URL tipo `https://xxx.up.railway.app`.

---

## 3. PythonAnywhere

**Ventajas:** Pensado para Python, tier gratis clásico.  
**Desventaja:** Configuración más manual (consola web, WSGI, etc.) y límites en el plan gratis.

1. Crea cuenta en [pythonanywhere.com](https://www.pythonanywhere.com) (plan Beginner / gratis).
2. Sube los archivos (o clona desde GitHub) en tu cuenta.
3. Crea una **Web app** (Flask), apunta al directorio del proyecto y al archivo `app.py` (WSGI).
4. En la pestaña **Virtualenv** crea un venv e instala: `pip install -r requirements.txt`.
5. Recarga la app y usa la URL que te dan (ej. `tuusuario.pythonanywhere.com`).

---

## Resumen rápido

| Servicio        | Plan gratis        | Dormir / límites        | Dificultad   |
|-----------------|--------------------|-------------------------|-------------|
| **Render**      | Sí, sin tarjeta    | Se duerme ~15 min       | Fácil       |
| **Railway**     | Créditos mensuales | Límite de uso al mes    | Fácil       |
| **PythonAnywhere** | Sí                | Límites de CPU/tráfico  | Media       |

Para tener la app actual funcionando en hosting gratis, la opción más directa es **Render**: mismo código, `Procfile` y `requirements.txt` que ya tienes, y despliegue desde GitHub en pocos clics.
