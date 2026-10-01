# Antes vs después de las correcciones

- **Antes:** tag `v1-vulnerable` (commit `4a45522`). Reportes en `03_bandit/antes/` y `04_codeql/antes/`.
- **Después:** tag `v2-corregido` (commit `8be3fc5`). Reportes en `03_bandit/despues/` y `04_codeql/despues/`.
- Commits de corrección: `340949c fix(V1)` · `ffd77ca fix(V2)` · `130a758 fix(V3)` · `221be5b fix(V4)` · `8be3fc5 fix(V5)`.

## Conteo de hallazgos por severidad

### Bandit 1.9.4
| Severidad | Antes | Después |
|---|---|---|
| High | 3 (B324, B602, B201) | **0** |
| Medium | 1 (B608) | **0** |
| Low | 2 (B404, B105) | 2 (B404, **B603**) |
| **Total** | **6** | **2** |

Los 2 que quedan son de severidad Low y solo informativos, no son vulnerabilidades reales:
- **B404** (app.py:11): avisa de que se importa `subprocess`. Siempre aparece si el módulo se usa.
- **B603** (app.py:150): `subprocess` sin shell. Bandit pide "revisar entrada no confiable", pero ya está validada con `host_valido()`.
  Si el equipo lo revisa y lo acepta, se puede marcar con `# nosec B603`.
- Quality gate `bandit -r app -lll` → exit 0 ✔.

### CodeQL 2.27.1 (security-extended + py/flask-constant-secret-key)
| Severidad (security-severity) | Antes | Después |
|---|---|---|
| Critical (≥9.0) | 1 (py/command-line-injection) | **0** |
| High (7.0–8.9) | 4 (py/sql-injection, py/flask-constant-secret-key, py/weak-sensitive-data-hashing, py/flask-debug) | **0** |
| Medium / Low | 0 | 0 |
| **Total** | **5** | **0** |

- Quality gate `scripts/sarif_gate.py codeql.sarif 7.0` → exit 0 ✔.
- CodeQL **no** marca el `subprocess.run([...])` corregido: su análisis de flujo distingue que el host es un argumento y no el comando, y que no pasa por un shell.

### Pruebas
pytest: 4 → **7 pruebas** (se añadió una prueba de regresión para V1, V2 y V4). Todas pasan.

---

## Código antes / después

### V1: SQL Injection (CWE-89), `buscar()`
```python
# ANTES
# VULNERABLE: V1 SQL Injection, la entrada del usuario se concatena con f-string (CWE-89)
consulta = f"SELECT id, titulo, contenido FROM notas WHERE usuario_id = {session['usuario_id']} AND titulo LIKE '%{q}%'"
filas = db.get_db().execute(consulta).fetchall()
```
```python
# DESPUÉS
# CORREGIDO: V1 consulta parametrizada (?), SQLite trata "q" como dato y nunca como SQL
filas = db.get_db().execute(
    "SELECT id, titulo, contenido FROM notas WHERE usuario_id = ? AND titulo LIKE ?",
    (session["usuario_id"], f"%{q}%"),
).fetchall()
```

### V2: Command Injection (CWE-78), `ping()`
```python
# ANTES
# VULNERABLE: V2 Command Injection, shell=True con entrada del usuario (CWE-78)
resultado = subprocess.run(
    f"ping {opcion} 1 {host}", shell=True, capture_output=True, text=True, timeout=10
)
```
```python
# DESPUÉS
HOST_REGEX = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9.-]{0,252})")

def host_valido(host):
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return HOST_REGEX.fullmatch(host) is not None
...
if not host_valido(host):
    salida = "Host no válido: ..."
...
# CORREGIDO: V2 lista de argumentos sin shell + host validado; "&&" o ";" ya no ejecutan nada
resultado = subprocess.run(
    [ejecutable, opcion, "1", host], capture_output=True, text=True, timeout=10
)
```

### V3: Secreto en el código (CWE-798)
```python
# ANTES
# VULNERABLE: V3 secreto escrito en el código fuente (CWE-798). Valor falso de demostración.
SECRET_KEY = "super-secreto-123"
app.config["SECRET_KEY"] = SECRET_KEY
```
```python
# DESPUÉS
# CORREGIDO: V3 el secreto se lee de una variable de entorno (Render / GitHub Secrets), nunca del código.
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
```
(En las pruebas, `tests/conftest.py` genera una clave aleatoria con `secrets.token_hex(16)`.)

### V4: Hash débil MD5 (CWE-327)
```python
# ANTES
def hash_password(password):
    # VULNERABLE: V4 MD5 es un hash débil y sin sal para contraseñas (CWE-327)
    return hashlib.md5(password.encode()).hexdigest()
...
if fila and fila["password"] == hash_password(request.form["password"]):
```
```python
# DESPUÉS
from werkzeug.security import check_password_hash, generate_password_hash

def hash_password(password):
    # CORREGIDO: V4 hash lento y con sal aleatoria (scrypt de Werkzeug) en lugar de MD5
    return generate_password_hash(password)
...
if fila and check_password_hash(fila["password"], request.form["password"]):
```
Efecto visible: las pruebas pasaron de ~0,2 s a ~1,1 s, porque scrypt es lento **a propósito** para frenar ataques de fuerza bruta.

### V5: Flask en modo debug (CWE-489/94)
```python
# ANTES
# VULNERABLE: V5 modo debug activo, expone el depurador interactivo de Werkzeug (CWE-489/CWE-94)
app.run(debug=True)
```
```python
# DESPUÉS
# CORREGIDO: V5 debug solo si FLASK_DEBUG=1 explícitamente; por defecto False
app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1")
```
Nota: en Render la app corre con **gunicorn**, que nunca activa el depurador. `app.run()` solo se usa en local.
