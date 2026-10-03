# %% Celda 1
#Mi pregunta de investigación es: ¿Qué segmentos de consultorios están impulsando el crecimiento del "revenue" del mercado GLP-1, y cómo está cambiando la composición de ese ingreso entre sustancias a lo largo del tiempo?

# %% Celda 2
import sys
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")  # evita UnicodeEncodeError con "≈" en consolas Windows (cp1252)

df_final = pd.read_csv("../Práctica 1/glp1_limpio.csv")

# %% Celda 3
#Voy a enfocarme en las métricas de "revenue" 

columnas_revenue = ['QUANTITY', 'ITEMS', 'TOTAL_QUANTITY', 'NIC', 'ACTUAL_COST']
print(df_final[columnas_revenue].describe())

# """  # [solo notebook]
# NIC: media ≈ 361.89, mediana ≈ 156.96
# ACTUAL_COST: media ≈ 350.93, mediana ≈ 156.97
# --> Es una distribución sesgada a la derecha, lo que indica que hay algunos consultorios con ingresos significativamente más altos que la mayoría.
# """
print("""
NIC: media ≈ 361.89, mediana ≈ 156.96
ACTUAL_COST: media ≈ 350.93, mediana ≈ 156.97
--> Es una distribución sesgada a la derecha, lo que indica que hay algunos consultorios con ingresos significativamente más altos que la mayoría.
""")

# %% Celda 4
#quiero la moda de quantity y de items para ver si hay un patrón en la cantidad de productos vendidos y en el número de artículos vendidos por consultorio.

print("Moda de QUANTITY:", df_final['QUANTITY'].mode()[0])
print("Moda de ITEMS:", df_final['ITEMS'].mode()[0])

# %% Celda 5
resumen_sustancia = df_final.groupby('SUSTANCIA')[['ACTUAL_COST', 'ITEMS']].sum()
print(resumen_sustancia.sort_values('ACTUAL_COST', ascending=False))
#Tirzepatide genera el revenue más alto (572M), pero NO tiene el mayor número de ITEMS

# %% Celda 6
#Costo promedio de cada item por sustancia
resumen_sustancia['costo_por_item'] = resumen_sustancia['ACTUAL_COST'] / resumen_sustancia['ITEMS']
print(resumen_sustancia.sort_values('costo_por_item', ascending=False))
#Tirzepatide tiene el costo promedio por item más alto , mientras que Semaglutide y dulaglutide tienen costo promedio por item más bajo. Esto sugiere que Tirzepatide está generando ingresos más altos a pesar de tener menos items vendidos, lo que podría indicar una estrategia de precios diferente o un mercado objetivo distinto.

# %% Celda 7
#para bajar la hipotesis planteada, necesito revisar que estemos comparando costos de la misma cantidad de quantity.
print(df_final.groupby('SUSTANCIA')['QUANTITY'].mean().sort_values(ascending=False))

#Noto que se refuta mi hipotesis y Tirzepatide no es caro "porque trae más unidades", es genuinamente más caro por unidad individual

# %% Celda 8

# %% Celda 9
#voy a calcular el verdadero precio por unidad
resumen_sustancia_v2 = df_final.groupby('SUSTANCIA')[['ACTUAL_COST', 'TOTAL_QUANTITY']].sum()
resumen_sustancia_v2['precio_por_unidad'] = resumen_sustancia_v2['ACTUAL_COST'] / resumen_sustancia_v2['TOTAL_QUANTITY']
print(resumen_sustancia_v2.sort_values('precio_por_unidad', ascending=False))
#veo que Tirzepatide sigue siendo el más caro por unidad, mientras que Semaglutide y dulaglutide siguen siendo los más baratos. Esto refuerza la idea de que Tirzepatide está generando ingresos más altos debido a un precio por unidad más alto, en lugar de simplemente vender más unidades.

# %% Celda 10
#quiero ver cómo se estaba inflando el costo_item con el verdaddero precio por unidad, para ver cómo una sustancia se está inflando en el costo_item debido a que tiene más unidades por item.
comparacion = resumen_sustancia[['costo_por_item']].join(resumen_sustancia_v2[['precio_por_unidad']])
comparacion['diferencia'] = comparacion['costo_por_item'] - comparacion['precio_por_unidad']
print(comparacion.sort_values('diferencia', ascending=False))

# %% Celda 11
"""
Tirzepatide es por mucho el más reciente de las 6 sustancias — su llegada a atención primaria
 en NHS fue apenas junio 2025, mientras que las demás (Liraglutide, Exenatide, etc.)
llevan años en el mercado y ya no tienen protección de patente tan fuerte.
 Un medicamento nuevo bajo patente, sin competencia de genéricos todavía, 
típicamente mantiene precios altos — eso podría explicar el precio
"""

# %% Celda 12
#Ahora haré un agrupamiento por region 

resumen_region = df_final.groupby(['REGIONAL_OFFICE_NAME'])[['ACTUAL_COST', 'ITEMS']].sum()
resumen_region['costo_por_item'] = resumen_region['ACTUAL_COST'] / resumen_region['ITEMS']
print(resumen_region.sort_values('ACTUAL_COST', ascending=False))


# %% Celda 13
"""
London tiene el costo por item más alto, a pesar de no tener el mayor número de items vendidos. 
las tasas de prescripción son mucho más altas en zonas de mayor nivel socioeconómico,
a pesar de tener menor prevalencia de obesidad porque las zonas más ricas parecen tener 
más facilidad de acceso a estos medicamentos
(posiblemente a sustancias/presentaciones más nuevas y caras, como Tirzepatide).
"""

# %% Celda 14
#Voy a obtener la distribucion de cada sustancia por region para ver si hay alguna region que esté impulsando el revenue de una sustancia en particular.
region_sustancia = df_final.groupby(['REGIONAL_OFFICE_NAME', 'SUSTANCIA'])['ITEMS'].sum()
print(region_sustancia)

# %% Celda 15
tabla_region_sustancia = region_sustancia.unstack()
print(tabla_region_sustancia)

# %% Celda 16
totales_por_region = tabla_region_sustancia.sum(axis=1)
porcentaje_tirzepatide = (tabla_region_sustancia['Tirzepatide'] / totales_por_region * 100).sort_values(ascending=False)
print(porcentaje_tirzepatide)
#Aqui descubri que el hecho de que London sea una region con mejor economía y con mayor acceso a medicamentos de patente, no es el que tiene una mayor venta de Tirzepatide, sino que es la region de South East, que tiene un 30% de sus items vendidos siendo Tirzepatide. Esto podría indicar que South East tiene un mercado objetivo más inclinado a este medicamento en particular, o que hay una estrategia de marketing más efectiva para Tirzepatide, la sustancia más cara.

# %% Celda 17
"voy a tratar de responder a : si no es la MEZCLA de sustancias lo que hace a Londres cara, ¿qué es entonces?"

