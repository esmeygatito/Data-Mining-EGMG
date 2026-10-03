# %% Celda 1
#Modelos lineales y correlación

# %% Celda 2
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

df_final = pd.read_csv("../Práctica 1/glp1_limpio.csv", parse_dates=['FECHA'])
df_final['ANIO'] = df_final['FECHA'].dt.year

paleta = plt.cm.tab10.colors
sustancias_orden = ['Semaglutide', 'Liraglutide', 'Dulaglutide', 'Exenatide', 'Lixisenatide', 'Tirzepatide']
color_sustancia = dict(zip(sustancias_orden, paleta))

# %% Celda 3
#Volumen --> revenue 
#¿qué tan bien predice el volumen de unidades dispensadas el revenue generado?

# %% Celda 4
#resumen de los datos por año y sustancia para un análisis de correlación
resumen_anio_sustancia = df_final[df_final['ANIO'] != 2026].groupby(['ANIO', 'SUSTANCIA'])[['ACTUAL_COST', 'TOTAL_QUANTITY']].sum().reset_index()
print(resumen_anio_sustancia.shape)

# %% Celda 5
resultado_lineal = stats.linregress(resumen_anio_sustancia['TOTAL_QUANTITY'], resumen_anio_sustancia['ACTUAL_COST'])
print(resultado_lineal)

# %% Celda 6
r_cuadrada = resultado_lineal.rvalue ** 2
print(r_cuadrada)

# %% Celda 7
#ya se que Tirzepatide se comporta diferente, así que vamos a ver si la correlación mejora si la quitamos del análisis
resumen_sin_tirze = resumen_anio_sustancia[resumen_anio_sustancia['SUSTANCIA'] != 'Tirzepatide']

resultado_sin_tirze = stats.linregress(resumen_sin_tirze['TOTAL_QUANTITY'], resumen_sin_tirze['ACTUAL_COST'])
r_cuadrada_sin_tirze = resultado_sin_tirze.rvalue ** 2

print(resultado_sin_tirze)
print('R² sin Tirzepatide:', r_cuadrada_sin_tirze)

# %% Celda 8
plt.style.use('seaborn-v0_8-whitegrid')

fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharey=True)

for sustancia in sustancias_orden:
    datos = resumen_anio_sustancia[resumen_anio_sustancia['SUSTANCIA'] == sustancia]
    axes[0].scatter(datos['TOTAL_QUANTITY'] / 1_000_000, datos['ACTUAL_COST'] / 1_000_000, 
                     color=color_sustancia[sustancia], label=sustancia, s=100, 
                     edgecolors='black', alpha=0.85, zorder=3)

x_linea = resumen_anio_sustancia['TOTAL_QUANTITY'].sort_values()
y_linea = resultado_lineal.intercept + resultado_lineal.slope * x_linea
axes[0].plot(x_linea / 1_000_000, y_linea / 1_000_000, color='black', linestyle='--', linewidth=2, zorder=2)
axes[0].text(0.62, 0.15, f'Pendiente: £{resultado_lineal.slope:.2f} por unidad\nR² = {r_cuadrada:.3f}', 
             transform=axes[0].transAxes, fontsize=10, va='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
axes[0].set_title('Con las 6 sustancias', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Volumen (millones de unidades)')
axes[0].set_ylabel('Revenue (millones de GBP)')

for sustancia in sustancias_orden:
    if sustancia == 'Tirzepatide':
        continue
    datos = resumen_sin_tirze[resumen_sin_tirze['SUSTANCIA'] == sustancia]
    axes[1].scatter(datos['TOTAL_QUANTITY'] / 1_000_000, datos['ACTUAL_COST'] / 1_000_000, 
                     color=color_sustancia[sustancia], label=sustancia, s=100, 
                     edgecolors='black', alpha=0.85, zorder=3)

x_linea2 = resumen_sin_tirze['TOTAL_QUANTITY'].sort_values()
y_linea2 = resultado_sin_tirze.intercept + resultado_sin_tirze.slope * x_linea2
axes[1].plot(x_linea2 / 1_000_000, y_linea2 / 1_000_000, color='black', linestyle='--', linewidth=2, zorder=2)
axes[1].text(0.62, 0.92, f'Pendiente: £{resultado_sin_tirze.slope:.2f} por unidad\nR² = {r_cuadrada_sin_tirze:.3f}', 
             transform=axes[1].transAxes, fontsize=10, va='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
axes[1].set_title('Sin Tirzepatide', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Volumen (millones de unidades)')

handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='center left', bbox_to_anchor=(1.0, 0.5), title='Sustancia')

fig.suptitle('Modelo lineal: Volumen vs. Revenue por sustancia GLP-1', fontsize=15, fontweight='bold')
plt.tight_layout()
plt.show()

# %% Celda 9
#Modelo agrupando datos por mes y sustancia para ver si la correlación mejora al tener más puntos de datos
resumen_mes_sustancia = df_final.groupby(['FECHA', 'SUSTANCIA'])[['ACTUAL_COST', 'TOTAL_QUANTITY']].sum().reset_index()
print(resumen_mes_sustancia.shape)

# %% Celda 10
resultado_mensual = stats.linregress(resumen_mes_sustancia['TOTAL_QUANTITY'], resumen_mes_sustancia['ACTUAL_COST'])
r_cuadrada_mensual = resultado_mensual.rvalue ** 2

resumen_mes_sin_tirze = resumen_mes_sustancia[resumen_mes_sustancia['SUSTANCIA'] != 'Tirzepatide']
resultado_mensual_sin_tirze = stats.linregress(resumen_mes_sin_tirze['TOTAL_QUANTITY'], resumen_mes_sin_tirze['ACTUAL_COST'])
r_cuadrada_mensual_sin_tirze = resultado_mensual_sin_tirze.rvalue ** 2

print('Mensual, con las 6 sustancias — R²:', r_cuadrada_mensual)
print('Mensual, sin Tirzepatide — R²:', r_cuadrada_mensual_sin_tirze)

# %% Celda 11
fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharey=True)

for sustancia in sustancias_orden:
    datos = resumen_mes_sustancia[resumen_mes_sustancia['SUSTANCIA'] == sustancia]
    axes[0].scatter(datos['TOTAL_QUANTITY'] / 1_000_000, datos['ACTUAL_COST'] / 1_000_000, 
                     color=color_sustancia[sustancia], label=sustancia, s=60, 
                     edgecolors='black', alpha=0.7, zorder=3)

x_linea = resumen_mes_sustancia['TOTAL_QUANTITY'].sort_values()
y_linea = resultado_mensual.intercept + resultado_mensual.slope * x_linea
axes[0].plot(x_linea / 1_000_000, y_linea / 1_000_000, color='black', linestyle='--', linewidth=2, zorder=2)
axes[0].text(0.62, 0.15, f'Pendiente: £{resultado_mensual.slope:.2f} por unidad\nR² = {r_cuadrada_mensual:.3f}', 
             transform=axes[0].transAxes, fontsize=10, va='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
axes[0].set_title('Con las 6 sustancias', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Volumen mensual (millones de unidades)')
axes[0].set_ylabel('Revenue mensual (millones de GBP)')

for sustancia in sustancias_orden:
    if sustancia == 'Tirzepatide':
        continue
    datos = resumen_mes_sin_tirze[resumen_mes_sin_tirze['SUSTANCIA'] == sustancia]
    axes[1].scatter(datos['TOTAL_QUANTITY'] / 1_000_000, datos['ACTUAL_COST'] / 1_000_000, 
                     color=color_sustancia[sustancia], label=sustancia, s=60, 
                     edgecolors='black', alpha=0.7, zorder=3)

x_linea2 = resumen_mes_sin_tirze['TOTAL_QUANTITY'].sort_values()
y_linea2 = resultado_mensual_sin_tirze.intercept + resultado_mensual_sin_tirze.slope * x_linea2
axes[1].plot(x_linea2 / 1_000_000, y_linea2 / 1_000_000, color='black', linestyle='--', linewidth=2, zorder=2)
axes[1].text(0.62, 0.92, f'Pendiente: £{resultado_mensual_sin_tirze.slope:.2f} por unidad\nR² = {r_cuadrada_mensual_sin_tirze:.3f}', 
             transform=axes[1].transAxes, fontsize=10, va='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
axes[1].set_title('Sin Tirzepatide', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Volumen mensual (millones de unidades)')

handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='center left', bbox_to_anchor=(1.0, 0.5), title='Sustancia')

fig.suptitle('Modelo lineal: Volumen vs. Revenue por sustancia GLP-1 (granularidad mensual)', fontsize=15, fontweight='bold')
plt.tight_layout()
plt.show()

# %% Celda 12
#verificar si cada sustancia tiene un comportamiento lineal similar al del conjunto de datos completo
resultados_por_sustancia = {}

for sustancia in sustancias_orden:
    datos = resumen_mes_sustancia[resumen_mes_sustancia['SUSTANCIA'] == sustancia]
    resultado = stats.linregress(datos['TOTAL_QUANTITY'], datos['ACTUAL_COST'])
    r2 = resultado.rvalue ** 2
    resultados_por_sustancia[sustancia] = {'slope': resultado.slope, 'r2': r2, 'n_puntos': len(datos)}

for sustancia, info in resultados_por_sustancia.items():
    print(f"{sustancia}: slope={info['slope']:.2f}, R²={info['r2']:.3f}, n={info['n_puntos']}")

# %% Celda 13
#investigar por qué semaglutide tiene un R² tan bajo comparado con las otras sustancias
##precio por unidad mes a mes
semaglutide_mensual = resumen_mes_sustancia[resumen_mes_sustancia['SUSTANCIA'] == 'Semaglutide'].copy()
semaglutide_mensual['precio_unidad'] = semaglutide_mensual['ACTUAL_COST'] / semaglutide_mensual['TOTAL_QUANTITY']
print(semaglutide_mensual['precio_unidad'].describe())

# %% Celda 14
#comparando con una sustancia con un R² alto, como dulaglutide
dulaglutide_mensual = resumen_mes_sustancia[resumen_mes_sustancia['SUSTANCIA'] == 'Dulaglutide'].copy()
dulaglutide_mensual['precio_unidad'] = dulaglutide_mensual['ACTUAL_COST'] / dulaglutide_mensual['TOTAL_QUANTITY']
print(dulaglutide_mensual['precio_unidad'].describe())

# %% Celda 15
#modelo 2 para descrbir la relaion entre el tiempo y el revenue, para ver si el revenue crece de manera lineal con el tiempo, o si hay un patrón diferente.
#se va a correr un modelo por sustancia  
resumen_mes_sustancia['MES_NUMERO'] = (resumen_mes_sustancia['FECHA'].dt.year - 2021) * 12 + resumen_mes_sustancia['FECHA'].dt.month
print(resumen_mes_sustancia[['FECHA', 'MES_NUMERO']].head())
print(resumen_mes_sustancia[['FECHA', 'MES_NUMERO']].tail())

# %% Celda 16
crecimiento_por_sustancia = {}

for sustancia in sustancias_orden:
    datos = resumen_mes_sustancia[resumen_mes_sustancia['SUSTANCIA'] == sustancia]
    resultado = stats.linregress(datos['MES_NUMERO'], datos['ACTUAL_COST'])
    r2 = resultado.rvalue ** 2
    crecimiento_por_sustancia[sustancia] = {'slope': resultado.slope, 'r2': r2, 'n_puntos': len(datos)}

for sustancia, info in crecimiento_por_sustancia.items():
    print(f"{sustancia}: crecimiento=£{info['slope']:,.0f}/mes, R²={info['r2']:.3f}, n={info['n_puntos']}")

# %% Celda 17
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
axes = axes.flatten()

for i, sustancia in enumerate(sustancias_orden):
    datos = resumen_mes_sustancia[resumen_mes_sustancia['SUSTANCIA'] == sustancia].sort_values('MES_NUMERO')
    axes[i].scatter(datos['MES_NUMERO'], datos['ACTUAL_COST'] / 1_000_000, 
                     color=color_sustancia[sustancia], s=40, alpha=0.7, zorder=3)
    
    info = crecimiento_por_sustancia[sustancia]
    x_linea = datos['MES_NUMERO']
    resultado_temp = stats.linregress(datos['MES_NUMERO'], datos['ACTUAL_COST'])
    y_linea = (resultado_temp.intercept + resultado_temp.slope * x_linea) / 1_000_000
    axes[i].plot(x_linea, y_linea, color='black', linestyle='--', linewidth=2, zorder=2)
    
    axes[i].set_title(f"{sustancia}\n£{info['slope']:,.0f}/mes, R²={info['r2']:.3f}", fontsize=11)
    axes[i].set_xlabel('Mes transcurrido')
    axes[i].set_ylabel('Revenue (millones GBP)')
axes[1].set_ylim(bottom=0)  # Liraglutide
axes[4].set_ylim(bottom=0)  # Lixisenatide
fig.suptitle('Tendencia mensual de revenue por sustancia GLP-1', fontsize=15, fontweight='bold')
plt.tight_layout()
plt.show()
