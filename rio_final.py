import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

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
# DETECCIÓN DE MODELO (MEJORADA)
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
# RETROALIMENTACIÓN AUTOMÁTICA
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
# GUARDAR DATOS
# --------------------------
if "datos" not in st.session_state:
    st.session_state["datos"] = []

if st.button("Guardar respuesta"):
    
    modelo = detectar_modelo(respuesta)
    comentario = feedback(modelo)
    
    st.session_state["datos"].append({
        "fecha": datetime.now(),
        "estudiante": nombre,
        "pH": pH,
        "nutrientes": nutrientes,
        "lluvia": lluvia,
        "tratamiento": tratamiento,
        "oxigeno": oxigeno,
        "metales": metales,
        "salud": salud,
        "modelo": modelo,
        "respuesta": respuesta
    })
    
    st.success(f"Modelo detectado: {modelo}")
    st.info(f"Retroalimentación: {comentario}")

# --------------------------
# TABLERO DOCENTE
# --------------------------
st.subheader("👨‍🏫 Tablero docente")

if st.session_state["datos"]:
    
    df = pd.DataFrame(st.session_state["datos"])
    
    st.dataframe(df)
    
    # ----------------------
    # DISTRIBUCIÓN MODELOS
    # ----------------------
    st.subheader("📊 Distribución de modelos")
    
    plt.figure()
    df["modelo"].value_counts().plot(kind="bar")
    st.pyplot(plt)
    
    # ----------------------
    # EVOLUCIÓN INDIVIDUAL
    # ----------------------
    st.subheader("📈 Evolución por estudiante")
    
    estudiante_sel = st.selectbox("Seleccionar estudiante", df["estudiante"].unique())
    
    df_est = df[df["estudiante"] == estudiante_sel]
    
    plt.figure()
    plt.plot(df_est["salud"], marker='o')
    plt.title("Evolución del sistema (según decisiones)")
    st.pyplot(plt)
    
    # ----------------------
    # COMPARACIÓN GLOBAL
    # ----------------------
    st.subheader("🔁 Relación nutrientes vs oxígeno")
    
    plt.figure()
    plt.scatter(df["nutrientes"], df["oxigeno"])
    plt.xlabel("Nutrientes")
    plt.ylabel("Oxígeno")
    st.pyplot(plt)
    
    # ----------------------
    # EXPORTAR
    # ----------------------
    st.download_button(
        "📥 Descargar resultados",
        df.to_csv(index=False),
        file_name="datos_clase.csv"
    )
