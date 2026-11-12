import { useEffect, useRef, useState } from "react";
import { ESTILO_ENTRADA } from "../estilos";

const COLORES_PRIORIDAD = {
  Alta: "bg-red-500 text-white",
  Media: "bg-amber-500 text-white",
  Baja: "bg-green-500 text-white",
};

function Segmentado({ valor, opciones, onChange, colores }) {
  return (
    <div className="flex gap-1 rounded-lg bg-gray-200 p-1 dark:bg-gray-700">
      {opciones.map((opcion) => {
        const activo = valor === opcion;
        return (
          <button
            key={opcion}
            type="button"
            onClick={() => onChange(opcion)}
            className={`flex-1 rounded-md px-2 py-1.5 text-xs font-semibold transition ${
              activo
                ? colores?.[opcion] || "bg-blue-600 text-white"
                : "text-gray-600 hover:bg-gray-300 dark:text-gray-300 dark:hover:bg-gray-600"
            }`}
          >
            {opcion}
          </button>
        );
      })}
    </div>
  );
}

function Etiqueta({ children }) {
  return (
    <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-gray-400">
      {children}
    </label>
  );
}

export default function Sidebar({
  onCrear,
  onEditar,
  onDemo,
  tema,
  onAlternarTema,
  elementoEditando,
  onCancelarEdicion,
}) {
  const [tipo, setTipo] = useState("Tarea");
  const [codigo, setCodigo] = useState("");
  const [titulo, setTitulo] = useState("");
  const [vencimiento, setVencimiento] = useState("");
  const [prioridad, setPrioridad] = useState("Media");
  const [etiquetas, setEtiquetas] = useState("");
  const [notas, setNotas] = useState("");
  const [error, setError] = useState("");
  const [enviando, setEnviando] = useState(false);
  const referencia = useRef(null);

  function limpiar() {
    setCodigo("");
    setTitulo("");
    setVencimiento("");
    setEtiquetas("");
    setNotas("");
    setTipo("Tarea");
    setPrioridad("Media");
    setError("");
  }

  // Al entrar o salir del modo edicion, el formulario se rellena o se limpia.
  useEffect(() => {
    if (elementoEditando) {
      setTipo(elementoEditando.tipo);
      setCodigo(String(elementoEditando.codigo));
      setTitulo(elementoEditando.titulo);
      setVencimiento(elementoEditando.vencimiento);
      setPrioridad(elementoEditando.prioridad);
      setEtiquetas(elementoEditando.etiquetas.join(", "));
      setNotas(elementoEditando.notas || "");
      setError("");
      referencia.current?.scrollTo({ top: 0, behavior: "smooth" });
    } else {
      limpiar();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [elementoEditando]);

  async function enviar(evento) {
    evento.preventDefault();
    setError("");

    if (!codigo.trim() || !Number.isInteger(Number(codigo))) {
      setError("El código debe ser un número entero.");
      return;
    }
    if (!titulo.trim()) {
      setError("El título no puede estar vacío.");
      return;
    }
    if (!vencimiento) {
      setError("Selecciona una fecha de vencimiento.");
      return;
    }

    const datos = {
      codigo: Number(codigo),
      tipo,
      titulo: titulo.trim(),
      vencimiento,
      prioridad,
      etiquetas: etiquetas
        .split(",")
        .map((etiqueta) => etiqueta.trim())
        .filter(Boolean),
      notas: notas.trim(),
    };

    setEnviando(true);
    const guardado = elementoEditando
      ? await onEditar(elementoEditando.codigo, datos)
      : await onCrear(datos);
    setEnviando(false);

    if (guardado) {
      if (elementoEditando) onCancelarEdicion();
      limpiar();
    }
  }

  return (
    <aside
      ref={referencia}
      className={`flex w-72 shrink-0 flex-col overflow-y-auto border-r bg-white p-4 dark:bg-gray-800 ${
        elementoEditando
          ? "border-amber-400 ring-2 ring-amber-400/60 ring-inset dark:border-amber-400"
          : "border-gray-200 dark:border-gray-700"
      }`}
      style={{ colorScheme: tema }}
    >
      <h1 className="text-xl font-bold">
        {elementoEditando ? "✏️ Editar elemento" : "📋 Gestor ABB"}
      </h1>
      <p className="mb-3 text-xs text-gray-500 dark:text-gray-400">
        {elementoEditando
          ? `#${elementoEditando.codigo} · ${elementoEditando.titulo}`
          : "Nueva tarea o proyecto"}
      </p>

      <form onSubmit={enviar} className="space-y-3">
        <div>
          <Etiqueta>Tipo</Etiqueta>
          <Segmentado valor={tipo} opciones={["Tarea", "Proyecto"]} onChange={setTipo} />
        </div>

        <div>
          <Etiqueta>Código</Etiqueta>
          <input
            type="number"
            value={codigo}
            onChange={(evento) => setCodigo(evento.target.value)}
            placeholder="Ej: 12"
            className={ESTILO_ENTRADA}
          />
        </div>

        <div>
          <Etiqueta>Título</Etiqueta>
          <input
            type="text"
            value={titulo}
            onChange={(evento) => setTitulo(evento.target.value)}
            placeholder="Ej: Entregar informe"
            className={ESTILO_ENTRADA}
          />
        </div>

        <div>
          <Etiqueta>Fecha de vencimiento</Etiqueta>
          <input
            type="date"
            value={vencimiento}
            onChange={(evento) => setVencimiento(evento.target.value)}
            className={ESTILO_ENTRADA}
          />
        </div>

        <div>
          <Etiqueta>Prioridad</Etiqueta>
          <Segmentado
            valor={prioridad}
            opciones={["Alta", "Media", "Baja"]}
            onChange={setPrioridad}
            colores={COLORES_PRIORIDAD}
          />
        </div>

        <div>
          <Etiqueta>Etiquetas (separadas por coma)</Etiqueta>
          <input
            type="text"
            value={etiquetas}
            onChange={(evento) => setEtiquetas(evento.target.value)}
            placeholder="Ej: web, trabajo"
            className={ESTILO_ENTRADA}
          />
        </div>

        <div>
          <Etiqueta>Notas</Etiqueta>
          <textarea
            rows={3}
            value={notas}
            onChange={(evento) => setNotas(evento.target.value)}
            placeholder="Detalles adicionales..."
            className={`${ESTILO_ENTRADA} resize-none`}
          />
        </div>

        <button
          type="submit"
          disabled={enviando}
          className={`w-full rounded-lg px-3 py-2.5 text-sm font-bold text-white transition disabled:opacity-60 ${
            elementoEditando
              ? "bg-amber-500 hover:bg-amber-600"
              : "bg-blue-600 hover:bg-blue-700"
          }`}
        >
          {enviando
            ? "Guardando..."
            : elementoEditando
              ? "💾  Guardar cambios"
              : "➕  Crear"}
        </button>

        {elementoEditando && (
          <button
            type="button"
            onClick={onCancelarEdicion}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-100 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
          >
            Cancelar edición
          </button>
        )}

        {error && (
          <p className="rounded-lg bg-red-100 px-3 py-2 text-xs font-medium text-red-700 dark:bg-red-900/40 dark:text-red-300">
            {error}
          </p>
        )}
      </form>

      <button
        type="button"
        onClick={onDemo}
        className="mt-3 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-100 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
      >
        Cargar ejemplos
      </button>

      <div className="mt-auto pt-6">
        <Etiqueta>Tema</Etiqueta>
        <button
          type="button"
          onClick={onAlternarTema}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium transition hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700"
        >
          {tema === "dark" ? "☀️ Modo claro" : "🌙 Modo oscuro"}
        </button>
      </div>
    </aside>
  );
}
