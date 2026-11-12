from tkinter import messagebox
from datetime import date, datetime
from arbol_tareas import Arbol, Elemento
import customtkinter as ctk

# .................... Apariencia general ....................
ctk.set_appearance_mode("dark")          # "dark", "light" o "system"
ctk.set_default_color_theme("blue")      # "blue", "green" o "dark-blue"

COLORES_PRIORIDAD = {"Alta": "#ef4444", "Media": "#f59e0b", "Baja": "#22c55e"}
COLOR_PILL = ("#e5e7eb", "#374151")      # (modo claro, modo oscuro)


class AplicacionTareas(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Tareas y Proyectos")
        self.geometry("1200x740")
        self.minsize(1000, 600)
        self.arbol = Arbol()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.construir_barra_lateral()
        self.construir_panel_principal()
        self.refrescar()

    # ....................................................
    # Barra lateral: formulario
    # ....................................................
    def construir_barra_lateral(self):
        lateral = ctk.CTkScrollableFrame(self, width=280, corner_radius=0)
        lateral.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(lateral, text="📋 Gestor ABB",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(padx=15, pady=(15, 5), anchor="w")
        ctk.CTkLabel(lateral, text="Nueva tarea o proyecto", text_color="gray",
                     anchor="w").pack(fill="x", padx=15)

        self.etiqueta_campo(lateral, "Tipo")
        self.seg_tipo = ctk.CTkSegmentedButton(lateral, values=["Tarea", "Proyecto"])
        self.seg_tipo.set("Tarea")
        self.seg_tipo.pack(fill="x", padx=15, pady=(2, 0))

        self.etiqueta_campo(lateral, "Código")
        self.entrada_codigo = ctk.CTkEntry(lateral, placeholder_text="Ej: 12")
        self.entrada_codigo.pack(fill="x", padx=15, pady=(2, 0))

        self.etiqueta_campo(lateral, "Título")
        self.entrada_titulo = ctk.CTkEntry(lateral, placeholder_text="Ej: Entregar informe")
        self.entrada_titulo.pack(fill="x", padx=15, pady=(2, 0))

        self.etiqueta_campo(lateral, "Fecha de vencimiento")
        self.entrada_fecha = ctk.CTkEntry(lateral, placeholder_text="AAAA-MM-DD")
        self.entrada_fecha.pack(fill="x", padx=15, pady=(2, 0))

        self.etiqueta_campo(lateral, "Prioridad")
        self.seg_prioridad = ctk.CTkSegmentedButton(lateral, values=["Alta", "Media", "Baja"])
        self.seg_prioridad.set("Media")
        self.seg_prioridad.pack(fill="x", padx=15, pady=(2, 0))

        self.etiqueta_campo(lateral, "Etiquetas (separadas por coma)")
        self.entrada_etiquetas = ctk.CTkEntry(lateral, placeholder_text="Ej: web, trabajo")
        self.entrada_etiquetas.pack(fill="x", padx=15, pady=(2, 0))

        self.etiqueta_campo(lateral, "Notas")
        self.texto_notas = ctk.CTkTextbox(lateral, height=90, border_width=2)
        self.texto_notas.pack(fill="x", padx=15, pady=(2, 0))

        ctk.CTkButton(lateral, text="➕  Crear", height=40,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self.crear).pack(fill="x", padx=15, pady=(18, 6))
        ctk.CTkButton(lateral, text="Cargar ejemplos", height=32, fg_color="transparent",
                      border_width=2, text_color=("gray10", "gray90"),
                      command=self.cargar_ejemplos).pack(fill="x", padx=15, pady=4)

        self.etiqueta_campo(lateral, "Tema")
        ctk.CTkOptionMenu(lateral, values=["Dark", "Light", "System"],
                          command=ctk.set_appearance_mode).pack(fill="x", padx=15, pady=(2, 15))

    def etiqueta_campo(self, padre, texto):
        ctk.CTkLabel(padre, text=texto, anchor="w", text_color="gray").pack(
            fill="x", padx=15, pady=(10, 0))

    # ....................................................
    # Panel principal: busqueda, reportes y tarjetas
    # ....................................................
    def construir_panel_principal(self):
        principal = ctk.CTkFrame(self, fg_color="transparent")
        principal.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        principal.grid_columnconfigure(0, weight=1)
        principal.grid_rowconfigure(3, weight=1)

        # Fila 0: busqueda
        fila_busqueda = ctk.CTkFrame(principal, fg_color="transparent")
        fila_busqueda.grid(row=0, column=0, sticky="ew")
        self.entrada_buscar = ctk.CTkEntry(fila_busqueda, width=320, height=36,
                                           placeholder_text="🔍  Buscar por código o por título...")
        self.entrada_buscar.pack(side="left")
        self.entrada_buscar.bind("<Return>", lambda evento: self.buscar())
        ctk.CTkButton(fila_busqueda, text="Buscar", width=90, height=36,
                      command=self.buscar).pack(side="left", padx=8)
        ctk.CTkButton(fila_busqueda, text="Ver todo", width=90, height=36,
                      fg_color="transparent", border_width=2,
                      text_color=("gray10", "gray90"),
                      command=self.refrescar).pack(side="left")

        # Fila 1: reportes
        fila_reportes = ctk.CTkFrame(principal, fg_color="transparent")
        fila_reportes.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        ctk.CTkButton(fila_reportes, text="⚠  Tareas vencidas", height=36,
                      fg_color="#ef4444", hover_color="#dc2626",
                      command=self.reporte_vencidas).pack(side="left")
        self.combo_etiquetas = ctk.CTkComboBox(fila_reportes, width=170, height=36, values=[])
        self.combo_etiquetas.set("")
        self.combo_etiquetas.pack(side="left", padx=(20, 8))
        ctk.CTkButton(fila_reportes, text="🏷  Reporte por etiqueta", height=36,
                      command=self.reporte_etiqueta).pack(side="left")

        # Fila 2: titulo de la vista y estadisticas
        fila_titulo = ctk.CTkFrame(principal, fg_color="transparent")
        fila_titulo.grid(row=2, column=0, sticky="ew", pady=(18, 4))
        self.etiqueta_vista = ctk.CTkLabel(fila_titulo, text="",
                                           font=ctk.CTkFont(size=18, weight="bold"))
        self.etiqueta_vista.pack(side="left")
        self.etiqueta_stats = ctk.CTkLabel(fila_titulo, text="", text_color="gray")
        self.etiqueta_stats.pack(side="right")

        # Fila 3: lista de tarjetas con scroll
        self.lista = ctk.CTkScrollableFrame(principal, fg_color="transparent")
        self.lista.grid(row=3, column=0, sticky="nsew")

    # ....................................................
    # Tarjeta de cada tarea / proyecto
    # ....................................................
    def crear_tarjeta(self, e):
        if e.completado:
            estado, color_estado = "Completado", "#6b7280"
        elif e.esta_vencido():
            estado, color_estado = "Vencido", "#ef4444"
        else:
            estado, color_estado = "Pendiente", "#3b82f6"

        tarjeta = ctk.CTkFrame(self.lista, corner_radius=12)
        tarjeta.pack(fill="x", padx=4, pady=6)
        tarjeta.grid_columnconfigure(1, weight=1)

        # Franja de color segun la prioridad
        ctk.CTkFrame(tarjeta, width=8, corner_radius=8,
                     fg_color=COLORES_PRIORIDAD[e.prioridad]).grid(
            row=0, column=0, rowspan=3, sticky="ns", padx=(8, 0), pady=10)

        # Titulo y código
        cabecera = ctk.CTkFrame(tarjeta, fg_color="transparent")
        cabecera.grid(row=0, column=1, sticky="ew", padx=12, pady=(10, 0))
        icono = "📁" if e.tipo == "Proyecto" else "📝"
        ctk.CTkLabel(cabecera, text=f"{icono}  {e.titulo}",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="gray" if e.completado else ("gray10", "gray95")).pack(side="left")
        ctk.CTkLabel(cabecera, text=f"#{e.codigo}", text_color="gray").pack(side="left", padx=8)

        # Fecha, prioridad y estado
        info = ctk.CTkFrame(tarjeta, fg_color="transparent")
        info.grid(row=1, column=1, sticky="ew", padx=12, pady=(2, 0))
        ctk.CTkLabel(info, text=f"Vence: {e.vencimiento.strftime('%Y-%m-%d')}   •   "
                                f"Prioridad: {e.prioridad}", text_color="gray").pack(side="left")
        ctk.CTkLabel(info, text=f" {estado} ", fg_color=color_estado, text_color="white",
                     corner_radius=6).pack(side="left", padx=10)

        # Etiquetas y notas
        pie = ctk.CTkFrame(tarjeta, fg_color="transparent")
        pie.grid(row=2, column=1, sticky="ew", padx=12, pady=(4, 10))
        fila_etiquetas = ctk.CTkFrame(pie, fg_color="transparent")
        fila_etiquetas.pack(fill="x")
        for etiqueta in e.etiquetas:
            ctk.CTkLabel(fila_etiquetas, text=f" {etiqueta} ", fg_color=COLOR_PILL,
                         corner_radius=8).pack(side="left", padx=(0, 6))
        if e.notas:
            notas = e.notas if len(e.notas) <= 150 else e.notas[:150] + "..."
            ctk.CTkLabel(pie, text=notas, text_color="gray", anchor="w", justify="left",
                         wraplength=520).pack(fill="x", pady=(6, 0))

        # Botones de accion
        botones = ctk.CTkFrame(tarjeta, fg_color="transparent")
        botones.grid(row=0, column=2, rowspan=3, padx=12, pady=10)
        texto_boton = "↩ Reabrir" if e.completado else "✔ Completar"
        ctk.CTkButton(botones, text=texto_boton, width=110, height=30,
                      fg_color="#22c55e", hover_color="#16a34a",
                      command=lambda c=e.codigo: self.alternar_completado(c)).pack(pady=3)
        ctk.CTkButton(botones, text="🗑 Eliminar", width=110, height=30,
                      fg_color="#ef4444", hover_color="#dc2626",
                      command=lambda c=e.codigo: self.eliminar(c)).pack(pady=3)

    # ....................................................
    # Acciones
    # ....................................................
    def crear(self):
        try:
            codigo = int(self.entrada_codigo.get())
        except ValueError:
            messagebox.showerror("Error", "El código debe ser un número entero.")
            return

        titulo = self.entrada_titulo.get().strip()
        if titulo == "":
            messagebox.showerror("Error", "El título no puede estar vacío.")
            return

        try:
            vencimiento = datetime.strptime(self.entrada_fecha.get().strip(), "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Error", "La fecha debe tener el formato AAAA-MM-DD (ej: 2026-12-15).")
            return

        etiquetas = [t.strip() for t in self.entrada_etiquetas.get().split(",") if t.strip()]
        notas = self.texto_notas.get("1.0", "end").strip()

        elemento = Elemento(codigo, self.seg_tipo.get(), titulo, vencimiento,
                            self.seg_prioridad.get(), etiquetas, notas)

        if not self.arbol.insertar(elemento):
            messagebox.showwarning("Código repetido", f"Ya existe un elemento con el código {codigo}.")
            return

        self.limpiar_formulario()
        self.refrescar()

    def limpiar_formulario(self):
        self.entrada_codigo.delete(0, "end")
        self.entrada_titulo.delete(0, "end")
        self.entrada_fecha.delete(0, "end")
        self.entrada_etiquetas.delete(0, "end")
        self.texto_notas.delete("1.0", "end")
        self.seg_tipo.set("Tarea")
        self.seg_prioridad.set("Media")

    def eliminar(self, codigo):
        elemento = self.arbol.buscar(codigo)
        if elemento and messagebox.askyesno("Confirmar", f"¿Eliminar '{elemento.titulo}'?"):
            self.arbol.eliminar(codigo)
            self.refrescar()

    def alternar_completado(self, codigo):
        elemento = self.arbol.buscar(codigo)
        if elemento:
            elemento.completado = not elemento.completado
            self.refrescar()

    def buscar(self):
        texto = self.entrada_buscar.get().strip()
        if texto == "":
            self.refrescar()
            return

        if texto.isdigit():
            # Busqueda por codigo con la busqueda recursiva del ABB
            elemento = self.arbol.buscar(int(texto))
            resultados = [elemento] if elemento else []
        else:
            # Busqueda por texto en el titulo
            resultados = self.arbol.recorrer(lambda e: texto.lower() in e.titulo.lower())

        self.refrescar(resultados, f"Resultados: '{texto}'")

    def reporte_vencidas(self):
        self.refrescar(self.arbol.reporte_vencidas(), "Reporte: tareas vencidas")

    def reporte_etiqueta(self):
        etiqueta = self.combo_etiquetas.get().strip()
        if etiqueta == "":
            messagebox.showinfo("Aviso", "Escribe o elige una etiqueta.")
            return
        self.refrescar(self.arbol.reporte_por_etiqueta(etiqueta), f"Reporte: etiqueta '{etiqueta}'")

    def cargar_ejemplos(self):
        ejemplos = [
            Elemento(8, "Proyecto", "Lanzar sitio web", date(2026, 12, 15), "Alta",
                     ["web", "trabajo"], "Coordinar diseño y desarrollo."),
            Elemento(3, "Tarea", "Entregar informe", date(2026, 10, 1), "Alta",
                     ["universidad"], "Revisar formato IEEE."),
            Elemento(10, "Tarea", "Comprar útiles", date(2026, 11, 20), "Baja",
                     ["personal"], ""),
            Elemento(1, "Tarea", "Estudiar para examen", date(2026, 10, 20), "Media",
                     ["universidad", "estudio"], "Repasar árboles ABB."),
            Elemento(6, "Proyecto", "Proyecto final de grupo", date(2026, 12, 1), "Alta",
                     ["universidad", "trabajo"], "Gestor de tareas con ABB."),
        ]
        for e in ejemplos:
            self.arbol.insertar(e)   # Los repetidos se ignoran
        self.refrescar()

    # ....................................................
    # Mostrar datos en pantalla
    # ....................................................
    def refrescar(self, elementos=None, titulo="Todos los elementos"):
        todos = self.arbol.recorrer()
        if elementos is None:
            elementos = todos

        for widget in self.lista.winfo_children():
            widget.destroy()

        if not elementos:
            ctk.CTkLabel(self.lista, text="No hay elementos para mostrar.",
                         text_color="gray", font=ctk.CTkFont(size=14)).pack(pady=40)
        for e in elementos:
            self.crear_tarjeta(e)

        vencidas = len(self.arbol.reporte_vencidas())
        self.etiqueta_vista.configure(text=f"{titulo} ({len(elementos)})")
        self.etiqueta_stats.configure(text=f"Total: {len(todos)}   |   Vencidas: {vencidas}")
        self.combo_etiquetas.configure(values=self.arbol.etiquetas_existentes())


# ....................................................
# PROGRAMA PRINCIPAL
# ....................................................
if __name__ == "__main__":
    app = AplicacionTareas()
    app.mainloop()