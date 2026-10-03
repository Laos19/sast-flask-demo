# Capturas del sistema funcionando (generadas el 2026-10-03)

Se generaron automáticamente con Playwright 1.63.0 y Microsoft Edge en modo headless. Como no hay barra de direcciones,
cada imagen lleva arriba una franja con la versión, la URL exacta y lo que demuestra:
🟥 rojo = versión vulnerable local · 🟩 verde = versión corregida local · 🟪 morado = Render (producción).

Datos de demostración (valores falsos): `ana / clave-ana` y `beto / clave-beto` (con la nota "Privado de Beto").

| Archivo | Versión | Qué muestra |
|---|---|---|
| `01_v1_inicio.png` | v1 local :5000 | Página de inicio |
| `02_v1_registro.png` | v1 local | Formulario de registro completado |
| `03_v1_login.png` | v1 local | Inicio de sesión como `ana` |
| `04_v1_mis_notas.png` | v1 local | "Mis notas": `ana` solo ve "Lista de Ana" |
| `05_v1_buscar_normal.png` | v1 local | Búsqueda `Lista`: 1 resultado (comportamiento normal) |
| `06_v1_sqli.png` | v1 local | **V1 SQLi** `' OR 1=1 --`: 2 resultados, se filtra "Privado de Beto" |
| `07_v1_ping_normal.png` | v1 local | Ping a `127.0.0.1` |
| `08_v1_cmdi.png` | v1 local | **V2 Command Injection** `127.0.0.1 && whoami`: al final aparece `adrianalaos\adriana` |
| `09_v2_mis_notas.png` | v2 local :5001 | Mismos datos de prueba en la versión corregida |
| `10_v2_sqli_bloqueada.png` | v2 local | **V1 corregida**: el mismo payload da 0 resultados (se trata como texto) |
| `11_v2_cmdi_bloqueada.png` | v2 local | **V2 corregida**: "Host no válido" |
| `12_v2_ping_normal.png` | v2 local | El ping legítimo sigue funcionando (sin línea de `whoami`) |
| `13_render_inicio.png` | Render | App en línea en https://sast-flask-demo.onrender.com |
| `14_render_registro.png` | Render | Formulario de registro en producción |
| `15_render_waf_sqli.png` | Render | `403 Forbidden`: el WAF de Render (Cloudflare) bloquea `' OR 1=1 --` antes de llegar a la app. La IP del visitante se ocultó |

Notas:
- En las capturas de ping (07, 08, 12) algunas tildes salen mal ("Estad¡sticas"). Es la codificación de consola de Windows (cp850) en la salida de `ping.exe`; no afecta a la demostración.
- Las páginas de Render que requieren iniciar sesión no se capturaron automáticamente. Las capturas 10–12 muestran la misma versión (`v2-corregido`) corriendo en local.
