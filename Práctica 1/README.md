# Práctica 1 — Limpieza de Datos

## Dataset
**GLP-1 Prescribing Data (Inglaterra)** — English Prescribing Dataset (EPD), NHSBSA.
Filtrado a las 6 sustancias GLP-1: Semaglutide, Liraglutide, Dulaglutide, Exenatide, Lixisenatide, Tirzepatide.

- Fuente: https://opendata.nhsbsa.net/dataset/english-prescribing-dataset-epd-with-snomed-code
- Periodo: enero 2021 - mayo 2026
- Extracción: API pública de NHSBSA (`datastore_search_sql`), con reintentos y paginación documentados en `log_extraccion.csv`

## Archivos
- `glp1_extraccion.ipynb` — notebook con extracción y limpieza completas, paso a paso
- `glp1_muestra.csv` — muestra de 10,000 filas del dataset limpio final
- `glp1_crudo.csv` y `glp1_limpio.csv` — **no incluidos en el repo** por tamaño (1.8GB y 748MB); se regeneran corriendo el notebook completo

## Decisiones de limpieza principales
- Se unificaron 6 pares de columnas renombradas por un cambio de esquema de NHS en marzo 2025 (ej. `CHEMICAL_SUBSTANCE_BNF_DESCR` → `BNF_CHEMICAL_SUBSTANCE`)
- Se eliminaron 2,597 filas sin consultorio identificable (`PRACTICE_NAME = 'UNIDENTIFIED DOCTORS'`)
- Se eliminaron 779,589 filas duplicadas (originadas por la paginación de la API en meses de alto volumen)
- Los nulos en `REGION_NAME` (2,280,653 filas) se explican por la disolución de los STPs y su reemplazo por ICBs en julio 2022; se marcaron como `"No disponible"`
- Los nulos en `POSTCODE` (2,123 filas, sin patrón temporal claro) se marcaron como `"SIN_CP"`
- Dataset final: **4,348,743 filas × 15 columnas**

## Cómo reproducir
Correr `glp1_extraccion.ipynb` de inicio a fin regenera `glp1_crudo.csv` y `glp1_limpio.csv` localmente.

## Descripción de los datos

| Columna | Tipo | Descripción |
|---|---|---|
| `PRACTICE_CODE` | texto | Código único del consultorio/GP practice que emitió la receta. Unidad de análisis ("cliente") para segmentación. |
| `PRACTICE_NAME` | texto | Nombre del consultorio. |
| `REGIONAL_OFFICE_NAME` | texto | Región geográfica amplia de NHS England (7 regiones). Cobertura completa en todo el periodo. |
| `REGION_NAME` | texto | Región administrativa de grano más fino (STP hasta jun-2022, ICB desde jul-2022). ~52% de filas marcadas `"No disponible"` por la reorganización STP→ICB. |
| `POSTCODE` | texto | Código postal del consultorio. |
| `FECHA` | fecha | Mes/año de la receta. Unificada a partir de `YEAR_MONTH`, que venía en 2 formatos distintos según el esquema (`202101` vs `'2026-05'`). |
| `SUSTANCIA` | texto | Ingrediente activo (ej. Semaglutide). Unificada de 2 columnas que intercambiaron significado con el cambio de esquema de NHS de marzo 2025. |
| `PRESENTACION` | texto | Producto comercial específico, con dosis y forma farmacéutica (ej. "Ozempic 1mg/0.74ml inj 3ml pre-filled pens"). Varias presentaciones pueden compartir la misma sustancia. |
| `QUANTITY` | numérico | Tamaño de paquete típico prescrito por presentación (pseudo pack size). |
| `ITEMS` | numérico | Número de veces que la presentación aparece en recetas, agregado por consultorio + mes. |
| `TOTAL_QUANTITY` | numérico | `QUANTITY × ITEMS` — total real de unidades (plumas, tabletas, etc.) dispensadas. |
| `NIC` | numérico | Net Ingredient Cost — costo base del medicamento, en GBP, sin ajustes por descuento nacional. |
| `ACTUAL_COST` | numérico | Costo real reembolsado, en GBP, después de ajustes por descuento nacional promedio. Variable principal de "revenue" para el análisis. |
| `ADQ_USAGE` | numérico | Average Daily Quantity — dosis diaria promedio calculada a partir de la cantidad prescrita. |
| `UNIDENTIFIED` | texto (Y/N) | Bandera de NHS que indica si la receta pudo asignarse con certeza a un consultorio conocido. |