# 🌳 Gestor de Tareas y Proyectos con ABB

Aplicación para gestionar tareas y proyectos usando un **Árbol Binario de Búsqueda (ABB)**.
Toda la lógica del árbol está implementada **exclusivamente en Python** (backend) y la
interfaz está construida con **React** (frontend).

Proyecto de la materia **Algoritmos II**.

---

## 📁 Estructura del proyecto

```
proyecto-Algoritmos/
├── backend/                  # Todo el codigo Python
│   ├── arbol_tareas.py       # Logica del ABB (insertar, buscar, eliminar)
│   ├── esquemas.py           # Validacion de datos con Pydantic
│   ├── servicio.py           # Arbol + persistencia en datos.json
│   ├── main.py               # API REST con FastAPI
│   ├── requirements.txt      # Dependencias del backend
│   └── tests/                # Pruebas con pytest
│       ├── test_arbol.py
│       └── test_api.py
├── frontend/                 # Interfaz en React + Vite + Tailwind
│   ├── package.json          # Dependencias del frontend
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── api.js
│       ├── estilos.js
│       ├── hooks/
│       └── components/
├── _legacy/                  # Version original en Tkinter (referencia)
├── package.json              # Dependencias del proyecto + scripts
├── pytest.ini
└── README.md
```

---

## ⚙️ Requisitos

- Python 3.10 o superior
- Node.js 18 o superior

---

## 🚀 Instalacion y ejecucion

### 1. Dependencias del backend (Python)

```bash
pip install -r backend/requirements.txt
```

### 2. Dependencias del proyecto (raiz)

```bash
npm install
```

### 3. Dependencias del frontend (React)

```bash
npm --prefix frontend install
```

### 4. Levantar la aplicacion

```bash
npm run dev
```

Esto inicia **los dos servidores a la vez**:

| Servicio | URL |
|---|---|
| Backend (API FastAPI) | http://127.0.0.1:8000 |
| Documentacion de la API | http://127.0.0.1:8000/docs |
| Frontend (React) | http://localhost:5173 |

> Tambien puedes levantarlos por separado con `npm run dev:backend` y `npm run dev:frontend`.

---

## 🧠 La estructura ABB

El árbol se ordena por el **código** de cada tarea o proyecto:

- Los códigos **menores** van a la izquierda y los **mayores** a la derecha.
- `insertar()` es recursivo y rechaza códigos repetidos.
- `buscar()` recorre el árbol comparando el código.
- `eliminar()` cubre los **3 casos** del ABB:
  1. Nodo hoja.
  2. Nodo con un solo hijo.
  3. Nodo con dos hijos (se reemplaza por el **sucesor inorden**).
- `recorrer()` devuelve los elementos en **inorden** (ordenados por código).
- La persistencia guarda en **preorden**, de modo que al reiniciar la aplicación se
  reconstruye **exactamente la misma forma del árbol** (no un árbol degenerado).
- Los reportes (vencidas y por etiqueta) se construyen con el recorrido inorden y un filtro.

En el frontend, la pestaña **🌳 Árbol** dibuja la estructura real del ABB.

---

## 🔌 Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/elementos` | Lista los elementos (query `orden=codigo\|fecha\|prioridad`) |
| `POST` | `/api/elementos` | Crea una tarea o proyecto |
| `GET` | `/api/elementos/{codigo}` | Busca por código |
| `PUT` | `/api/elementos/{codigo}` | Actualiza un elemento |
| `DELETE` | `/api/elementos/{codigo}` | Elimina un elemento |
| `PATCH` | `/api/elementos/{codigo}/completado` | Marca como completado / reabre |
| `GET` | `/api/buscar?texto=` | Busca por código, título o etiqueta |
| `GET` | `/api/reportes/vencidas` | Reporte de tareas vencidas |
| `GET` | `/api/reportes/etiqueta/{etiqueta}` | Reporte por etiqueta |
| `GET` | `/api/etiquetas` | Etiquetas existentes |
| `GET` | `/api/estadisticas` | Totales por estado, prioridad y tipo |
| `GET` | `/api/arbol` | Estructura anidada del ABB |
| `POST` | `/api/demo` | Carga los datos de ejemplo |

Los datos se guardan automáticamente en `datos.json` (raíz del proyecto).

---

## 🧪 Pruebas

```bash
npm test
```

o directamente:

```bash
python -m pytest
```

Las pruebas cubren la lógica del ABB (incluidos los 3 casos de eliminación) y los
endpoints de la API (creación, búsqueda, eliminación, reportes y persistencia).

---

## 🎨 Interfaz

La interfaz replica la versión original de Tkinter:

- Barra lateral con formulario (tipo, código, título, fecha, prioridad, etiquetas y notas).
- Buscador por código o título.
- Reportes de vencidas y por etiqueta.
- Tarjetas con franja de color según la prioridad y estado (pendiente, vencida, completada).
- Estadísticas, carga de ejemplos y tema claro/oscuro.
- Visualización del árbol ABB en SVG.
