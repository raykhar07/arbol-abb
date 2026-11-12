import { useEffect, useState } from "react";

/**
 * Hook para el tema claro/oscuro.
 * Guarda la preferencia en localStorage y aplica la clase .dark al <html>.
 */
export function useTema() {
  const [tema, setTema] = useState(() => localStorage.getItem("tema") || "dark");

  useEffect(() => {
    const raiz = document.documentElement;
    raiz.classList.toggle("dark", tema === "dark");
    localStorage.setItem("tema", tema);
  }, [tema]);

  const alternarTema = () =>
    setTema((actual) => (actual === "dark" ? "light" : "dark"));

  return { tema, alternarTema };
}
