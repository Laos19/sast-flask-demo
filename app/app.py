"""NotasApp: app Flask mínima con 5 vulnerabilidades A PROPÓSITO (V1–V5).

Sirve como objetivo para las herramientas SAST Bandit y Bearer CLI.
¡No usar en producción!
"""
import functools
import hashlib
import os
import subprocess

from flask import Flask, redirect, render_template, request, session, url_for

from app import db

app = Flask(__name__)

# VULNERABLE: V3 secreto escrito en el código fuente (CWE-798). Valor falso de demostración.
SECRET_KEY = "super-secreto-123"
app.config["SECRET_KEY"] = SECRET_KEY
app.config["DATABASE"] = os.environ.get("DATABASE_PATH", "notas.db")
app.teardown_appcontext(db.close_db)

with app.app_context():
    db.init_db()


def hash_password(password):
    # VULNERABLE: V4 MD5 es un hash débil y sin sal para contraseñas (CWE-327)
    return hashlib.md5(password.encode()).hexdigest()


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
        if fila and fila["password"] == hash_password(request.form["password"]):
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
        # VULNERABLE: V1 SQL Injection, la entrada del usuario se concatena con f-string (CWE-89)
        consulta = f"SELECT id, titulo, contenido FROM notas WHERE usuario_id = {session['usuario_id']} AND titulo LIKE '%{q}%'"
        filas = db.get_db().execute(consulta).fetchall()
    return render_template("buscar.html", q=q, notas=filas)


@app.route("/ping")
@login_requerido
def ping():
    host = request.args.get("host", "")
    salida = ""
    if host:
        opcion = "-n" if os.name == "nt" else "-c"
        # VULNERABLE: V2 Command Injection, shell=True con entrada del usuario (CWE-78)
        resultado = subprocess.run(
            f"ping {opcion} 1 {host}", shell=True, capture_output=True, text=True, timeout=10
        )
        salida = resultado.stdout + resultado.stderr
    return render_template("ping.html", host=host, salida=salida)


if __name__ == "__main__":
    # VULNERABLE: V5 modo debug activo, expone el depurador interactivo de Werkzeug (CWE-489/CWE-94)
    app.run(debug=True)
