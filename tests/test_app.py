"""Pruebas funcionales básicas de NotasApp (pytest + cliente de pruebas de Flask)."""
import pytest

from app import db
from app.app import app


@pytest.fixture
def cliente(tmp_path):
    # Cada prueba usa su propia base SQLite temporal
    app.config.update(TESTING=True, DATABASE=str(tmp_path / "test.db"))
    with app.app_context():
        db.init_db()
    with app.test_client() as cliente:
        yield cliente


def registrar(cliente, usuario="ana", password="clave-demo"):
    return cliente.post("/registro", data={"usuario": usuario, "password": password})


def iniciar_sesion(cliente, usuario="ana", password="clave-demo"):
    return cliente.post("/login", data={"usuario": usuario, "password": password})


def test_home_responde_200(cliente):
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    assert "NotasApp" in respuesta.get_data(as_text=True)


def test_registro_redirige_al_login(cliente):
    respuesta = registrar(cliente)
    assert respuesta.status_code == 302
    assert respuesta.headers["Location"].endswith("/login")


def test_login_correcto_e_incorrecto(cliente):
    registrar(cliente)
    assert iniciar_sesion(cliente).status_code == 302
    respuesta = iniciar_sesion(cliente, password="otra")
    assert "incorrectos" in respuesta.get_data(as_text=True)


def test_crear_y_listar_nota(cliente):
    registrar(cliente)
    iniciar_sesion(cliente)
    cliente.post("/notas", data={"titulo": "Compras", "contenido": "leche y pan"})
    html = cliente.get("/notas").get_data(as_text=True)
    assert "Compras" in html and "leche y pan" in html


def test_v1_busqueda_no_filtra_notas_ajenas(cliente):
    registrar(cliente, "beto", "clave-beto")
    iniciar_sesion(cliente, "beto", "clave-beto")
    cliente.post("/notas", data={"titulo": "Privado de Beto", "contenido": "secreto"})
    cliente.get("/logout")
    registrar(cliente)
    iniciar_sesion(cliente)
    html = cliente.get("/buscar", query_string={"q": "' OR 1=1 --"}).get_data(as_text=True)
    assert "Privado de Beto" not in html


def test_v4_password_no_se_guarda_en_md5(cliente):
    registrar(cliente)
    with app.app_context():
        guardado = db.get_db().execute("SELECT password FROM usuarios").fetchone()["password"]
    assert guardado.startswith("scrypt:")  # formato de werkzeug: metodo$sal$hash
    assert len(guardado) != 32             # un MD5 en hex mide 32 caracteres


def test_v2_ping_rechaza_inyeccion_de_comandos(cliente):
    registrar(cliente)
    iniciar_sesion(cliente)
    html = cliente.get("/ping", query_string={"host": "127.0.0.1 && whoami"}).get_data(as_text=True)
    assert "Host no válido" in html
