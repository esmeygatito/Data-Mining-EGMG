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
- Dataset final: 4,348,743 filas × 15 columnas

## Cómo reproducir
Correr `glp1_extraccion.ipynb` de inicio a fin regenera `glp1_crudo.csv` y `glp1_limpio.csv` localmente.