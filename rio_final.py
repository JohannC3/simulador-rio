import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Sistema hídrico - análisis docente", layout="wide")

st.title("🌊 Simulación y análisis de modelos explicativos")

# --------------------------
# IDENTIFICACIÓN ESTUDIANTE
# --------------------------
st.sidebar.subheader("👤 Estudiante")
nombre = st.sidebar.text_input("Nombre o código")

# --------------------------
# VARIABLES DEL SISTEMA
# --------------------------
st.subheader("⚙️ Ajuste del sistema")

col1, col2 = st.columns(2)

with col1:
    pH = st.slider("pH", 4.0, 8.0, 7.0)
    nutrientes = st.slider("Nutrientes", 0, 20, 5)

with col2:
    lluvia = st.slider("Lluvia", 0, 10, 5)
    tratamiento = st.slider("Tratamiento (%)", 0, 100, 60)

# --------------------------
# MODELO DIDÁCTICO
# --------------------------
oxigeno = 8 - (nutrientes * 0.25) - (lluvia * 0.15)
metales = max(0, (7 - pH) * 2.5)
salud = 10 - abs(7 - pH)*1.5 - nutrientes*0.2 - metales*0.2

# --------------------------
# RESULTADOS
# --------------------------
st.subheader("📊 Estado del sistema")

col3, col4, col5 = st.columns(3)
col3.metric("Oxígeno", round(oxigeno,2))
col4.metric("Metales", round(metales,2))
col5.metric("Salud", round(salud,2))

# --------------------------
# RESPUESTA
# --------------------------
st.subheader("✍️ Explicación del estudiante")
respuesta = st.text_area("Explica qué está pasando en el sistema")

# --------------------------
# DETECCIÓN DE MODELO
# --------------------------
def detectar_modelo(texto):
    texto = texto.lower()
    
    conexiones = ["relación", "interacción", "depende", "afecta", "influye"]
    multiples = ["también", "además", "varios", "diferentes"]
    
    score = 0
    
    for palabra in conexiones:
        if palabra in texto:
            score += 2
            
    for palabra in multiples:
        if palabra in texto:
            score += 1
    
    if score >= 4:
        return "Sistémico"
    elif score >= 2:
        return "Multicausal"
    elif len(texto) > 10:
        return "Lineal"
    else:
        return "Muy básico"

# --------------------------
# FEEDBACK
# --------------------------
def feedback(modelo):
    if modelo == "Lineal":
        return "Intenta incluir más de una relación entre variables."
    elif modelo == "Multicausal":
        return "Vas bien, ahora conecta esas variables entre sí."
    elif modelo == "Sistémico":
        return "Buen modelo. Intenta identificar límites o incertidumbres."
    else:
        return "Desarrolla más tu explicación."

# --------------------------
# FUNCIÓN GOOGLE SHEETS
# --------------------------
def guardar_en_sheets(datos):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    
    sheet = client.open_by_key("1d6LMSQVbhRGa_v0bsA0T2cJ7OXM6AxG0ctDRMoff5Tw").sheet1
    
    sheet.append_row(datos)

# --------------------------
# GUARDAR
# --------------------------
if st.button("Guardar respuesta"):
    
    modelo = detectar_modelo(respuesta)
    comentario = feedback(modelo)
    
    # Guardar en Google Sheets
    guardar_en_sheets([
        str(datetime.now()),
        nombre,
        pH,
        nutrientes,
        lluvia,
        tratamiento,
        oxigeno,
        metales,
        salud,
        modelo,
        respuesta
    ])
    
    st.success(f"Guardado en la nube - Modelo: {modelo}")
    st.info(f"Retroalimentación: {comentario}")
