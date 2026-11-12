const COLOR_PRIORIDAD = {
  Alta: "border-red-500",
  Media: "border-amber-500",
  Baja: "border-green-500",
};

const PILL_ESTADO = {
  Completado: "bg-gray-500",
  Vencido: "bg-red-500",
  Pendiente: "bg-blue-500",
};

export default function Tarjeta({ elemento, onAlternar, onEditar, onEliminar }) {
  const estado = elemento.completado
    ? "Completado"
    : elemento.vencido
      ? "Vencido"
      : "Pendiente";
  const icono = elemento.tipo === "Proyecto" ? "📁" : "📝";
  const notas =
    elemento.notas && elemento.notas.length > 150
      ? `${elemento.notas.slice(0, 150)}...`
      : elemento.notas;

  return (
    <article
      className={`flex gap-3 rounded-xl border-l-8 ${
        COLOR_PRIORIDAD[elemento.prioridad] || "border-gray-400"
      } bg-white p-4 shadow-sm ring-1 ring-gray-200/70 dark:bg-gray-800 dark:ring-gray-700`}
    >
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <h3
            className={`text-base font-bold ${
              elemento.completado ? "text-gray-400 line-through" : ""
            }`}
          >
            {icono} {elemento.titulo}
          </h3>
          <span className="text-sm text-gray-400">#{elemento.codigo}</span>
          <span
            className={`rounded-md px-2 py-0.5 text-xs font-semibold text-white ${PILL_ESTADO[estado]}`}
          >
            {estado}
          </span>
        </div>

        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Vence: {elemento.vencimiento} · Prioridad: {elemento.prioridad} · {elemento.tipo}
        </p>

        {elemento.etiquetas.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1.5">
            {elemento.etiquetas.map((etiqueta) => (
              <span
                key={etiqueta}
                className="rounded-md bg-gray-200 px-2 py-0.5 text-xs text-gray-700 dark:bg-gray-700 dark:text-gray-200"
              >
                {etiqueta}
              </span>
            ))}
          </div>
        )}

        {notas && (
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">{notas}</p>
        )}
      </div>

      <div className="flex shrink-0 flex-col justify-center gap-2">
        <button
          type="button"
          onClick={() => onEditar(elemento)}
          className="rounded-lg bg-amber-500 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-amber-600"
        >
          ✏️ Editar
        </button>
        <button
          type="button"
          onClick={() => onAlternar(elemento.codigo)}
          className="rounded-lg bg-green-500 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-green-600"
        >
          {elemento.completado ? "↩ Reabrir" : "✔ Completar"}
        </button>
        <button
          type="button"
          onClick={() => onEliminar(elemento)}
          className="rounded-lg bg-red-500 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-red-600"
        >
          🗑 Eliminar
        </button>
      </div>
    </article>
  );
}
