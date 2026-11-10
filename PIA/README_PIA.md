# PIA — Crecimiento del revenue GLP-1 en NHS England

## Video de la presentación
**https://youtu.be/3b3E6YgtCLA**

Presentación usada en el video: [`PIA_GLP1.pptx`](PIA_GLP1.pptx) (también en [PDF](PIA_GLP1.pdf))

---

## Pregunta ancla
> ¿Qué segmentos de consultorios están impulsando el crecimiento del revenue del mercado GLP-1, y cómo está cambiando la composición de ese ingreso entre sustancias a lo largo del tiempo? ¿Existe además una desigualdad geográfica en cómo se distribuye ese revenue?

## Hallazgo
El GLP-1 se volvió mucho más popular en NHS England y el crecimiento del revenue está **concentrado**: en un producto, en pocos consultorios y, en menor medida, en ciertas regiones.

| Parte de la pregunta | Evidencia |
|---|---|
| **Sustancia** | Tirzepatide pasó de 0 % del revenue (2021–2023) a 83 % en mayo de 2026, con solo el 64 % de las recetas: cada receta cuesta £232 contra £83 del resto (2.8×). El gasto en los demás GLP-1 bajó de £238 M (2023) a £189 M (2025). |
| **Segmentos de consultorios** | K-Means (k = 4) sobre ~6,500 consultorios: las *Cuentas clave* son el 28 % de los consultorios y aportan el 56 % del crecimiento. |
| **Geografía** | Un consultorio de South East genera en promedio 2.1× lo de uno de London (£19.2 mil contra £9.2 mil al mes, mayo 2026). El 10 % de los consultorios genera el 31 % del revenue (Gini = 0.45); Kruskal-Wallis entre regiones: ε² = 0.07, es decir, la región explica ~7 % de la variación. |
| **Hacia adelante** | Holt amortiguado: error de 3.6 % en jun–ago 2026 (línea recta 6.0 %, "igual al último mes" 9.9 %). Proyección sep 2026 – feb 2027: ≈ £539 M (rango £485–593 M con ±10 % de precio). |

## Técnicas aplicadas
- **Clustering (K-Means)** para segmentar consultorios — Práctica 7.
- **Pronóstico de series de tiempo (Holt con tendencia amortiguada)** validado contra datos que el modelo no vio — Práctica 8.
- **Pruebas estadísticas:** Gini, curva de concentración y Kruskal-Wallis con tamaño de efecto (ε²).

## Datos
- **Fuente:** NHSBSA, *English Prescribing Dataset* (API oficial).
- **Periodo:** enero 2021 – mayo 2026 (65 meses); junio–agosto 2026 solo para validar el pronóstico.
- **Alcance:** 6 sustancias GLP-1 (Dulaglutide, Semaglutide, Tirzepatide, Liraglutide, Exenatide, Lixisenatide).
- **Revenue** = `ACTUAL_COST` (libras). **Conversión a pesos** en la presentación: £1 = $24.9 MXN (9 nov 2026), solo informativa.
- **Validación externa:** el cálculo propio de 2025/26 (£570 M, 3.06 M de recetas) coincide con lo publicado por Pulse Today (£574 M, 3.1 M).

## Limitaciones
- **Datos de Inglaterra:** no representan a México ni a otros mercados.
- **Recetas, no personas:** el dataset cuenta recetas dispensadas, no pacientes; no incluye la indicación.
- **Segmentos:** silueta de 0.25 (estructura débil). Son una partición útil para el negocio, no grupos naturales; con datos exactos, el 74.7 % de los consultorios conserva su segmento.
- **Pronóstico:** serie corta (30 meses), sin estacionalidad y con precio constante (£218.1 por unidad); el precio de Tirzepatide se duplicó en septiembre de 2025.
- **Datos de sep–oct 2026** aún no estaban publicados al momento del análisis.

## Contenido de esta carpeta
- `README.md` — este archivo
- `PIA_GLP1.pptx` — presentación
- `PIA_GLP1.pdf` — misma presentación en PDF