# -*- coding: utf-8 -*-
"""
@author: karinavallejos
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Ruta del archivo CSV
archivo_csv = 'C:/Users/kvallejos/Documents/SQL/Collahuasi_extended.csv'

# Cargar y limpiar datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv(archivo_csv, sep=';', encoding='ISO-8859-1')
    df = df.rename(columns=lambda x: x.strip())
    df = df.rename(columns={"Date / Time": "fecha"})
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df = df.dropna(subset=['fecha'])
    return df

# Crear base de datos SQLite
def crear_bd(df):
    conn = sqlite3.connect('collahuasi.db')
    df.to_sql('analisis', conn, if_exists='replace', index=False)
    conn.commit()
    return conn

# Consultar promedios mensuales desde la base de datos
def promedios_mensuales(conn):
    query = """
    SELECT strftime('%Y-%m', fecha) as mes,
           AVG(Throughput_L1) as Prom_Throughput_L1,
           AVG(Throughput_L2) as Prom_Throughput_L2,
           AVG(Ley_de_cabeza_CuT_L1) as Prom_Ley_Cu_L1,
           AVG(Ley_de_cabeza_CuT_L2) as Prom_Ley_Cu_L2
    FROM analisis
    GROUP BY mes
    """
    return pd.read_sql(query, conn)

# Consultar promedios anuales desde la base de datos
def promedios_anuales(conn):
    query = """
    SELECT strftime('%Y', fecha) as año,
           AVG(Throughput_L1) as Prom_Throughput_L1,
           AVG(Throughput_L2) as Prom_Throughput_L2,
           AVG(Ley_de_cabeza_CuT_L1) as Prom_Ley_Cu_L1,
           AVG(Ley_de_cabeza_CuT_L2) as Prom_Ley_Cu_L2
    FROM analisis
    GROUP BY año
    """
    return pd.read_sql(query, conn)

# App Streamlit
st.title("📊 Análisis de Laboratorio - Flotación Cobre (Collahuasi)")
df = cargar_datos()
conn = crear_bd(df)

# Navegación
opcion = st.sidebar.radio("Selecciona una opción:", 
                          ["Ver datos", "Promedios Mensuales", "Promedios Anuales", "Exportar CSV"])

# Opción 1: Ver datos
if opcion == "Ver datos":
    st.subheader("Vista general de los datos")
    st.dataframe(df.head(50))

# Opción 2: Promedios Mensuales
elif opcion == "Promedios Mensuales":
    st.subheader("Promedios mensuales")
    promedio_mensual = promedios_mensuales(conn)
    st.dataframe(promedio_mensual)

# Opción 3: Promedios Anuales
elif opcion == "Promedios Anuales":
    st.subheader("Promedios anuales")
    if 'año' not in df.columns:
        df['año'] = df['fecha'].dt.year
    columnas_numericas = df.select_dtypes(include='number').columns
    promedio_anual = df.groupby('año')[columnas_numericas].mean().reset_index()
    st.dataframe(promedio_anual)

# Opción 4: Exportar serie
elif opcion == "Exportar CSV":
    st.subheader("Exportar datos filtrados a CSV")
    fecha_inicio = st.date_input("Fecha de inicio")
    fecha_fin = st.date_input("Fecha de fin")

    if st.button("Exportar"):
        query_export = f"""
        SELECT *
        FROM analisis
        WHERE fecha >= '{fecha_inicio}' AND fecha <= '{fecha_fin}'
        """
        df_export = pd.read_sql(query_export, conn)
        df_export.to_csv("serie_exportada.csv", index=False)
        st.success("✅ Archivo 'serie_exportada.csv' guardado con éxito en el directorio actual.")

# Cerrar conexión al final
conn.close()
