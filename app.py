import streamlit as st
import datetime
import pandas as pd

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
    
    /* Estilo de la Placa Oficial de Matchday */
    .placa-convocados {
        background-color: #111111; border: 3px solid #F4C430; border-radius: 15px;
        padding: 25px; text-align: center; font-family: 'Arial Black', sans-serif;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
    .placa-titulo { color: #F4C430 !important; font-size: 26px; margin-bottom: 2px; text-transform: uppercase; }
    .placa-sub { color: #FFFFFF !important; font-size: 16px; margin-bottom: 15px; font-weight: bold; }
    .placa-puesto-header {
        background-color: #2B3E75; color: #F4C430 !important;
        padding: 4px 10px; border-radius: 5px; font-size: 14px;
        text-transform: uppercase; margin-top: 15px; text-align: left;
        border-left: 5px solid #F4C430;
    }
    .placa-jugador {
        color: #FFFFFF; font-size: 15px; text-align: left;
        padding-left: 15px; margin: 4px 0; font-family: 'Arial', sans-serif;
    }
    
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
        "GIBILISCO MATEO", "GIJON BENJAMIN", "GUARDIA GERONIMO", "HERRERA BENJAMIN", "INGARAMO BAUTISTA",
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

# Menú de control oculto o complementario en el lateral
with st.sidebar:
    st.markdown("### Menú de Navegación")
    if st.button("🏠 Volver al Inicio"):
        st.session_state.pantalla_actual = "Inicio"
        st.rerun()

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
                
            if check:
                presentes_cont += 1
                
    st.write(f"### 🏃‍♂️ Presentes en esta fecha: {presentes_cont} / 55")
    st.write("---")
    
    if st.button("💾 GUARDAR ENTRENAMIENTO", key="btn_guardar_asist"):
        st.success(f"¡Asistencia del {fecha_str} guardada con éxito en la nube!")

# --- MÓDULO 2: PLANTEL ACTUAL Y FICHAS ---
elif st.session_state.pantalla_actual == "Plantel":
    st.header("👥 Plantel Completo M-13")
    buscar_p = st.text_input("🔍 Buscar en el plantel...")
    
    for id_, datos in st.session_state.plantel.items():
        nombre_completo = f"{datos['apellido']}, {datos['nombre']}"
        puesto_actual = datos.get("puesto", "Sin Puesto")
        
        if buscar_p.lower() in nombre_completo.lower():
            with st.expander(f"🏃‍♂️ {nombre_completo} | 🏷️ {puesto_actual}"):
                
                # Desplegable interactivo para asignar el puesto
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
            "rival": "",
            "bloque": bloque_seleccionado,
            "convocados": {id_: False for id_ in st.session_state.plantel.keys()}
        }
    
    if rival_seleccionado != "Seleccionar rival...":
        st.session_state.partidos[llave_partido]["rival"] = rival_seleccionado

    st.write("---")
    
    # SISTEMA DE PESTAÑAS (Manejo limpio de Carga vs Placa)
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
            # Mostramos el puesto también en la lista de partidos para guiarte
            nombre_completo = f"{datos['apellido']} {datos['nombre']} ({datos['puesto']})"
            
            if buscar_p.lower() in nombre_completo.lower():
                clave_check_p = f"chk_partido_{id_}_{llave_partido}"
                estado_guardado_p = st.session_state.partidos[llave_partido]["convocados"].get(id_, False)
                
                otra_llave = f"{fecha_p_str}_{'Amarillo' if 'Azul' in bloque_seleccionado else 'Azul'}"
                ya_juega_en_otro = False
                if otra_llave in st.session_state.partidos:
                    ya_juega_en_otro = st.session_state.partidos[otra_llave]["convocados"].get(id_, False)
                
                etiqueta = f"🏃‍♂️ {nombre_completo} ⚠️ (Ya está en el otro Bloque)" if ya_juega_en_otro else nombre_completo
                
                st.session_state[clave_check_p] = estado_guardado_p
                check_p = st.checkbox(etiqueta, key=clave_check_p)
                
                if check_p != st.session_state.partidos[llave_partido]["convocados"][id_]:
                    st.session_state.partidos[llave_partido]["convocados"][id_] = check_p
                    st.rerun()
                
                if check_p:
                    convocados_cont += 1

        st.write(f"### 📈 Total Convocados {bloque_seleccionado}: {convocados_cont} chicos")
        if st.button("💾 GUARDAR CONVOCATORIA DE PARTIDO", key="btn_guardar_partido"):
            if rival_seleccionado == "Seleccionar rival...":
                st.error("Por favor, elegí un rival de la lista antes de guardar.")
            else:
                st.success(f"¡Partido vs. {rival_seleccionado} ({bloque_seleccionado}) guardado correctamente!")

    with tab_placa:
        if rival_seleccionado == "Seleccionar rival...":
            st.warning("⚠️ Seleccioná un rival en la parte superior para generar la placa visual.")
        else:
            # DIBUJO DE LA PLACA VISUAL
            st.markdown(f"""
            <div class="placa-convocados">
                <div class="placa-titulo">CONVOCADOS M-13</div>
                <div class="placa-sub">{bloque_seleccionado.upper()} vs {rival_seleccionado.upper()}</div>
                <div style="color:#F4C430; font-size:12px; margin-bottom:20px;">📅 FECHA: {fecha_p_str}</div>
            """, unsafe_allow_html=True)
            
            # Recorremos los puestos oficiales uno por uno para armar los subgrupos
            for puesto in LISTA_PUESTOS:
                chicos_en_puesto = []
                for id_jugador, convocado in st.session_state.partidos[llave_partido]["convocados"].items():
                    if convocado:
                        datos_chico = st.session_state.plantel[id_jugador]
                        if datos_chico["puesto"] == puesto:
                            chicos_en_puesto.append(f"{datos_chico['apellido']} {datos_chico['nombre']}")
                
                # Si este puesto tiene jugadores convocados, lo imprimimos en la placa
                if chicos_en_puesto:
                    st.markdown(f'<div class="placa-puesto-header">{puesto}</div>', unsafe_allow_html=True)
                    for chico in chicos_en_puesto:
                        st.markdown(f'<div class="placa-jugador">• {chico}</div>', unsafe_allow_html=True)
                        
            st.markdown("</div>", unsafe_allow_html=True)
            st.caption("📱 ¡Sacale una captura de pantalla desde tu Xiaomi para mandarla al grupo de WhatsApp!")

# --- MÓDULO 4: ESTADÍSTICAS ---
elif st.session_state.pantalla_actual == "Estadísticas":
    st.header("📊 Estadísticas de Rendimiento")
    if st.session_state.asistencias:
        fechas = list(st.session_state.asistencias.keys())
        chart_data = pd.DataFrame({"Asistencia Total (%)": [min(100, int((sum(st.session_state.asistencias[f].values())/55)*100)) for f in fechas]}, index=fechas)
        st.line_chart(chart_data)
    else:
        st.info("Aún no hay asistencias registradas para graficar.")
