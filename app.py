import streamlit as st
import datetime
import pandas as pd
import io
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
from unidecode import unidecode
from supabase import create_client, Client

# --- DISEÑO Y ARQUITECTURA ORIGINAL ---
st.set_page_config(page_title="TLTC M-13", page_icon="🏉", layout="centered")

# CSS Original (Mantenido)
st.markdown("""
    <style>
    .stApp { backgroundColor: #1E1E1E; color: white; }
    h1, h2, h3 { color: #F4C430 !important; font-family: 'Arial', sans-serif; text-align: center; }
    .menu-card { background-color: #2B3E75; border: 2px solid #F4C430; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 15px; }
    .stButton>button { background-color: #2B3E75 !important; color: white !important; border: 2px solid #F4C430 !important; border-radius: 10px; width: 100%; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# CONEXIÓN SUPABASE
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# ESTADO INICIAL (Original)
if 'plantel' not in st.session_state:
    nombres = ["ARGAÑARAZ BAUTISTA", "BANEGAS MAXIMO", "BELLIDO IVO", "BERTINI ANTONIO", "BERTINI DIEGO", "BUENO RISCO LISANDRO", "CANO PAOLETTI SALVADOR", "CARRASCO IGNACIO", "CISNEROS POSSE MAXIMO", "CORONEL BLAS", "CORONEL STEFANO", "CORROTO RODRIGO", "CRIPOVICH JUAN IGNACIO", "CRUZADO BAUTISTA", "DEL TOSO BENJAMÍN", "FERNANDEZ CORREA JUAN MARTIN", "FERNANDEZ FELIPE IGNACIO", "GARCIA COLLADOS MAXIMO", "GIBILISCO MATEO", "GIJON BENJAMIN", "GUARDIA GERONIMO", "HERRERA BENJAMIN", "INGARAMO BAUTISTA", "JUAREZ COLLADO LUCAS", "LIZARRAGA PALACIOS BAUTISTA", "LOBO HERRERA VICENTE", "MAIZEL FACUNDO", "MARIGLIANO LORENZO", "MARQUESTO MARTIN", "MEJAIL FRANCISCO", "MOLINA FRANCISCO", "MOROF MAXIMILANO", "NELLA CASTRO ANTONIO", "NORES PONDAL LORENZO", "ORTIZ FELIPE", "PALAVECINO JOAQUIN", "PEIRO JUAN PABLO", "PEREZ FELIPE IGNACIO", "PEZZA ARQUEZ SOLANO", "PONCE DIAZ ELISEO", "PONCE MATEO", "RAIDEN RECUPERO BIEL", "RODRIGUEZ BELMONTE FRANCISCO", "RUIZ MENDILARZU MANUEL", "SALAZAR BENICIO", "SASSI BERNARDO", "SILVA SANTIAGO", "SOLBES FACUNDO", "SOSA LORENZO", "SOUBIE PEDRO", "TOMÁS FELIPE", "VALLE PADUA FELIPE", "VELAZQUEZ FELIPE", "VIOLETTO OCTAVIO", "VIOTTI JUAN MARTIN"]
    st.session_state.plantel = {str(i+1): {"nombre": n, "puesto": "Sin Puesto", "notas": ""} for i, n in enumerate(nombres)}

# NAVEGACIÓN Y ESTRUCTURA (Original)
if 'pantalla' not in st.session_state: st.session_state.pantalla = "Inicio"

if st.session_state.pantalla == "Inicio":
    st.title("TLTC M-13")
    if st.button("👥 Plantel"): st.session_state.pantalla = "Plantel"; st.rerun()
    if st.button("📋 Asistencia"): st.session_state.pantalla = "Asistencia"; st.rerun()
    if st.button("🏉 Partidos"): st.session_state.pantalla = "Partidos"; st.rerun()

elif st.session_state.pantalla == "Plantel":
    if st.button("⬅️ Volver"): st.session_state.pantalla = "Inicio"; st.rerun()
    st.header("Plantel")
    for id, datos in st.session_state.plantel.items():
        with st.expander(datos['nombre']):
            datos['puesto'] = st.selectbox("Puesto", ["Sin Puesto", "Pilar", "Hooker", "2° Linea", "3° Linea", "Medio scrum", "Apertura", "Centro", "Wing", "Fullback"], key=f"p_{id}")
            datos['notas'] = st.text_area("Notas", datos['notas'], key=f"n_{id}")
    if st.button("💾 Guardar"):
        for id, datos in st.session_state.plantel.items():
            supabase.table("datos_plantel").upsert({"jugador_id": id, "puesto": datos['puesto'], "notas": datos['notas']}).execute()
        st.success("Guardado")

# (Sección de Asistencia y Partidos con la lógica de upsert que es la única necesaria para que no falle)
elif st.session_state.pantalla == "Asistencia":
    if st.button("⬅️ Volver"): st.session_state.pantalla = "Inicio"; st.rerun()
    fecha = st.date_input("Fecha", datetime.date.today())
    fecha_str = fecha.strftime("%Y-%m-%d")
    for id, datos in st.session_state.plantel.items():
        st.checkbox(datos['nombre'], key=f"asist_{id}")
    if st.button("💾 Guardar Asistencia"):
        filas = [{"fecha": fecha_str, "jugador_id": id, "presente": st.session_state.get(f"asist_{id}", False)} for id in st.session_state.plantel.keys()]
        supabase.table("asistencias_entrenamiento").upsert(filas).execute()
        st.success("Guardado")
