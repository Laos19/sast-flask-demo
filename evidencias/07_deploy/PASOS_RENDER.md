# Despliegue en Render (plan Free)

Se despliega la versión **corregida** (`v2-corregido` y lo que siga en `main`). La vulnerable nunca se publicó, por seguridad (ver BITACORA, Fase 6).

## 1. Crear el Web Service
1. https://render.com → **Get Started** → **GitHub** (registrarse con la cuenta de GitHub `Laos19`).
2. Dashboard → **+ New** → **Web Service** → **Git Provider: GitHub** → autorizar el acceso **solo** al repo `sast-flask-demo` → **Connect**.
3. Configuración:

| Campo | Valor |
|---|---|
| Name | `sast-flask-demo` (define la URL `https://sast-flask-demo.onrender.com`; si está ocupada, Render agrega un sufijo) |
| Language | `Python 3` |
| Branch | `main` |
| Root Directory | *(vacío)* |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app.app:app` |
| Instance Type | **Free** |

4. **Environment Variables** (en la misma pantalla, "Add Environment Variable"):

| Key | Value |
|---|---|
| `SECRET_KEY` | botón **Generate** (Render crea un valor aleatorio; no lo copies a ningún lado) |
| `FLASK_DEBUG` | `0` |

   Python 3.12 se toma del archivo `.python-version` del repo.
5. **Deploy Web Service**. El primer despliegue lo hace Render mismo (~2–3 min). Espera a ver "Your service is live".

## 2. Desactivar Auto-Deploy y copiar el Deploy Hook
1. En el servicio → **Settings** → sección **Build & Deploy** → **Auto-Deploy** → **Off** → Save.
   (Así solo despliega GitHub Actions, después de pasar las pruebas y los escaneos.)
2. En la misma página de **Settings** → **Deploy Hook** → copiar la URL (`https://api.render.com/deploy/srv-...?key=...`).
   Es un secreto: quien la tenga puede disparar despliegues.

## 3. Guardar el hook en GitHub
https://github.com/Laos19/sast-flask-demo/settings/secrets/actions → **New repository secret**
- Name: `RENDER_DEPLOY_HOOK`
- Secret: pegar la URL del Deploy Hook → **Add secret**

## 4. Verificar
Avisar a Claude, que hará un push. El job `deploy` llamará al hook y en Render → **Events** aparecerá un deploy nuevo "Deploy triggered via Deploy Hook".

## Limitaciones del plan Free (para el artículo)
- El servicio "se duerme" tras 15 min sin tráfico; la primera visita tarda ~50 s en despertar.
- El disco es efímero: `notas.db` (SQLite) se borra en cada redeploy o reinicio. Es aceptable para la demo.
- La imagen nativa de Render puede no traer `ping`; la app lo detecta y muestra "El comando ping no está disponible".
