# Práctica 9 — Análisis de Texto
# Conversión del notebook practica9.ipynb a script.
# Ejecutar desde la carpeta "Práctica 9": python practica_9.py

import matplotlib
matplotlib.use("Agg")

# ===== Análisis de Texto =====

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df_final = pd.read_csv("../Práctica 1/glp1_limpio.csv", parse_dates=['FECHA'])

print(df_final['PRESENTACION'].value_counts().head(20))

# ===== Primera palabra y filas vs recetas =====

# 1) Primera palabra de cada presentación
df_final['PRIMERA_PALABRA'] = df_final['PRESENTACION'].str.split().str[0]

print(df_final['PRIMERA_PALABRA'].nunique())
print(df_final['PRIMERA_PALABRA'].value_counts())

# 2) Filas vs recetas
comparacion = df_final.groupby('PRIMERA_PALABRA').agg(
    filas=('PRESENTACION', 'count'),
    recetas=('ITEMS', 'sum')
)
comparacion['rank_filas'] = comparacion['filas'].rank(ascending=False)
comparacion['rank_recetas'] = comparacion['recetas'].rank(ascending=False)
comparacion['recetas_por_fila'] = comparacion['recetas'] / comparacion['filas']
print(comparacion.sort_values('recetas', ascending=False))

# ===== Variables de texto: ES_COMERCIAL, FORMA, DOSIS =====

import numpy as np

# 1) ¿es nombre comercial?
df_final['ES_COMERCIAL'] = df_final['PRIMERA_PALABRA'] != df_final['SUSTANCIA']

# 2) forma: tableta o inyección
df_final['FORMA'] = np.where(df_final['PRESENTACION'].str.contains('tablets', case=False), 'Tableta', 'Inyección')   # pista: palabra que aparece en las tabletas

# 3) dosis (el número que va justo antes de la unidad)
df_final['DOSIS'] = df_final['PRESENTACION'].str.extract(r'(\d+\.?\d*)mg', expand=False).astype(float)

# revisiones
print(df_final['ES_COMERCIAL'].value_counts())
print(df_final['FORMA'].value_counts())
print("sin dosis:", df_final['DOSIS'].isna().sum())
print(df_final[df_final['DOSIS'].isna()]['PRESENTACION'].unique()[:10])

# ===== Mezcla de dosis de Tirzepatide =====

tirz = df_final[df_final['SUSTANCIA'] == 'Tirzepatide'].copy()

mezcla = tirz.groupby(['FECHA', 'DOSIS'])['ITEMS'].sum().unstack(fill_value=0)
mezcla_pct = mezcla.div(mezcla.sum(axis=1), axis=0) * 100

print(sorted(tirz['DOSIS'].dropna().unique()))
print("filas Tirzepatide sin dosis:", tirz['DOSIS'].isna().sum())
print(mezcla_pct.round(1).tail(6))

# ===== Gráfica de mezcla de dosis (periodo completo) =====
# Nota: esta versión se sobrescribe más abajo con la versión desde marzo de 2024.

import matplotlib.pyplot as plt

print(mezcla_pct.round(1).head(6))
colores = ['#86b6ef', '#5598e7', '#2a78d6', '#1c5cab', '#184f95', '#0d366b']   # de dosis baja (claro) a alta (oscuro)

fig, ax = plt.subplots(figsize=(10, 5))
ax.stackplot(mezcla_pct.index,
             [mezcla_pct[d] for d in mezcla_pct.columns],
             labels=[f"{d:g} mg" for d in mezcla_pct.columns],
             colors=colores)
ax.set_ylim(0, 100)
ax.set_ylabel('Porcentaje')
ax.set_title('Distribución de Dosis de Tirzepatide')
ax.legend(title='Dosis', loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)
fig.savefig('p9_mezcla_dosis.png', dpi=200, bbox_inches='tight')
plt.close(fig)

# ===== Volumen mensual de Tirzepatide =====

print(mezcla.sum(axis=1).head(12))
print(mezcla.sum(axis=1).tail(3))

# ===== Mezcla de dosis desde marzo de 2024 (porcentaje) =====

mezcla_pct2 = mezcla_pct.loc['2024-03':]

fig, ax = plt.subplots(figsize=(10, 5))
ax.stackplot(mezcla_pct2.index,
             [mezcla_pct2[d] for d in mezcla_pct2.columns],
             labels=[f"{d:g} mg" for d in mezcla_pct2.columns],
             colors=colores)
ax.set_ylim(0, 100)
ax.set_ylabel('Porcentaje de recetas')
ax.set_title('Distribución de dosis de Tirzepatide')
ax.legend(title='Dosis', loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)
fig.savefig('p9_mezcla_dosis.png', dpi=200, bbox_inches='tight')
plt.close(fig)

# ===== Mezcla de dosis desde marzo de 2024 (volumen) =====

mezcla2 = mezcla.loc['2024-03':]

fig, ax = plt.subplots(figsize=(10, 5))
ax.stackplot(mezcla2.index,
             [mezcla2[d] for d in mezcla2.columns],
             labels=[f"{d:g} mg" for d in mezcla2.columns],
             colors=colores)
#ax.set_ylim(0, 100)
ax.set_ylabel('Recetas al mes')
ax.set_title('Recetas mensuales de Tirzepatide por dosis')
ax.legend(title='Dosis', loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)
fig.savefig('p9_mezcla_dosis_volumen.png', dpi=200, bbox_inches='tight')
plt.close(fig)

# ===== Nube de palabras por recetas =====
# Requiere: pip install wordcloud
# Nota: esta versión se sobrescribe más abajo con la nube coloreada por sustancia.

from wordcloud import WordCloud

frecuencias = df_final.groupby('PRIMERA_PALABRA')['ITEMS'].sum().to_dict()

nube = WordCloud(width=1000, height=500, background_color='white', colormap='Blues').generate_from_frequencies(frecuencias)

plt.figure(figsize=(10, 5))
plt.imshow(nube, interpolation='bilinear')
plt.axis('off')
plt.title('Productos GLP-1 por recetas')
plt.savefig('p9_nube_recetas.png', dpi=200, bbox_inches='tight')
plt.close()

# ===== Recetas por sustancia =====

print(df_final.groupby('SUSTANCIA')['ITEMS'].sum().sort_values(ascending=False))

# ===== Nube de palabras coloreada por sustancia =====

import matplotlib.colors as mcolors
from matplotlib.patches import Patch

# si no la tienes en este notebook, defínela como en la Práctica 3
sustancias_orden = ['Semaglutide', 'Liraglutide', 'Dulaglutide', 'Exenatide', 'Lixisenatide', 'Tirzepatide']
color_sustancia = dict(zip(sustancias_orden, plt.cm.tab10.colors))

# a qué sustancia pertenece cada primera palabra
mapa_sustancia = df_final.drop_duplicates('PRIMERA_PALABRA').set_index('PRIMERA_PALABRA')['SUSTANCIA'].to_dict()

def color_por_sustancia(word, **kwargs):
    return mcolors.to_hex(color_sustancia[mapa_sustancia[word]])

nube = WordCloud(width=1000, height=500, background_color='white',
                 color_func=color_por_sustancia).generate_from_frequencies(frecuencias)   # pista: la función que acabas de definir

plt.figure(figsize=(10, 5))
plt.imshow(nube, interpolation='bilinear')
plt.axis('off')
plt.title('Trulicity, Mounjaro y Ozempic concentran las recetas de GLP-1')   # tu título
leyenda = [Patch(color=mcolors.to_hex(c), label=s) for s, c in color_sustancia.items()]
plt.legend(handles=leyenda, loc='center left', bbox_to_anchor=(1, 0.5), frameon=False, title='Sustancia')
plt.savefig('p9_nube_recetas.png', dpi=200, bbox_inches='tight')
plt.close()

# ===== Concentración de los tres productos más grandes =====

frecuencias_s = pd.Series(frecuencias).sort_values(ascending=False)
print(frecuencias_s.head(3).sum() / frecuencias_s.sum() * 100)

# ===== Nombre de marca contra nombre de molécula =====

marca = df_final.groupby(['SUSTANCIA', 'ES_COMERCIAL'])['ITEMS'].sum().unstack(fill_value=0)   # pista: función que suma
marca_pct = marca.div(marca.sum(axis=1), axis=0) * 100                                         # pista: total por sustancia
print(marca_pct.round(1))

# ===== Primera aparición de cada producto =====

print(df_final.groupby('PRIMERA_PALABRA')['FECHA'].min().sort_values())
