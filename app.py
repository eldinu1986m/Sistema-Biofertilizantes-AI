import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import plotly.express as px
import sqlite3

# Configuración
st.set_page_config(page_title="Biofertilizantes AI", page_icon="leaf")
st.title("Sistema de Recomendación de Biofertilizantes con IA")
st.markdown("### Para Pymes Agroindustriales Sostenibles")

# Conexión SQLite
conn = sqlite3.connect('bio_db.sqlite')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS bio_data
             (id INTEGER PRIMARY KEY, empresa TEXT, ph REAL, nitrogeno REAL, fosforo REAL, 
              potasio REAL, clima TEXT, emisiones REAL, bio_recomendado TEXT, impacto TEXT)''')
conn.commit()

# Datos de entrenamiento
data = {
    'ph': [6.5, 7.0, 5.5, 6.8, 7.2, 6.0, 5.8, 7.5, 6.2, 6.9],
    'nitrogeno': [80, 70, 90, 65, 75, 85, 55, 88, 72, 68],
    'fosforo': [60, 50, 70, 55, 65, 75, 48, 82, 61, 58],
    'potasio': [90, 80, 95, 85, 88, 92, 78, 96, 89, 84],
    'clima': ['seco', 'templado', 'seco', 'humedo', 'templado', 'seco', 'humedo', 'seco', 'templado', 'humedo'],
    'emisiones': [150, 200, 100, 120, 180, 140, 160, 110, 175, 130],
}
df_train = pd.DataFrame(data)

# Modelo
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
    # Predecir emisiones actuales
    input_data = [[ph, nitrogeno, fosforo, potasio]]
    emisiones_actual = model.predict(input_data)[0]
    
    # REGLAS EN ORDEN CORRECTO (clima primero)
    if clima == 'humedo':
        bio = "Compost tea"
        reduccion_pct = 0.30
        beneficio = "Mejora retención de agua y reduce fertilizantes químicos"
    elif ph < 6.0 and nitrogeno < 60:
        bio = "Lixiviado de lombriz"
        reduccion_pct = 0.35
        beneficio = "Regenera suelos ácidos y mejora absorción de nutrientes"
    else:
        bio = "Fermento bokashi"
        reduccion_pct = 0.25
        beneficio = "Acelera descomposición y regenera suelo en 30 días"
    
    # Calcular reducción (siempre positivo)
    ahorro = abs(emisiones_actual * reduccion_pct)
    emisiones_futuras = emisiones_actual - ahorro
    
    st.success(f"**Recomendación**: {bio}")
    st.success(f"**Reducción estimada**: {ahorro:.1f} ton CO₂/año")
    st.info(f"Emisiones actuales: {emisiones_actual:.1f} ton → Futuras: {emisiones_futuras:.1f} ton")
    st.info(f"**Beneficio adicional**: {beneficio}")
    
    # Guardar
    c.execute("""INSERT INTO bio_data 
                 (empresa, ph, nitrogeno, fosforo, potasio, clima, emisiones, bio_recomendado, impacto) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (empresa, ph, nitrogeno, fosforo, potasio, clima, emisiones_actual, bio, f"{ahorro:.1f}"))
    conn.commit()

# Dashboard
st.header("Dashboard de Recomendaciones")
df = pd.read_sql("SELECT empresa, bio_recomendado, impacto FROM bio_data", conn)
if not df.empty:
    fig = px.bar(df, 
                 x='empresa', 
                 y='impacto', 
                 color='bio_recomendado', 
                 title="Reducción de CO₂ por Pyme",
                 labels={'impacto': 'Reducción (ton/año)', 'empresa': 'Pyme'})
    st.plotly_chart(fig)
    st.write("### Historial de Recomendaciones")
    st.dataframe(df)
else:
    st.info("Ingresa datos para ver el dashboard")

# Exportar
if st.button("Exportar a Excel"):
    df_export = pd.read_sql("SELECT * FROM bio_data", conn)
    df_export.to_excel("reporte_biofertilizantes.xlsx", index=False)
    st.success("Exportado como reporte_biofertilizantes.xlsx")

conn.close()