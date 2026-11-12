// Cliente centralizado para consumir la API del backend Python.
const BASE = "/api";

async function pedir(ruta, opciones = {}) {
  let respuesta;
  try {
    respuesta = await fetch(`${BASE}${ruta}`, {
      headers: { "Content-Type": "application/json" },
      ...opciones,
    });
  } catch {
    throw new Error(
      "No se pudo conectar con el backend. Verifica que esté corriendo en el puerto 8000."
    );
  }

  const texto = await respuesta.text();
  let datos = null;
  if (texto) {
    try {
      datos = JSON.parse(texto);
    } catch {
      datos = texto;
    }
  }

  if (!respuesta.ok) {
    const detalle = datos?.detail;
    let mensaje = "Ocurrió un error inesperado.";
    if (typeof detalle === "string") {
      mensaje = detalle;
    } else if (Array.isArray(detalle)) {
      mensaje = detalle
        .map((error) => error.msg || error.message || "Dato inválido")
        .join(" · ");
    }
    throw new Error(mensaje);
  }

  return datos;
}

export const api = {
  listar: (orden = "codigo") => pedir(`/elementos?orden=${encodeURIComponent(orden)}`),
  obtener: (codigo) => pedir(`/elementos/${codigo}`),
  crear: (elemento) => pedir("/elementos", { method: "POST", body: JSON.stringify(elemento) }),
  actualizar: (codigo, elemento) =>
    pedir(`/elementos/${codigo}`, { method: "PUT", body: JSON.stringify(elemento) }),
  eliminar: (codigo) => pedir(`/elementos/${codigo}`, { method: "DELETE" }),
  alternar: (codigo) => pedir(`/elementos/${codigo}/completado`, { method: "PATCH" }),
  buscar: (texto) => pedir(`/buscar?texto=${encodeURIComponent(texto)}`),
  vencidas: () => pedir("/reportes/vencidas"),
  porEtiqueta: (etiqueta) => pedir(`/reportes/etiqueta/${encodeURIComponent(etiqueta)}`),
  etiquetas: () => pedir("/etiquetas"),
  estadisticas: () => pedir("/estadisticas"),
  arbol: () => pedir("/arbol"),
  demo: () => pedir("/demo", { method: "POST" }),
};
