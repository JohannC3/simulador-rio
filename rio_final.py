import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

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
col3.metric("Oxígeno", round(oxigeno, 2))
col4.metric("Metales", round(metales, 2))
col5.metric("Salud", round(salud, 2))

# --------------------------
# GRÁFICA
# --------------------------
st.subheader("📈 Visualización del sistema")

valores = [oxigeno, metales, salud]
etiquetas = ["Oxígeno", "Metales", "Salud"]

fig, ax = plt.subplots()
ax.bar(etiquetas, valores)
ax.set_ylabel("Nivel")
ax.set_title("Estado del sistema hídrico")

st.pyplot(fig)

# --------------------------
# RESPUESTA
# --------------------------
st.subheader("✍️ Explicación del estudiante")
respuesta = st.text_area("Explica qué está pasando en el sistema")

# --------------------------
# DETECCIÓN DE MODELO
# --------------------------
def detectar_modelo(texto: str) -> str:
    texto = (texto or "").lower()

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
def feedback(modelo: str) -> str:
    if modelo == "Lineal":
        return "Intenta incluir más de una relación entre variables."
    elif modelo == "Multicausal":
        return "Vas bien, ahora conecta esas variables entre sí."
    elif modelo == "Sistémico":
        return "Buen modelo. Intenta identificar límites o incertidumbres."
    else:
        return "Desarrolla más tu explicación."

# --------------------------
# GOOGLE SHEETS (VERSIÓN FINAL)
# --------------------------
def guardar_en_sheets(datos) -> bool:
    try:
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        creds_dict = st.secrets["gcp"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)

        sheet = client.open_by_key("1BI5S_nlcL6k1gO30XUjCIrSdyUPm1RG6A-XEfoUtaQA").sheet1

        # 🔥 ENCABEZADOS
        headers = [
            "Fecha",
            "Nombre",
            "pH",
            "Nutrientes",
            "Lluvia",
            "Tratamiento",
            "Oxígeno",
            "Metales",
            "Salud",
            "Modelo",
            "Respuesta"
        ]

        # 🔥 SOLO CREA ENCABEZADOS SI LA HOJA ESTÁ VACÍA
        if sheet.row_count == 0 or not sheet.get_all_values():
            sheet.append_row(headers)

        # 🔥 AGREGA LOS DATOS
        sheet.append_row(datos)

        return True

    except Exception as e:
        st.error(f"Error al guardar en Sheets: {e}")
        return False

# --------------------------
# BOTÓN GUARDAR
# --------------------------
if st.button("Guardar respuesta") and not st.session_state["guardado"]:

    if not nombre or not respuesta.strip():
        st.warning("⚠️ Debes ingresar tu nombre y una explicación.")
    else:
        modelo = detectar_modelo(respuesta)
        comentario = feedback(modelo)

        exito = guardar_en_sheets([
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

        if exito:
            st.session_state["guardado"] = True
            st.success(f"✅ Guardado en la nube - Modelo: {modelo}")
            st.info(f"💡 Retroalimentación: {comentario}")

# --------------------------
# BOTÓN NUEVA RESPUESTA
# --------------------------
if st.button("Nueva respuesta"):
    st.session_state["guardado"] = False
