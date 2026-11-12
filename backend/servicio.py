"""Servicio de aplicacion: envuelve el ABB y gestiona la persistencia JSON."""
from __future__ import annotations

import json
import threading
from datetime import date
from pathlib import Path

from .arbol_tareas import Arbol, Elemento
from .esquemas import ElementoEntrada

# El archivo de datos vive en la raiz del proyecto.
RUTA_DATOS = Path(__file__).resolve().parent.parent / "datos.json"

PRIORIDAD_ORDEN = {"Alta": 0, "Media": 1, "Baja": 2}


class CodigoDuplicado(Exception):
    """El codigo ya existe en el arbol."""


class NoEncontrado(Exception):
    """No existe un elemento con ese codigo."""


class GestorTareas:
    """Encapsula el ABB y mantiene los datos sincronizados con datos.json."""

    def __init__(self, ruta_datos: str | Path | None = None):
        self.ruta_datos = Path(ruta_datos) if ruta_datos else RUTA_DATOS
        self.arbol = Arbol()
        self._candado = threading.Lock()
        self.cargar()

    # ------------------------- Persistencia -------------------------
    def cargar(self) -> None:
        if not self.ruta_datos.exists():
            return
        try:
            with self.ruta_datos.open("r", encoding="utf-8") as archivo:
                registros = json.load(archivo)
        except (json.JSONDecodeError, OSError) as error:
            print(f"[aviso] No se pudo leer {self.ruta_datos}: {error}")
            return

        for registro in registros:
            try:
                self.arbol.insertar(self._desde_dict(registro))
            except (KeyError, TypeError, ValueError) as error:
                print(f"[aviso] Registro invalido ignorado: {error}")

    def guardar(self) -> None:
        # Se guarda en preorden para que, al reinsertar al iniciar,
        # se reconstruya exactamente la misma forma del ABB.
        registros = [self._a_dict(elemento) for elemento in self.arbol.recorrer_preorden()]
        self.ruta_datos.parent.mkdir(parents=True, exist_ok=True)
        with self.ruta_datos.open("w", encoding="utf-8") as archivo:
            json.dump(registros, archivo, ensure_ascii=False, indent=2)

    def _a_dict(self, elemento: Elemento) -> dict:
        return {
            "codigo": elemento.codigo,
            "tipo": elemento.tipo,
            "titulo": elemento.titulo,
            "vencimiento": elemento.vencimiento.isoformat(),
            "prioridad": elemento.prioridad,
            "etiquetas": list(elemento.etiquetas),
            "notas": elemento.notas,
            "completado": elemento.completado,
        }

    def _desde_dict(self, datos: dict) -> Elemento:
        elemento = Elemento(
            codigo=datos["codigo"],
            tipo=datos["tipo"],
            titulo=datos["titulo"],
            vencimiento=date.fromisoformat(datos["vencimiento"]),
            prioridad=datos["prioridad"],
            etiquetas=list(datos.get("etiquetas", [])),
            notas=datos.get("notas", ""),
        )
        elemento.completado = bool(datos.get("completado", False))
        return elemento

    def _construir(self, datos: ElementoEntrada) -> Elemento:
        return Elemento(
            codigo=datos.codigo,
            tipo=datos.tipo,
            titulo=datos.titulo,
            vencimiento=datos.vencimiento,
            prioridad=datos.prioridad,
            etiquetas=list(datos.etiquetas),
            notas=datos.notas,
        )

    def a_salida(self, elemento: Elemento) -> dict:
        salida = self._a_dict(elemento)
        salida["vencido"] = elemento.esta_vencido()
        return salida

    # ------------------------- CRUD -------------------------
    def listar(self, orden: str = "codigo") -> list[dict]:
        elementos = self.arbol.recorrer()
        if orden == "fecha":
            elementos = sorted(elementos, key=lambda e: (e.vencimiento, e.codigo))
        elif orden == "prioridad":
            elementos = sorted(
                elementos,
                key=lambda e: (PRIORIDAD_ORDEN.get(e.prioridad, 9), e.vencimiento, e.codigo),
            )
        return [self.a_salida(elemento) for elemento in elementos]

    def obtener(self, codigo: int) -> dict:
        elemento = self.arbol.buscar(codigo)
        if elemento is None:
            raise NoEncontrado(f"No existe un elemento con el codigo {codigo}.")
        return self.a_salida(elemento)

    def crear(self, datos: ElementoEntrada) -> dict:
        with self._candado:
            if self.arbol.buscar(datos.codigo) is not None:
                raise CodigoDuplicado(f"Ya existe un elemento con el codigo {datos.codigo}.")
            elemento = self._construir(datos)
            self.arbol.insertar(elemento)
            self.guardar()
        return self.a_salida(elemento)

    def actualizar(self, codigo: int, datos: ElementoEntrada) -> dict:
        with self._candado:
            actual = self.arbol.buscar(codigo)
            if actual is None:
                raise NoEncontrado(f"No existe un elemento con el codigo {codigo}.")
            if datos.codigo != codigo and self.arbol.buscar(datos.codigo) is not None:
                raise CodigoDuplicado(f"Ya existe un elemento con el codigo {datos.codigo}.")

            completado = actual.completado
            if datos.codigo != codigo:
                # El ABB se ordena por codigo: si cambia, se reinserta.
                self.arbol.eliminar(codigo)
                elemento = self._construir(datos)
                elemento.completado = completado
                self.arbol.insertar(elemento)
            else:
                actual.tipo = datos.tipo
                actual.titulo = datos.titulo
                actual.vencimiento = datos.vencimiento
                actual.prioridad = datos.prioridad
                actual.etiquetas = list(datos.etiquetas)
                actual.notas = datos.notas
                elemento = actual

            self.guardar()
        return self.a_salida(elemento)

    def eliminar(self, codigo: int) -> None:
        with self._candado:
            if self.arbol.buscar(codigo) is None:
                raise NoEncontrado(f"No existe un elemento con el codigo {codigo}.")
            self.arbol.eliminar(codigo)
            self.guardar()

    def alternar_completado(self, codigo: int) -> dict:
        with self._candado:
            elemento = self.arbol.buscar(codigo)
            if elemento is None:
                raise NoEncontrado(f"No existe un elemento con el codigo {codigo}.")
            elemento.completado = not elemento.completado
            self.guardar()
        return self.a_salida(elemento)

    # ------------------------- Consultas -------------------------
    def buscar(self, texto: str) -> list[dict]:
        texto = texto.strip()
        if not texto:
            return self.listar()

        # Si el texto es un numero se usa la busqueda recursiva del ABB.
        if texto.lstrip("-").isdigit():
            elemento = self.arbol.buscar(int(texto))
            return [self.a_salida(elemento)] if elemento else []

        minusculas = texto.lower()
        return [
            self.a_salida(elemento)
            for elemento in self.arbol.recorrer(
                lambda e: minusculas in e.titulo.lower()
                or any(minusculas in etiqueta.lower() for etiqueta in e.etiquetas)
            )
        ]

    def reporte_vencidas(self) -> list[dict]:
        return [self.a_salida(elemento) for elemento in self.arbol.reporte_vencidas()]

    def reporte_por_etiqueta(self, etiqueta: str) -> list[dict]:
        return [self.a_salida(elemento) for elemento in self.arbol.reporte_por_etiqueta(etiqueta)]

    def etiquetas(self) -> list[str]:
        return self.arbol.etiquetas_existentes()

    def estadisticas(self) -> dict:
        elementos = self.arbol.recorrer()
        por_prioridad = {"Alta": 0, "Media": 0, "Baja": 0}
        por_tipo = {"Tarea": 0, "Proyecto": 0}
        completadas = 0
        vencidas = 0

        for elemento in elementos:
            por_prioridad[elemento.prioridad] = por_prioridad.get(elemento.prioridad, 0) + 1
            por_tipo[elemento.tipo] = por_tipo.get(elemento.tipo, 0) + 1
            if elemento.completado:
                completadas += 1
            if elemento.esta_vencido():
                vencidas += 1

        total = len(elementos)
        return {
            "total": total,
            "completadas": completadas,
            "pendientes": total - completadas,
            "vencidas": vencidas,
            "por_prioridad": por_prioridad,
            "por_tipo": por_tipo,
        }

    def estructura(self):
        return self.arbol.estructura()

    def cargar_demo(self) -> int:
        ejemplos = [
            Elemento(8, "Proyecto", "Lanzar sitio web", date(2026, 12, 15), "Alta",
                     ["web", "trabajo"], "Coordinar diseno y desarrollo."),
            Elemento(3, "Tarea", "Entregar informe", date(2026, 10, 1), "Alta",
                     ["universidad"], "Revisar formato IEEE."),
            Elemento(10, "Tarea", "Comprar utiles", date(2026, 11, 20), "Baja",
                     ["personal"], ""),
            Elemento(1, "Tarea", "Estudiar para examen", date(2026, 10, 20), "Media",
                     ["universidad", "estudio"], "Repasar arboles ABB."),
            Elemento(6, "Proyecto", "Proyecto final de grupo", date(2026, 12, 1), "Alta",
                     ["universidad", "trabajo"], "Gestor de tareas con ABB."),
        ]

        insertados = 0
        with self._candado:
            for elemento in ejemplos:
                if self.arbol.insertar(elemento):
                    insertados += 1
            if insertados:
                self.guardar()
        return insertados


# Instancia unica que usan las rutas de FastAPI.
gestor = GestorTareas()
