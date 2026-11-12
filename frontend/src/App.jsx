import { useCallback, useEffect, useState } from "react";
import { api } from "./api";
import { ESTILO_ENTRADA, ESTILO_SECUNDARIO } from "./estilos";
import { useTema } from "./hooks/useTema";
import Sidebar from "./components/Sidebar";
import Tarjeta from "./components/Tarjeta";
import ArbolSVG from "./components/ArbolSVG";

const ESTILO_SELECT =
  "rounded-lg border border-gray-300 bg-white px-2 py-2 text-sm text-gray-900 outline-none focus:border-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100";

export default function App() {
  const { tema, alternarTema } = useTema();

  const [elementos, setElementos] = useState([]);
  const [estadisticas, setEstadisticas] = useState(null);
  const [etiquetas, setEtiquetas] = useState([]);
  const [estructura, setEstructura] = useState(null);
  const [vista, setVista] = useState("Todos los elementos");
  const [orden, setOrden] = useState("codigo");
  const [texto, setTexto] = useState("");
  const [etiqueta, setEtiqueta] = useState("");
  const [seccion, setSeccion] = useState("lista");
  const [toast, setToast] = useState(null);
  const [editando, setEditando] = useState(null);

  const mostrarToast = useCallback((mensaje, tipo = "ok") => {
    setToast({ mensaje, tipo });
  }, []);

  useEffect(() => {
    if (!toast) return;
    const temporizador = setTimeout(() => setToast(null), 3200);
    return () => clearTimeout(temporizador);
  }, [toast]);

  const recargar = useCallback(
    async (ordenElegido, tituloVista = "Todos los elementos") => {
      try {
        const ordenActual = ordenElegido ?? orden;
        const [lista, stats, tags, arbol] = await Promise.all([
          api.listar(ordenActual),
          api.estadisticas(),
          api.etiquetas(),
          api.arbol(),
        ]);
        setElementos(lista);
        setEstadisticas(stats);
        setEtiquetas(tags);
        setEstructura(arbol.raiz);
        setVista(tituloVista);
      } catch (error) {
        mostrarToast(error.message, "error");
      }
    },
    [orden, mostrarToast]
  );

  useEffect(() => {
    recargar();
  }, [recargar]);

  async function crear(datos) {
    try {
      await api.crear(datos);
      mostrarToast("Elemento creado correctamente.");
      await recargar(orden);
      return true;
    } catch (error) {
      mostrarToast(error.message, "error");
      return false;
    }
  }

  async function guardarEdicion(codigoOriginal, datos) {
    try {
      await api.actualizar(codigoOriginal, datos);
      mostrarToast("Elemento actualizado correctamente.");
      setEditando(null);
      await recargar(orden);
      return true;
    } catch (error) {
      mostrarToast(error.message, "error");
      return false;
    }
  }

  async function eliminar(elemento) {
    if (!window.confirm(`¿Eliminar "${elemento.titulo}"?`)) return;
    try {
      await api.eliminar(elemento.codigo);
      if (editando && editando.codigo === elemento.codigo) {
        setEditando(null);
      }
      mostrarToast("Elemento eliminado.");
      await recargar(orden);
    } catch (error) {
      mostrarToast(error.message, "error");
    }
  }

  async function alternar(codigo) {
    try {
      await api.alternar(codigo);
      await recargar(orden);
    } catch (error) {
      mostrarToast(error.message, "error");
    }
  }

  async function cargarDemo() {
    try {
      const resultado = await api.demo();
      mostrarToast(resultado.mensaje);
      await recargar(orden);
    } catch (error) {
      mostrarToast(error.message, "error");
    }
  }

  async function buscar() {
    const limpio = texto.trim();
    if (!limpio) {
      await recargar(orden);
      return;
    }
    try {
      const resultados = await api.buscar(limpio);
      setElementos(resultados);
      setVista(`Resultados: '${limpio}'`);
      setSeccion("lista");
    } catch (error) {
      mostrarToast(error.message, "error");
    }
  }

  async function reporteVencidas() {
    try {
      const resultados = await api.vencidas();
      setElementos(resultados);
      setVista("Reporte: tareas vencidas");
      setSeccion("lista");
    } catch (error) {
      mostrarToast(error.message, "error");
    }
  }

  async function reporteEtiqueta() {
    const valor = etiqueta.trim();
    if (!valor) {
      mostrarToast("Escribe o elige una etiqueta.", "error");
      return;
    }
    try {
      const resultados = await api.porEtiqueta(valor);
      setElementos(resultados);
      setVista(`Reporte: etiqueta '${valor}'`);
      setSeccion("lista");
    } catch (error) {
      mostrarToast(error.message, "error");
    }
  }

  return (
    <div
      className="flex h-screen overflow-hidden bg-gray-100 text-gray-900 dark:bg-gray-900 dark:text-gray-100"
      style={{ colorScheme: tema }}
    >
      <Sidebar
        onCrear={crear}
        onEditar={guardarEdicion}
        onDemo={cargarDemo}
        tema={tema}
        onAlternarTema={alternarTema}
        elementoEditando={editando}
        onCancelarEdicion={() => setEditando(null)}
      />

      <main className="flex min-w-0 flex-1 flex-col gap-4 overflow-hidden p-5">
        {/* Fila 0: busqueda y orden */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="max-w-md min-w-55 flex-1">
            <input
              value={texto}
              onChange={(evento) => setTexto(evento.target.value)}
              onKeyDown={(evento) => evento.key === "Enter" && buscar()}
              placeholder="🔍  Buscar por código o por título..."
              className={ESTILO_ENTRADA}
            />
          </div>
          <button
            type="button"
            onClick={buscar}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
          >
            Buscar
          </button>
          <button
            type="button"
            onClick={() => {
              setTexto("");
              recargar(orden);
            }}
            className={ESTILO_SECUNDARIO}
          >
            Ver todo
          </button>

          <div className="ml-auto flex items-center gap-2">
            <label className="text-xs text-gray-500 dark:text-gray-400">Ordenar</label>
            <select
              value={orden}
              onChange={(evento) => setOrden(evento.target.value)}
              className={ESTILO_SELECT}
            >
              <option value="codigo">Código (ABB)</option>
              <option value="fecha">Fecha</option>
              <option value="prioridad">Prioridad</option>
            </select>

            <div className="flex rounded-lg bg-gray-200 p-1 dark:bg-gray-700">
              <button
                type="button"
                onClick={() => setSeccion("lista")}
                className={`rounded-md px-3 py-1 text-xs font-semibold transition ${
                  seccion === "lista"
                    ? "bg-white shadow dark:bg-gray-600"
                    : "text-gray-500 dark:text-gray-300"
                }`}
              >
                📋 Lista
              </button>
              <button
                type="button"
                onClick={() => setSeccion("arbol")}
                className={`rounded-md px-3 py-1 text-xs font-semibold transition ${
                  seccion === "arbol"
                    ? "bg-white shadow dark:bg-gray-600"
                    : "text-gray-500 dark:text-gray-300"
                }`}
              >
                🌳 Árbol
              </button>
            </div>
          </div>
        </div>

        {/* Fila 1: reportes */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={reporteVencidas}
            className="rounded-lg bg-red-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-red-600"
          >
            ⚠ Tareas vencidas
          </button>
          <select
            value={etiqueta}
            onChange={(evento) => setEtiqueta(evento.target.value)}
            className={`${ESTILO_SELECT} min-w-42.5`}
          >
            <option value="">Etiqueta...</option>
            {etiquetas.map((tag) => (
              <option key={tag} value={tag}>
                {tag}
              </option>
            ))}
          </select>
          <button type="button" onClick={reporteEtiqueta} className={ESTILO_SECUNDARIO}>
            🏷 Reporte por etiqueta
          </button>
        </div>

        {/* Fila 2: titulo de la vista y estadisticas */}
        <div className="flex flex-wrap items-end justify-between gap-2">
          <h2 className="text-lg font-bold">
            {vista} <span className="text-gray-400">({elementos.length})</span>
          </h2>

          {estadisticas && (
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-gray-500 dark:text-gray-400">
              <span>
                Total: <b className="text-gray-800 dark:text-gray-100">{estadisticas.total}</b>
              </span>
              <span>
                Pendientes:{" "}
                <b className="text-gray-800 dark:text-gray-100">{estadisticas.pendientes}</b>
              </span>
              <span>
                Completadas:{" "}
                <b className="text-gray-800 dark:text-gray-100">{estadisticas.completadas}</b>
              </span>
              <span className="text-red-500">
                Vencidas: <b>{estadisticas.vencidas}</b>
              </span>
            </div>
          )}
        </div>

        {/* Fila 3: contenido */}
        {seccion === "lista" ? (
          <div className="flex-1 space-y-3 overflow-y-auto pr-1">
            {elementos.length === 0 ? (
              <div className="flex h-full flex-col items-center justify-center gap-2 text-gray-500 dark:text-gray-400">
                <p className="text-3xl">🌳</p>
                <p>No hay elementos para mostrar.</p>
              </div>
            ) : (
              elementos.map((elemento) => (
                <Tarjeta
                  key={elemento.codigo}
                  elemento={elemento}
                  onAlternar={alternar}
                  onEditar={setEditando}
                  onEliminar={eliminar}
                />
              ))
            )}
          </div>
        ) : (
          <ArbolSVG estructura={estructura} />
        )}
      </main>

      {toast && (
        <div
          className={`fixed right-5 bottom-5 z-50 rounded-xl px-4 py-3 text-sm font-medium text-white shadow-xl ${
            toast.tipo === "error" ? "bg-red-600" : "bg-emerald-600"
          }`}
        >
          {toast.mensaje}
        </div>
      )}
    </div>
  );
}
