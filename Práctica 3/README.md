# Práctica 3 — Visualización de Datos

## Objetivo
Generar al menos 5 tipos de gráficas distintas, usando ciclos o automatización en código, para explorar visualmente la pregunta ancla del proyecto sobre revenue intelligence en el mercado GLP-1.

## Dataset base
Este análisis parte de `glp1_limpio.csv`, generado en la Práctica 1. Cada notebook de práctica carga el CSV de forma independiente:
```python
df_final = pd.read_csv("../Práctica 1/glp1_limpio.csv", parse_dates=['FECHA'])
```
**Importante:** `parse_dates=['FECHA']` es indispensable — sin este parámetro, la columna se lee como texto (no como fecha), lo que rompe cualquier gráfica de series de tiempo o agrupamiento por año.

## Consistencia visual
Se definió una paleta de colores fija por sustancia, reutilizada en todas las gráficas del reporte, para que cada sustancia se identifique siempre con el mismo color:
```python
sustancias_orden = ['Semaglutide', 'Liraglutide', 'Dulaglutide', 'Exenatide', 'Lixisenatide', 'Tirzepatide']
color_sustancia = dict(zip(sustancias_orden, plt.cm.tab10.colors))
plt.style.use('seaborn-v0_8-whitegrid')
```

## Nota sobre automatización (ciclos)
El requisito pide "usando ciclos **o** automatización en código". Se usó automatización real donde generaba valor (evitando repetir código manualmente):
- **Histograma** y **líneas de tiempo**: un `for` recorre las 6 sustancias para generar cada subgráfica/línea.
- **Pasteles y barras por año**: un `for` recorre los 5 años completos para generar cada mini-gráfica de la cuadrícula.
- **Barras, caja, pastel general y dispersión**: usan una sola llamada que ya grafica todas las categorías de un jalón (matplotlib/pandas lo resuelven nativamente). Forzar un `for` aquí generaría gráficas redundantes sin aportar información nueva, en vez de automatización genuina.

---

## 1. Histograma — distribución del costo por receta, por sustancia

**Diseño:** cuadrícula 2×3, un histograma por sustancia, generado con un `for`. Se limitó el eje X al percentil 99 de `ACTUAL_COST` (~£3,060) para que el 1% de recetas más costosas no aplanara visualmente el resto — decisión declarada explícitamente en el título de la gráfica.

**Hallazgo:** las 6 sustancias muestran sesgo a la derecha (consistente con la Práctica 2), pero con formas distintas entre sí. Semaglutide, Dulaglutide y Exenatide concentran casi todas sus recetas en precios bajos. Tirzepatide es la excepción: sus recetas están repartidas en todo el rango de precios. Se confirmó numéricamente con la desviación estándar de `ACTUAL_COST` por sustancia:

| Sustancia | Desviación estándar (GBP) |
|---|---|
| Tirzepatide | 1,571.38 |
| Dulaglutide | 382.87 |
| Semaglutide | 358.49 |
| Liraglutide | 192.51 |
| Exenatide | 133.10 |
| Lixisenatide | 68.86 |

Tirzepatide no solo es la más cara en promedio (Práctica 2) — es también la más *variable* en precio, más de 4 veces la desviación estándar de la segunda sustancia (Dulaglutide).

---

## 2. Línea de tiempo — revenue mensual por sustancia (2021-2026)

**Diseño:** una sola figura con las 6 sustancias superpuestas (colores consistentes), eje Y en escala logarítmica para poder ver la tendencia de sustancias pequeñas (Exenatide, Lixisenatide) que en escala normal se veían aplastadas en cero. **Limitación declarada:** la escala logarítmica no puede representar el valor 0, por lo que la línea de Tirzepatide "aparece" en el punto donde deja de ser cero, no antes.

**Hallazgo:** se puede identificar visualmente el momento exacto de la descontinuación de Liraglutide (~agosto 2023) y Lixisenatide, coincidiendo con la evidencia externa documentada en la Práctica 1. La irrupción de Tirzepatide es visible como un despegue pronunciado a partir de 2023-2024, superando en poco tiempo a sustancias con años de trayectoria en el mercado.

---

## 3. Barras — revenue total por sustancia (con número de recetas)

**Diseño:** barras ordenadas de mayor a menor revenue, con el número de recetas (`ITEMS`) anotado sobre cada barra como texto, para poder comparar revenue y volumen en una sola imagen.

**Hallazgo:** confirma visualmente el Hallazgo 1 de la Práctica 2 — Tirzepatide genera el mayor revenue (£572M) con menos recetas (3.4M) que Semaglutide (£433M, 4.96M recetas) y Dulaglutide (£381M, 4.89M recetas).

---

## 4. Caja (boxplot) — distribución del costo por receta, por región

**Diseño:** se optó por analizar esta gráfica por **región** en vez de por sustancia (para no ser redundante con el histograma), ordenada de mayor a menor mediana. `showfliers=False` para ocultar valores atípicos extremos (declarado en el título).

**Hallazgo:** las medianas de las 7 regiones son similares (£145-185), sin destacar una como "más cara" en su receta típica. Donde sí hay diferencia real es en la variabilidad: **London es la región más compacta** (caja y bigote más cortos de las 7), mientras que **North East and Yorkshire** y **South West** toleran mucha más variedad de precios altos antes de considerarse atípicos (bigotes cercanos a £800).

**Pregunta abierta:** en la Práctica 2, London tenía el `costo_por_item` (promedio ponderado por volumen) más alto de las 7 regiones, pese a ser la más compacta en este boxplot. Como no depende de valores extremos (bigote corto), la explicación más probable es que las recetas de London se concentran consistentemente hacia la parte alta de su propio rango angosto, combinado con alto volumen en esas filas — patrón a explorar con más detalle en una práctica futura (posiblemente al segmentar consultorios en la Práctica 7).

---

## 5. Pastel — composición del revenue por sustancia

### 5a. Periodo completo (2021-2026)
**Diseño:** porcentajes y nombres movidos a una leyenda externa (en vez de texto sobre las rebanadas), para evitar amontonamiento en las sustancias pequeñas (Exenatide, Lixisenatide).

**Hallazgo:** Tirzepatide lidera con ~37.5% del revenue acumulado histórico, por encima de Semaglutide (~28.4%) y Dulaglutide (~25%) — a pesar de no haber existido hasta 2023. Liraglutide, Exenatide y Lixisenatide combinadas apenas suman ~9%.

### 5b. Por año (2021-2025) — extra, con `for`
**Diseño:** cuadrícula 2×3 (un pastel por año), con una leyenda compartida en el sexto casillero. Se excluyó 2026 de esta cuadrícula por no ser un año completo (ver 5c).

**Hallazgo:** revela la verdadera transformación del mercado, invisible en el pastel general. En 2021 el mercado se repartía entre Dulaglutide (38%), Semaglutide (32%) y Liraglutide (25%) — Tirzepatide no existía. Para 2025, Tirzepatide domina con 66% de participación; Liraglutide y Lixisenatide prácticamente desaparecen del pastel, confirmando visualmente sus descontinuaciones.

### 5c. 2026 (parcial, enero-mayo) — extra
**Diseño:** gráfica separada de la cuadrícula anterior, con nota explícita en el título de que el dato es parcial (mayo es el último mes disponible en el dataset a la fecha de extracción).

**Hallazgo:** la tendencia se acelera — Tirzepatide ya controla 80.8% del revenue en lo que va de 2026, Semaglutide baja a 12.9%. Dato preliminar, sujeto a confirmación con el resto del año.

---

## 6. Barras por año (2021-2025, y 2026 parcial) — extra, con `for`

**Diseño:** mismo criterio que el pastel por año (cuadrícula 2×3 + gráfica separada para 2026), pero mostrando montos absolutos de revenue en vez de proporciones — para distinguir crecimiento real de cambios de participación relativa.

**Hallazgo:** el liderazgo del mercado cambió de manos **dos veces** en 5 años, no de golpe: Dulaglutide lideró en revenue absoluto 2021-2023, Semaglutide tomó la delantera en 2024, y Tirzepatide domina desde 2025 dejando al resto muy por debajo. Este matiz (la transición intermedia por Semaglutide) no era visible en el pastel general ni en la línea de tiempo logarítmica.

---

## 7. Dispersión — relación entre volumen y revenue

**Diseño:** un punto por combinación año-sustancia (28 de 30 posibles; Tirzepatide no tiene datos en 2021-2022), volumen total (`TOTAL_QUANTITY`, millones de unidades) en el eje X, revenue anual (millones de GBP) en el eje Y, coloreado por sustancia con transparencia y borde para distinguir puntos cercanos.

**Hallazgo:** Semaglutide, Dulaglutide y Liraglutide siguen una relación esperada entre volumen y revenue (los puntos se alinean en una diagonal ascendente). **Tirzepatide es un outlier claro respecto a esa relación**: en 2025 genera un revenue comparable o mayor al de Semaglutide con aproximadamente 10 veces menos volumen — confirma, con una tercera gráfica distinta (además del histograma y las barras), que el valor de Tirzepatide viene del precio, no del volumen vendido.

---

## Resumen de hallazgos de la práctica
1. Tirzepatide es la sustancia más variable en precio (histograma), no solo la más cara en promedio.
2. La transición del mercado ocurrió en 2 etapas (Dulaglutide → Semaglutide → Tirzepatide), visible solo al ver montos absolutos por año.
3. London es la región más compacta en distribución de costo, lo cual profundiza (sin resolver aún) la pregunta abierta de por qué tiene el mayor costo promedio ponderado.
4. Tirzepatide rompe la relación esperada entre volumen y revenue — confirmado con 3 gráficas independientes (histograma, barras, dispersión).

## Archivos
- `practica_3.ipynb` — notebook con las 8 gráficas y su código
- Este `README.md`