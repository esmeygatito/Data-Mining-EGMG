# %% Celda 1
##KNN --> Clasificación de Datos

# %% Celda 2
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

df_final = pd.read_csv("../Práctica 1/glp1_limpio.csv", parse_dates=['FECHA'])
df_final['ANIO'] = df_final['FECHA'].dt.year

# %% Celda 3
resumen_consultorio = df_final.groupby('PRACTICE_CODE').agg(
    revenue_total=('ACTUAL_COST', 'sum'),
    items_total=('ITEMS', 'sum'),
    meses_activo=('FECHA', 'nunique'),
    sustancias_distintas=('SUSTANCIA', 'nunique'),
    region=('REGIONAL_OFFICE_NAME', 'first')
).reset_index()

print(resumen_consultorio.shape)
print(resumen_consultorio.head())

# %% Celda 4
print(resumen_consultorio['revenue_total'].describe())

# %% Celda 5
mediana_revenue = resumen_consultorio['revenue_total'].median()

resumen_consultorio['ALTO_VALOR'] = (resumen_consultorio['revenue_total'] > mediana_revenue).astype(int)

print(resumen_consultorio['ALTO_VALOR'].value_counts())

# %% Celda 6
print(resumen_consultorio[['revenue_total', 'items_total']].corr())

# %% Celda 7
print(resumen_consultorio[['revenue_total', 'meses_activo', 'sustancias_distintas']].corr())

# %% Celda 8
dummies_region = pd.get_dummies(resumen_consultorio['region'], prefix='REGION')
print(dummies_region.head())

# %% Celda 9
resumen_consultorio = pd.concat([resumen_consultorio, dummies_region], axis=1)

columnas_predictoras = ['meses_activo', 'sustancias_distintas'] + list(dummies_region.columns)
X = resumen_consultorio[columnas_predictoras]
y = resumen_consultorio['ALTO_VALOR']

print(X.shape, y.shape)

# %% Celda 10
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(X_train.shape, X_test.shape)

# %% Celda 11
from sklearn.preprocessing import StandardScaler

escalador = StandardScaler()
X_train_escalado = escalador.fit_transform(X_train)
X_test_escalado = escalador.transform(X_test)

# %% Celda 12
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

modelo = KNeighborsClassifier(n_neighbors=5)
modelo.fit(X_train_escalado, y_train)

predicciones = modelo.predict(X_test_escalado)
exactitud = accuracy_score(y_test, predicciones)
print(f'Exactitud con k=5: {exactitud:.3f}')

# %% Celda 13
valores_k = range(1, 21)
exactitudes = []

for k in valores_k:
    modelo_k = KNeighborsClassifier(n_neighbors=k)
    modelo_k.fit(X_train_escalado, y_train)
    pred_k = modelo_k.predict(X_test_escalado)
    exactitudes.append(accuracy_score(y_test, pred_k))

for k, ex in zip(valores_k, exactitudes):
    print(f'k={k}: exactitud={ex:.3f}')

# %% Celda 14
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

modelo_final = KNeighborsClassifier(n_neighbors=13)
modelo_final.fit(X_train_escalado, y_train)
predicciones_final = modelo_final.predict(X_test_escalado)

matriz = confusion_matrix(y_test, predicciones_final)
print(matriz)

disp = ConfusionMatrixDisplay(confusion_matrix=matriz, display_labels=['Bajo valor', 'Alto valor'])
disp.plot(cmap='Blues')
plt.title('Matriz de confusión — KNN (k=13)')
plt.show()

# %% Celda 15
from sklearn.metrics import classification_report

print(classification_report(y_test, predicciones_final, target_names=['Bajo valor', 'Alto valor']))

# %% Celda 16
revenue_temprano = df_final[df_final['FECHA'].dt.year.isin([2021, 2022])].groupby('PRACTICE_CODE')['ACTUAL_COST'].sum()
revenue_tardio = df_final[df_final['FECHA'].dt.year.isin([2024, 2025])].groupby('PRACTICE_CODE')['ACTUAL_COST'].sum()

print(len(revenue_temprano), len(revenue_tardio))

# %% Celda 17
crecimiento_consultorio = pd.DataFrame({
    'revenue_temprano': revenue_temprano,
    'revenue_tardio': revenue_tardio
}).dropna()

crecimiento_consultorio['crecimiento'] = crecimiento_consultorio['revenue_tardio'] - crecimiento_consultorio['revenue_temprano']

print(crecimiento_consultorio.shape)
print(crecimiento_consultorio['crecimiento'].describe())

# %% Celda 18
mediana_crecimiento = crecimiento_consultorio['crecimiento'].median()
crecimiento_consultorio['ALTO_CRECIMIENTO'] = (crecimiento_consultorio['crecimiento'] > mediana_crecimiento).astype(int)

print(crecimiento_consultorio['ALTO_CRECIMIENTO'].value_counts())

# %% Celda 19
crecimiento_consultorio = crecimiento_consultorio.reset_index().rename(columns={'index': 'PRACTICE_CODE'})

datos_crecimiento = crecimiento_consultorio.merge(
    resumen_consultorio[['PRACTICE_CODE', 'meses_activo', 'sustancias_distintas'] + list(dummies_region.columns)],
    on='PRACTICE_CODE'
)

print(datos_crecimiento.shape)

# %% Celda 20
columnas_predictoras_crec = ['meses_activo', 'sustancias_distintas'] + list(dummies_region.columns)
X_crec = datos_crecimiento[columnas_predictoras_crec]
y_crec = datos_crecimiento['ALTO_CRECIMIENTO']

X_train_crec, X_test_crec, y_train_crec, y_test_crec = train_test_split(X_crec, y_crec, test_size=0.2, random_state=42)
print(X_train_crec.shape, X_test_crec.shape)

# %% Celda 21
escalador_crec = StandardScaler()
X_train_crec_escalado = escalador_crec.fit_transform(X_train_crec)
X_test_crec_escalado = escalador_crec.transform(X_test_crec)

# %% Celda 22
exactitudes_crec = []

for k in valores_k:
    modelo_k = KNeighborsClassifier(n_neighbors=k)
    modelo_k.fit(X_train_crec_escalado, y_train_crec)
    pred_k = modelo_k.predict(X_test_crec_escalado)
    exactitudes_crec.append(accuracy_score(y_test_crec, pred_k))

for k, ex in zip(valores_k, exactitudes_crec):
    print(f'k={k}: exactitud={ex:.3f}')

# %% Celda 23
modelo_final_crec = KNeighborsClassifier(n_neighbors=13)
modelo_final_crec.fit(X_train_crec_escalado, y_train_crec)
predicciones_final_crec = modelo_final_crec.predict(X_test_crec_escalado)

matriz_crec = confusion_matrix(y_test_crec, predicciones_final_crec)
print(matriz_crec)

disp_crec = ConfusionMatrixDisplay(confusion_matrix=matriz_crec, display_labels=['Bajo crecimiento', 'Alto crecimiento'])
disp_crec.plot(cmap='Greens')
plt.title('Matriz de confusión — KNN crecimiento (k=13)')
plt.show()

print(classification_report(y_test_crec, predicciones_final_crec, target_names=['Bajo crecimiento', 'Alto crecimiento']))

# %% Celda 24
columnas_sin_meses = ['sustancias_distintas'] + list(dummies_region.columns)
columnas_sin_sustancias = ['meses_activo'] + list(dummies_region.columns)

for nombre, columnas in [('Sin meses_activo', columnas_sin_meses), ('Sin sustancias_distintas', columnas_sin_sustancias)]:
    X_var = resumen_consultorio[columnas]
    X_train_var, X_test_var, y_train_var, y_test_var = train_test_split(X_var, y, test_size=0.2, random_state=42)
    
    escalador_var = StandardScaler()
    X_train_var_esc = escalador_var.fit_transform(X_train_var)
    X_test_var_esc = escalador_var.transform(X_test_var)
    
    modelo_var = KNeighborsClassifier(n_neighbors=13)
    modelo_var.fit(X_train_var_esc, y_train_var)
    pred_var = modelo_var.predict(X_test_var_esc)
    
    print(f'{nombre}: exactitud={accuracy_score(y_test_var, pred_var):.3f}')
