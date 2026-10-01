# Hallazgos en la versión vulnerable (tag `v1-vulnerable`)

Archivo analizado: `app/app.py` (135 líneas de código). Fecha: 2026-10-01.
Versiones: Bandit 1.9.4 · CodeQL 2.27.1 (suite `security-extended` + consulta experimental `py/flask-constant-secret-key`) · Bearer CLI 2.1.1 (descartado, solo como referencia).

## Tabla V1–V5

| V# | Vulnerabilidad | Bandit (regla · severidad/confianza · línea) | CodeQL (regla · security-severity · línea) | Bearer 2.1.1 (descartado) | Comentarios |
|---|---|---|---|---|---|
| V1 | SQL Injection (CWE-89) | ✔ **B608** hardcoded_sql_expressions · Medium / **Low** · 114 | ✔ **py/sql-injection** · 8.8 High · 115 | ✘ | Bandit solo ve "un string SQL armado con f-string" (por eso su confianza es baja). CodeQL sigue el **flujo de datos** desde `request.args` (l.110) hasta `execute()` (l.115). |
| V2 | Command Injection (CWE-78) | ✔ **B602** subprocess_popen_with_shell_equals_true · High / High · 128 | ✔ **py/command-line-injection** · 9.8 Critical · 128 | ✘ | Bandit marca `shell=True` aunque el comando fuera fijo. CodeQL confirma que `host` viene de `request.args` (l.122). |
| V3 | Secreto en el código (CWE-798) | ✔ **B105** hardcoded_password_string · Low / Medium · 18 | ✔ **py/flask-constant-secret-key** · 8.5 High · 19 | ✘ | Bandit lo detecta por el nombre de la variable (`SECRET_KEY` coincide con `secret`). En CodeQL hizo falta activar la consulta **experimental**; con la suite por defecto no aparece. |
| V4 | Hash débil MD5 (CWE-327) | ✔ **B324** hashlib · High / High · 29 | ✔ **py/weak-sensitive-data-hashing** · 7.5 High · 29 | ✔ `python_lang_weak_hash_md5` · Medium · 29 | CodeQL sabe que lo que se hashea es una **contraseña**. Bandit marca cualquier uso de MD5 (sugiere `usedforsecurity=False`). |
| V5 | Flask `debug=True` (CWE-489/94) | ✔ **B201** flask_debug_true · High / Medium · 136 | ✔ **py/flask-debug** · 7.5 High · 136 | ✘ | Las dos lo detectan. Bearer solo tiene esta regla para Django. |
| — | Extra | **B404** blacklist (import subprocess) · Low / High · 9 | — | — | Informativo: solo avisa del `import`. Podría considerarse ruido o falso positivo. |

## Conteo por severidad

| Herramienta | Critical | High | Medium | Low | Total | V1–V5 detectadas | Tiempo de escaneo |
|---|---|---|---|---|---|---|---|
| Bandit | — (no usa esa escala) | 3 | 1 | 2 | **6** | **5/5** | ~0,4 s |
| CodeQL | 1 | 4 | 0 | 0 | **5** | **5/5** (4/5 sin la consulta experimental) | ~6 s crear BD + ~14 s analizar |
| Bearer CLI | 0 | 0 | 1 | 0 | 1 | 1/5 | ~4 s (Docker) |

Notas:
- La severidad de CodeQL es el valor `security-severity` del SARIF, en la misma escala que usa GitHub Code Scanning: ≥9 Critical, ≥7 High, ≥4 Medium.
- **Falsos positivos:** ninguno en CodeQL. En Bandit, B404 es solo informativo.
- **Diferencia clave:** Bandit es un analizador de **patrones sobre el AST**, rápido y sin configuración. CodeQL hace **análisis de flujo de datos (taint tracking)**: es más preciso y muestra el camino fuente → sumidero, pero es más lento y pesado (paquete de ~700 MB).
- Bearer quedó descartado porque su versión 2.1.1 no reconoce `flask.request` como entrada del usuario. Detalle en `evidencias/10_bearer_descartado/`.
