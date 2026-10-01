# Pipeline `.github/workflows/ci-sast-deploy.yml`, explicado bloque por bloque

Copia del archivo: `06_pipeline/ci-sast-deploy.yml`.

| Bloque | Explicación (1 línea) |
|---|---|
| `on: push / pull_request / workflow_dispatch` | Se ejecuta con cada push o PR a `main` y también a mano desde la pestaña Actions. |
| `permissions: contents: read` | Por defecto el token del workflow solo puede leer el repo (mínimo privilegio). |
| **job `tests`** | Instala Python 3.12 y las dependencias, y corre `pytest -v`. |
| `actions/setup-python@v5` + `cache: pip` | Instala Python 3.12 y guarda en caché las descargas de pip para acelerar las siguientes ejecuciones. |
| **job `sast-bandit`** | Instala Bandit y analiza la carpeta `app/`. |
| `security-events: write` | Permiso que el job necesita para publicar hallazgos en GitHub Code Scanning. |
| `bandit ... --exit-zero` | Genera reportes txt, html y sarif **sin romper** el pipeline (modo "reportar"). |
| `# bandit -r app -lll` (comentado) | **Quality gate:** solo considera severidad ALTA y devuelve exit 1 si encuentra algo, lo que bloquea el pipeline. |
| `actions/upload-artifact@v4` (reporte-bandit) | Guarda `bandit.html` y `bandit.sarif` como artifacts descargables de la ejecución. |
| `github/codeql-action/upload-sarif@v4` | Sube `bandit.sarif` a la pestaña **Security → Code scanning** con la categoría `bandit`. |
| **job `sast-codeql`** | Análisis semántico con CodeQL usando `.github/codeql/codeql-config.yml`. |
| `codeql-action/init@v4` | Descarga CodeQL, prepara la base de datos de Python y carga la suite `security-extended` + la consulta experimental de `SECRET_KEY`. |
| `codeql-action/analyze@v4` | Ejecuta las consultas, sube los resultados a Code Scanning (categoría `codeql-python`) y guarda el SARIF en `codeql-sarif/`. |
| `# scripts/sarif_gate.py ... 7.0` (comentado) | **Quality gate:** CodeQL no bloquea por sí solo; este script falla si hay hallazgos con `security-severity >= 7.0` (High o Critical). |
| `upload-artifact@v4` (reporte-codeql) | Guarda el SARIF de CodeQL como artifact. |
| **job `deploy`** | Despliega en Render solo si los 3 jobs anteriores pasaron. |
| `needs: [tests, sast-bandit, sast-codeql]` | El despliegue depende de las pruebas y de los dos escaneos. Si alguno falla, no se despliega. |
| `if: github.ref == 'refs/heads/main' && ... != 'pull_request'` | Solo despliega en push a `main`, nunca desde un Pull Request. |
| `curl -fsS -X POST "$RENDER_DEPLOY_HOOK"` | Llama al Deploy Hook secreto de Render, que reconstruye y publica la app. Si el secreto no existe todavía, solo muestra un aviso. |

## Por qué `if: always()` en los uploads
Así los reportes se suben aunque el quality gate falle (Fase 7). De lo contrario no habría reporte justo cuando más se necesita.

## Diferencia de quality gate entre herramientas
- Bandit trae el gate incluido: el filtro de severidad `-lll` más su código de salida.
- CodeQL (acción oficial) **nunca** falla por hallazgos, así que hizo falta un script propio (`scripts/sarif_gate.py`) que lee el SARIF.
