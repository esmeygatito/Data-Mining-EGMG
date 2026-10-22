# Práctica 8 — Pronóstico (series de tiempo): Tirzepatide en NHS England
# Algunas celdas consultan la API de NHSBSA (opendata.nhsbsa.net) y requieren conexión a internet.

# %% Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import requests
import time
from scipy.stats import linregress

# %% Celda 1
##Forecasting, predecir datos futuros 

## Exploración inicial con glp1_limpio.csv

# %% Celda 2

df_final = pd.read_csv("../Práctica 1/glp1_limpio.csv", parse_dates=['FECHA'])

serie_total = df_final.groupby('FECHA')['ACTUAL_COST'].sum()
serie_tirz = df_final[df_final['SUSTANCIA'] == 'Tirzepatide'].groupby('FECHA')['ACTUAL_COST'].sum()

print(len(serie_total), serie_total.index.min(), serie_total.index.max())
print(len(serie_tirz), serie_tirz.index.min(), serie_tirz.index.max())

fig, ax = plt.subplots(figsize=(10, 4))
serie_total.plot(ax=ax, label='Mercado GLP-1 total')
serie_tirz.plot(ax=ax, label='Tirzepatide')
ax.legend()
ax.set_title('Revenue mensual (GBP)')
plt.show()

# %% Celda 3
tirz = df_final[df_final['SUSTANCIA'] == 'Tirzepatide']
chequeo = tirz.groupby('FECHA').agg(
    revenue=('ACTUAL_COST', 'sum'),
    unidades=('TOTAL_QUANTITY', 'sum'),
    recetas=('ITEMS', 'sum')
)
chequeo['precio_por_unidad'] = chequeo['revenue'] / chequeo['unidades']
print(chequeo.loc['2025-05':'2025-12'].round(1))

# %% Celda 4
serie_unidades = df_final[df_final['SUSTANCIA'] == 'Tirzepatide'].groupby('FECHA')['TOTAL_QUANTITY'].sum()

print(serie_unidades.loc['2023-01':'2024-06'])

fig, ax = plt.subplots(figsize=(10, 4))
serie_unidades.plot(ax=ax)
ax.axvline(pd.Timestamp('2025-09-01'), color='gray', linestyle='--')
ax.set_title('Tirzepatide: unidades mensuales (línea punteada = septiembre 2025)')
plt.show()

# %% Celda 5
# 1) serie mensual completa desde marzo 2024
u = serie_unidades.asfreq('MS', fill_value=0).loc['2024-03':]
print(len(u), u.index.min(), u.index.max())

# 2) corte por fecha: los últimos 6 meses son la prueba
train = u.iloc[:-6]
test = u.iloc[-6:]
print(train.index.max(), test.index.min(), test.index.max())

# 3) modelo ingenuo: se repite el último valor de entrenamiento
pred_naive = pd.Series(train.iloc[-1], index=test.index)

mae_naive = (test - pred_naive).abs().mean()
mape_naive = ((test - pred_naive).abs() / test).mean() * 100
print(round(mae_naive), round(mape_naive, 1))

# %% Celda 6

# --- Modelo 2: regresión lineal contra el tiempo ---
t_train = np.arange(len(train))
t_test = np.arange(len(train), len(train) + len(test))

res = stats.linregress(t_train, train.values)
pred_lin = pd.Series(res.intercept + res.slope * t_test, index=test.index)

mae_lin = (test - pred_lin).abs().mean()
mape_lin = ((test - pred_lin).abs() / test).mean() * 100
print("Pendiente (unidades por mes):", round(res.slope), "| R² en entrenamiento:", round(res.rvalue**2, 3))

# --- Modelo 3: Holt con tendencia amortiguada ---
holt = ExponentialSmoothing(train, trend='add', damped_trend=True, seasonal=None).fit()
pred_holt = holt.forecast(len(test))
pred_holt.index = test.index

mae_holt = (test - pred_holt).abs().mean()
mape_holt = ((test - pred_holt).abs() / test).mean() * 100

# --- Comparación ---
resultados = pd.DataFrame(
    {'MAE (unidades)': [mae_naive, mae_lin, mae_holt],
     'MAPE (%)': [mape_naive, mape_lin, mape_holt]},
    index=['Ingenuo', 'Regresión lineal', 'Holt amortiguado']
).round(1)
print(resultados)

fig, ax = plt.subplots(figsize=(10, 4))
train.plot(ax=ax, label='Entrenamiento', color='#898781')
test.plot(ax=ax, label='Real (prueba)', color='black')
pred_naive.plot(ax=ax, label='Ingenuo', color='#2a78d6')
pred_lin.plot(ax=ax, label='Regresión lineal', color='#eb6834')
pred_holt.plot(ax=ax, label='Holt amortiguado', color='#1baf7a')
ax.legend()
ax.set_title('Tirzepatide: unidades reales vs. pronóstico (6 meses de prueba)')
plt.show()

# %% Celda 7
holt_final = ExponentialSmoothing(u, trend='add', damped_trend=True, seasonal=None).fit()
pron = holt_final.forecast(6)   # junio a noviembre de 2026
print(pron.round())

fig, ax = plt.subplots(figsize=(10, 4))
u.plot(ax=ax, label='Real', color='black')
pron.plot(ax=ax, label='Pronóstico (Holt amortiguado)', color='#1baf7a', linestyle='--')
ax.legend()
ax.set_title('Tirzepatide: unidades reales y pronóstico (junio-noviembre 2026)')
plt.show()

# %% Celda 8
tirz = df_final[df_final['SUSTANCIA'] == 'Tirzepatide']
agg = tirz.groupby('FECHA')[['ACTUAL_COST', 'TOTAL_QUANTITY']].sum()
precio_mes = agg['ACTUAL_COST'] / agg['TOTAL_QUANTITY']

print(precio_mes.loc['2025-09':].round(1))

precio_supuesto = precio_mes.loc['2026-03':'2026-05'].mean()
print("Precio supuesto (promedio mar-may 2026):", round(precio_supuesto, 1))

escenarios = pd.DataFrame({
    'Unidades': pron.round(),
    'Libras, precio -10% (M)': pron * precio_supuesto * 0.9 / 1e6,
    'Libras, precio base (M)': pron * precio_supuesto / 1e6,
    'Libras, precio +10% (M)': pron * precio_supuesto * 1.1 / 1e6,
}).round(1)
print(escenarios)

# %% Celda 9
segmentos = pd.read_csv("../Práctica 7/segmentos_p7.csv")
df_seg = df_final.merge(segmentos, on='PRACTICE_CODE', how='inner')

orden = ['Cuentas clave', 'En expansión', 'Emergentes', 'Estables de bajo crecimiento']
rev_seg = (df_seg.pivot_table(index='FECHA', columns='segmento', values='ACTUAL_COST', aggfunc='sum') / 1e6)[orden]

colores = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100']   # mismos colores que en la Práctica 7

fig, ax = plt.subplots(figsize=(10, 4.5))
ax.stackplot(rev_seg.index, rev_seg.T.values, labels=orden, colors=colores)
ax.legend(loc='upper left')
ax.set_ylabel('Millones de GBP')
ax.set_title('Revenue mensual por segmento (6,455 consultorios de la Práctica 7)')
plt.show()

# %% Celda 10
#### Versión final: serie exacta desde la API

# %% Celda 11

BASE_URL = "https://opendata.nhsbsa.net/api/3/action/datastore_search_sql?"

def extraer_records(j):  
    nivel1 = j.get('result', {})
    if 'records' in nivel1:
        return nivel1['records']
    else:
        nivel2 = nivel1.get('result', {})
        return nivel2.get('records', [])

# %% Celda 12

meses_tirz = [f.strftime('%Y%m') for f in pd.date_range('2024-01-01', '2026-08-01', freq='MS')]
filas = []
for mes in meses_tirz:
    resource_id = f"EPD_SNOMED_{mes}"
    columna = "BNF_CHEMICAL_SUBSTANCE" if mes >= "202503" else "CHEMICAL_SUBSTANCE_BNF_DESCR"
    sql = f"""SELECT COUNT(*) AS n_filas,
                     SUM(SAFE_CAST(TOTAL_QUANTITY AS FLOAT64)) AS unidades,
                     SUM(SAFE_CAST(ACTUAL_COST AS FLOAT64)) AS revenue
              FROM `{resource_id}` WHERE {columna} = 'Tirzepatide'"""
    r = requests.get(BASE_URL, params={'resource_id': resource_id, 'sql': sql}, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"{mes}: {r.status_code} {r.text[:200]}")
    rec = extraer_records(r.json())
    if not rec:
        raise RuntimeError(f"{mes}: la API no devolvió registros")
    filas.append({'mes': mes, **rec[0]})
    time.sleep(0.3)

api_tirz = pd.DataFrame(filas)
for c in ['n_filas', 'unidades', 'revenue']:
    api_tirz[c] = pd.to_numeric(api_tirz[c])
api_tirz['FECHA'] = pd.to_datetime(api_tirz['mes'], format='%Y%m')
api_tirz = api_tirz.set_index('FECHA')

print(len(api_tirz), "meses")                  # debe salir 32
print(api_tirz[['n_filas', 'unidades', 'revenue']].tail(8))

# NOTA: redefine serie_unidades, precio_mes y u con la serie exacta de la API
# %% Celda 13
serie_unidades = api_tirz['unidades']
precio_mes = api_tirz['revenue'] / api_tirz['unidades']

u = serie_unidades.asfreq('MS').loc['2024-03':'2026-05']     
real = serie_unidades.loc['2026-06':'2026-08']               
print("meses sin dato en u:", u.isna().sum())                 
print(u.tail(3))
print(real)

# %% Celda 14
for col in ["CHEMICAL_SUBSTANCE_BNF_DESCR", "BNF_CHEMICAL_SUBSTANCE"]:
    sql = f"SELECT COUNT(*) AS n FROM `EPD_SNOMED_202503` where {col} = 'Tirzepatide'"
    r = requests.get(BASE_URL, params={'resource_id': 'EPD_SNOMED_202503', 'sql': sql}, timeout=60)
    print(col, '| status:', r.status_code)
    print(r.text[:400])
    print('---')

sql = "SELECT * FROM `EPD_SNOMED_202503` LIMIT 1"
r = requests.get(BASE_URL, params={'resource_id': 'EPD_SNOMED_202503', 'sql': sql}, timeout=60)
print(r.status_code, r.text[:800])

# %% Celda 15
sql = "SELECT COUNT(*) AS n_filas, SUM(TOTAL_QUANTITY) AS unidades, SUM(ACTUAL_COST) AS revenue FROM `EPD_SNOMED_202503` where BNF_CHEMICAL_SUBSTANCE = 'Tirzepatide'"
r = requests.get(BASE_URL, params={'resource_id': 'EPD_SNOMED_202503', 'sql': sql}, timeout=60)
print(r.status_code, r.text[:500])

sql = "SELECT * FROM `EPD_SNOMED_202503` LIMIT 1"
r = requests.get(BASE_URL, params={'resource_id': 'EPD_SNOMED_202503', 'sql': sql}, timeout=60)
print(list(extraer_records(r.json())[0].keys()))

# %% Celda 16
sql = """SELECT COUNT(*) AS n_filas,
                SUM(SAFE_CAST(TOTAL_QUANTITY AS FLOAT64)) AS unidades,
                SUM(SAFE_CAST(ACTUAL_COST AS FLOAT64)) AS revenue
         FROM `EPD_SNOMED_202503` where BNF_CHEMICAL_SUBSTANCE = 'Tirzepatide'"""
r = requests.get(BASE_URL, params={'resource_id': 'EPD_SNOMED_202503', 'sql': sql}, timeout=60)
print(r.status_code)
rec = extraer_records(r.json())
print(rec)

api_tirz.loc[pd.Timestamp('2025-03-01'), ['n_filas', 'unidades', 'revenue']] = [float(rec[0]['n_filas']), float(rec[0]['unidades']), float(rec[0]['revenue'])]
api_tirz = api_tirz.sort_index()
print(api_tirz.loc['2025-01':'2025-06', ['unidades', 'revenue']])

# NOTA: redefine serie_unidades, precio_mes, u y real con la serie exacta de la API
# %% Celda 17
serie_unidades = api_tirz['unidades']
precio_mes = api_tirz['revenue'] / api_tirz['unidades']

u = serie_unidades.asfreq('MS').loc['2024-03':'2026-05']
real = serie_unidades.loc['2026-06':'2026-08']
print("meses sin dato en u:", u.isna().sum())      
print("meses en u:", len(u))
print(precio_mes.loc['2025-06':'2025-11'].round(1))

# %% Celda 18

print(u.index[0], u.index[-1], len(u))   

train2, test2 = u.iloc[:-6], u.iloc[-6:]

def metricas(real_s, pred_s):
    mae = (real_s - pred_s).abs().mean()
    mape = ((real_s - pred_s).abs() / real_s).mean() * 100
    return round(mae), round(mape, 1)

# Naive: repetir el último valor de train
pred_naive2 = pd.Series(train2.iloc[-1], index=test2.index)

# Lineal: recta sobre el tiempo
t_train = np.arange(len(train2))
t_test = np.arange(len(train2), len(train2) + len(test2))
reg = linregress(t_train, train2.values)
pred_lin2 = pd.Series(reg.intercept + reg.slope * t_test, index=test2.index)

# Holt con tendencia amortiguada
holt_tr = ExponentialSmoothing(train2, trend='add', damped_trend=True, seasonal=None).fit()
pred_holt2 = holt_tr.forecast(6)

res = []
for nombre, pred in [('Naive', pred_naive2), ('Lineal', pred_lin2), ('Holt amortiguado', pred_holt2)]:
    mae, mape = metricas(test2, pred)
    res.append({'Modelo': nombre, 'MAE': mae, 'MAPE %': mape})
print(pd.DataFrame(res))

# %% Celda 19
# Los tres modelos reentrenados con toda u (hasta mayo 2026), pronosticando 3 meses
holt_f2 = ExponentialSmoothing(u, trend='add', damped_trend=True, seasonal=None).fit()
pron_holt = holt_f2.forecast(3)

t_all = np.arange(len(u))
reg_all = linregress(t_all, u.values)
pron_lin = pd.Series(reg_all.intercept + reg_all.slope * np.arange(len(u), len(u) + 3), index=real.index)
pron_naive = pd.Series(u.iloc[-1], index=real.index)

val = pd.DataFrame({
    'Real': real,
    'Naive': pron_naive.round(),
    'Lineal': pron_lin.round(),
    'Holt': pron_holt.values.round(),
})
print(val)

res_val = []
for nombre, pred in [('Naive', pron_naive), ('Lineal', pron_lin), ('Holt amortiguado', pd.Series(pron_holt.values, index=real.index))]:
    mae, mape = metricas(real, pred)
    res_val.append({'Modelo': nombre, 'MAE': mae, 'MAPE %': mape})
print(pd.DataFrame(res_val))

# %% Celda 20
u_full = serie_unidades.asfreq('MS').loc['2024-03':'2026-08']
print("huecos:", u_full.isna().sum(), "| meses:", len(u_full))   

holt_full = ExponentialSmoothing(u_full, trend='add', damped_trend=True, seasonal=None).fit()
pron_unidades = holt_full.forecast(6)          # sep 2026 – feb 2027
print("phi (amortiguamiento):", round(holt_full.params['damping_trend'], 3))

precio_ref = precio_mes.loc['2026-06':'2026-08'].mean()
print("precio de referencia jun-ago 2026: £", round(precio_ref, 1))

esc = pd.DataFrame({
    'unidades': pron_unidades.round(),
    'revenue_base_£M': pron_unidades * precio_ref / 1e6,
    'revenue_-10%_£M': pron_unidades * precio_ref * 0.9 / 1e6,
    'revenue_+10%_£M': pron_unidades * precio_ref * 1.1 / 1e6,
}).round(2)
print(esc)

# %% Celda 21

AZUL, NARANJA, AQUA = '#2a78d6', '#eb6834', '#1baf7a'
TINTA, GRIS, FONDO, REJILLA = '#0b0b0b', '#52514e', '#fcfcfb', '#e1e0d9'

fig, ax = plt.subplots(figsize=(10, 4.8))
fig.patch.set_facecolor(FONDO); ax.set_facecolor(FONDO)

ax.plot(u_full.index, u_full / 1e3, color=AZUL, lw=2.2)
union = pd.concat([u_full.iloc[[-1]], pron_unidades])
ax.plot(union.index, union / 1e3, color=NARANJA, lw=2.2, ls='--')
ax.axvspan(pron_unidades.index[0], pron_unidades.index[-1], color=NARANJA, alpha=0.08)

# marca del salto de precio
f_precio = pd.Timestamp('2025-09-01')
ax.axvline(f_precio, color=GRIS, lw=1, ls=':')
ax.text(f_precio, 20, ' Sep 2025: precio por unidad\n ×2.1 (£98 → £209)', color=GRIS, fontsize=9, va='bottom')

# etiquetas directas
ax.text(pd.Timestamp('2026-03-01'), 352, 'Real', color=AZUL, fontsize=10, fontweight='bold', ha='center')
ax.text(pron_unidades.index[-1], pron_unidades.iloc[-1] / 1e3 + 12, 'Pronóstico (Holt)', color=NARANJA, fontsize=10, fontweight='bold', ha='right')

ax.set_ylabel('Miles de unidades al mes', color=GRIS)
ax.set_title('Tirzepatide en NHS England: unidades mensuales y pronóstico a 6 meses', color=TINTA, loc='left', fontsize=12)
ax.grid(axis='y', color=REJILLA, lw=0.8); ax.set_axisbelow(True)
for s in ['top', 'right']:
    ax.spines[s].set_visible(False)
ax.tick_params(colors=GRIS)
fig.savefig('p8_pronostico.png', dpi=200, bbox_inches='tight', facecolor=FONDO)
plt.show()

# %% Celda 22
fig, ax = plt.subplots(figsize=(8, 4.4))
fig.patch.set_facecolor(FONDO); ax.set_facecolor(FONDO)

ax.plot(val.index, val['Real'] / 1e3, color=TINTA, lw=2.6, marker='o')
ax.plot(val.index, val['Naive'] / 1e3, color=AQUA, lw=1.8, marker='o')
ax.plot(val.index, val['Lineal'] / 1e3, color=AZUL, lw=1.8, marker='o')
ax.plot(val.index, val['Holt'] / 1e3, color=NARANJA, lw=2.2, marker='o')

x_fin = val.index[-1] + pd.Timedelta(days=4)
for col, color in [('Real', TINTA), ('Naive', AQUA), ('Lineal', AZUL), ('Holt', NARANJA)]:
    ax.text(x_fin, val[col].iloc[-1] / 1e3, col, color=color, fontsize=10, fontweight='bold', va='center')

ax.set_xlim(val.index[0] - pd.Timedelta(days=5), val.index[-1] + pd.Timedelta(days=24))
ax.set_xticks(val.index); ax.set_xticklabels(['Jun 2026', 'Jul 2026', 'Ago 2026'])
ax.set_ylabel('Miles de unidades', color=GRIS)
ax.set_title('Validación con datos reales', color=TINTA, loc='left', fontsize=12)
ax.grid(axis='y', color=REJILLA, lw=0.8); ax.set_axisbelow(True)
for s in ['top', 'right']:
    ax.spines[s].set_visible(False)
ax.tick_params(colors=GRIS)
fig.savefig('p8_validacion.png', dpi=200, bbox_inches='tight', facecolor=FONDO)
plt.show()
