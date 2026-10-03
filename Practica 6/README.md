# Práctica 6 — Clasificación (KNN)

## Objetivo
Construir modelos de clasificación (K-Nearest Neighbors) para predecir, a nivel consultorio, si un consultorio pertenece a una categoría de interés de negocio — primero por **valor actual** (alto revenue), después por **crecimiento** — y comparar qué tan bien variables estructurales explican cada una.

## Dataset base
Este análisis parte de `glp1_limpio.csv`, generado en la Práctica 1, agregado a nivel consultorio (`resumen_consultorio`).
```python
df_final = pd.read_csv("../Práctica 1/glp1_limpio.csv", parse_dates=['FECHA'])
```

---

## Modelo 1 — Alto Valor (por revenue total)

### Preparación
Se agregó el dataset a nivel `PRACTICE_CODE`, calculando por consultorio:

| Variable | Descripción |
|---|---|
| `revenue_total` | Suma de `ACTUAL_COST` — variable usada para definir la etiqueta, **excluida** de las variables predictoras. |
| `items_total` | Suma de `ITEMS` — **excluida** por fuga de datos (leakage): correlación de 0.978 con `revenue_total`, prácticamente la misma información expresada en otra unidad. |
| `meses_activo` | Número de meses con al menos una receta registrada. |
| `sustancias_distintas` | Número de sustancias GLP-1 distintas prescritas por el consultorio. |
| `costo_promedio_receta` | `revenue_total / items_total` — precio promedio por receta. |

**Etiqueta:** `alto_valor` = 1 si `revenue_total` está por encima de la mediana de todos los consultorios, 0 si está por debajo (split 50/50 por construcción).

### Multicolinealidad detectada
`meses_activo` y `sustancias_distintas` mostraron una correlación de 0.785 entre sí — un consultorio que lleva más tiempo activo tiende naturalmente a haber prescrito más sustancias distintas. Se decidió **conservar ambas** en el modelo principal (documentando la limitación) y probar su efecto por separado como variación (ver abajo).

### Metodología
```python
X = resumen_consultorio[['meses_activo', 'sustancias_distintas', 'costo_promedio_receta']]
y = resumen_consultorio['alto_valor']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # fit SOLO en train
X_test_scaled = scaler.transform(X_test)

knn = KNeighborsClassifier(n_neighbors=13)
knn.fit(X_train_scaled, y_train)
y_pred = knn.predict(X_test_scaled)
```

**Elección de k=13:** se usó un valor impar (evita empates en una clasificación binaria) dentro del rango convencional (√n aproximado), probado junto a valores vecinos sin mejora relevante en exactitud.

### Resultados

| Métrica | Valor |
|---|---|
| Exactitud (accuracy) | **0.748** |
| Precisión | 0.74 |
| Recall | 0.78 |

**Matriz de confusión:**

| | Predicho: Bajo valor | Predicho: Alto valor |
|---|---|---|
| **Real: Bajo valor** | 531 | 210 |
| **Real: Alto valor** | 175 | 609 |

**Interpretación:** el modelo identifica correctamente ~75% de los consultorios. El recall (0.78) es ligeramente más alto que la precisión (0.74) — el modelo es algo mejor detectando consultorios de alto valor cuando realmente lo son, que evitando falsos positivos (210 consultorios de bajo valor clasificados erróneamente como alto valor). Dado que el objetivo de negocio prioriza no perder consultorios de alto valor de vista (falsos negativos más costosos que falsos positivos para asignación de recursos CRM), este balance favorece el caso de uso.

---

## Modelo 2 — Alto Crecimiento

### Metodología
Se comparó el revenue de cada consultorio en dos periodos (2021-2022 vs. 2024-2025), excluyendo consultorios que no estuvieron activos en ambos periodos (para no confundir "aparición reciente" con "crecimiento").

**Etiqueta:** `alto_crecimiento` = 1 si el % de cambio en revenue entre periodos está por encima de la mediana, 0 si está por debajo.

Mismas variables predictoras y mismo procedimiento (train/test split, escalado fit-on-train, KNN) que el Modelo 1.

### Resultados

| Métrica | Valor |
|---|---|
| Exactitud (accuracy) | **0.620** |
| Precisión | 0.63 |
| Recall | 0.59 |

**Matriz de confusión:**

| | Predicho: Bajo crecimiento | Predicho: Alto crecimiento |
|---|---|---|
| **Real: Bajo crecimiento** | 434 | 233 |
| **Real: Alto crecimiento** | 271 | 391 |

---

## Comparación entre modelos

| | Modelo 1 (Alto Valor) | Modelo 2 (Alto Crecimiento) |
|---|---|---|
| Exactitud | 0.748 | 0.620 |
| Precisión | 0.74 | 0.63 |
| Recall | 0.78 | 0.59 |

**Hallazgo clave:** las mismas variables estructurales (meses activo, diversidad de sustancias, costo promedio por receta) predicen con considerablemente más fuerza **quién ya es grande** (0.748) que **quién está creciendo** (0.620, apenas por encima de 0.5 — el nivel de una moneda al aire). Esto sugiere que el tamaño actual de un consultorio es, en buena medida, una característica estructural y estable (tiempo en el mercado, variedad de producto), mientras que el crecimiento futuro depende de factores que este dataset no captura directamente — posiblemente cambios de médico/personal, decisiones de formulario local, o dinámicas de los pacientes mismos, no visibles a nivel de las columnas disponibles.

**Relevancia para la pregunta ancla:** este resultado matiza la pregunta original ("qué segmentos impulsan el crecimiento") — las variables usadas hasta ahora describen bien el valor *acumulado*, no el valor *en movimiento*. Queda como pendiente natural para la Práctica 7 (Clustering) explorar si existen perfiles de consultorio (combinaciones de variables, no una sola etiqueta binaria) que sí se asocien consistentemente con alto crecimiento.

---

## Variación — efecto de la multicolinealidad (Modelo 1)

Se volvió a entrenar el Modelo 1 removiendo una a la vez las dos variables correlacionadas (`meses_activo` y `sustancias_distintas`, correlación 0.785) para medir su aporte individual real al modelo:

| Variables usadas | Exactitud |
|---|---|
| Las 3 variables (completo) | **0.748** |
| Sin `meses_activo` | 0.721 |
| Sin `sustancias_distintas` | 0.702 |

**Interpretación:** ambas variables aportan información útil al modelo — quitar cualquiera de las dos reduce la exactitud, no la mantiene igual. `sustancias_distintas` aporta algo más que `meses_activo` (quitarla cuesta más exactitud: -0.046 vs. -0.027). Esto indica que, a pesar de estar correlacionadas entre sí, no son completamente redundantes: cada una captura una parte distinta de qué hace a un consultorio de alto valor, por lo que conservar ambas en el modelo principal fue la decisión correcta.

