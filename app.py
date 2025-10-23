import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import plotly.express as px
import sqlite3
import openpyxl

# Configuración
st.set_page_config(page_title="Biofertilizantes AI", page_icon="leaf")
st.title("Sistema de Recomendación de Biofertilizantes con IA")
st.markdown("### Para Pymes Agroindustriales Sostenibles")

# Conexión SQLite
conn = sqlite3.connect('bio_db.sqlite')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS bio_data
             (id INTEGER PRIMARY KEY, empresa TEXT, ph REAL, nitrogeno REAL, fosforo REAL, potasio REAL, clima TEXT, emisiones REAL, bio_recomendado TEXT, impacto TEXT)''')
conn.commit()

# Cargar datos de entrenamiento (ficticios por ahora)
data = {
    'ph': [6.5, 7.0, 5.5, 6.8, 7.2, 6.0],
    'nitrogeno': [80, 70, 90, 65, 75, 85],
    'fosforo': [60, 50, 70, 55, 65, 75],
    'potasio': [90, 80, 95, 85, 88, 92],
    'clima': ['seco', 'templado', 'seco', 'humedo', 'templado', 'seco'],
    'emisiones': [150, 200, 100, 120, 180, 140],
    'bio_recomendado': ['Lixiviado de lombriz', 'Fermento bokashi', 'Lixiviado de lombriz', 'Compost tea', 'Fermento bokashi', 'Lixiviado de lombriz']
}
df_train = pd.DataFrame(data)

# Entrenar modelo
X = df_train[['ph', 'nitrogeno', 'fosforo', 'potasio']]
y = df_train['emisiones']
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Formulario
st.header("Ingresar Datos del Suelo")
with st.form("bio_form"):
    empresa = st.text_input("Nombre de la Pyme")
    ph = st.slider("pH del suelo", 3.0, 9.0, 6.5)
    nitrogeno = st.slider("Nitrógeno (%)", 0, 100, 70)
    fosforo = st.slider("Fósforo (%)", 0, 100, 60)
    potasio = st.slider("Potasio (%)", 0, 100, 85)
    clima = st.selectbox("Clima predominante", ['seco', 'templado', 'humedo'])
    submitted = st.form_submit_button("Recomendar Biofertilizante")

if submitted:
    # Predecir impacto
    input_data = [[ph, nitrogeno, fosforo, potasio]]
    emisiones_pred = model.predict(input_data)[0]
    
    # Recomendación simple
    if ph < 6.0 and nitrogeno < 60:
        bio = "Lixiviado de lombriz"
        impacto = f"Reducirá emisiones en ~{int(150 - emisiones_pred)} ton/año"
    elif clima == 'humedo':
        bio = "Compost tea"
        impacto = "Mejora retención de agua y reduce fertilizantes químicos"
    else:
        bio = "Fermento bokashi"
        impacto = "Acelera descomposición y regenera suelo en 30 días"
    
    st.success(f"**Recomendación**: {bio}")
    st.info(f"**Impacto estimado**: {impacto}")
    
    # Guardar en DB
    c.execute("INSERT INTO bio_data (empresa, ph, nitrogeno, fosforo, potasio, clima, emisiones, bio_recomendado, impacto) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (empresa, ph, nitrogeno, fosforo, potasio, clima, emisiones_pred, bio, impacto))
    conn.commit()

# Dashboard
st.header("Dashboard de Recomendaciones")
df = pd.read_sql("SELECT empresa, bio_recomendado, impacto FROM bio_data", conn)
if not df.empty:
    fig = px.bar(df, x='empresa', y='impacto', color='bio_recomendado', title="Impacto por Pyme")
    st.plotly_chart(fig)
else:
    st.info("Ingresa datos para ver el dashboard")

# Exportar
if st.button("Exportar a Excel"):
    df_export = pd.read_sql("SELECT * FROM bio_data", conn)
    df_export.to_excel("reporte_biofertilizantes.xlsx", index=False)
    st.success("Exportado como reporte_biofertilizantes.xlsx")

conn.close()