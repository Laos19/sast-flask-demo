"""Configuración común de pytest: se ejecuta antes de importar la app."""
import os
import secrets

# La app exige SECRET_KEY en el entorno (corrección de V3); en pruebas se genera una aleatoria
os.environ.setdefault("SECRET_KEY", secrets.token_hex(16))
