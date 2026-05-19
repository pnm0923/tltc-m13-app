import streamlit as st
import datetime
import pandas as pd
import io
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
from unidecode import unidecode

# CONFIGURACIÓN DE LA PÁGINA (Estilo TLTC)
st.set_page_config(page_title="TLTC M-13", page_icon="🏉", layout="centered")

# Inyección de CSS para diseño responsivo en tu Xiaomi y Placa Estilo Pro
st.markdown("""
    <style>
    .stApp { backgroundColor: #1E1E1E; color: white; }
    h1, h2, h3 { color: #F4C430 !important; font-family: 'Arial', sans-serif; text-align: center; }
    
    /* Botones grandes de la pantalla principal */
    .menu-card {
        background-color: #2B3E75;
        border: 2px solid #F4C430;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 15px;
        cursor: pointer;
    }
    .menu-card h4 { margin: 0; color: white !important; font-size: 18px; }
    .menu-card p { margin: 5px 0 0 0; color: #CCCCCC; font-size: 13px; }
    
    /* Botones del sistema de Streamlit */
    .stButton>button { 
        background-color: #2B3E75 !important; color: white !important; 
        border: 2px solid #F4C430 !important; border-radius: 10px; width: 100%;
        font-weight: bold;
    }
    .stButton>button:hover { background-color: #F4C430 !important; color: #2B3E75 !important; }
    div[data-testid="stExpander"] { background-color: #2A2A2A !important; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# Lista de puestos oficiales solicitados
LISTA_PUESTOS = ["Sin Puesto", "Pilar", "Hooker", "2° Linea", "3° Linea", "Medio scrum", "Apertura", "Centro", "Wing", "Fullback"]

# 2. BASE DE DATOS SEMILLA (Los 55 chicos de la M-13)
if 'plantel' not in st.session_state:
    nombres_crudos = [
        "ARGAÑARAZ BAUTISTA", "BANEGAS MAXIMO", "BELLIDO IVO", "BERTINI ANTONIO", "BERTINI DIEGO",
        "BUENO RISCO LISANDRO", "CANO PAOLETTI SALVADOR", "CARRASCO IGNACIO", "CISNEROS POSSE MAXIMO",
        "CORONEL BLAS", "CORONEL STEFANO", "CORROTO RODRIGO", "CRIPOVICH JUAN IGNACIO", "CRUZADO BAUTISTA",
        "DEL TOSO BENJAMÍN", "FERNANDEZ CORREA JUAN MARTIN", "FERNANDEZ FELIPE IGNACIO", "GARCIA COLLADOS MAXIMO",
        "GIBILISCO MATEO", "GIJON BENJAMIN", "GUARDIA GERONIMO", HERRERA BENJAMIN", "INGARAMO BAUTISTA",
        "JUAREZ COLLADO LUCAS", "LIZARRAGA PALACIOS BAUTISTA", "LOBO HERRERA VICENTE", "MAIZEL FACUNDO",
        "MARIGLIANO LORENZO", "MARQUESTO MARTIN", "MEJAIL FRANCISCO", "MOLINA FRANCISCO", "MOROF MAXIMILANO",
        "NELLA CASTRO ANTONIO", "NORES PONDAL LORENZO", "ORTIZ FELIPE", "PALAVECINO JOAQUIN", "PEIRO JUAN PABLO",
        "PEREZ FELIPE IGNACIO", "PEZZA ARQUEZ SOLANO", "PONCE DIAZ ELISEO", "PONCE MATEO", "RAIDEN RECUPERO BIEL",
        "RODRIGUEZ BELMONTE FRANCISCO", "RUIZ MENDILARZU MANUEL", "SALAZAR BENICIO", "SASSI BERNARDO",
        "SILVA SANTIAGO", "SOLBES FACUNDO", "SOSA LORENZO", "SOUBIE PEDRO", "TOMÁS FELIPE", "VALLE PADUA FELIPE",
        "VELAZQUEZ FELIPE", "VIOLETTO OCTAVIO", "VIOTTI JUAN MARTIN"
    ]
    st.session_state.plantel = {
        str(i+1): {
            "apellido": nombre.split()[0],
            "nombre": " ".join(nombre.split()[1:]),
            "nacimiento": datetime.date(2013, 1, 1),
            "puesto": "Sin Puesto",
            "foto": None,
            "notas_tecnicas": "Sin observaciones técnicas.",
            "notas_actitud": "Buena predisposición en el club."
        } for i, nombre in enumerate(nombres_crudos)
    }

if 'asistencias' not in st.session_state:
    st.session_state.asistencias = {}

if 'partidos' not in st.session_state:
    st.session_state.partidos = {}

# Gestión de pantallas mediante Estado de Sesión
if 'pantalla_actual' not in st.session_state:
    st.session_state.pantalla_actual = "Inicio"

# --- PANTALLA PRINCIPAL (HOME) ---
if st.session_state.pantalla_actual == "Inicio":
    # Imagen del Escudo Local
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("escudo.png", use_container_width=True)
        except:
            st.markdown("<h3 style='text-align:center;'>🟨 TLTC M-13 🟦</h3>", unsafe_allow_html=True)
    
    st.title("TLTC M-13")
    st.write("Panel de Control del Entrenador")
    st.write("---")
    
    # Grid de opciones interactivas
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown('<div class="menu-card"><h4>👥 Plantel Actual</h4><p>Lista, puestos y fotos de perfil</p></div>', unsafe_allow_html=True)
        if st.button("Ir a Plantel", key="btn_plantel"):
            st.session_state.pantalla_actual = "Plantel"
            st.rerun()
            
        st.markdown('<div class="menu-card"><h4>📋 Asistencia Entr.</h4><p>Cargar fecha y presentes</p></div>', unsafe_allow_html=True)
        if st.button("Ir a Asistencia", key="btn_asistencia"):
            st.session_state.pantalla_actual = "Asistencia"
            st.rerun()

    with col_b:
        st.markdown('<div class="menu-card"><h4>🏉 Partidos y Placas</h4><p>Selección por Bloques y Placas</p></div>', unsafe_allow_html=True)
        if st.button("Ir a Partidos", key="btn_partidos"):
            st.session_state.pantalla_actual = "Partidos"
            st.rerun()
            
        st.markdown('<div class="menu-card"><h4>📊 Estadísticas</h4><p>Ver evolución del jugador</p></div>', unsafe_allow_html=True)
        if st.button("Ir a Estadísticas", key="btn_stats"):
            st.session_state.pantalla_actual = "Estadísticas"
            st.rerun()

# --- MÓDULO 1: ASISTENCIA A ENTRENAMIENTO ---
elif st.session_state.pantalla_actual == "Asistencia":
    # Botón de regreso directo en la interfaz central
    if st.button("⬅️ Volver al Menú Principal", key="back_asist"):
        st.session_state.pantalla_actual = "Inicio"
        st.rerun()
        
    st.header("📋 Asistencia a Entrenamiento")
    fecha = st.date_input("Fecha del Entrenamiento", datetime.date.today(), key="selector_fecha_entr")
    fecha_str = fecha.strftime("%Y-%m-%d")
    
    if fecha_str not in st.session_state.asistencias:
        st.session_state.asistencias[fecha_str] = {id_: False for id_ in st.session_state.plantel.keys()}

    for id_ in st.session_state.plantel.keys():
        clave_check = f"chk_asist_{id_}_{fecha_str}"
        st.session_state[clave_check] = st.session_state.asistencias[fecha_str][id_]

    # BOTONES DE ACCIÓN MASIVA
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("✔️ Todos Presentes", key="btn_todos_pres"):
            for id_ in st.session_state.plantel.keys():
                st.session_state.asistencias[fecha_str][id_] = True
            st.rerun()
            
    with col_btn2:
        if st.button("❌ Reiniciar (Todos Ausentes)", key="btn_todos_aus"):
            for id_ in st.session_state.plantel.keys():
                st.session_state.asistencias[fecha_str][id_] = False
            st.rerun()
            
    buscar = st.text_input("🔍 Buscar jugador en esta fecha...")
    st.write("---")
    
    presentes_cont = 0
    for id_, datos in st.session_state.plantel.items():
        nombre_completo = f"{datos['apellido']} {datos['nombre']}"
        if buscar.lower() in nombre_completo.lower():
            clave_check = f"chk_asist_{id_}_{fecha_str}"
            check = st.checkbox(nombre_completo, key=clave_check)
            
            if check != st.session_state.asistencias[fecha_str][id_]:
                st.session_state.asistencias[fecha_str][id_] = check
                st.rerun()
                
            if check: presentes_cont += 1
                
    st.write(f"### 🏃‍♂️ Presentes en esta fecha: {presentes_cont} / 55")
    st.write("---")
    if st.button("💾 GUARDAR ENTRENAMIENTO", key="btn_guardar_asist"):
        st.success(f"¡Asistencia del {fecha_str} guardada con éxito!")

# --- MÓDULO 2: PLANTEL ACTUAL Y FICHAS ---
elif st.session_state.pantalla_actual == "Plantel":
    if st.button("⬅️ Volver al Menú Principal", key="back_plantel"):
        st.session_state.pantalla_actual = "Inicio"
        st.rerun()
        
    st.header("👥 Plantel Completo M-13")
    buscar_p = st.text_input("🔍 Buscar en el plantel...")
    
    for id_, datos in st.session_state.plantel.items():
        nombre_completo = f"{datos['apellido']}, {datos['nombre']}"
        puesto_actual = datos.get("puesto", "Sin Puesto")
        
        if buscar_p.lower() in nombre_completo.lower():
            with st.expander(f"🏃‍♂️ {nombre_completo} | 🏷️ {puesto_actual}"):
                indice_puesto = LISTA_PUESTOS.index(puesto_actual) if puesto_actual in LISTA_PUESTOS else 0
                nuevo_puesto = st.selectbox(f"Asignar Puesto para {datos['nombre']}:", LISTA_PUESTOS, index=indice_puesto, key=f"puesto_{id_}")
                
                if nuevo_puesto != puesto_actual:
                    st.session_state.plantel[id_]["puesto"] = nuevo_puesto
                    st.rerun()
                
                foto_archivo = st.file_uploader(f"Foto de Perfil", type=["jpg", "png", "jpeg"], key=f"foto_{id_}")
                if foto_archivo:
                    st.session_state.plantel[id_]["foto"] = foto_archivo
                    st.image(foto_archivo, width=120)
                st.session_state.plantel[id_]["notas_actitud"] = st.text_area("🌟 Notas Actitudinales:", datos["notas_actitud"], key=f"act_{id_}")
                st.session_state.plantel[id_]["notas_tecnicas"] = st.text_area("🏉 Notas Técnicas (Pases/Tackles):", datos["notas_tecnicas"], key=f"tec_{id_}")

# --- MÓDULO 3: PARTIDOS Y CONVOCATORIAS ---
elif st.session_state.pantalla_actual == "Partidos":
    if st.button("⬅️ Volver al Menú Principal", key="back_partidos"):
        st.session_state.pantalla_actual = "Inicio"
        st.rerun()
        
    st.header("🏉 Carga de Partidos y Bloques")
    st.markdown("### 1. Datos del Encuentro")
    
    lista_rivales = ["Seleccionar rival...", "Tucumán Rugby", "Universitario", "Jockey Club", "Cardenales", "Natación y Gimnasia", "Los Tarcos", "Lince", "Huirapuca", "Aguará Guazú", "San Martín/Liceo/Corsarios"]
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        bloque_seleccionado = st.selectbox("Seleccionar Bloque del TLTC", ["Tucumán Lawn Tennis Azul", "Tucumán Lawn Tennis Amarillo"], key="sb_bloque")
    with col_p2:
        rival_seleccionado = st.selectbox("Rival de la Fecha", lista_rivales, key="sb_rival")
        
    fecha_partido = st.date_input("Fecha del Partido", datetime.date.today(), key="di_fecha_partido")
    fecha_p_str = fecha_partido.strftime("%Y-%m-%d")
    
    llave_partido = f"{fecha_p_str}_{'Azul' if 'Azul' in bloque_seleccionado else 'Amarillo'}"
    
    if llave_partido not in st.session_state.partidos:
        st.session_state.partidos[llave_partido] = {
            "rival": "", "bloque": bloque_seleccionado,
            "convocados": {id_: False for id_ in st.session_state.plantel.keys()}
        }
    
    if rival_seleccionado != "Seleccionar rival...":
        st.session_state.partidos[llave_partido]["rival"] = rival_seleccionado

    for id_ in st.session_state.plantel.keys():
        clave_check_p = f"chk_partido_{id_}_{llave_partido}"
        st.session_state[clave_check_p] = st.session_state.partidos[llave_partido]["convocados"].get(id_, False)

    st.write("---")
    
    tab_carga, tab_placa = st.tabs(["📝 Cargar Convocados", "🖼️ Ver Placa de Matchday"])
    
    with tab_carga:
        if st.button("❌ Limpiar Convocatoria de este Bloque", key="btn_limpiar_partido"):
            for id_ in st.session_state.plantel.keys():
                st.session_state.partidos[llave_partido]["convocados"][id_] = False
            st.rerun()

        buscar_p = st.text_input("🔍 Buscar jugador para convocar...")
        st.write("---")
        
        convocados_cont = 0
        for id_, datos in st.session_state.plantel.items():
            nombre_completo = f"{datos['apellido']} {datos['nombre']} ({datos['puesto']})"
            
            if buscar_p.lower() in nombre_completo.lower():
                clave_check_p = f"chk_partido_{id_}_{llave_partido}"
                check_p = st.checkbox(nombre_completo, value=st.session_state.partidos[llave_partido]["convocados"].get(id_, False), key=f"chk_p_visual_{id_}_{llave_partido}")
                
                if check_p != st.session_state.partidos[llave_partido]["convocados"][id_]:
                    st.session_state.partidos[llave_partido]["convocados"][id_] = check_p
                    st.rerun()
                
                if check_p: convocados_cont += 1

        st.write(f"### 📈 Total Convocados {bloque_seleccionado}: {convocados_cont} chicos")
        if st.button("💾 GUARDAR CONVOCATORIA DE PARTIDO", key="btn_guardar_partido"):
            if rival_seleccionado == "Seleccionar rival...":
                st.error("Por favor, elegí un rival de la lista antes de guardar.")
            else:
                st.success(f"¡Convocatoria vs. {rival_seleccionado} guardada con éxito!")

    with tab_placa:
        total_convocados_reales = sum(st.session_state.partidos[llave_partido]["convocados"].values())
        if rival_seleccionado == "Seleccionar rival..." or total_convocados_reales == 0:
            st.warning("⚠️ Asegurate de seleccionar un rival arriba y tildar al menos un convocado en la otra pestaña.")
        else:
            if st.button("🖼️ GENERAR PLACA COMPLETA"):
                with st.spinner("Dibujando la placa profesional..."):
                    plt.rcParams['font.family'] = 'sans-serif'
                    plt.rcParams['font.size'] = 12
                    
                    fig, ax = plt.subplots(figsize=(8, 14), dpi=100)
                    ax.set_facecolor('#111111')
                    plt.tight_layout()
                    ax.set_xlim(0, 10)
                    ax.set_ylim(0, 20)
                    ax.axis('off')
                    
                    try:
                        escudo_img = plt.imread("escudo.png")
                        ax.imshow(escudo_img, extent=[4, 6, 17.5, 19.5], zorder=1)
                    except: pass

                    ax.text(5, 17.2, f"CONVOCADOS M-13", color='#F4C430', fontsize=28, fontweight='bold', ha='center')
                    bloque_texto = 'AZUL' if 'Azul' in bloque_seleccionado else 'AMARILLO'
                    ax.text(5, 16.4, f"TLTC {bloque_texto} vs {unidecode(rival_seleccionado).upper()}", color='white', fontsize=16, fontweight='bold', ha='center')
                    ax.text(5, 15.9, f"📅 {fecha_p_str}", color='#AAAAAA', fontsize=11, ha='center')
                    
                    y_text = 14.9
                    for puesto in LISTA_PUESTOS:
                        chicos_en_puesto = []
                        for id_jugador, convocado in st.session_state.partidos[llave_partido]["convocados"].items():
                            if convocado and st.session_state.plantel[id_jugador]["puesto"] == puesto:
                                chicos_en_puesto.append(f"{unidecode(st.session_state.plantel[id_jugador]['apellido']).upper()} {unidecode(st.session_state.plantel[id_jugador]['nombre']).upper()}")
                        
                        if chicos_en_puesto:
                            y_text -= 0.6
                            rect = patches.Rectangle((1, y_text - 0.2), 8, 0.6, facecolor='#2B3E75', edgecolor='#F4C430', linewidth=1.5, zorder=0)
                            ax.add_patch(rect)
                            ax.text(1.3, y_text + 0.1, f"{puesto.upper()}", color='#F4C430', fontsize=13, fontweight='bold', ha='left', va='center')
                            
                            y_text -= 0.5
                            for chico in chicos_en_puesto:
                                txt = ax.text(1.5, y_text, chico, color='white', fontsize=12, ha='left', va='center')
                                txt.set_path_effects([path_effects.withStroke(linewidth=2, foreground='#000000')])
                                y_text -= 0.4
                                
                    ax.text(5, 1.0, f"“RESPETO • COMPAÑERISMO • PASIÓN” • TLTC", color='#AAAAAA', fontsize=11, ha='center')
                    ax.text(5, 0.5, "🏉 Matchday Convocatoria 🏉", color='#F4C430', fontsize=10, ha='center')

                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
                    buf.seek(0)
                    plt.close()
                    
                    st.write("---")
                    st.image(buf, caption=f"Placa Matchday vs {rival_seleccionado}", use_container_width=True)
                    
                    st.sidebar.markdown("### Descargar Placa")
                    st.download_button(label="📥 DESCARGAR PLACA PARA WHATSAPP", data=buf, file_name=f"tltc_m13_matchday_{fecha_p_str}_{bloque_texto}.png", mime="image/png")

# --- MÓDULO 4: ESTADÍSTICAS ---
elif st.session_state.pantalla_actual == "Estadísticas":
    if st.button("⬅️ Volver al Menú Principal", key="back_stats"):
        st.session_state.pantalla_actual = "Inicio"
        st.rerun()
        
    st.header("📊 Estadísticas de Rendimiento")
    if st.session_state.asistencias:
        fechas = list(st.session_state.asistencias.keys())
        chart_data = pd.DataFrame({"Asistencia Total (%)": [min(100, int((sum(st.session_state.asistencias[f].values())/55)*100)) for f in fechas]}, index=fechas)
        st.line_chart(chart_data)
    else:
        st.info("Aún no hay asistencias registradas para graficar.")
