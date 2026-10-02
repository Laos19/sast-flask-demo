"""NotasApp: app Flask mínima para demostrar análisis SAST con Bandit y CodeQL.

La versión vulnerable (tag v1-vulnerable) tenía 5 fallas a propósito (V1–V5);
cada corrección está marcada con "# CORREGIDO:" (tag v2-corregido).
"""
import functools
import ipaddress
import os
import re
import shutil
import subprocess

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app import db

app = Flask(__name__)

# CORREGIDO: V3 el secreto se lee de una variable de entorno (Render / GitHub Secrets), nunca del código.
# Si falta, la app no arranca (KeyError) en lugar de usar una clave insegura por defecto.
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["DATABASE"] = os.environ.get("DATABASE_PATH", "notas.db")
app.teardown_appcontext(db.close_db)


def hash_password(password):
    # CORREGIDO: V4 hash lento y con sal aleatoria (scrypt de Werkzeug) en lugar de MD5
    return generate_password_hash(password)


def crear_usuario_demo():
    """Crea el usuario de demostración si DEMO_USUARIO y DEMO_PASSWORD están definidos.

    En Render el disco es efímero y la BD se borra al reiniciar; así el usuario demo
    vuelve a existir en cada arranque sin escribir credenciales en el código.
    """
    usuario = os.environ.get("DEMO_USUARIO")
    password = os.environ.get("DEMO_PASSWORD")
    if usuario and password:
        conexion = db.get_db()
        conexion.execute(
            "INSERT OR IGNORE INTO usuarios (usuario, password) VALUES (?, ?)",
            (usuario, hash_password(password)),
        )
        conexion.commit()


with app.app_context():
    db.init_db()
    crear_usuario_demo()


HOST_REGEX = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9.-]{0,252})")


def host_valido(host):
    """Acepta solo una IP (v4/v6) o un nombre de host sin espacios ni símbolos de shell."""
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return HOST_REGEX.fullmatch(host) is not None


def login_requerido(vista):
    """Redirige al login si no hay sesión iniciada."""
    @functools.wraps(vista)
    def envoltura(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        return vista(*args, **kwargs)
    return envoltura


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    error = None
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]
        conexion = db.get_db()
        try:
            conexion.execute(
                "INSERT INTO usuarios (usuario, password) VALUES (?, ?)",
                (usuario, hash_password(password)),
            )
            conexion.commit()
            return redirect(url_for("login"))
        except conexion.IntegrityError:
            error = "El usuario ya existe"
    return render_template("login.html", titulo="Registro", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        fila = db.get_db().execute(
            "SELECT id, password FROM usuarios WHERE usuario = ?",
            (request.form["usuario"],),
        ).fetchone()
        if fila and check_password_hash(fila["password"], request.form["password"]):
            session.clear()
            session["usuario_id"] = fila["id"]
            session["usuario"] = request.form["usuario"]
            return redirect(url_for("notas"))
        error = "Usuario o contraseña incorrectos"
    return render_template("login.html", titulo="Iniciar sesión", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/notas", methods=["GET", "POST"])
@login_requerido
def notas():
    conexion = db.get_db()
    if request.method == "POST":
        conexion.execute(
            "INSERT INTO notas (usuario_id, titulo, contenido) VALUES (?, ?, ?)",
            (session["usuario_id"], request.form["titulo"], request.form["contenido"]),
        )
        conexion.commit()
        return redirect(url_for("notas"))
    filas = conexion.execute(
        "SELECT id, titulo, contenido FROM notas WHERE usuario_id = ?",
        (session["usuario_id"],),
    ).fetchall()
    return render_template("notas.html", notas=filas)


@app.route("/buscar")
@login_requerido
def buscar():
    q = request.args.get("q", "")
    filas = []
    if q:
        # CORREGIDO: V1 consulta parametrizada (?), SQLite trata "q" como dato y nunca como SQL
        filas = db.get_db().execute(
            "SELECT id, titulo, contenido FROM notas WHERE usuario_id = ? AND titulo LIKE ?",
            (session["usuario_id"], f"%{q}%"),
        ).fetchall()
    return render_template("buscar.html", q=q, notas=filas)


@app.route("/ping")
@login_requerido
def ping():
    host = request.args.get("host", "")
    salida = ""
    if host:
        opcion = "-n" if os.name == "nt" else "-c"
        # VULNERABLE: V2 reintroducida a propósito (rama demo-gate) para mostrar que el quality gate bloquea el PR
        resultado = subprocess.run(
            f"ping {opcion} 1 {host}", shell=True, capture_output=True, text=True, timeout=10
        )
        salida = resultado.stdout + resultado.stderr
    return render_template("ping.html", host=host, salida=salida)


if __name__ == "__main__":
    # CORREGIDO: V5 debug solo si FLASK_DEBUG=1 explícitamente; por defecto False
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1")
