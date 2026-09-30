# %% Celda 1
##Pruebas estadisticas  

# %% Celda 2
import pandas as pd

df_final = pd.read_csv("../Práctica 1/glp1_limpio.csv", parse_dates=['FECHA'])

# %% Celda 3
##¿las 7 regiones tienen costos realmente distintos entre sí, o podría ser casualidad?

# %% Celda 4
#Kruskal-Wallis
from scipy import stats

regiones_lista = df_final['REGIONAL_OFFICE_NAME'].unique()
grupos_region = [df_final[df_final['REGIONAL_OFFICE_NAME'] == r]['ACTUAL_COST'] for r in regiones_lista]

resultado = stats.kruskal(*grupos_region)
print(resultado)

# %% Celda 5
#Sí existe una diferencia estadísticamente real entre las 7 regiones (p<0.05, de hecho prácticamente 0) — no es casualidad del muestreo. Pero, dado que tengo 4.3 millones de filas, incluso una diferencia pequeña en términos de negocio sería detectada como 'significativa' por la prueba. Al revisar las medianas reales de la Práctica 2 (£145-185, un rango de solo £40 entre la región más barata y la más cara), la diferencia, aunque real, es modesta en magnitud — no estamos hablando de que una región cueste el doble que otra.

# %% Celda 6
#¿Londres específicamente es distinto al resto de las regiones juntas?

# %% Celda 7
#Mann-Whitney U
costo_londres = df_final[df_final['REGIONAL_OFFICE_NAME'] == 'LONDON']['ACTUAL_COST']
costo_resto = df_final[df_final['REGIONAL_OFFICE_NAME'] != 'LONDON']['ACTUAL_COST']

resultado_londres = stats.mannwhitneyu(costo_londres, costo_resto)
print(resultado_londres)

# %% Celda 8
#La prueba de Mann-Whitney U confirma que el costo por receta en London es estadísticamente distinto al del resto de las regiones (p≈0.0). Dado el tamaño de la muestra (más de 4 millones de filas), este resultado no debe interpretarse como una diferencia necesariamente grande — y, en efecto, al revisar los valores reales (Práctica 2), London tiene un costo_por_item de £118.75 frente a un rango de £97.94-111.05 en las demás regiones: una diferencia real pero moderada. La causa exacta de esta diferencia (posiblemente relacionada con el nivel socioeconómico de la región, un patrón documentado en la literatura de acceso a GLP-1 en NHS) queda como hipótesis para investigar más a fondo, no como algo confirmado por esta prueba.

# %% Celda 9
#¿las 6 sustancias tienen precios realmente distintos entre sí?

# %% Celda 10
#Kruskal-Wallis
sustancias_lista = df_final['SUSTANCIA'].unique()
grupos_sustancia = [df_final[df_final['SUSTANCIA'] == s]['ACTUAL_COST'] for s in sustancias_lista]

resultado_sustancia = stats.kruskal(*grupos_sustancia)
print(resultado_sustancia)

# %% Celda 11
#¿Tirzepatide específicamente es distinta al resto de las sustancias juntas?

# %% Celda 12
#La prueba de Kruskal-Wallis confirma que existe una diferencia estadísticamente real en el costo entre las 6 sustancias (p≈0.0) — no es casualidad del muestreo. A diferencia de la comparación por regiones, aquí la magnitud de la diferencia sí es considerable: el precio_por_unidad va de £6.96 (Semaglutide) a £153.44 (Tirzepatide), más de 20 veces de diferencia entre extremos. Sin embargo, esta prueba general no identifica cuál sustancia específica impulsa esa diferencia — eso se confirma en la siguiente prueba (Tirzepatide vs. el resto).

# %% Celda 13
costo_tirzepatide = df_final[df_final['SUSTANCIA'] == 'Tirzepatide']['ACTUAL_COST']
costo_resto_sustancias = df_final[df_final['SUSTANCIA'] != 'Tirzepatide']['ACTUAL_COST']

resultado_tirzepatide = stats.mannwhitneyu(costo_tirzepatide, costo_resto_sustancias)
print(resultado_tirzepatide)

# %% Celda 14
#La prueba de Mann-Whitney U confirma que el costo de Tirzepatide es estadísticamente distinto al del resto de las sustancias combinadas (p≈0.0). A diferencia de la diferencia modesta encontrada entre regiones, aquí la magnitud es considerable y consistente en múltiples métricas: su precio_por_unidad (£153.44) es más de 4 veces el de la segunda sustancia más cara (Liraglutide, £36.58), y su desviación estándar de costo (£1,571.38) es igualmente más de 4 veces la segunda más alta (Dulaglutide, £382.87). Esta prueba confirma que Tirzepatide es un caso genuinamente atípico dentro del grupo GLP-1, respaldando con rigor estadístico lo ya observado visualmente en el histograma, las barras y la dispersión de la Práctica 3. La causa de este comportamiento (posible protección de patente por ser la sustancia más reciente, u otro factor de mercado) permanece como hipótesis a explorar, no como algo confirmado por esta prueba

# %% Celda 15
#¿hay más actividad (recetas) en enero/febrero, por los propósitos de año nuevo, comparado con el resto del año?

# %% Celda 16
df_final['MES'] = df_final['FECHA'].dt.month

# %% Celda 17
items_ene_feb = df_final[df_final['MES'].isin([1, 2])]['ITEMS']
items_resto = df_final[~df_final['MES'].isin([1, 2])]['ITEMS']

resultado_estacional = stats.mannwhitneyu(items_ene_feb, items_resto)
print(resultado_estacional)

# %% Celda 18
print('Promedio ITEMS enero-febrero:', items_ene_feb.mean())
print('Promedio ITEMS resto del año:', items_resto.mean())

# %% Celda 19
#La prueba de Mann-Whitney U confirma una diferencia estadísticamente real entre el volumen de recetas (ITEMS) en enero-febrero frente al resto del año (p≈7.9×10⁻¹⁰⁷). Sin embargo, la dirección es contraria a la hipótesis planteada: el promedio en enero-febrero (3.27) es ligeramente MENOR al del resto del año (3.39), no mayor. La diferencia, aunque real, es de magnitud pequeña (0.115 recetas en promedio). Una posible explicación es que la hipótesis de "propósito de año nuevo" aplica más naturalmente al uso de GLP-1 para pérdida de peso, mientras que la mayoría del histórico de este dataset (especialmente 2021-2023) refleja uso médico continuo para diabetes, sin relación con estacionalidad de resoluciones de año nuevo. Esta hipótesis podría probarse de forma más específica filtrando solo presentaciones asociadas a indicación de pérdida de peso (ej. Wegovy) en el periodo donde ya tuvo disponibilidad amplia (2024-2026) — pendiente para una práctica futura

# %% Celda 20
