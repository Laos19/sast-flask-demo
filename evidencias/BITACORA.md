# Bitácora de comandos

Proyecto: `sast-flask-demo` (NotasApp) — curso SI784 Calidad y Pruebas de Software, UPT.
Herramientas SAST: **Bandit** (integrante 1) y **CodeQL** (integrante 2; reemplazó a Bearer CLI en la Fase 3).
Herramientas ya usadas en labs anteriores (excluidas): SonarCloud (lab01), Snyk (lab02), Semgrep (lab03).

---

## Fase 0: Preparación (2026-10-01)

Ruta local del proyecto: `C:\Users\adriana\Documents\UPT\2026II\si784\sast-flask-demo`

```powershell
git --version              # git version 2.51.0.windows.1
python --version           # Python 3.14.0
pip --version              # ERROR: 'pip' no está en el PATH -> se usa "python -m pip"
python -m pip --version    # pip 25.2 (python 3.14)
gh --version               # ERROR: GitHub CLI no instalado
```

Notas:
- En Windows `pip` no está en el PATH; se usa siempre `python -m pip` (dentro del venv no hay problema).
- Localmente solo está Python 3.14. En GitHub Actions y Render se fijará **Python 3.12** (versión pedida por el curso). Flask, pytest y Bandit funcionan igual en ambas.

```powershell
mkdir sast-flask-demo
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip   # pip 26.2.1
```

- Se creó `.gitignore` (excluye `.venv/`, `__pycache__/`, `*.db`, `.env`).
- Se creó la estructura `evidencias/00_entorno … 09_capturas`.
- Evidencia: `evidencias/00_entorno/versiones.txt`.

---

## Fase 1: App vulnerable "NotasApp" (2026-10-01)

Integrantes: **Antony Solorzano (2023078696) → Bandit**, **Adriana Laos (2023077474) → Bearer CLI**.

Archivos creados: `app/__init__.py`, `app/app.py`, `app/db.py`, `app/templates/{base,index,login,notas,buscar,ping}.html`,
`tests/test_app.py`, `requirements.txt` (flask 3.1.2, gunicorn 23.0.0, pytest 8.4.2), `pytest.ini`.

Vulnerabilidades intencionales (marcadas con `# VULNERABLE:` en `app/app.py`):

| # | Vulnerabilidad | Dónde | CWE |
|---|---|---|---|
| V1 | SQL Injection (f-string) | `buscar()` | CWE-89 |
| V2 | Command Injection (`shell=True`) | `ping()` | CWE-78 |
| V3 | Secreto en el código `SECRET_KEY = "super-secreto-123"` | inicio de `app.py` | CWE-798 |
| V4 | MD5 para contraseñas | `hash_password()` | CWE-327 |
| V5 | `app.run(debug=True)` | `if __name__ == "__main__"` | CWE-489/94 |

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -v        # 4 passed in 0.25s
.\.venv\Scripts\python.exe -m app.app          # Running on http://127.0.0.1:5000 (debug on)
```

Demostración de V1 con curl (usuarios `ana` y `beto`):
```bash
curl -b cookies_ana -G --data-urlencode "q=Lista" http://127.0.0.1:5000/buscar          # 1 resultado (solo la nota de ana)
curl -b cookies_ana -G --data-urlencode "q=' OR 1=1 --" http://127.0.0.1:5000/buscar   # 2 resultados: aparece "Privado de Beto"
```
Nota: el payload `' OR '1'='1` no basta en esta consulta (queda `'1'='1%'`, que es falso); se usa `' OR 1=1 --`.

Demostración de V2:
```bash
curl -b cookies_ana -G --data-urlencode "host=127.0.0.1 && whoami" http://127.0.0.1:5000/ping   # imprime adrianalaos\adriana
```

Evidencias: `01_app_local/pytest.txt`, `demo_sqli.txt`, `demo_cmdi.txt`, `CAPTURAS_PENDIENTES.md`.
Capturas tomadas: `09_capturas/cap_home.png`, `cap_notas.png`, `cap_sqli.png`, `cap_cmdi.png`.

---

## Fase 2: Repositorio público (2026-10-01)

```powershell
git init -b main
git add .                       # .venv/, notas.db y .pytest_cache/ quedan ignorados
git commit -m "feat: app NotasApp versión vulnerable"
git tag -a v1-vulnerable -m "Versión con V1–V5 sin corregir"
```
Se añadió `.gitattributes` (`* text=auto eol=lf`) para usar finales de línea LF, porque Actions y Render corren en Linux.

El repo público `Laos19/sast-flask-demo` se creó a mano desde https://github.com/new (vacío, sin README).
```powershell
git remote add origin https://github.com/Laos19/sast-flask-demo.git
git push -u origin main --follow-tags
#  * [new branch]      main -> main
#  * [new tag]         v1-vulnerable -> v1-vulnerable
```
Verificación con la API de GitHub: `"visibility": "public"`, `"default_branch": "main"`.
URL: https://github.com/Laos19/sast-flask-demo (en `02_repo/url_repo.txt`).
Captura: `09_capturas/cap_repo.png`.

---

## Fase 3: Escaneo local de la versión vulnerable (2026-10-01)

### Bandit (Antony Solorzano)
```powershell
.\.venv\Scripts\python.exe -m pip install "bandit[sarif]"
bandit --version                                   # bandit 1.9.4 (python 3.14.0)
bandit -r app -f txt   -o evidencias\03_bandit\antes\bandit.txt
bandit -r app -f json  -o evidencias\03_bandit\antes\bandit.json
bandit -r app -f html  -o evidencias\03_bandit\antes\bandit.html
bandit -r app -f sarif -o evidencias\03_bandit\antes\bandit.sarif
```
- Tiempo de escaneo: ~0,36 s. Se analizaron 135 líneas de código.
- Código de salida 1, porque hay hallazgos. En CI se usará `--exit-zero` para que no bloquee.
- Resultado: **6 hallazgos** (High 3, Medium 1, Low 2):

| Regla | Severidad / Confianza | Línea | V# |
|---|---|---|---|
| B404 blacklist (import subprocess) | Low / High | app.py:9 | (extra, informativo) |
| B105 hardcoded_password_string | Low / Medium | app.py:18 | V3 |
| B324 hashlib (MD5) | High / High | app.py:29 | V4 |
| B608 hardcoded_sql_expressions | Medium / Low | app.py:114 | V1 |
| B602 subprocess_popen_with_shell_equals_true | High / High | app.py:128 | V2 |
| B201 flask_debug_true | High / Medium | app.py:136 | V5 |

### Bearer CLI (Adriana Laos)
- Última versión: v2.1.1. Solo se publican binarios para **Linux y macOS**; no hay versión para Windows.
- En esta PC no hay ninguna distribución de WSL instalada (solo `docker-desktop`). Docker 29.7.2 sí está instalado.
- Decisión: usar la imagen oficial de Docker (`bearer/bearer:latest-amd64`, ~121 MB).

```powershell
docker pull bearer/bearer:latest-amd64
docker run --rm bearer/bearer:latest-amd64 version        # bearer version 2.1.1
# Primer intento: escanear "." con bearer.yml (scan.skip-path) -> analizó 1709 archivos (incluyó .venv); 50,8 s
# Segundo intento: --skip-path ".venv,evidencias,tests" -> igual, 1709 archivos (el skip-path no excluye .venv)
# Solución: escanear solo la carpeta app (3 archivos, 3,9 s)
docker run --rm -v "${PWD}:/tmp/scan" -w /tmp/scan bearer/bearer:latest-amd64 scan app --quiet --output evidencias/04_bearer/antes/bearer.txt
docker run ... scan app --quiet --format json  --output evidencias/04_bearer/antes/bearer.json
docker run ... scan app --quiet --format sarif --output evidencias/04_bearer/antes/bearer.sarif
```
- Resultado: **1 hallazgo**, `python_lang_weak_hash_md5` MEDIUM (CWE-328) en app.py:29 (V4). Se ejecutaron 88 reglas de Python.
- **Problema importante:** V1, V2, V3 y V5 **no** se detectan. Revisando las reglas oficiales (repo `Bearer/bearer-rules`, carpeta `rules/python`):
  - `python_lang_sql_injection` y `python_lang_os_command_injection` necesitan una fuente de "entrada externa"
    (`python_shared_common_external_input`), que solo incluye Django `request`, `input()`, `sys.argv`, `sys.stdin`,
    `argparse`, `getopt` y AWS Lambda. **`flask.request` no está entre las fuentes.**
  - La regla de SQLi además exige que la conexión venga de `.cursor()` o de un parámetro llamado `conn`.
  - Las reglas `debug_mode_enabled` y `weak_secret_key` existen **solo para Django** (`rules/python/django`). No hay reglas para Flask.
- **Decisión del equipo: reemplazar Bearer por CodeQL.** Los reportes de Bearer y su `bearer.yml` se movieron a
  `evidencias/10_bearer_descartado/`, junto con `POR_QUE_SE_DESCARTO.md`.

### CodeQL (Adriana Laos, reemplaza a Bearer)
Instalación: paquete oficial `codeql-bundle-win64.tar.gz` v2.27.1 (698 MB) desde `github/codeql-action/releases`.
```bash
curl -L -o codeql-bundle-win64.tar.gz https://github.com/github/codeql-action/releases/download/codeql-bundle-v2.27.1/codeql-bundle-win64.tar.gz
sha256sum codeql-bundle-win64.tar.gz   # 721209b5...f97202 = coincide con el .checksum.txt oficial
tar -xzf codeql-bundle-win64.tar.gz    # -> C:\Users\adriana\tools\codeql
codeql version                         # CodeQL command-line toolchain release 2.27.1
```
Configuración `.github/codeql/codeql-config.yml`: suite `security-extended` y `paths: [app]`.
```powershell
codeql database create codeql-db --language=python --source-root=. --codescanning-config=.github/codeql/codeql-config.yml --overwrite   # 10,1 s
codeql database analyze codeql-db --format=sarif-latest --output=evidencias\04_codeql\antes\codeql.sarif --sarif-category=python        # 16,1 s
codeql database interpret-results codeql-db --format=csv --output=evidencias\04_codeql\antes\codeql.csv
```
- Primer resultado: **4/5** (V1, V2, V4, V5). V3 (secreto en el código) **no** se detecta con la suite estándar.
- Dentro del paquete se encontró la consulta experimental `py/flask-constant-secret-key` (precisión high). Se añadió en
  `codeql-config.yml` con `packs: python: - codeql/python-queries:experimental/Security/CWE-287-ConstantSecretKey/WebAppConstantSecretKey.ql`.
- Segundo resultado (create 6,1 s + analyze 14,3 s, 51 reglas): **5/5**.

| Regla CodeQL | security-severity | Línea | V# |
|---|---|---|---|
| py/flask-constant-secret-key | 8.5 High | app.py:19 | V3 |
| py/weak-sensitive-data-hashing | 7.5 High | app.py:29 | V4 |
| py/sql-injection | 8.8 High | app.py:115 | V1 |
| py/command-line-injection | 9.8 Critical | app.py:128 | V2 |
| py/flask-debug | 7.5 High | app.py:136 | V5 |

Reporte legible generado con `scripts/sarif_resumen.py` (convierte el SARIF a texto e incluye el flujo de datos):
```powershell
python scripts\sarif_resumen.py evidencias\04_codeql\antes\codeql.sarif evidencias\04_codeql\antes\codeql.txt
```
Evidencias: `04_codeql/antes/{codeql.sarif, codeql.csv, codeql.txt}` y `05_comparativa/hallazgos_antes.md`.

---

## Fase 4: Pipeline en GitHub Actions (2026-10-01)

Se crearon `.github/workflows/ci-sast-deploy.yml` (jobs `tests`, `sast-bandit`, `sast-codeql`, `deploy`) y `scripts/sarif_gate.py`.
En la versión vulnerable los escaneos **reportan sin bloquear**. Las líneas del quality gate quedan comentadas para la Fase 7.

Prueba local de los gates contra la versión vulnerable (los dos deben fallar):
```powershell
python scripts\sarif_gate.py evidencias\04_codeql\antes\codeql.sarif 7.0   # 5 hallazgos >= 7.0 -> exit 1
bandit -r app -lll                                                        # High: 3 (B324, B602, B201) -> exit 1
```
Nota: con `-lll` Bandit no bloquearía por V1 (B608 es Medium) ni por V3 (B105 es Low). CodeQL sí bloquea por las 5.

```powershell
git commit -m "ci: pipeline con pytest, Bandit, CodeQL y deploy a Render"   # 85ed98f
git push origin main
```
Ejecución https://github.com/Laos19/sast-flask-demo/actions/runs/36840091260 → **success**
(tests ✔, sast-bandit ✔, sast-codeql ✔, deploy ✔ con aviso "Falta el secreto RENDER_DEPLOY_HOOK"). Artifacts: `reporte-bandit`, `reporte-codeql`.
Evidencias: `06_pipeline/ci-sast-deploy.yml`, `explicacion_yaml.md`, `url_ejecucion.txt`.

---

## Fase 6: Corrección de vulnerabilidades (2026-10-01), adelantada antes de la Fase 5

**Cambio de orden decidido por el equipo:** publicar la versión vulnerable en Render habría dejado una ejecución remota de
comandos (V2) abierta a cualquiera en internet. Por eso se corrigió primero y en Render solo se despliega `v2-corregido`.

Un commit por vulnerabilidad (pytest se ejecutó después de cada uno):
```
340949c fix(V1): consulta parametrizada en la búsqueda de notas (CWE-89)          # 5 passed
ffd77ca fix(V2): ping sin shell y con validación del host (CWE-78)                 # 6 passed
130a758 fix(V3): SECRET_KEY desde variable de entorno (CWE-798)                    # 6 passed; sin la variable -> KeyError: 'SECRET_KEY'
221be5b fix(V4): contraseñas con generate_password_hash de Werkzeug en vez de MD5  # 7 passed (1,10 s, por scrypt)
8be3fc5 fix(V5): modo debug desde FLASK_DEBUG, desactivado por defecto (CWE-489)   # 7 passed
```
Archivos nuevos: `tests/conftest.py` (genera una SECRET_KEY aleatoria para las pruebas) y `.env.example`.

Prueba de `host_valido()`: `127.0.0.1` ✔, `::1` ✔, `google.com` ✔, `127.0.0.1 && whoami` ✘, `-c 99 x` ✘, `a;ls` ✘.

Escaneos después de las correcciones:
```powershell
bandit -r app -f txt|json|html|sarif -o evidencias\03_bandit\despues\bandit.<ext>
#   Total: 2 (Low 2): B404 import subprocess (l.11), B603 subprocess_without_shell (l.150). High 0, Medium 0
codeql database create ... ; codeql database analyze ... --output=evidencias\04_codeql\despues\codeql.sarif
#   Hallazgos: 0
python scripts\sarif_gate.py evidencias\04_codeql\despues\codeql.sarif 7.0   # 0 -> exit 0
bandit -r app -lll                                                          # exit 0
```
Evidencias: `03_bandit/despues/*`, `04_codeql/despues/*`, `05_comparativa/antes_vs_despues.md`.

Push de las correcciones + tag: `git push origin main --follow-tags` (85ed98f..ef74754, nuevo tag `v2-corregido`).
Ejecución https://github.com/Laos19/sast-flask-demo/actions/runs/36840882782 → **success**.
En Code Scanning, las alertas de la versión vulnerable deben quedar como **Fixed/Closed** tras este análisis.

---

## Fase 5: Despliegue en Render (2026-10-01)

Pasos manuales en `07_deploy/PASOS_RENDER.md`. Se agregó `.python-version` (3.12) para que Render use Python 3.12.

### Problema 1: "Deploy failed" en el primer despliegue
- Build correcto (Python 3.12, flask 3.1.2, gunicorn 23.0.0), pero el arranque falló:
  `==> Running 'gunicorn app:app'` → `gunicorn.errors.AppImportError: Failed to find attribute 'app' in 'app'.` → `Exited with status 1`
- Causa: el Start Command quedó con el valor que Render sugiere por defecto (`gunicorn app:app`). Con esa ruta gunicorn busca
  el objeto `app` dentro del **paquete** `app/` (`app/__init__.py`), pero la app Flask está en el **módulo** `app/app.py`.
- Solución: Settings → Build & Deploy → Start Command = `gunicorn app.app:app` (formato `paquete.módulo:variable`) → Manual Deploy.
- Tras corregir el Start Command: deploy **Live** (trigger "Start command updated", 51,8 s). URL: https://sast-flask-demo.onrender.com
- Verificación con curl en `07_deploy/verificacion_online.txt`: V2 y V5 corregidos en producción.
- **Hallazgo extra:** el payload `' OR 1=1 --` recibe `403 Blocked` del **WAF de Cloudflare** que Render pone delante del servicio.
- El Deploy Hook **no** se guardó en el repo; se configura solo como secreto de GitHub (`RENDER_DEPLOY_HOOK`).
- Secreto `RENDER_DEPLOY_HOOK` cargado en GitHub por Adriana (a mano). Auto-Deploy de Render en Off.
- `git push` (ef74754..52eb041) → https://github.com/Laos19/sast-flask-demo/actions/runs/36843519408 → success.
  El job `deploy` ejecutó `curl -fsS -X POST "$RENDER_DEPLOY_HOOK"` sin errores y ya no muestra el aviso de secreto faltante.
- Captura: `09_capturas/cap_app_online.png`.

---

## Fase 7: Quality gate (2026-10-01)

```powershell
# Se descomentaron los dos gates del YAML
git commit -m "ci: activar quality gate de Bandit y CodeQL (severidad alta)"   # 90fec56
git push origin main
```
→ https://github.com/Laos19/sast-flask-demo/actions/runs/36843839029 **success** (los dos gates ✔, deploy ✔).

Demostración del bloqueo (se eligió reintroducir **V2**, porque Bandit con `-lll` no bloquea V1, que es Medium):
```powershell
git switch -c demo-gate
# app.py ping(): vuelve shell=True con f-string y sin host_valido()
pytest -q            # 1 failed (test_v2_ping_rechaza_inyeccion_de_comandos), 6 passed
bandit -r app -lll   # B602 High -> exit 1
git commit -m "demo: reintroducir V2 (shell=True) para probar el quality gate"
git push -u origin demo-gate
git switch main
```
El PR se abre a mano desde la web (no hay GitHub CLI). Evidencias: `08_quality_gate/links.md`.
PR https://github.com/Laos19/sast-flask-demo/pull/1 (demo-gate → main), abierto por Adriana.
Ejecución https://github.com/Laos19/sast-flask-demo/actions/runs/36844157546 → **failure**:
tests ✘ · sast-bandit ✘ (gate) · sast-codeql ✘ (gate; anotación `py/command-line-injection (9.8) en app/app.py:145`) · deploy **skipped**.
