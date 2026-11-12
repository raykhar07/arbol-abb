"""API REST del gestor de tareas y proyectos con ABB (FastAPI)."""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from . import servicio
from .esquemas import ElementoEntrada, ElementoSalida, Estadisticas

app = FastAPI(
    title="Gestor de Tareas y Proyectos (ABB)",
    description=(
        "Backend del proyecto de Algoritmos II. Toda la logica del arbol "
        "binario de busqueda esta implementada en Python."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/salud")
def salud():
    """Comprobacion rapida de que el servidor esta vivo."""
    return {"estado": "ok"}


@app.get("/api/elementos", response_model=list[ElementoSalida])
def listar(orden: str = Query("codigo", pattern="^(codigo|fecha|prioridad)$")):
    return servicio.gestor.listar(orden)


@app.post("/api/elementos", response_model=ElementoSalida, status_code=201)
def crear(datos: ElementoEntrada):
    try:
        return servicio.gestor.crear(datos)
    except servicio.CodigoDuplicado as error:
        raise HTTPException(status_code=409, detail=str(error))


@app.get("/api/elementos/{codigo}", response_model=ElementoSalida)
def obtener(codigo: int):
    try:
        return servicio.gestor.obtener(codigo)
    except servicio.NoEncontrado as error:
        raise HTTPException(status_code=404, detail=str(error))


@app.put("/api/elementos/{codigo}", response_model=ElementoSalida)
def actualizar(codigo: int, datos: ElementoEntrada):
    try:
        return servicio.gestor.actualizar(codigo, datos)
    except servicio.NoEncontrado as error:
        raise HTTPException(status_code=404, detail=str(error))
    except servicio.CodigoDuplicado as error:
        raise HTTPException(status_code=409, detail=str(error))


@app.delete("/api/elementos/{codigo}")
def eliminar(codigo: int):
    try:
        servicio.gestor.eliminar(codigo)
    except servicio.NoEncontrado as error:
        raise HTTPException(status_code=404, detail=str(error))
    return {"mensaje": f"Elemento {codigo} eliminado."}


@app.patch("/api/elementos/{codigo}/completado", response_model=ElementoSalida)
def alternar_completado(codigo: int):
    try:
        return servicio.gestor.alternar_completado(codigo)
    except servicio.NoEncontrado as error:
        raise HTTPException(status_code=404, detail=str(error))


@app.get("/api/buscar", response_model=list[ElementoSalida])
def buscar(texto: str = Query("")):
    return servicio.gestor.buscar(texto)


@app.get("/api/reportes/vencidas", response_model=list[ElementoSalida])
def reporte_vencidas():
    return servicio.gestor.reporte_vencidas()


@app.get("/api/reportes/etiqueta/{etiqueta}", response_model=list[ElementoSalida])
def reporte_por_etiqueta(etiqueta: str):
    return servicio.gestor.reporte_por_etiqueta(etiqueta)


@app.get("/api/etiquetas", response_model=list[str])
def etiquetas():
    return servicio.gestor.etiquetas()


@app.get("/api/estadisticas", response_model=Estadisticas)
def estadisticas():
    return servicio.gestor.estadisticas()


@app.get("/api/arbol")
def arbol():
    """Estructura anidada del ABB para dibujarlo en el frontend."""
    return {"raiz": servicio.gestor.estructura()}


@app.post("/api/demo")
def cargar_demo():
    insertados = servicio.gestor.cargar_demo()
    return {
        "insertados": insertados,
        "mensaje": f"Se cargaron {insertados} elementos de ejemplo.",
    }
