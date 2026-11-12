"""Pruebas unitarias de la logica del arbol binario de busqueda."""
from datetime import date, timedelta

import pytest

from backend.arbol_tareas import Arbol, Elemento


def elemento(codigo, titulo="Elemento", vencimiento=None, prioridad="Media",
             etiquetas=None, tipo="Tarea", notas=""):
    return Elemento(
        codigo=codigo,
        tipo=tipo,
        titulo=titulo,
        vencimiento=vencimiento or date(2026, 12, 31),
        prioridad=prioridad,
        etiquetas=etiquetas or [],
        notas=notas,
    )


@pytest.fixture
def arbol():
    """Arbol de ejemplo: 8 es la raiz, 3 e 10 sus hijos."""
    estructura = Arbol()
    for codigo in [8, 3, 10, 1, 6]:
        assert estructura.insertar(elemento(codigo, f"Elemento {codigo}"))
    return estructura


def test_insertar_rechaza_codigos_duplicados(arbol):
    assert not arbol.insertar(elemento(3))
    assert len(arbol.recorrer()) == 5


def test_buscar_existente_e_inexistente(arbol):
    assert arbol.buscar(6).titulo == "Elemento 6"
    assert arbol.buscar(99) is None


def test_recorrido_inorden_ordenado_por_codigo(arbol):
    assert [e.codigo for e in arbol.recorrer()] == [1, 3, 6, 8, 10]


def test_recorrido_preorden_conserva_la_forma(arbol):
    assert [e.codigo for e in arbol.recorrer_preorden()] == [8, 3, 1, 6, 10]


def test_eliminar_hoja(arbol):
    assert arbol.eliminar(1)
    assert arbol.buscar(1) is None
    assert [e.codigo for e in arbol.recorrer()] == [3, 6, 8, 10]


def test_eliminar_nodo_con_un_hijo(arbol):
    # Al quitar 6, el nodo 3 queda con un unico hijo (1).
    arbol.eliminar(6)
    assert arbol.eliminar(3)
    assert arbol.buscar(3) is None
    assert arbol.buscar(1) is not None
    assert [e.codigo for e in arbol.recorrer()] == [1, 8, 10]


def test_eliminar_nodo_con_dos_hijos(arbol):
    # La raiz 8 tiene dos hijos: se reemplaza por el sucesor inorden (10).
    assert arbol.eliminar(8)
    assert arbol.buscar(8) is None
    assert [e.codigo for e in arbol.recorrer()] == [1, 3, 6, 10]


def test_reporte_de_vencidas_ignora_completadas():
    hoy = date.today()
    arbol = Arbol()
    vencida = elemento(1, vencimiento=hoy - timedelta(days=2))
    futura = elemento(2, vencimiento=hoy + timedelta(days=5))
    completada = elemento(3, vencimiento=hoy - timedelta(days=10))
    completada.completado = True

    for item in (vencida, futura, completada):
        arbol.insertar(item)

    assert [e.codigo for e in arbol.reporte_vencidas()] == [1]


def test_reporte_por_etiqueta_y_catalogo(arbol):
    arbol.buscar(3).etiquetas = ["Universidad", "Estudio"]
    arbol.buscar(8).etiquetas = ["trabajo"]

    assert [e.codigo for e in arbol.reporte_por_etiqueta("universidad")] == [3]
    assert arbol.etiquetas_existentes() == ["estudio", "trabajo", "universidad"]


def test_estructura_refleja_el_abb(arbol):
    estructura = arbol.estructura()
    assert estructura["codigo"] == 8
    assert estructura["izquierdo"]["codigo"] == 3
    assert estructura["derecho"]["codigo"] == 10
    assert estructura["izquierdo"]["izquierdo"]["codigo"] == 1
    assert estructura["izquierdo"]["derecho"]["codigo"] == 6
