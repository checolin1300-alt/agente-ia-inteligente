"""
adaptadores/__init__.py
=======================
Exporta las clases principales de los adaptadores para
facilitar las importaciones desde el resto del proyecto.
"""

from .nginx import AdaptadorNginx
from .mariadb import AdaptadorMariaDB
from .postgres import BaseDatos
from .mongodb import AdaptadorMongoDB
from .sistema import AdaptadorSistema
from .docker import AdaptadorDocker

__all__ = ["AdaptadorNginx", "AdaptadorMariaDB", "BaseDatos", "AdaptadorMongoDB", "AdaptadorSistema", "AdaptadorDocker"]
