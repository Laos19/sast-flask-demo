# Capturas de la Fase 1 (guardar en `evidencias/09_capturas/`)

Con la app corriendo (`.\.venv\Scripts\python.exe -m app.app` → http://127.0.0.1:5000):

| Archivo | Qué mostrar |
|---|---|
| `cap_home.png` | Página de inicio de NotasApp en el navegador (barra de direcciones visible). |
| `cap_sqli.png` | Logueado como `ana` / `clave-ana`, en **Buscar** escribir `' OR 1=1 --` → se ve la nota "Privado de Beto". |
| `cap_cmdi.png` *(opcional)* | En **Ping** escribir `127.0.0.1 && whoami` → al final aparece el usuario de Windows. |

Usuarios de demo ya creados en `notas.db` local: `ana / clave-ana`, `beto / clave-beto` (valores falsos).
