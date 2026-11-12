// Visualizacion del ABB con SVG nativo (sin librerias externas).
const COLOR_PRIORIDAD = {
  Alta: "#ef4444",
  Media: "#f59e0b",
  Baja: "#22c55e",
};

function aplanar(nodo, profundidad = 0, acumulado = []) {
  if (!nodo) return acumulado;
  aplanar(nodo.izquierdo, profundidad + 1, acumulado);
  acumulado.push({ nodo, profundidad });
  aplanar(nodo.derecho, profundidad + 1, acumulado);
  return acumulado;
}

export default function ArbolSVG({ estructura }) {
  if (!estructura) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-2 rounded-xl bg-white text-gray-500 ring-1 ring-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:ring-gray-700">
        <p className="text-3xl">🌳</p>
        <p>El árbol está vacío. Crea un elemento para verlo.</p>
      </div>
    );
  }

  const nodos = aplanar(estructura);
  const maximaProfundidad = Math.max(...nodos.map((nodo) => nodo.profundidad));
  const separacion = 82;
  const altoNivel = 96;
  const ancho = Math.max(nodos.length * separacion + 90, 440);
  const alto = (maximaProfundidad + 1) * altoNivel + 80;

  const posiciones = new Map();
  nodos.forEach(({ nodo, profundidad }, indice) => {
    posiciones.set(nodo.codigo, {
      x: 55 + indice * separacion,
      y: 55 + profundidad * altoNivel,
    });
  });

  const aristas = [];
  function recorrer(nodo) {
    if (!nodo) return;
    const origen = posiciones.get(nodo.codigo);
    for (const hijo of [nodo.izquierdo, nodo.derecho]) {
      if (!hijo) continue;
      const destino = posiciones.get(hijo.codigo);
      aristas.push({
        id: `${nodo.codigo}-${hijo.codigo}`,
        x1: origen.x,
        y1: origen.y,
        x2: destino.x,
        y2: destino.y,
      });
      recorrer(hijo);
    }
  }
  recorrer(estructura);

  return (
    <div className="flex-1 overflow-auto rounded-xl bg-white p-2 ring-1 ring-gray-200 dark:bg-gray-800 dark:ring-gray-700">
      <svg
        viewBox={`0 0 ${ancho} ${alto}`}
        className="mx-auto"
        style={{ minWidth: ancho, minHeight: alto }}
      >
        {aristas.map((arista) => (
          <line
            key={arista.id}
            x1={arista.x1}
            y1={arista.y1}
            x2={arista.x2}
            y2={arista.y2}
            stroke="#9ca3af"
            strokeWidth="2"
          />
        ))}

        {nodos.map(({ nodo }) => {
          const { x, y } = posiciones.get(nodo.codigo);
          const titulo =
            nodo.titulo.length > 12 ? `${nodo.titulo.slice(0, 12)}…` : nodo.titulo;
          return (
            <g key={nodo.codigo}>
              <circle
                cx={x}
                cy={y}
                r="23"
                fill={COLOR_PRIORIDAD[nodo.prioridad] || "#3b82f6"}
                stroke="#ffffff"
                strokeWidth="3"
              >
                <title>
                  #{nodo.codigo} · {nodo.titulo} ({nodo.tipo})
                </title>
              </circle>
              <text
                x={x}
                y={y + 5}
                textAnchor="middle"
                fontSize="13"
                fontWeight="700"
                fill="#ffffff"
              >
                {nodo.codigo}
              </text>
              <text
                x={x}
                y={y + 43}
                textAnchor="middle"
                fontSize="10"
                fill="#6b7280"
              >
                {titulo}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
