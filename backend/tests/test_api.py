"""Pruebas de los endpoints de la API con un gestor aislado."""
import pytest
from fastapi.testclient import TestClient

from backend import servicio
from backend.esquemas import ElementoEntrada
from backend.main import app


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    """Cada prueba usa su propio datos.json temporal."""
    gestor = servicio.GestorTareas(tmp_path / "datos.json")
    monkeypatch.setattr(servicio, "gestor", gestor)
    with TestClient(app) as cliente:
        yield cliente


def datos(codigo=1, **cambios):
    base = {
        "codigo": codigo,
        "tipo": "Tarea",
        "titulo": f"Tarea {codigo}",
        "vencimiento": "2026-12-31",
        "prioridad": "Media",
        "etiquetas": ["demo"],
        "notas": "",
    }
    base.update(cambios)
    return base


def test_crear_y_listar(cliente):
    respuesta = cliente.post("/api/elementos", json=datos(5))
    assert respuesta.status_code == 201
    assert respuesta.json()["codigo"] == 5
    assert respuesta.json()["vencido"] is False

    lista = cliente.get("/api/elementos").json()
    assert [elemento["codigo"] for elemento in lista] == [5]


def test_codigo_duplicado(cliente):
    assert cliente.post("/api/elementos", json=datos(5)).status_code == 201
    respuesta = cliente.post("/api/elementos", json=datos(5))
    assert respuesta.status_code == 409


def test_validacion_de_datos(cliente):
    assert cliente.post("/api/elementos", json=datos(1, titulo="   ")).status_code == 422
    assert cliente.post("/api/elementos", json=datos(1, prioridad="Urgente")).status_code == 422
    assert cliente.post("/api/elementos", json=datos(1, vencimiento="31/12/2026")).status_code == 422


def test_buscar_por_codigo_y_por_texto(cliente):
    cliente.post("/api/elementos", json=datos(2, titulo="Estudiar ABB"))

    por_codigo = cliente.get("/api/buscar", params={"texto": "2"}).json()
    assert [elemento["codigo"] for elemento in por_codigo] == [2]

    por_texto = cliente.get("/api/buscar", params={"texto": "abb"}).json()
    assert [elemento["codigo"] for elemento in por_texto] == [2]


def test_obtener_inexistente(cliente):
    assert cliente.get("/api/elementos/99").status_code == 404


def test_completar_y_eliminar(cliente):
    cliente.post("/api/elementos", json=datos(1))

    completado = cliente.patch("/api/elementos/1/completado").json()
    assert completado["completado"] is True

    assert cliente.delete("/api/elementos/1").status_code == 200
    assert cliente.get("/api/elementos/1").status_code == 404


def test_actualizar_elemento(cliente):
    cliente.post("/api/elementos", json=datos(1))
    respuesta = cliente.put(
        "/api/elementos/1",
        json=datos(1, titulo="Actualizada", prioridad="Alta"),
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["titulo"] == "Actualizada"
    assert respuesta.json()["prioridad"] == "Alta"


def test_estadisticas_y_estructura(cliente):
    for codigo in (2, 1, 3):
        cliente.post("/api/elementos", json=datos(codigo))

    estadisticas = cliente.get("/api/estadisticas").json()
    assert estadisticas["total"] == 3
    assert estadisticas["por_tipo"]["Tarea"] == 3

    raiz = cliente.get("/api/arbol").json()["raiz"]
    assert raiz["codigo"] == 2
    assert raiz["izquierdo"]["codigo"] == 1
    assert raiz["derecho"]["codigo"] == 3


def test_reportes_y_etiquetas(cliente):
    cliente.post("/api/elementos", json=datos(1, vencimiento="2020-01-01", etiquetas=["universidad"]))
    cliente.post("/api/elementos", json=datos(2, vencimiento="2099-01-01", etiquetas=["trabajo"]))

    vencidas = cliente.get("/api/reportes/vencidas").json()
    assert [elemento["codigo"] for elemento in vencidas] == [1]

    por_etiqueta = cliente.get("/api/reportes/etiqueta/universidad").json()
    assert [elemento["codigo"] for elemento in por_etiqueta] == [1]

    assert set(cliente.get("/api/etiquetas").json()) == {"universidad", "trabajo"}


def test_demo_y_persistencia(cliente, tmp_path):
    respuesta = cliente.post("/api/demo")
    assert respuesta.status_code == 200
    assert respuesta.json()["insertados"] == 5

    ruta = tmp_path / "datos.json"
    assert ruta.exists()

    # Un gestor nuevo debe recuperar los mismos datos desde el archivo.
    otro = servicio.GestorTareas(ruta)
    assert len(otro.listar()) == 5


def test_persistencia_conserva_la_forma_del_abb(tmp_path):
    """Guardar en preorden debe reconstruir exactamente el mismo arbol."""
    ruta = tmp_path / "datos.json"
    gestor = servicio.GestorTareas(ruta)

    for codigo in (8, 3, 10, 1, 6):
        gestor.crear(
            ElementoEntrada(
                codigo=codigo,
                tipo="Tarea",
                titulo=f"Tarea {codigo}",
                vencimiento="2026-12-31",
                prioridad="Media",
                etiquetas=[],
                notas="",
            )
        )

    recargado = servicio.GestorTareas(ruta)
    estructura = recargado.estructura()

    assert estructura["codigo"] == 8
    assert estructura["izquierdo"]["codigo"] == 3
    assert estructura["derecho"]["codigo"] == 10
    assert estructura["izquierdo"]["izquierdo"]["codigo"] == 1
    assert estructura["izquierdo"]["derecho"]["codigo"] == 6
