"""
adaptadores/docker.py
=====================
Adaptador para monitorear y gestionar contenedores Docker.
Soporta ejecución local (vía subprocess) o remota (vía SSH con Paramiko).
"""

import logging
import subprocess
from typing import Optional, Any, List, Dict
import paramiko

logger = logging.getLogger("agente-ia.docker")


class AdaptadorDocker:
    """
    Gestiona y monitorea contenedores Docker.

    Uso:
        docker_adapter = AdaptadorDocker(ssh_client=nginx_client)
        contenedores = docker_adapter.obtener_contenedores()
    """

    def __init__(
        self,
        host: str = "",
        user: str = "",
        key_path: str = "",
        port: int = 22,
        ssh_client: Optional[paramiko.SSHClient] = None,
    ) -> None:
        self.host = host
        self.user = user
        self.key_path = key_path
        self.port = port
        self._cliente_ssh = ssh_client
        self._externo = ssh_client is not None or bool(host)
        self._auto_conectado = False

    def _conectar_ssh(self) -> None:
        """Establece la conexión SSH si se configuraron credenciales y no hay cliente provisto."""
        if self._cliente_ssh is not None:
            return
        if not self.host:
            return

        try:
            self._cliente_ssh = paramiko.SSHClient()
            self._cliente_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self._cliente_ssh.connect(
                hostname=self.host,
                port=self.port,
                username=self.user,
                key_filename=self.key_path,
                timeout=10,
            )
            self._auto_conectado = True
            logger.info("SSH conectado para monitoreo de Docker a %s:%s", self.host, self.port)
        except Exception as e:
            logger.error("Error SSH al conectar para Docker: %s", e)
            self._cliente_ssh = None
            raise

    def ejecutar_comando(self, cmd: str) -> str:
        """Ejecuta un comando de consola local o remoto."""
        if self._externo:
            if self._cliente_ssh is None:
                self._conectar_ssh()
            if self._cliente_ssh is None:
                return ""
            try:
                _, stdout, stderr = self._cliente_ssh.exec_command(cmd, timeout=10)
                salida = stdout.read().decode("utf-8", errors="replace").strip()
                return salida
            except Exception as e:
                logger.error("Error ejecutando comando remoto de Docker '%s': %s", cmd, e)
                return ""
        else:
            try:
                resultado = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, timeout=10
                )
                if resultado.returncode != 0:
                    logger.debug("Comando local Docker falló con stderr: %s", resultado.stderr)
                return resultado.stdout.strip()
            except subprocess.TimeoutExpired:
                logger.error("Timeout ejecutando comando local Docker '%s'", cmd)
                return ""
            except Exception as e:
                logger.error("Error ejecutando comando local Docker '%s': %s", cmd, e)
                return ""

    def obtener_contenedores(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista completa de contenedores e integra sus estadísticas de consumo.

        Returns:
            List[Dict] con id, nombre, imagen, estado, status, puertos, cpu, memoria.
        """
        logger.debug("Obteniendo lista de contenedores Docker...")
        cmd_ps = "docker ps -a --format '{{.ID}}\\t{{.Names}}\\t{{.Image}}\\t{{.Status}}\\t{{.State}}\\t{{.Ports}}'"
        salida_ps = self.ejecutar_comando(cmd_ps)

        if not salida_ps:
            return []

        contenedores = []
        lineas = salida_ps.splitlines()

        for linea in lineas:
            partes = linea.split("\t")
            if len(partes) >= 5:
                contenedores.append({
                    "id": partes[0],
                    "nombre": partes[1],
                    "imagen": partes[2],
                    "status": partes[3],  # Ej: "Up 2 hours" o "Exited (1) 5m ago"
                    "estado": partes[4],  # Ej: "running", "exited", "restarting"
                    "puertos": partes[5] if len(partes) > 5 else "",
                    "cpu": "—",
                    "memoria": "—",
                })

        # Si hay contenedores activos, obtener estadísticas de consumo de CPU/RAM
        activos = [c for c in contenedores if c["estado"] == "running"]
        if activos:
            cmd_stats = "docker stats --no-stream --format '{{.Name}}\\t{{.CPUPerc}}\\t{{.MemUsage}}\\t{{.MemPerc}}'"
            salida_stats = self.ejecutar_comando(cmd_stats)
            if salida_stats:
                stats_dict = {}
                for linea in salida_stats.splitlines():
                    partes = linea.split("\t")
                    if len(partes) >= 4:
                        stats_dict[partes[0]] = {
                            "cpu": partes[1],
                            "mem_raw": partes[2],
                            "mem_pct": partes[3],
                        }
                # Enriquecer contenedores con estadísticas
                for c in contenedores:
                    nombre = c["nombre"]
                    if nombre in stats_dict:
                        c["cpu"] = stats_dict[nombre]["cpu"]
                        c["memoria"] = f"{stats_dict[nombre]['mem_raw']} ({stats_dict[nombre]['mem_pct']})"

        return contenedores

    def obtener_logs(self, id_o_nombre: str, lineas: int = 50) -> str:
        """Obtiene la bitácora de logs reciente de un contenedor."""
        logger.info("Obteniendo logs para contenedor '%s'...", id_o_nombre)
        # Sanitizar entrada para seguridad básica contra inyección
        id_sanitizado = "".join(c for c in id_o_nombre if c.isalnum() or c in "-_.")
        cmd = f"docker logs --tail {lineas} {id_sanitizado} 2>&1"
        return self.ejecutar_comando(cmd)

    def iniciar_contenedor(self, id_o_nombre: str) -> Dict[str, Any]:
        """Arranca un contenedor detenido."""
        logger.warning("Arrancando contenedor '%s'...", id_o_nombre)
        id_sanitizado = "".join(c for c in id_o_nombre if c.isalnum() or c in "-_.")
        cmd = f"docker start {id_sanitizado}"
        salida = self.ejecutar_comando(cmd)
        exito = salida == id_sanitizado or id_sanitizado in salida
        return {
            "exito": exito,
            "mensaje": f"Contenedor '{id_o_nombre}' arrancado con éxito" if exito else f"Error al arrancar: {salida}",
        }

    def detener_contenedor(self, id_o_nombre: str) -> Dict[str, Any]:
        """Detiene un contenedor en ejecución."""
        logger.warning("Deteniendo contenedor '%s'...", id_o_nombre)
        id_sanitizado = "".join(c for c in id_o_nombre if c.isalnum() or c in "-_.")
        cmd = f"docker stop {id_sanitizado}"
        salida = self.ejecutar_comando(cmd)
        exito = salida == id_sanitizado or id_sanitizado in salida
        return {
            "exito": exito,
            "mensaje": f"Contenedor '{id_o_nombre}' detenido con éxito" if exito else f"Error al detener: {salida}",
        }

    def reiniciar_contenedor(self, id_o_nombre: str) -> Dict[str, Any]:
        """Reinicia un contenedor."""
        logger.warning("Reiniciando contenedor '%s'...", id_o_nombre)
        id_sanitizado = "".join(c for c in id_o_nombre if c.isalnum() or c in "-_.")
        cmd = f"docker restart {id_sanitizado}"
        salida = self.ejecutar_comando(cmd)
        exito = salida == id_sanitizado or id_sanitizado in salida
        return {
            "exito": exito,
            "mensaje": f"Contenedor '{id_o_nombre}' reiniciado con éxito" if exito else f"Error al reiniciar: {salida}",
        }

    def obtener_metricas(self) -> Dict[str, Any]:
        """Recopila las métricas globales para la persistencia del agente."""
        logger.info("Recopilando telemetría de microservicios Docker...")
        try:
            contenedores = self.obtener_contenedores()
            total = len(contenedores)
            activos = sum(1 for c in contenedores if c["estado"] == "running")
            detenidos = total - activos
            return {
                "origen": "docker",
                "contenedores": contenedores,
                "resumen": {
                    "total": total,
                    "activos": activos,
                    "detenidos": detenidos,
                },
                "ok": True,
            }
        except Exception as e:
            logger.error("Error al obtener telemetría de Docker: %s", e)
            return {"origen": "docker", "ok": False, "error": str(e)}

    def desconectar(self) -> None:
        """Cierra la conexión SSH auto-generada."""
        if self._auto_conectado and self._cliente_ssh:
            self._cliente_ssh.close()
            self._cliente_ssh = None
            self._auto_conectado = False
            logger.info("Conexión SSH auto-conectada de Docker cerrada")

    def __del__(self):
        self.desconectar()
