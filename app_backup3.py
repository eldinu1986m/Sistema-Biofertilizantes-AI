import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import plotly.express as px
import matplotlib.pyplot as plt
import openpyxl
import sqlite3

# Configuración de la página
st.set_page_config(page_title="Analizador de ESG", page_icon="🌱")
st.title("Analizador de ESG para Pymes Agroindustriales")

# Conexión a SQLite
conn = sqlite3.connect('db.sqlite')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS esg_data
             (empresa TEXT, emisiones_co2 REAL, uso_agua REAL, uso_fertilizantes REAL, impacto_social REAL, score_esg_actual REAL, score_predicho REAL)''')
conn.commit()

# Cargar datos desde SQLite
df = pd.read_sql_query("SELECT * FROM esg_data", conn)

# Si la tabla está vacía, inicializar DataFrame
if df.empty:
    df = pd.DataFrame(columns=['empresa', 'emisiones_co2', 'uso_agua', 'uso_fertilizantes', 'impacto_social', 'score_esg_actual', 'score_predicho'])

# Convertir columnas numéricas a tipo float
numeric_columns = ['emisiones_co2', 'uso_agua', 'uso_fertilizantes', 'impacto_social', 'score_esg_actual', 'score_predicho']
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Formulario
st.header("Ingresar Datos de la Pyme")
with st.form("esg_form"):
    empresa = st.text_input("Nombre de la Pyme")
    emisiones_co2 = st.number_input("Emisiones CO2 (toneladas)", min_value=0.0, step=0.01)
    uso_agua = st.number_input("Uso de agua (litros)", min_value=0.0, step=0.01)
    uso_fertilizantes = st.number_input("Uso de fertilizantes (kg)", min_value=0.0, step=0.01)
    impacto_social = st.number_input("Impacto social (puntaje 0-100)", min_value=0.0, max_value=100.0, step=0.01)
    score_esg_actual = st.number_input("Score ESG actual (0-100)", min_value=0.0, max_value=100.0, step=0.01)
    submitted = st.form_submit_button("Analizar y Predecir")

# Procesar datos
if submitted:
    if df.shape[0] >= 4:  # Necesitamos al menos 4 registros para entrenar
        X = df[['emisiones_co2', 'uso_agua', 'uso_fertilizantes', 'impacto_social']].dropna()
        y = df['score_esg_actual'].dropna()
        if len(X) >= 4 and len(y) >= 4:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            model = LinearRegression()
            model.fit(X_train, y_train)
            new_data = pd.DataFrame([[emisiones_co2, uso_agua, uso_fertilizantes, impacto_social]],
                                    columns=['emisiones_co2', 'uso_agua', 'uso_fertilizantes', 'impacto_social'])
            score_predicho = model.predict(new_data)[0]
            score_predicho = max(0, min(100, score_predicho))  # Limitar entre 0 y 100
            st.write(f"**Score ESG predicho con mejoras: {score_predicho:.2f}**")
            
            # Sugerencias
            if score_predicho < 60:
                st.write("Sugerencia: Implementa biofertilizantes para reducir emisiones.")
            elif score_predicho < 80:
                st.write("Sugerencia: Optimiza el uso de agua con sistemas de riego eficiente.")
            else:
                st.write("Sugerencia: Mantén las prácticas actuales y explora certificaciones ESG.")
            
            # Guardar en SQLite
            c.execute("INSERT INTO esg_data (empresa, emisiones_co2, uso_agua, uso_fertilizantes, impacto_social, score_esg_actual, score_predicho) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (empresa, emisiones_co2, uso_agua, uso_fertilizantes, impacto_social, score_esg_actual, score_predicho))
            conn.commit()
            
            # Actualizar DataFrame
            df = pd.read_sql_query("SELECT * FROM esg_data", conn)
            df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
        else:
            st.write("Se necesitan al menos 4 registros completos en la base de datos para entrenar el modelo.")
    else:
        st.write("Se necesitan al menos 4 registros en la base de datos para entrenar el modelo. Ingresa más datos.")

# Dashboard
st.header("Dashboard ESG")
df = df.dropna(subset=['score_esg_actual', 'score_predicho'])  # Eliminar filas con NaN en estas columnas
if not df.empty:
    fig = px.bar(df, x='empresa', y=['score_esg_actual', 'score_predicho'], barmode='group')
    st.plotly_chart(fig)
else:
    st.write("No hay datos suficientes para mostrar el dashboard. Ingresa más datos.")

# Gráfico de emisiones
st.header("Gráfico de Emisiones")
if not df.empty:
    fig, ax = plt.subplots()
    ax.plot(df['empresa'], df['emisiones_co2'], marker='o')
    ax.set_xlabel("Empresa")
    ax.set_ylabel("Emisiones CO2 (toneladas)")
    ax.set_title("Emisiones de CO2 por Empresa")
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.write("No hay datos suficientes para mostrar el gráfico de emisiones. Ingresa más datos.")

# Exportar a Excel
if st.button("Exportar a Excel"):
    c.execute("SELECT * FROM esg_data")
    data = c.fetchall()
    df_export = pd.DataFrame(data, columns=['empresa', 'emisiones_co2', 'uso_agua', 'uso_fertilizantes', 'impacto_social', 'score_esg_actual', 'score_predicho'])
    df_export.to_excel('reporte_esg.xlsx', index=False)
    st.write("Datos exportados a reporte_esg.xlsx")

conn.close()