"""Esquemas de validacion (Pydantic) para la API del gestor de tareas."""
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator

TipoElemento = Literal["Tarea", "Proyecto"]
Prioridad = Literal["Alta", "Media", "Baja"]


class ElementoEntrada(BaseModel):
    """Datos que el frontend envia para crear o actualizar un elemento."""

    codigo: int = Field(..., description="Codigo entero unico que ordena el ABB")
    tipo: TipoElemento = "Tarea"
    titulo: str = Field(..., min_length=1, max_length=200)
    vencimiento: date
    prioridad: Prioridad = "Media"
    etiquetas: list[str] = Field(default_factory=list)
    notas: str = ""

    @field_validator("titulo")
    @classmethod
    def titulo_no_vacio(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("El titulo no puede estar vacio")
        return valor

    @field_validator("etiquetas")
    @classmethod
    def limpiar_etiquetas(cls, valores: list[str]) -> list[str]:
        return [valor.strip() for valor in valores if valor and valor.strip()]


class ElementoSalida(ElementoEntrada):
    """Elemento tal como lo devuelve la API."""

    completado: bool
    vencido: bool


class Estadisticas(BaseModel):
    total: int
    completadas: int
    pendientes: int
    vencidas: int
    por_prioridad: dict[str, int]
    por_tipo: dict[str, int]


class Mensaje(BaseModel):
    mensaje: str
