# Práctica 4 — Pruebas Estadísticas

## Objetivo
Comprobar, con rigor estadístico (no solo visual), diferencias entre grupos identificados en prácticas anteriores — profundizando la parte geográfica y de composición de mercado de la pregunta ancla del proyecto.


## Justificación de la familia de pruebas
El profesor pide ANOVA + Prueba t **o** Kruskal-Wallis. Se optó por la familia no paramétrica (**Kruskal-Wallis** para 3+ grupos, **Mann-Whitney U** para 2 grupos) en lugar de ANOVA/prueba t, porque estas últimas asumen que los datos numéricos siguen una distribución normal — y ya se demostró en la Práctica 2 y 3 (histograma, desviación estándar) que `ACTUAL_COST` tiene un sesgo fuerte a la derecha, no una forma de campana. Usar ANOVA sobre datos así violaría uno de sus supuestos base.

## Marco de interpretación usado en todas las pruebas
- **Hipótesis nula (H₀):** no existe diferencia real entre los grupos comparados; cualquier diferencia observada se debe al azar del muestreo.
- **p-value:** probabilidad de observar una diferencia tan grande como la encontrada, *si* la hipótesis nula fuera cierta. Un p-value < 0.05 lleva a rechazar H₀ (concluir que la diferencia es real). **No es la probabilidad de que H₀ sea verdadera o falsa.**
- **Advertencia sobre el tamaño de muestra:** con 4.3+ millones de filas, prácticamente cualquier diferencia, por mínima que sea, resultará "estadísticamente significativa". Por eso cada prueba aquí se interpreta en 2 pasos: (1) ¿hay diferencia real? y (2) ¿qué tan grande es, según los valores reales de las Prácticas 2-3?

---

## 1. ¿Las 7 regiones tienen costos distintos entre sí? (Kruskal-Wallis)

**H₀:** no existe diferencia en el costo por receta (`ACTUAL_COST`) entre las 7 regiones.

```python
grupos_region = [df_final[df_final['REGIONAL_OFFICE_NAME'] == r]['ACTUAL_COST'] for r in regiones_lista]
stats.kruskal(*grupos_region)
```
**Resultado:** estadístico = 17,090.94, **p-value ≈ 0.0**

**Interpretación:** existe una diferencia estadísticamente real entre las 7 regiones (se rechaza H₀). Sin embargo, dado el tamaño de la muestra, esto no implica que la diferencia sea grande: las medianas reales (Práctica 2) van de £97.94 a £118.75 — un rango de solo ~£40. La diferencia es real, pero modesta en magnitud.

## 2. ¿London es distinto al resto de las regiones? (Mann-Whitney U)

**H₀:** el costo por receta en London es igual al del resto de las regiones combinadas.

```python
costo_londres = df_final[df_final['REGIONAL_OFFICE_NAME'] == 'LONDON']['ACTUAL_COST']
costo_resto = df_final[df_final['REGIONAL_OFFICE_NAME'] != 'LONDON']['ACTUAL_COST']
stats.mannwhitneyu(costo_londres, costo_resto)
```
**Resultado:** estadístico = 1,200,535,237,880.5, **p-value ≈ 0.0**

**Interpretación:** el costo por receta en London es estadísticamente distinto al del resto de las regiones. La magnitud es real pero moderada: London tiene `costo_por_item` de £118.75 frente a £97.94-111.05 en las demás regiones. **La causa de esta diferencia (posible relación con nivel socioeconómico, documentada en la literatura de acceso a GLP-1 en NHS) permanece como hipótesis — esta prueba no la confirma ni la descarta, solo confirma que la diferencia de costo existe.**

## 3. ¿Las 6 sustancias tienen costos distintos entre sí? (Kruskal-Wallis)

**H₀:** no existe diferencia en el costo por receta entre las 6 sustancias.

```python
grupos_sustancia = [df_final[df_final['SUSTANCIA'] == s]['ACTUAL_COST'] for s in sustancias_lista]
stats.kruskal(*grupos_sustancia)
```
**Resultado:** estadístico = 506,240.04, **p-value ≈ 0.0**

**Interpretación:** existe diferencia real entre sustancias. A diferencia de la comparación regional, aquí la magnitud sí es considerable: el `precio_por_unidad` (Práctica 2) va de £6.96 (Semaglutide) a £153.44 (Tirzepatide) — más de 20 veces de diferencia entre extremos.

## 4. ¿Tirzepatide es distinto al resto de las sustancias? (Mann-Whitney U)

**H₀:** el costo de Tirzepatide es igual al del resto de las sustancias combinadas.

```python
costo_tirzepatide = df_final[df_final['SUSTANCIA'] == 'Tirzepatide']['ACTUAL_COST']
costo_resto_sustancias = df_final[df_final['SUSTANCIA'] != 'Tirzepatide']['ACTUAL_COST']
stats.mannwhitneyu(costo_tirzepatide, costo_resto_sustancias)
```
**Resultado:** estadístico = 1,818,456,949,534.0, **p-value ≈ 0.0**

**Interpretación:** Tirzepatide es estadísticamente distinta al resto, y con magnitud considerable en múltiples métricas: `precio_por_unidad` (£153.44) más de 4 veces el de la segunda sustancia más cara (Liraglutide, £36.58), y desviación estándar de costo (£1,571.38) igualmente más de 4 veces la segunda más alta (Dulaglutide, £382.87). Confirma con rigor estadístico lo ya observado visualmente en 3 gráficas independientes de la Práctica 3 (histograma, barras, dispersión). **La causa de este comportamiento (posible protección de patente por ser la sustancia más reciente, posicionamiento de marca) permanece como hipótesis, no confirmada por esta prueba.**

## 5. [Bonus] ¿Hay más recetas en enero-febrero por estacionalidad de año nuevo? (Mann-Whitney U)

A diferencia de las pruebas anteriores (sobre `ACTUAL_COST`), esta compara `ITEMS` (volumen de recetas), ya que la hipótesis es sobre actividad/demanda, no precio.

**H₀:** el volumen de recetas (`ITEMS`) en enero-febrero es igual al del resto del año.

```python
df_final['MES'] = df_final['FECHA'].dt.month
items_ene_feb = df_final[df_final['MES'].isin([1, 2])]['ITEMS']
items_resto = df_final[~df_final['MES'].isin([1, 2])]['ITEMS']
stats.mannwhitneyu(items_ene_feb, items_resto)
```
**Resultado:** estadístico = 1,358,349,450,074.5, **p-value ≈ 7.9×10⁻¹⁰⁷**

Promedio de `ITEMS`: enero-febrero = **3.27**, resto del año = **3.39**

**Interpretación:** existe una diferencia estadísticamente real, pero **en dirección contraria a la hipótesis planteada** — el volumen en enero-febrero es ligeramente *menor*, no mayor, al del resto del año. La diferencia además es de magnitud pequeña (0.115 recetas en promedio). Una explicación posible: la hipótesis de "propósito de año nuevo" aplica más naturalmente al uso de GLP-1 para pérdida de peso, mientras que la mayoría del histórico de este dataset (especialmente 2021-2023) refleja uso médico continuo para diabetes, sin relación con estacionalidad de resoluciones de año nuevo. **Pendiente para la Práctica 8:** repetir esta prueba filtrando solo presentaciones asociadas a indicación de pérdida de peso, en el periodo donde ya tuvieron disponibilidad amplia (2024-2026).

---

## Resumen de hallazgos de la práctica

| Prueba | ¿Diferencia real? | ¿Magnitud? |
|---|---|---|
| 7 regiones (costo) | Sí | Modesta (~£40 de rango) |
| London vs. resto | Sí | Moderada (£118.75 vs. £97.94-111.05) |
| 6 sustancias (costo) | Sí | Considerable (20x entre extremos) |
| Tirzepatide vs. resto | Sí | Considerable (4x+ en precio y variabilidad) |
| Enero-febrero vs. resto (bonus) | Sí | Pequeña, y **contraria** a la hipótesis inicial |

Estas pruebas dan respaldo estadístico formal a la parte de "desigualdad geográfica" y "composición del mercado" de la pregunta ancla del proyecto. La parte de "qué consultorios impulsan el crecimiento" queda pendiente para la Práctica 7 (Clustering), ya que requiere una técnica de agrupamiento exploratorio, no de comprobación de hipótesis.

## Archivos
- `practica_4.ipynb` — notebook con las 5 pruebas y su código
- Este `README.md`