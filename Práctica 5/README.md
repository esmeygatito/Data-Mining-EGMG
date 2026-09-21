# Práctica 5 — Modelos Lineales y Correlación

## Objetivo
Generar modelos lineales para cuantificar relaciones ya observadas visualmente en prácticas anteriores, obtener la métrica R², y explorar cómo cambia el ajuste del modelo al variar granularidad y composición de los datos.

## Marco de interpretación
- **R²** (0 a 1): qué proporción de la variación en Y es explicada por el modelo lineal en función de X. No mide si hay o no relación (eso lo indica el p-value del modelo) — mide qué tan bien esa relación se ajusta a una línea recta.
- Un **R² bajo con p-value significativo** indica que la relación es real, pero una línea recta no la describe bien (útil para detectar patrones no lineales, mezclas de subgrupos, o outliers).

---

## Parte 1 — Volumen (`TOTAL_QUANTITY`) → Revenue (`ACTUAL_COST`)

### 1a. Granularidad anual (28 puntos: sustancia × año, 2021-2025)

| Modelo | Pendiente (£/unidad) | R² | p-value |
|---|---|---|---|
| Con las 6 sustancias | 4.58 | 0.174 | 0.027 |
| Sin Tirzepatide | 4.97 | **0.561** | 1.63×10⁻⁵ |

**Hallazgo:** excluir Tirzepatide más que triplica el R² (0.174 → 0.561), confirmando cuantitativamente que rompe la relación esperada entre volumen y revenue observada visualmente en la Práctica 3.

### 1b. Granularidad mensual (355 puntos: sustancia × mes)

| Modelo | R² |
|---|---|
| Con las 6 sustancias | 0.075 |
| Sin Tirzepatide | 0.569 |

**Hallazgo:** al bajar a nivel mensual, el R² con las 6 sustancias cae aún más (0.174 → 0.075), pero el modelo sin Tirzepatide se mantiene prácticamente igual (0.561 → 0.569). Esto indica que la inestabilidad adicional capturada al ver el detalle mensual proviene casi por completo de Tirzepatide — su comportamiento no solo rompe la relación de precio esperada (Práctica 4), sino que introduce variabilidad mes a mes ausente en el resto del mercado.

*(Gráficas: dispersión con línea de tendencia superpuesta, ambos paneles con eje Y compartido y texto con pendiente/R² dentro de cada panel; versiones anual y mensual)*

### 1c. Modelos individuales por sustancia (mensual)

| Sustancia | Pendiente (£/unidad) | R² | n |
|---|---|---|---|
| Liraglutide | 36.82 | 1.000 | 65 |
| Lixisenatide | 27.10 | 1.000 | 60 |
| Dulaglutide | 16.31 | 0.996 | 65 |
| Exenatide | 24.96 | 0.954 | 65 |
| Tirzepatide | 191.77 | 0.817 | 35 |
| Semaglutide | 1.64 | 0.572 | 65 |

**Hallazgo clave:** vistas individualmente, 5 de 6 sustancias tienen un ajuste casi perfecto entre volumen y revenue. El problema del modelo conjunto no es que los datos sean ruidosos — es que cada sustancia tiene su **propia** tasa de conversión volumen→precio, con pendientes que van de £1.64 a £191.77 (más de 100 veces de diferencia). Forzar una sola línea sobre 6 negocios con tasas tan distintas nunca puede ajustar bien.

**Caso Semaglutide (R²=0.572, el más bajo de las 5 "normales"):** se investigó comparando la variabilidad de su precio por unidad mensual contra Dulaglutide:

| | Media (£/unidad) | Desv. estándar |
|---|---|---|
| Semaglutide | 12.58 | 10.25 |
| Dulaglutide | 17.57 | 0.54 |

El precio por unidad de Semaglutide varía más de 11 veces (£4.24 a £48.53) mes a mes, mientras que Dulaglutide es casi constante. Esto se explica porque "Semaglutide" agrupa 3 productos con roles de mercado distintos (Ozempic y Rybelsus para diabetes, Wegovy para pérdida de peso) cuyo peso relativo cambia con el tiempo — a diferencia de las demás sustancias, que no tienen esta mezcla.

---

## Parte 2 — Tiempo → Revenue por sustancia

Se convirtió `FECHA` a un número consecutivo de mes transcurrido (`MES_NUMERO`, 1=enero 2021) y se corrió un modelo lineal independiente por sustancia.

| Sustancia | Crecimiento mensual | R² |
|---|---|---|
| **Tirzepatide** | **+£1,451,473/mes** | 0.813 |
| Semaglutide | +£50,279/mes | 0.433 |
| Exenatide | -£7,294/mes | 0.797 |
| Lixisenatide | -£2,977/mes | 0.951 |
| Dulaglutide | -£43,772/mes | 0.253 |
| Liraglutide | -£73,931/mes | 0.849 |

**Hallazgos:**
- Tirzepatide crece más de 28 veces más rápido que la siguiente sustancia en crecimiento (Semaglutide).
- 4 de 6 sustancias muestran pendiente negativa — no solo crecen más lento, están en declive absoluto.
- **El R² de una tendencia decreciente no indica "qué tan grave" es la caída, sino qué tan predecible/consistente es su causa.** Lixisenatide (R²=0.951) y Liraglutide (R²=0.849) tienen caídas muy limpias porque responden a una causa mecánica única y sin freno (descontinuación y agotamiento de inventario, documentado en la Práctica 1). Dulaglutide (R²=0.253, el más bajo) sigue activa en el mercado compitiendo contra Tirzepatide y Semaglutide; su declive está sujeto a múltiples fuerzas cambiantes mes a mes, resultando en un ajuste menos limpio pese a la misma dirección general.
- **Limitación visual identificada:** al graficar, Dulaglutide muestra una forma de "montaña" (sube hasta ~mes 30, luego cae) — un patrón no monótono que una línea recta no puede describir bien, explicando su bajo R². Liraglutide y Lixisenatide muestran un declive seguido de un "piso" cercano a cero una vez agotado el inventario; el modelo lineal no captura ese aplanamiento y proyecta valores negativos sin sentido de negocio más allá de ese punto (se ajustó el eje Y de sus gráficas para omitir esa proyección sin sentido).
- **Consistencia entre modelos:** Semaglutide vuelve a mostrar el R² más bajo entre las sustancias "normales" (0.433) también en este modelo de tiempo, reforzando la causa ya identificada en la Parte 1 (mezcla cambiante de productos con roles de mercado distintos).

*(Gráfica: cuadrícula 2×3, un panel por sustancia con puntos reales + línea de tendencia; ejes X no comparables entre paneles ya que Tirzepatide solo tiene datos desde el mes 25, cuando comenzó a tener actividad)*

## Archivos
- `practica_5.ipynb` — notebook con los modelos y gráficas
- Este `README.md`