# Bitácora de comandos

Proyecto: `sast-flask-demo` (NotasApp) — curso SI784 Calidad y Pruebas de Software, UPT.
Herramientas SAST: **Bandit** (integrante 1) y **Bearer CLI** (integrante 2).
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
