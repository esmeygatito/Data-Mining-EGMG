# %% Celda 1
import requests
import pandas as pd
from datetime import date
from urllib.parse import quote_plus
import time

# %% Celda 2
##FUENTE : https://opendata.nhsbsa.net/dataset/english-prescribing-dataset-epd-with-snomed-code/resource/004d6f4e-9881-4312-82dc-094f9a543885

# %% Celda 3
BASE_URL = "https://opendata.nhsbsa.net/api/3/action/datastore_search_sql?"
sustancias = ["Semaglutide", "Liraglutide", "Dulaglutide", "Exenatide", "Lixisenatide", "Tirzepatide"] #sustancias a buscar


# %% Celda 4
#ver el contenido de la API para ver los nombres de los recursos    
package_url = "https://opendata.nhsbsa.net/api/3/action/package_show?id=english-prescribing-dataset-epd-with-snomed-code"
resp = requests.get(package_url)
resp.raise_for_status()
data = resp.json()

for resource in data['result']['resources']:
    print(resource['name'])

# %% Celda 5
print(data.get('result')) #revisar que el recurso que queremos está en la lista de recursos

# %% Celda 6
fechas = pd.date_range(start='2021-01-01', end=pd.Timestamp.today(), freq='MS')
print(fechas) #fechas en que se va a buscar la información

# %% Celda 7
meses = [f.strftime('%Y%m') for f in fechas] #formato de fechas para buscar en la API

# %% Celda 8
def extraer_records(j): #función para extraer los registros de la respuesta de la API
    nivel1 = j.get('result', {})
    if 'records' in nivel1:
        return nivel1['records']
    else:
        nivel2 = nivel1.get('result', {})
        return nivel2.get('records', [])

# %% Celda 9
resultados = [] #primer ciclo para recorrer los meses y el segundo para recorrer las sustancias y lograr extraer la información de la API

for mes in meses:
    for sustancia in sustancias:
        resource_id = f"EPD_SNOMED_{mes}"
        sql = f"""SELECT * FROM `{resource_id}` where CHEMICAL_SUBSTANCE_BNF_DESCR = '{sustancia}'"""

        try:
            r = requests.get(
                BASE_URL,
                params={
                    'resource_id': resource_id,
                    'sql': sql
                },
                timeout=60
            )
            print('HTTP status:', r.status_code)
            j = r.json()
            records = extraer_records(j)
            print('Registros devueltos:', len(records))
            time.sleep(0.3)
            if records:
                df = pd.DataFrame(records)
                resultados.append(df)   
            else:
                print('Error:', j.get('error'))
        except Exception as e:
            print('Error en la petición:', e)

# %% Celda 10
print(len(resultados)) #verificar que se hayan extraído los datos de todos los meses y sustancias  (no necesariamente todos los meses tienen datos para todas las sustancias)

# %% Celda 11
combinaciones_totales = len(meses) * len(sustancias) #noto que me faltan combinaciones de meses y sustancias, por lo que calculo el total de combinaciones posibles y las comparo con los resultados obtenidos
print(f"Total posible: {combinaciones_totales}, con datos: {len(resultados)}, sin datos: {combinaciones_totales - len(resultados)}")

# %% Celda 12
resultados = [] #ciclo para recorrer por segunda vez los meses y sustancias, pero ahora guardando un log de lo que se va haciendo y si hubo error o no
log = [] 

for mes in meses:
    for sustancia in sustancias:
        resource_id = f"EPD_SNOMED_{mes}"
        sql = f"""SELECT * FROM `{resource_id}` where CHEMICAL_SUBSTANCE_BNF_DESCR = '{sustancia}'"""
        
        entrada = {'mes': mes, 'sustancia': sustancia}  
        
        try:
            r = requests.get(BASE_URL, params={'resource_id': resource_id, 'sql': sql}, timeout=60)
            j = r.json()
            
            if r.status_code == 200 and 'error' not in j:         
                records = extraer_records(j)
                if records:
                    df = pd.DataFrame(records)
                    resultados.append(df)
                    entrada['status'] = 'ok'
                    entrada['filas'] = len(records)
                else:
                    entrada['status'] = 'zero'         # cero real, confirmado sin error
            else:
                entrada['status'] = 'error'                
                entrada['detalle'] = j.get('error')
        except Exception as e:
            entrada['status'] = 'error'
            entrada['detalle'] = str(e)
        
        log.append(entrada)
        print(mes, sustancia, entrada['status'])
        time.sleep(0.3)

# %% Celda 13
mes = "202303"  # uno de los meses que salió "zero"
sustancia = "Semaglutide"
resource_id = f"EPD_SNOMED_{mes}"
sql = f"""SELECT * FROM `{resource_id}` where CHEMICAL_SUBSTANCE_BNF_DESCR = '{sustancia}' LIMIT 100"""

r = requests.get(BASE_URL, params={'resource_id': resource_id, 'sql': sql}, timeout=60)
j =r.json()
print('HTTP status:', r.status_code)
print('Registros devueltos:', len(extraer_records(j)))
#prueba porque no me trae registros, aunque en la API sí hay registros para ese mes y sustancia.    



# %% Celda 14
mes = "202503"
sustancia = "Semaglutide"
resource_id = f"EPD_SNOMED_{mes}"
sql = f"""SELECT * FROM `{resource_id}` where CHEMICAL_SUBSTANCE_BNF_DESCR = '{sustancia}' LIMIT 5"""
r = requests.get(BASE_URL, params={'resource_id': resource_id, 'sql': sql}, timeout=60)
j =r.json()
print('HTTP status:', r.status_code)
print('Registros devueltos:', len(extraer_records(j)))
#era demasiada información, por lo que le puse un límite de 5 registros y ahora sí me trae registros.

# %% Celda 15
def columna_sustancia(mes):
    if mes >= "202503":  
        return "BNF_CHEMICAL_SUBSTANCE"
    else:
        return "CHEMICAL_SUBSTANCE_BNF_DESCR"

   #noté que la columna que contiene la sustancia cambia a partir de marzo 2025, por lo que hice una función para determinar qué columna usar según el mes. 

# %% Celda 16
#aquí hago un ciclo para reintentar los errores que se registraron en el log, usando la función columna_sustancia() para determinar qué columna usar según el mes.
errores = [e for e in log if e['status'] == 'error']
print(f"Total a reintentar: {len(errores)}")

for entrada in errores:
    mes = entrada['mes']
    sustancia = entrada['sustancia']                          
    resource_id = f"EPD_SNOMED_{mes}"
    columna = columna_sustancia(mes)                             
    
    sql = f"""SELECT * FROM `{resource_id}` where {columna} = '{sustancia}'"""
    
    try:
        r = requests.get(BASE_URL, params={'resource_id': resource_id, 'sql': sql}, timeout=60)
        j = r.json()
        
        if r.status_code == 200 and 'error' not in j:
            records = extraer_records(j)
            if records:
                df = pd.DataFrame(records)
                resultados.append(df)
                entrada['status'] = 'ok'          # actualizamos el log, ya no es error
                entrada['filas'] = len(records)
            else:
                entrada['status'] = 'zero'
        else:
            entrada['detalle'] = j.get('error')   # seguirá en 'error' si vuelve a fallar
    except Exception as e:
        entrada['detalle'] = str(e)
    
    print(mes, sustancia, entrada['status'])
    time.sleep(0.3)

# %% Celda 17
# [e for e in log if e['mes'] == '202606' and e['sustancia'] == 'Semaglutide']  # [solo notebook]
print([e for e in log if e['mes'] == '202606' and e['sustancia'] == 'Semaglutide'])
#noto que alguno no están porque es informacion muy reciente y la API no tiene información de ese mes, por lo que no hay registros para esa combinación de mes y sustancia.

# %% Celda 18
#hago una función para traer los registros de manera paginada, ya que la API tiene un límite de 1000 registros por consulta y algunas combinaciones de mes y sustancia tienen más de 1000 registros.
def traer_paginado(resource_id, columna, sustancia, tamano_pagina=1000):
    todas = []
    offset = 0
    while True:
        sql = f"""SELECT * FROM `{resource_id}` where {columna} = '{sustancia}' LIMIT {tamano_pagina} OFFSET {offset}"""
        r = requests.get(BASE_URL, params={'resource_id': resource_id, 'sql': sql}, timeout=60)
        j = r.json()
        records = extraer_records(j)
        
        if not records:
            break                       # ya no hay más páginas
        
        todas.extend(records)
        
        if len(records) < tamano_pagina:
            break                       
        
        offset += tamano_pagina                    
        time.sleep(0.3)
    
    return todas

# %% Celda 19
errores_restantes = [e for e in log if e['status'] == 'error']
for e in errores_restantes:
    print(e['mes'], e['sustancia'], e.get('detalle'))
    #estos son todos los que siguen con error, ya que la API no tiene información de ese mes y sustancia, por lo que no hay registros para esa combinación.

# %% Celda 20
#extraigo los registros de las combinaciones que salieron como "zero" en el log, usando la función traer_paginado() para traer todos los registros de manera paginada.
zeros = [e for e in log if e['status'] == 'zero']
print(f"Total a revisar: {len(zeros)}")

for entrada in zeros:
    mes = entrada['mes']
    sustancia = entrada['sustancia']                                
    resource_id = f"EPD_SNOMED_{mes}"
    columna = columna_sustancia(mes)                                 

    records = traer_paginado(resource_id, columna, sustancia)

    if records:
        df = pd.DataFrame(records)
        resultados.append(df)
        entrada['status'] = 'ok'
        entrada['filas'] = len(records)
        print(mes, sustancia, '-> recuperado:', len(records))
    else:
        print(mes, sustancia, '-> cero confirmado')

# %% Celda 21
print(len(resultados)) #ya tengo todos los registros de todas las combinaciones de mes y sustancia, ya que ya no hay errores ni combinaciones con cero registros.

# %% Celda 22
df_final = pd.concat(resultados, ignore_index=True)

# %% Celda 23
df_final.to_csv("glp1_crudo.csv", index=False) #lo guardo en un archivo CSV para poder trabajar con él después sin tener que volver a hacer todas las consultas a la API.

# %% Celda 24
print(df_final.shape) #son aproximadamente 1.5 millones de registros, por lo que es un archivo grande, pero manejable en memoria.   

# %% Celda 25
print(df_final.iloc[0]['BNF_CHEMICAL_SUBSTANCE'])      # una fila de los primeros meses
print(df_final.iloc[-1]['BNF_CHEMICAL_SUBSTANCE'])      # una fila de los últimos meses
#DETECTANDO LOS ASPECTOS EN QUE HAY QUE HACER LIMPIEZA DE DATOS, YA QUE HAY REGISTROS QUE NO SON RELEVANTES PARA EL ANÁLISIS, COMO LOS QUE TIENEN CERO PRESCRIPCIONES O CERO COSTO.

# %% Celda 26
pd.DataFrame(log).to_csv("log_extraccion.csv", index=False)
#Guardo el log de la extracción en un archivo CSV para poder revisarlo después y ver qué combinaciones de mes y sustancia tuvieron errores o cero registros.

# %% Celda 27
# ##LIMPIEZA DE DATOS

# %% Celda 28
import pandas as pd

df_final = pd.read_csv("glp1_crudo.csv")
print(df_final.shape)



# %% Celda 29
print(df_final.iloc[0]['YEAR_MONTH'], type(df_final.iloc[0]['YEAR_MONTH']))
print(df_final.iloc[-1]['YEAR_MONTH'], type(df_final.iloc[-1]['YEAR_MONTH']))
#se oupa ajustar tipo de dato en la columna YEAR_MONTH, ya que es un string y debería ser un entero para poder hacer análisis de series de tiempo.

# %% Celda 30
year_month_texto = df_final['YEAR_MONTH'].astype(str)
year_month_limpio = year_month_texto.str.replace('-', '')  
df_final['FECHA'] = pd.to_datetime(year_month_limpio, format='%Y%m')

# %% Celda 31
print(df_final['FECHA'].min(), df_final['FECHA'].max())
print(df_final['FECHA'].isnull().sum())
#fecha arreglada, ya que ahora es un objeto datetime y se puede usar para análisis de series de tiempo.

# %% Celda 32
import numpy as np

corte = pd.Timestamp('2025-03-01')

df_final['SUSTANCIA'] = np.where(
    df_final['FECHA'] < corte,
    df_final['CHEMICAL_SUBSTANCE_BNF_DESCR'],
    df_final['BNF_CHEMICAL_SUBSTANCE']                           
)

#Hay un problema con la columna SUSTANCIA, ya que a partir de marzo 2025 la columna que contiene el nombre de la sustancia cambia de CHEMICAL_SUBSTANCE_BNF_DESCR a BNF_CHEMICAL_SUBSTANCE, por lo que hay que hacer un ajuste para que todas las filas tengan el nombre de la sustancia en la misma columna.

# %% Celda 33
print(df_final[df_final['FECHA'] < corte]['SUSTANCIA'].unique())
print(df_final[df_final['FECHA'] >= corte]['SUSTANCIA'].unique())
#olumna de sustancia ya arreglada, ya que ahora todas las filas tienen el nombre de la sustancia en la misma columna, independientemente de la fecha.

# %% Celda 34
df_final['PRESENTACION'] = np.where(
    df_final['FECHA'] < corte,
    df_final['BNF_DESCRIPTION'],    
    df_final['BNF_PRESENTATION_NAME']    
)
#la Columna de presentación también tiene el mismo problema que la columna de sustancia, por lo que se hace el mismo ajuste para que todas las filas tengan el nombre de la presentación en la misma columna.

# %% Celda 35
print(df_final[df_final['FECHA'] < corte]['PRESENTACION'].unique()[:5])
print(df_final[df_final['FECHA'] >= corte]['PRESENTACION'].unique()[:5])

# %% Celda 36
df_final['REGION_NAME'] = np.where(
    df_final['FECHA'] < corte,
    df_final['STP_NAME'],    
    df_final['ICB_NAME']    
)
#la columna de región también tiene el mismo problema que las columnas de sustancia y presentación, por lo que se hace el mismo ajuste para que todas las filas tengan el nombre de la región en la misma columna.

df_final['ADQ_USAGE'] = np.where(
    df_final['FECHA'] < corte,
    df_final['ADQUSAGE'],    
    df_final['ADQ_USAGE']    
)
#la columna de ADQ_USAGE también tiene el mismo problema que las columnas de sustancia, presentación y región, por lo que se hace el mismo ajuste para que todas las filas tengan el valor de ADQ_USAGE en la misma columna.


# %% Celda 37
print(df_final[df_final['FECHA'] < corte]['REGION_NAME'].unique()[:5])
print(df_final[df_final['FECHA'] >= corte]['REGION_NAME'].unique()[:5])

print(df_final['ADQ_USAGE'].describe())


# %% Celda 38
print(df_final['BNF_CHAPTER_PLUS_CODE'].unique())
#se va a eliminar porque no es relevante parab el análisis, ya que todos los registros son de GLP-1 y no hay variación en esta columna.

# %% Celda 39
columnas_a_eliminar = [
    'YEAR_MONTH', 'STP_NAME', 'STP_CODE', 'ICB_NAME', 'ICB_CODE',
    'CHEMICAL_SUBSTANCE_BNF_DESCR', 'BNF_CHEMICAL_SUBSTANCE', 'BNF_CHEMICAL_SUBSTANCE_CODE',
    'BNF_CODE', 'BNF_DESCRIPTION', 'BNF_PRESENTATION_CODE', 'BNF_PRESENTATION_NAME',
    'ADQUSAGE', 'BNF_CHAPTER_PLUS_CODE',
    'PCO_NAME', 'PCO_CODE', 'REGIONAL_OFFICE_CODE',
    'ADDRESS_1', 'ADDRESS_2', 'ADDRESS_3', 'ADDRESS_4', 'SNOMED_CODE'
]

df_final = df_final.drop(columns=columnas_a_eliminar)
#eliminar columnas que no son relevantes para el análisis


# %% Celda 40
print(df_final.columns.tolist())
print(df_final.shape)
#olumnas finales y forma del dataframe después de la limpieza de datos, ya que se eliminaron columnas que no son relevantes para el análisis.


# %% Celda 41
#Buscar valores raros en columnas
columnas_texto = ['REGIONAL_OFFICE_NAME', 'PRACTICE_NAME', 'PRACTICE_CODE', 
                   'POSTCODE', 'SUSTANCIA', 'PRESENTACION', 'REGION_NAME', 'UNIDENTIFIED']

for columna in columnas_texto:
    print(f"--- {columna} ---")
    print(df_final[columna].value_counts().head(10)) 
    print()

# %% Celda 42
mascara = df_final['PRACTICE_NAME'] == '-'
print(mascara.sum())

mascara = df_final['PRACTICE_CODE'] == '-'
print(mascara.sum())

mascara = df_final['POSTCODE'] == '-'
print(mascara.sum())


# %% Celda 43
mascara = df_final['PRACTICE_NAME'] == 'UNIDENTIFIED DOCTORS'
print(mascara.sum())

combinado = (df_final['PRACTICE_CODE'] == '-') & (df_final['REGIONAL_OFFICE_NAME'] == 'UNIDENTIFIED')
print(combinado.sum())

combinado2 = combinado & (df_final['UNIDENTIFIED'] == 'Y')
print(combinado2.sum())

# %% Celda 44
grupo_grande = df_final['PRACTICE_NAME'] == 'UNIDENTIFIED DOCTORS'
grupo_chico = (df_final['PRACTICE_CODE'] == '-') & (df_final['REGIONAL_OFFICE_NAME'] == 'UNIDENTIFIED')

print('Grande:', grupo_grande.sum())
print('Chico:', grupo_chico.sum())
print('Ambos a la vez:', (grupo_grande & grupo_chico).sum())
#Hay un grupo grande de registros que tienen PRACTICE_NAME = 'UNIDENTIFIED DOCTORS' y un grupo chico que tiene PRACTICE_CODE = '-' y REGIONAL_OFFICE_NAME = 'UNIDENTIFIED', pero no son los mismos registros, por lo que se van a eliminar.

# %% Celda 45
df_final = df_final[~grupo_grande]
#conservar solo los registros que no están en el grupo grande, ya que son los que tienen información relevante para el análisis.

# %% Celda 46
print(df_final.dtypes)
#los tipos de datos de las columnas son correctos, ya que las columnas numéricas son de tipo float64 y las columnas de texto son de tipo object.

# %% Celda 47
#revisar si hay duplicados
duplicados = df_final.duplicated()
print(duplicados.sum())

# %% Celda 48
filas_duplicadas = df_final[df_final.duplicated(keep=False)]
print(filas_duplicadas['SUSTANCIA'].value_counts())
#se van a eliminar los duplicados, ya que no son relevantes para el análisis y solo ocupan espacio en memoria.

# %% Celda 49
df_final = df_final.drop_duplicates()

# %% Celda 50
print(df_final.shape)
print(df_final.duplicated().sum())

# %% Celda 51
print(df_final.isnull().sum())
#nulos

# %% Celda 52
#sanidad en numericas
print(df_final[['QUANTITY', 'ITEMS', 'TOTAL_QUANTITY', 'NIC', 'ACTUAL_COST', 'ADQ_USAGE']].describe())

# %% Celda 53
df_final['REGION_NAME'] = df_final['REGION_NAME'].fillna('No disponible')
#nulos en REGION_NAME reemplazados por 'No disponible', ya que es una columna de texto y no se puede dejar con valores nulos para el análisis.

# %% Celda 54
df_final['POSTCODE'] = df_final['POSTCODE'].fillna('SIN_CP')
#NULOS en postcode reemplazados por 'SIN_CP', ya que es una columna de texto y no se puede dejar con valores nulos para el análisis.

# %% Celda 55
df_final.to_csv("glp1_limpio.csv", index=False)

# %% Celda 56
import os
print('Crudo:', os.path.getsize("glp1_crudo.csv") / (1024*1024), 'MB')
print('Limpio:', os.path.getsize("glp1_limpio.csv") / (1024*1024), 'MB')

# %% Celda 57
df_final.head(10000).to_csv("glp1_muestra.csv", index=False)
