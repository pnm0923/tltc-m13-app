import streamlit as st
import datetime
import pandas as pd

# CONFIGURACIÓN DE LA PÁGINA (Colores y Estilo TLTC)
st.set_page_config(page_title="TLTC M-13", page_icon="🏉", layout="centered")

# Inyección de CSS para forzar la paleta Azul y Oro sobre fondo oscuro
st.markdown("""
    <style>
    .stApp { backgroundColor: #1E1E1E; color: white; }
    h1, h2, h3 { color: #F4C430 !important; font-family: 'Arial Black', sans-serif; }
    .stButton>button { 
        background-color: #2B3E75 !important; color: white !important; 
        border: 2px solid #F4C430 !important; border-radius: 10px; width: 100%;
    }
    .stButton>button:hover { background-color: #F4C430 !important; color: #2B3E75 !important; }
    div[data-testid="stExpander"] { background-color: #2A2A2A !important; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# 2. BASE DE DATOS SEMILLA (Los 55 chicos de la M-13)
if 'plantel' not in st.session_state:
    nombres_crudos = [
        "ARGAÑARAZ BAUTISTA", "BANEGAS MAXIMO", "BELLIDO IVO", "BERTINI ANTONIO", "BERTINI DIEGO",
        "BUENO RISCO LISANDRO", "CANO PAOLETTI SALVADOR", "CARRASCO IGNACIO", "CISNEROS POSSE MAXIMO",
        "CORONEL BLAS", "CORONEL STEFANO", "CORROTO RODRIGO", "CRIPOVICH JUAN IGNACIO", "CRUZADO BAUTISTA",
        "DEL TOSO BENJAMÍN", "FERNANDEZ CORREA JUAN MARTIN", "FERNANDEZ FELIPE IGNACIO", "GARCIA COLLADOS MAXIMO",
        "GIBILISCO MATEO", "GIJON BENJAMIN", "GUARDIA GERONIMO", "HERRERA BENJAMIN", "INGARAMO BAUTISTA",
        "JUAREZ COLLADO LUCAS", "LIZARRAGA PALACIOS BAUTISTA", "LOBO HERRERA VICENTE", "MAIZEL FACUNDO",
        "MARIGLIANO LORENZO", "MARQUESTO MARTIN", "MEJAIL FRANCISCO", "MOLINA FRANCISCO", "MOROF MAXIMILANO",
        "NELLA CASTRO ANTONIO", "NORES PONDAL LORENZO", "ORTIZ FELIPE", "PALAVECINO JOAQUIN", "PEIRO JUAN PABLO",
        "PEREZ FELIPE IGNACIO", "PEZZA ARQUEZ SOLANO", "PONCE DIAZ ELISEO", "PONCE MATEO", "RAIDEN RECUPERO BIEL",
        "RODRIGUEZ BELMONTE FRANCISCO", "RUIZ MENDILARZU MANUEL", "SALAZAR BENICIO", "SASSI BERNARDO",
        "SILVA SANTIAGO", "SOLBES FACUNDO", "SOSA LORENZO", "SOUBIE PEDRO", "TOMÁS FELIPE", "VALLE PADUA FELIPE",
        "VELAZQUEZ FELIPE", "VIOLETTO OCTAVIO", "VIOTTI JUAN MARTIN"
    ]
    
    # Estructuramos el plantel en un diccionario dinámico
    st.session_state.plantel = {
        str(i+1): {
            "apellido": nombre.split()[0],
            "nombre": " ".join(nombre.split()[1:]),
            "nacimiento": datetime.date(2013, 1, 1),
            "foto": None,
            "notas_tecnicas": "Sin observaciones técnicas.",
            "notas_actitud": "Buena predisposición en el club."
        } for i, nombre in enumerate(nombres_crudos)
    }

if 'asistencias' not in st.session_state:
    st.session_state.asistencias = {}

# 3. INTERFAZ PRINCIPAL
st.title("🏉 TLTC M-13")
st.subheader("Panel de Control del Entrenador")

menu = st.sidebar.radio("Navegación", ["Asistencia Entrenamiento", "Plantel Actual", "Estadísticas Rápidas"])

# --- MÓDULO 1: ASISTENCIA A ENTRENAMIENTO ---
if menu == "Asistencia Entrenamiento":
    st.header("📋 Registro de Asistencia")
    
    fecha = st.date_input("Fecha del Entrenamiento", datetime.date.today())
    fecha_str = fecha.strftime("%Y-%m-%d")
    
    # Inicializar fecha si no existe
    if fecha_str not in st.session_state.asistencias:
        st.session_state.asistencias[fecha_str] = {id_: False for id_ in st.session_state.plantel.keys()}
    
    # Acciones en masa para el Xiaomi
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("✔️ Todos Presentes"):
            st.session_state.asistencias[fecha_str] = {id_: True for id_ in st.session_state.plantel.keys()}
    with col_btn2:
        if st.button("❌ Reiniciar Lista"):
            st.session_state.asistencias[fecha_str] = {id_: False for id_ in st.session_state.plantel.keys()}
            
    # Buscador rápido
    buscar = st.text_input("🔍 Buscar jugador para asistencia...")
    
    st.write("---")
    presentes_cont = 0
    
    # Listado con Checkboxes
    for id_, datos in st.session_state.plantel.items():
        nombre_completo = f"{datos['apellido']} {datos['nombre']}"
        if buscar.lower() in nombre_completo.lower():
            # Checkbox interactivo
            estado_actual = st.session_state.asistencias[fecha_str].get(id_, False)
            check = st.checkbox(nombre_completo, value=estado_actual, key=f"asist_{id_}_{fecha_str}")
            st.session_state.asistencias[fecha_str][id_] = check
            if check:
                presentes_cont += 1
                
    st.sidebar.metric("Chicos en Cancha", f"{presentes_cont} / 55")
    if st.button("💾 GUARDAR ENTRENAMIENTO"):
        st.success(f"¡Asistencia del {fecha_str} guardada con éxito!")

# --- MÓDULO 2: PLANTEL ACTUAL Y FICHAS ---
elif menu == "Plantel Actual":
    st.header("👥 Plantel Completo M-13")
    
    buscar_p = st.text_input("🔍 Buscar en el plantel...")
    
    for id_, datos in st.session_state.plantel.items():
        nombre_completo = f"{datos['apellido']}, {datos['nombre']}"
        if buscar_p.lower() in nombre_completo.lower():
            with st.expander(f"🏃‍♂️ {nombre_completo}"):
                st.write(f"**Categoría:** 2013 (M-13)")
                
                # Carga de Foto de Perfil usando la cámara del Xiaomi
                foto_archivo = st.file_uploader(f"Foto de Perfil ({datos['apellido']})", type=["jpg", "png", "jpeg"], key=f"foto_{id_}")
                if foto_archivo:
                    st.session_state.plantel[id_]["foto"] = foto_archivo
                    st.image(foto_archivo, width=120)
                elif datos["foto"]:
                    st.image(datos["foto"], width=120)
                
                # Edición de Notas de Coaching en vivo
                st.session_state.plantel[id_]["notas_actitud"] = st.text_area("🌟 Notas Actitudinales / Valores:", datos["notas_actitud"], key=f"act_{id_}")
                st.session_state.plantel[id_]["notas_tecnicas"] = st.text_area("🏉 Notas Técnicas (Pases/Tackles):", datos["notas_tecnicas"], key=f"tec_{id_}")

# --- MÓDULO 3: ESTADÍSTICAS RÁPIDAS ---
elif menu == "Estadísticas Rápidas":
    st.header("📊 Resumen de Rendimiento")
    st.write("Evolución del porcentaje de asistencia del plantel.")
    
    if st.session_state.asistencias:
        fechas = list(st.session_state.asistencias.keys())
        porcentajes = []
        for f in fechas:
            total_ps = sum(st.session_state.asistencias[f].values())
            porcentajes.append((total_ps / 55) * 180) # Escala visual
            
        chart_data = pd.DataFrame({"Asistencia Total (%)": [min(100, int((sum(st.session_state.asistencias[f].values())/55)*100)) for f in fechas]}, index=fechas)
        st.line_chart(chart_data)
    else:
        st.info("Aún no hay datos cargados para generar estadísticas. Registrá asistencia en algún entrenamiento.")