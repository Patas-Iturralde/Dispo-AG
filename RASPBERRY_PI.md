# Correr Dispo en una Raspberry Pi como servidor

La app Flask (Python + pandas + Excel) funciona en una Raspberry Pi. Puedes usarla en la red local desde el navegador de cualquier dispositivo.

## Requisitos

- Raspberry Pi 3 o 4 (recomendado 2 GB RAM o más).
- Raspberry Pi OS (o cualquier Linux en la Pi).

## Instalación en la Pi

### 1. Clonar o copiar el proyecto

Si tienes el repo en GitHub:

```bash
cd ~
git clone https://github.com/TU_USUARIO/TU_REPO.git dispo-ag
cd dispo-ag
```

O copia la carpeta del proyecto (con `app.py`, `excel_processor.py`, `requirements.txt`, `templates/`) a la Pi por SCP, USB, etc.

### 2. Crear entorno virtual e instalar dependencias

```bash
cd ~/dispo-ag   # o la ruta donde esté el proyecto
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Si falla por falta de memoria al instalar pandas, cierra otras apps o usa:

```bash
pip install --no-cache-dir -r requirements.txt
```

### 3. Probar que arranca

```bash
source venv/bin/activate
gunicorn --bind 0.0.0.0:5000 --workers 1 app:app
```

Desde otro dispositivo en la misma red (PC, móvil), abre en el navegador:

`http://IP_DE_LA_PI:5000`

(La IP la ves en la Pi con `hostname -I` o en el router.)

Pulsa Ctrl+C para parar el servidor.

### 4. Servicio al arrancar (opcional)

Para que la app se inicie sola al encender la Pi y se reinicie si se cae:

```bash
sudo nano /etc/systemd/system/dispo.service
```

Pega esto (ajusta `WorkingDirectory` y `ExecStart` si tu proyecto está en otra ruta):

```ini
[Unit]
Description=Dispo Flask App
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/dispo-ag
Environment="PATH=/home/pi/dispo-ag/venv/bin"
ExecStart=/home/pi/dispo-ag/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 1 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Activa e inicia el servicio:

```bash
sudo systemctl daemon-reload
sudo systemctl enable dispo
sudo systemctl start dispo
sudo systemctl status dispo
```

Para ver logs: `journalctl -u dispo -f`

## Acceso desde internet (opcional)

- En el router, abre el **puerto 5000** (o el que uses) y redirígelo a la IP de la Pi.
- Usa un servicio tipo **No-IP** o **DuckDNS** si tu IP pública cambia, y entra con `http://tu-dominio.dyndns.org:5000`.

## Resumen

- **Sí funciona** en una Raspberry Pi como servidor.
- Usa **1 worker** de Gunicorn para no pasarte de RAM.
- Con 2 GB RAM o más y tus archivos Excel de tamaño normal, debería ir correcto.
