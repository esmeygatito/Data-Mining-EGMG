# Data-Mining-EGMG

Minería de Datos aplicada a la prescripción de medicamentos GLP-1 en NHS England — prácticas del semestre y proyecto integrador (PIA).

**Autora:** Esmeralda Gabriela Mendieta González · Matrícula 2064574
**Materia:** Minería de Datos · Licenciatura en Ciencias Computacionales, FCFM, UANL

## De qué trata
Todo el repositorio trabaja con un mismo dataset: el *English Prescribing Dataset* de NHSBSA (NHS England), filtrado a seis sustancias GLP-1 (Dulaglutide, Semaglutide, Tirzepatide, Liraglutide, Exenatide y Lixisenatide), de enero de 2021 a mayo de 2026.

La pregunta que guía el proyecto:
> ¿Qué segmentos de consultorios están impulsando el crecimiento del revenue del mercado GLP-1, y cómo está cambiando la composición de ese ingreso entre sustancias a lo largo del tiempo? ¿Existe además una desigualdad geográfica en cómo se distribuye ese revenue?

## Estructura
Cada práctica tiene su propia carpeta con un `README.md` que explica objetivo, método, resultados y limitaciones.

| Carpeta | Contenido |
|---|---|
| `Práctica 1` … `Práctica 9` | Una práctica por carpeta: extracción y limpieza del dataset (Práctica 1), segmentación de consultorios con K-Means (Práctica 7), pronóstico de series de tiempo (Práctica 8), análisis de texto (Práctica 9) y las demás |
| `Respuestas adicionales` | Cálculos complementarios (geografía, concentración, Gini y Kruskal-Wallis) |
| `PIA` | Proyecto integrador: presentación, video y README con los hallazgos |

## Resultado principal
El crecimiento del revenue GLP-1 está concentrado: en un producto (Tirzepatide pasó de 0 % a 83 % del revenue), en pocos consultorios y, en menor medida, en ciertas regiones. El detalle está en la carpeta `PIA`.
