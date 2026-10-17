# Práctica 7 — Agrupamiento de Datos (K-Means)

## Objetivo
Crear y evaluar un modelo de agrupamiento con K-Means para segmentar a los consultorios (GP practices) según su tamaño, ritmo de crecimiento y mezcla de producto, y con eso responder la parte de la pregunta ancla que quedaba pendiente: **¿qué segmentos de consultorios están impulsando el crecimiento del revenue GLP-1?** Además se cruzan los segmentos con la región para retomar la parte geográfica de la pregunta.

## Dataset base
Este análisis parte de `glp1_limpio.csv`, generado en la Práctica 1.
```python
df_final = pd.read_csv("../Práctica 1/glp1_limpio.csv", parse_dates=['FECHA'])
```

## Marco de interpretación
- **K-Means** agrupa consultorios parecidos entre sí midiendo distancias. Es un método **no supervisado**: no hay una etiqueta "correcta" que predecir (a diferencia de la Práctica 6), por eso no se separa en train/test: el objetivo es describir y segmentar los consultorios que ya existen.
- Como mide distancias, las variables se **escalan** (`StandardScaler`) para que ninguna domine por sus unidades (miles de libras vs. porcentajes).
- **Método del codo (inercia):** la inercia siempre baja al subir k; se busca el punto donde dejar de subir k ya casi no mejora.
- **Coeficiente de silueta:** mide qué tan cerca está cada consultorio de su propio grupo frente al grupo vecino más cercano (-1 a 1). Arriba de ~0.5 indica estructura clara; entre 0.25 y 0.5, débil; abajo de 0.25, casi nula.

---

## 1. Preparación de los datos

### Unidad de análisis
Un renglón por consultorio (`PRACTICE_CODE`), comparando dos periodos: **2021-2022** y **2024-2025**. Se conservaron solo los consultorios con actividad en **ambos** periodos (para no confundir "consultorio nuevo" con "consultorio que crece"): **6,642 consultorios**.

### Variables usadas en el clustering (4)

| Variable | Qué mide | Por qué se incluyó |
|---|---|---|
| `rev_2024_2025` | Revenue (`ACTUAL_COST`) del consultorio en 2024-2025 | Qué tan grande es hoy |
| `crecimiento_pct` | % de cambio de revenue entre 2021-2022 y 2024-2025 | Qué tan rápido crece |
| `pct_tirzepatide` | % de su revenue 2024-2025 que es Tirzepatide | Composición del ingreso por sustancia |
| `costo_promedio_receta` | `revenue_total / items_total` | Qué tan caro es lo que receta |

### Variables descartadas
- `meses_activo`: más del 75% de los consultorios vale 65 (activos todos los meses), así que casi no separa grupos.
- `items_total` (correlación 0.978 con revenue, ver Práctica 6) y `sustancias_distintas`: redundantes con las variables elegidas.

### Revisión de multicolinealidad
La correlación más alta entre las 4 variables es **0.35** (`pct_tirzepatide` con `costo_promedio_receta`, consistente con que Tirzepatide es la sustancia más cara). No hay pares de variables repitiendo la misma información, a diferencia de la Práctica 6 (0.785).

### Tratamiento de valores extremos
Con K-Means los puntos muy lejanos pesan de más (la distancia se eleva al cuadrado) y pueden deformar un grupo o quedarse solos en uno. Por ejemplo, el máximo de `crecimiento_pct` era 98,433% frente a un percentil 99 de 818% (consultorios con una base mínima en 2021-2022).

**Regla aplicada:** se excluyeron del ajuste los consultorios por encima del **percentil 99** en cualquiera de estas 3 variables:

| Variable | Corte (percentil 99) |
|---|---|
| `rev_2024_2025` | £442,262 |
| `crecimiento_pct` | 817.6% |
| `costo_promedio_receta` | £171.9 |

`pct_tirzepatide` **no se recortó**: es una variable acotada entre 0% y 100%, sin valores absurdos posibles; un consultorio con 95% de Tirzepatide es un caso real, no un extremo.

**Resultado:** 187 consultorios excluidos (2.8%), que concentran el **6.7% del revenue** 2024-2025 y el **8.2% del crecimiento total**. Quedan **6,455 consultorios** para el modelo. Los excluidos no se descartan del análisis: al asignarlos con el modelo ya entrenado caen **88 en Emergentes, 65 en Cuentas clave y 34 en En expansión** (ninguno en Estables), es decir, son sobre todo consultorios de perfil de crecimiento fuerte o muy grandes. Por eso los porcentajes de crecimiento por segmento de este documento se calculan sobre los 6,455 y subestiman un poco el peso de esos tipos de consultorio.

---

## 2. Elección de k (evaluación del modelo)

Se corrió K-Means con k = 2 a 8 (`random_state=42`, `n_init=10`, que repite el modelo con 10 arranques distintos y se queda con el mejor para que el resultado no dependa de un mal arranque).

| k | Inercia | Silueta |
|---|---|---|
| 2 | 18,961 | 0.254 |
| 3 | 15,655 | 0.264 |
| 4 | 13,148 | 0.254 |
| 5 | 11,332 | 0.235 |
| 6 | 10,427 | 0.204 |
| 7 | 9,659 | 0.210 |
| 8 | 8,991 | 0.200 |

*(Gráfica: dos paneles, método del codo y coeficiente de silueta.)*

- **Codo:** las caídas de inercia son ~3,300 (2→3), ~2,500 (3→4), ~1,800 (4→5) y ya solo ~900 (5→6): la curva se aplana después de k=5, sin una esquina marcada.
- **Silueta:** el máximo es k=3 (0.264), pero k=2, 3 y 4 casi empatan. En k=6 es de las más bajas.
- **Lectura honesta:** todas las siluetas están en la franja baja (~0.2-0.26). Los consultorios forman un continuo, no grupos naturales bien separados. Los segmentos son una **partición útil para el negocio**, no "tipos de consultorio" que existan por sí solos en los datos.

### Decisión: k = 4 como modelo principal
1. Su silueta (0.254) está prácticamente empatada con el máximo (0.264).
2. Da el nivel de detalle justo para accionar (con k=3 se pierde matiz; con k=5 el grupo extra no cambia la historia, ver sección 5).
3. Produce 4 segmentos con perfiles distintos y accionables.

Variación probada: **k = 5** (el k que marca el codo). Ver sección 5.

---

## 3. Los 4 segmentos (k = 4)

### Perfil de cada segmento

| Segmento | Consultorios | Revenue medio 2024-25 | Crecimiento mediano | % Tirzepatide (medio) | Costo por receta (medio) |
|---|---|---|---|---|---|
| **Cuentas clave** | 1,182 (18.3%) | £222,897 | 94.1% | 57.7% | £105.3 |
| **En expansión** | 2,369 (36.7%) | £67,868 | 80.2% | 57.6% | £116.9 |
| **Emergentes** | 466 (7.2%) | £81,816 | 321.0% | 61.6% | £119.5 |
| **Estables de bajo crecimiento** | 2,438 (37.8%) | £61,762 | 36.4% | 30.7% | £93.0 |

*(Gráfica: mapa de calor del perfil de cada segmento, en desviaciones estándar respecto al consultorio promedio. Abajo, los valores.)*

| Segmento | Revenue | Crecimiento % | % Tirzepatide | Costo por receta |
|---|---|---|---|---|
| Cuentas clave | **+1.63** | +0.12 | +0.50 | -0.03 |
| En expansión | -0.35 | -0.07 | +0.49 | +0.59 |
| Emergentes | -0.17 | **+2.58** | +0.69 | +0.72 |
| Estables de bajo crecimiento | -0.42 | -0.49 | **-0.85** | -0.69 |

**Cómo se leen:**
- **Cuentas clave:** los distingue el **tamaño** (+1.63); en lo demás están cerca del promedio.
- **Emergentes:** los distingue el **crecimiento** (+2.58), también con el Tirzepatide y el costo por receta más altos.
- **Estables de bajo crecimiento:** están por debajo del promedio en las 4 variables, sobre todo en Tirzepatide (-0.85).
- **En expansión:** tamaño ligeramente menor al promedio y crecimiento cercano al promedio (-0.07); lo que los define es su **costo por receta alto** (+0.59) y su mayor peso de Tirzepatide. *Aclaración sobre el nombre:* se conservó "En expansión" por claridad de negocio, pero este segmento crece a un ritmo cercano al promedio; no es el que más crece.

### Visualización de los segmentos
*(Gráfica: mapa 2D por PCA, un panel por segmento con ese grupo resaltado y los demás en gris.)* El PCA comprime las 4 variables en 2 ejes artificiales (sin unidades) que conservan el 68% de la variación (44% + 24%). Lo único que importa es la cercanía: puntos cercanos son consultorios parecidos. Cada segmento ocupa una zona distinta del mapa, pero con bordes traslapados, coherente con la silueta baja.

---

## 4. ¿Quién impulsa el crecimiento? (respuesta a la pregunta ancla)

Crecimiento en libras = `rev_2024_2025 - rev_2021_2022`, sumado por segmento.

| Segmento | % de consultorios | % del crecimiento total | Aporte vs. peso | Crecimiento por consultorio | Revenue medio 2021-22 (aprox.) |
|---|---|---|---|---|---|
| Cuentas clave | 18.3% | **48.1%** | **2.63** | £104,964 | £117,933 |
| En expansión | 36.7% | 26.3% | 0.72 | £28,648 | £39,220 |
| Emergentes | 7.2% | 11.3% | 1.57 | £62,606 | £19,210 |
| Estables de bajo crecimiento | 37.8% | 14.3% | 0.38 | £15,142 | £46,620 |

*(Gráfica: barras agrupadas, % de consultorios vs. % del crecimiento por segmento.)*

*"Aporte vs. peso" = % del crecimiento ÷ % de consultorios. Mayor a 1: aporta más de lo que pesa; menor a 1: aporta menos.*

**Hallazgos:**
- **Las Cuentas clave son el motor:** 18% de los consultorios generan casi la mitad (48%) del crecimiento.
- **Los Emergentes crecen rapidísimo en porcentaje pero pesan poco en el total:** pasaron en promedio de ~£19k a ~£82k por consultorio (×4.3), pero son solo 466 consultorios. Su porcentaje es altísimo porque partían de una base muy pequeña; las Cuentas clave se multiplicaron ×1.9 pero desde una base mucho mayor.
- **Estables de bajo crecimiento** y **En expansión** pesan mucho en cantidad (74.5% de los consultorios) y aportan menos de lo que pesan.
- **Tirzepatide y el crecimiento:** Tirzepatide no existía en 2021-2022, por lo que todo el revenue actual de esa sustancia es crecimiento nuevo. Una cuenta aproximada (porcentaje medio de Tirzepatide por revenue medio) sugiere que explica gran parte del crecimiento en todos los segmentos. Lo que **no** explica es por qué los Emergentes crecen más en porcentaje que los demás: eso se debe a su base pequeña.

### Nombres y acciones sugeridas
Acciones pensadas como si los consultorios fueran clientes de un programa comercial:

| Segmento | Idea de negocio |
|---|---|
| Cuentas clave | Proteger y dar atención prioritaria |
| En expansión | Acompañar su desarrollo; su rasgo es el ticket alto, no el ritmo de crecimiento |
| Emergentes | Vigilar: pueden convertirse en la siguiente Cuenta clave |
| Estables de bajo crecimiento | Evaluar si hay oportunidad de activarlos (hoy adoptan poco Tirzepatide) |

---

## 5. Variación: k = 5

| Grupo (k=5) | Consultorios | Revenue medio | Crec. mediano | % Tirzepatide | Costo por receta | % del crecimiento |
|---|---|---|---|---|---|---|
| 0 | 1,759 (27.3%) | £57,638 | 30.9% | 24.6% | £92.4 | 8.4% |
| 1 | 1,180 (18.3%) | £73,610 | 85.0% | 53.0% | £132.0 | 15.0% |
| 2 | 2,152 (33.3%) | £76,853 | 67.9% | 56.7% | £100.3 | 24.4% |
| 3 | 441 (6.8%) | £80,637 | 328.7% | 62.1% | £118.2 | 10.6% |
| 4 | 923 (14.3%) | £242,420 | 99.1% | 57.6% | £105.8 | 41.6% |

Cómo se reparten los segmentos del k=4 dentro del k=5:

| k=4 \ k=5 | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| Estables (k4-0) | 1,759 | 19 | 659 | 1 | 0 |
| Cuentas clave (k4-1) | 0 | 40 | 220 | 2 | 920 |
| En expansión (k4-2) | 0 | 1,094 | 1,264 | 9 | 2 |
| Emergentes (k4-3) | 0 | 27 | 9 | 429 | 1 |

**Hallazgos de la variación:**
- **Cuentas clave y Emergentes son estables:** 920 de 1,182 Cuentas clave forman juntos el grupo 4, y 429 de 466 Emergentes forman el grupo 3. Los dos segmentos más importantes para la pregunta ancla casi no cambian.
- **Lo que se parte es el medio:** "En expansión" se divide en dos grupos casi iguales que se distinguen por el **costo por receta** (£132 vs. £100), no por su aporte al crecimiento (15.0% y 24.4%). "Estables" se divide en un grupo con muy poco Tirzepatide (25%) y otro intermedio.
- **Conclusión:** el quinto grupo agrega un matiz de precio pero no cambia quién impulsa el crecimiento, y su silueta es menor (0.235 vs. 0.254). Se conserva k=4 por simplicidad y claridad de negocio.

---

## 6. Cruce con región (parte geográfica de la pregunta ancla)

Porcentaje de los consultorios de cada región que pertenece a cada segmento (cada fila suma 100%):

| Región | Cuentas clave | En expansión | Emergentes | Estables de bajo crecimiento |
|---|---|---|---|---|
| EAST OF ENGLAND | 23.1 | 28.8 | 5.9 | 42.1 |
| LONDON | **6.8** | **53.9** | 9.7 | 29.6 |
| MIDLANDS | 20.0 | 36.6 | 5.7 | 37.7 |
| NORTH EAST AND YORKSHIRE | 18.0 | 29.0 | 9.7 | 43.2 |
| NORTH WEST | 15.7 | 27.6 | 5.1 | **51.5** |
| SOUTH EAST | **28.8** | 38.9 | 6.6 | **25.7** |
| SOUTH WEST | 22.5 | 37.7 | 7.6 | 32.2 |
| **Reparto general** | 18.3 | 36.7 | 7.2 | 37.8 |

**Hallazgos:**
- **London** tiene muy pocas Cuentas clave (6.8% vs. 18.3% general) y una concentración alta de "En expansión" (53.9% vs. 36.7%), el segmento de ticket alto. Esto es coherente con lo visto en las Prácticas 2 y 3 (London: el costo por receta más alto y el volumen más bajo): su perfil se explica por **precio por receta**, no por tamaño de los consultorios ni por mezcla de Tirzepatide (en la Práctica 2 su % de Tirzepatide era de los más bajos). Es un patrón consistente, no una prueba de causa.
- **North West** concentra más Estables de bajo crecimiento (51.5%), y **South East** más Cuentas clave (28.8%) y menos Estables (25.7%). En la Práctica 2, North West tenía el menor % de Tirzepatide entre las regiones (19.63%) y South East el mayor (25.74%).
- **Salvedad:** `pct_tirzepatide` es una de las variables con las que se construyeron los segmentos, así que esta coincidencia es una verificación de consistencia, no una evidencia independiente. La región en sí no se usó para agrupar. Además, el cruce es descriptivo: no se hizo una prueba estadística de independencia.

---

## Limitaciones
- **Estructura débil:** con silueta de ~0.25, los segmentos son una forma útil de ordenar los consultorios, no grupos naturales.
- **El crecimiento mezcla desempeño con momento de adopción:** Tirzepatide arrancó en 2023; un consultorio que "crece mucho" puede ser simplemente uno que la adoptó pronto.
- **Extremos:** se excluyó el 2.8% de los consultorios del ajuste (6.7% del revenue, 8.2% del crecimiento); los porcentajes por segmento se calculan sobre el resto.

