# ................................................................
# Logica del gestor de tareas y proyectos con arbol binario
# de busqueda (ABB). El arbol se ordena por el codigo.
# ................................................................
from datetime import date


class Elemento:
    """Representa una tarea o un proyecto."""

    def __init__(self, codigo, tipo, titulo, vencimiento, prioridad, etiquetas, notas=""):
        self.codigo = codigo            # entero unico 
        self.tipo = tipo                # "tarea" o "proyecto"
        self.titulo = titulo
        self.vencimiento = vencimiento  # objeto date
        self.prioridad = prioridad      # "Alta", "Media" o "Baja"
        self.etiquetas = etiquetas      # lista de textos
        self.notas = notas
        self.completado = False

    def esta_vencido(self, hoy=None):
        hoy = hoy or date.today()
        return (not self.completado) and self.vencimiento < hoy

    def tiene_etiqueta(self, etiqueta):
        return etiqueta.lower() in [e.lower() for e in self.etiquetas]


class Nodo:
    def __init__(self, elemento):
        self.elemento = elemento
        self.izquierdo = None   # codigos menores
        self.derecho = None     # codigos mayores


class Arbol:
    def __init__(self):
        self.raiz = None

    # ....................................................
    # Crear / insercion recursiva
    # ....................................................
    def insertar(self, elemento):
        """Devuelve False si el código ya existe."""
        if self.buscar(elemento.codigo) is not None:
            return False
        self.raiz = self._insertar(self.raiz, elemento)
        return True

    def _insertar(self, nodo, elemento):
        if nodo is None:
            return Nodo(elemento)
        if elemento.codigo < nodo.elemento.codigo:
            nodo.izquierdo = self._insertar(nodo.izquierdo, elemento)
        else:
            nodo.derecho = self._insertar(nodo.derecho, elemento)
        return nodo

    # ....................................................
    # Buscar por código / recursiva
    # ....................................................
    def buscar(self, codigo):
        return self._buscar(self.raiz, codigo)

    def _buscar(self, nodo, codigo):
        if nodo is None:
            return None
        if codigo == nodo.elemento.codigo:
            return nodo.elemento
        if codigo < nodo.elemento.codigo:
            return self._buscar(nodo.izquierdo, codigo)
        return self._buscar(nodo.derecho, codigo)

    # ....................................................
    # Eliminar/ recursiva, maneja los 3 casos del ABB
    # ....................................................
    def eliminar(self, codigo):
        """Devuelve False si el código no existe."""
        if self.buscar(codigo) is None:
            return False
        self.raiz = self._eliminar(self.raiz, codigo)
        return True

    def _eliminar(self, nodo, codigo):
        if nodo is None:
            return None
        if codigo < nodo.elemento.codigo:
            nodo.izquierdo = self._eliminar(nodo.izquierdo, codigo)
        elif codigo > nodo.elemento.codigo:
            nodo.derecho = self._eliminar(nodo.derecho, codigo)
        else:
            # caso 1 y 2: sin hijos o con un solo hijo
            if nodo.izquierdo is None:
                return nodo.derecho
            if nodo.derecho is None:
                return nodo.izquierdo
            # Caso 3: dos hijos -> se reemplaza por el sucesor inorden
            sucesor = self._minimo(nodo.derecho)
            nodo.elemento = sucesor.elemento
            nodo.derecho = self._eliminar(nodo.derecho, sucesor.elemento.codigo)
        return nodo

    def _minimo(self, nodo):
        if nodo.izquierdo is None:
            return nodo
        return self._minimo(nodo.izquierdo)

    # ....................................................
    # Recorrido inorden con filtro opcional.
    # Sirve para listar todo y también para los reportes
    # ....................................................
    def recorrer(self, filtro=None):
        resultado = []
        self._inorden(self.raiz, filtro, resultado)
        return resultado

    def _inorden(self, nodo, filtro, resultado):
        if nodo is not None:
            self._inorden(nodo.izquierdo, filtro, resultado)
            if filtro is None or filtro(nodo.elemento):
                resultado.append(nodo.elemento)
            self._inorden(nodo.derecho, filtro, resultado)

    # ....................................................
    # Reportes
    # ....................................................
    def reporte_vencidas(self):
        return self.recorrer(lambda e: e.esta_vencido())

    def reporte_por_etiqueta(self, etiqueta):
        return self.recorrer(lambda e: e.tiene_etiqueta(etiqueta))

    def etiquetas_existentes(self):
        etiquetas = set()
        for e in self.recorrer():
            for etiqueta in e.etiquetas:
                etiquetas.add(etiqueta.lower())
        return sorted(etiquetas)