# Por qué se descartó Bearer CLI

Bearer CLI era la herramienta asignada a Adriana Laos y se **reemplazó por CodeQL** el 2026-10-01.

- Versión probada: Bearer CLI 2.1.1 (reglas v0.48.4), imagen oficial de Docker `bearer/bearer:latest-amd64`. No hay binario para Windows.
- Comando: `docker run --rm -v "${PWD}:/tmp/scan" -w /tmp/scan bearer/bearer:latest-amd64 scan app --format json|sarif`
- Resultado: **1 de 5** vulnerabilidades (solo V4, MD5). Reportes en esta carpeta: `bearer.txt`, `bearer.json`, `bearer.sarif`.

## Causa (revisada en el repo oficial `Bearer/bearer-rules`, carpeta `rules/python`)
1. Las reglas de inyección (`python_lang_sql_injection`, `python_lang_os_command_injection`) solo se activan si el dato
   viene de una "entrada externa". Para Python eso incluye Django `request`, `input()`, `sys.argv`, `sys.stdin`,
   `argparse`, `getopt` y AWS Lambda, pero **no `flask.request`**.
2. La regla de SQLi además exige que el objeto venga de `.cursor()` o de un parámetro llamado `conn`.
3. `debug_mode_enabled` y `weak_secret_key` existen **solo** en `rules/python/django`. No hay ninguna regla para Flask.
4. Detalle extra: la opción `skip-path` (en `bearer.yml` o en la línea de comandos) no excluyó `.venv`, así que escaneó 1709 archivos.
   Se resolvió escaneando solo la carpeta `app`.

## Alternativas evaluadas
- Bearer + reglas propias (`--external-rule-dir`): posible, pero da más trabajo y el resultado es incierto.
- DevSkim: se basa en patrones regex, sin análisis de flujo de datos.
- Horusec: para Python usa Bandit por dentro, así que duplicaría la herramienta del integrante 1.
- **CodeQL (elegida):** aparece en la lista de OWASP, tiene reglas para Flask y se integra directo con GitHub Code Scanning.
