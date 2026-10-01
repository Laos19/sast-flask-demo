"""Acceso a la base de datos SQLite de NotasApp."""
import sqlite3

from flask import current_app, g

ESQUEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario  TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS notas (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    titulo     TEXT NOT NULL,
    contenido  TEXT NOT NULL
);
"""


def get_db():
    """Devuelve una conexión por petición (se guarda en flask.g)."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_error=None):
    """Cierra la conexión al terminar la petición."""
    conexion = g.pop("db", None)
    if conexion is not None:
        conexion.close()


def init_db():
    """Crea las tablas si no existen."""
    get_db().executescript(ESQUEMA)
