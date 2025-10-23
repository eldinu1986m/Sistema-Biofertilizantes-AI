# Sistema de Recomendación de Biofertilizantes con IA

**App web que recomienda el biofertilizante óptimo para Pymes agroindustriales**  
Reduce emisiones CO₂ y regenera suelos con IA.

---

## Tecnologías
- **Python** | **Streamlit** | **Scikit-learn** | **Plotly** | **SQLite**

---

## Funcionalidades
- Ingreso de datos de suelo (pH, N, P, K, clima)
- Modelo ML predice emisiones actuales
- Recomendación personalizada (3 opciones)
- Dashboard con gráficos
- Exportar a Excel

---

## Capturas

### Formulario + Recomendación
![Formulario](capturas/Formulario%20llenar%20+%20recomendaci%C3%B3n.png)

### Dashboard
![Dashboard](capturas/Dashboard%20con%20barras%20y%20tabla.png)

---

## Instalación

```bash
git clone https://github.com/eldinu1986m/Sistema-Biofertilizantes-AI
cd Sistema-Biofertilizantes-AI
conda create -n bio_ai python=3.11
conda activate bio_ai
conda install streamlit pandas scikit-learn plotly openpyxl pyarrow -c conda-forge
streamlit run app.py
