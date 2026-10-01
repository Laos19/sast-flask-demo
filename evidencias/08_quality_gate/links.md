# Quality gate (Fase 7)

## Gates activados en `.github/workflows/ci-sast-deploy.yml` (commit `90fec56`)
```yaml
# job sast-bandit
- name: Quality gate Bandit (severidad alta)
  run: bandit -r app -lll                       # exit 1 si hay algún hallazgo High

# job sast-codeql
- name: Quality gate CodeQL (severidad alta)
  run: python3 scripts/sarif_gate.py codeql-sarif/python.sarif 7.0   # exit 1 si security-severity >= 7.0
```

## Verde: versión corregida en `main`
https://github.com/Laos19/sast-flask-demo/actions/runs/36843839029
tests ✔ · sast-bandit ✔ (gate ✔) · sast-codeql ✔ (gate ✔) · deploy ✔ (Render actualizado)
Captura: `09_capturas/cap_gate_verde.png`

## Rojo: rama `demo-gate` con V2 reintroducida (commit "demo: reintroducir V2 (shell=True) ...")
Cambio: en `ping()` se vuelve a usar `subprocess.run(f"ping {opcion} 1 {host}", shell=True, ...)` y se quita `host_valido()`.
Prueba local antes del PR:
- `bandit -r app -lll` → B602 subprocess_popen_with_shell_equals_true (High) → exit 1
- `pytest` → 1 failed (`test_v2_ping_rechaza_inyeccion_de_comandos`), 6 passed. La prueba de regresión también lo detecta.

Pull Request: https://github.com/Laos19/sast-flask-demo/pull/1 (NO se fusiona; se cierra tras la demo)
Ejecución del PR: https://github.com/Laos19/sast-flask-demo/actions/runs/36844157546 -> **failure**
Resultado real:
- tests ✘: falló "Run pytest -v" (prueba de regresión de V2)
- sast-bandit ✘: falló "Quality gate Bandit (severidad alta)" (B602)
- sast-codeql ✘: falló "Quality gate CodeQL (severidad alta)", con la anotación `py/command-line-injection (9.8) en app/app.py:145`
- deploy ⏭ **skipped**: no se despliega nada
Captura: `09_capturas/cap_gate_rojo.png`
