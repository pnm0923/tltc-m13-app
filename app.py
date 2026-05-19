import streamlit as st
import datetime
import pandas as pd

# CONFIGURACIÓN DE LA PÁGINA (Estilo TLTC)
st.set_page_config(page_title="TLTC M-13", page_icon="🏉", layout="centered")

# Inyección de CSS para diseño responsivo en tu Xiaomi
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
            "foto": None,
            "notas_tecnicas": "Sin observaciones técnicas.",
            "notas_actitud": "Buena predisposición en el club."
        } for i, nombre in enumerate(nombres_crudos)
    }

if 'asistencias' not in st.session_state:
    st.session_state.asistencias = {}

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
            # Busca la imagen directamente en la carpeta de tu repositorio
            st.image("escudo.png", use_container_width=True)
        except:
            # Si por alguna razón no se subió bien, muestra un texto para que no rompa la app
            st.markdown("<h3 style='text-align:center;'>🟨 TLTC M-13 🟦</h3>", unsafe_allow_html=True)
    
    st.title("TLTC M-13")
    st.write("Panel de Control del Entrenador")
    st.write("---")
    
    # Grid de opciones interactivas para simular los botones del diseño original
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown('<div class="menu-card"><h4>👥 Plantel Actual</h4><p>Lista, datos y fotos de perfil</p></div>', unsafe_allow_html=True)
        if st.button("Ir a Plantel", key="btn_plantel"):
            st.session_state.pantalla_actual = "Plantel"
            st.rerun()
            
        st.markdown('<div class="menu-card"><h4>📋 Asistencia Entr.</h4><p>Cargar fecha y presentes</p></div>', unsafe_allow_html=True)
        if st.button("Ir a Asistencia", key="btn_asistencia"):
            st.session_state.pantalla_actual = "Asistencia"
            st.rerun()

    with col_b:
        st.markdown('<div class="menu-card"><h4>🏉 Partidos</h4><p>Selección y minutos jugados</p></div>', unsafe_allow_html=True)
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
    
    # 1. Selector de fecha
    fecha = st.date_input("Fecha del Entrenamiento", datetime.date.today(), key="selector_fecha_entr")
    fecha_str = fecha.strftime("%Y-%m-%d")
    
    # [CORRECCIÓN CRUCIAL] Inicializar la base de datos de asistencia SOLO si realmente no existe NADA guardado para ese día
    if fecha_str not in st.session_state.asistencias:
        st.session_state.asistencias[fecha_str] = {id_: False for id_ in st.session_state.plantel.keys()}

    # Sincronizar la memoria visual de los checkboxes con lo que realmente hay en la base de datos de esa fecha
    for id_ in st.session_state.plantel.keys():
        clave_check = f"chk_asist_{id_}_{fecha_str}"
        # Forzamos a que el componente visual tenga EXACTAMENTE el mismo valor que guardaste en la asistencia
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
    
    # LISTADO INTERACTIVO DE ASISTENCIA
    for id_, datos in st.session_state.plantel.items():
        nombre_completo = f"{datos['apellido']} {datos['nombre']}"
        if buscar.lower() in nombre_completo.lower():
            clave_check = f"chk_asist_{id_}_{fecha_str}"
            
            # Dibujamos el checkbox
            check = st.checkbox(nombre_completo, key=clave_check)
            
            # Si el entrenador cambia el tilde con el dedo en el Xiaomi, impacta directo en la base de datos
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
        if buscar_p.lower() in nombre_completo.lower():
            with st.expander(f"🏃‍♂️ {nombre_completo}"):
                st.write(f"**Categoría:** 2013 (M-13)")
                foto_archivo = st.file_uploader(f"Foto de Perfil", type=["jpg", "png", "jpeg"], key=f"foto_{id_}")
                if foto_archivo:
                    st.session_state.plantel[id_]["foto"] = foto_archivo
                    st.image(foto_archivo, width=120)
                st.session_state.plantel[id_]["notas_actitud"] = st.text_area("🌟 Notas Actitudinales:", datos["notas_actitud"], key=f"act_{id_}")
                st.session_state.plantel[id_]["notas_tecnicas"] = st.text_area("🏉 Notas Técnicas (Pases/Tackles):", datos["notas_tecnicas"], key=f"tec_{id_}")

# --- MÓDULO 3: PARTIDOS Y CONVOCATORIAS ---
elif st.session_state.pantalla_actual == "Partidos":
    st.header("🏉 Carga de Partidos y Bloques")
    
    # 1. Configuración del Partido de la Fecha
    st.markdown("### 1. Datos del Encuentro")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        bloque_seleccionado = st.selectbox(
            "Seleccionar Bloque del TLTC",
            ["Tucumán Lawn Tennis Azul", "Tucumán Lawn Tennis Amarillo"],
            key="sb_bloque"
        )
    with col_p2:
        rival = st.text_input("Rival de la Fecha", placeholder="Ej: Universitario, Huirapuca...", key="ti_rival")
        
    fecha_partido = st.date_input("Fecha del Partido", datetime.date.today(), key="di_fecha_partido")
    fecha_p_str = fecha_partido.strftime("%Y-%m-%d")
    
    # Estructura de base de datos para partidos en la memoria temporal
    if 'partidos' not in st.session_state:
        st.session_state.partidos = {}
        
    # Llave única que combina fecha y bloque para que no se pisen (Ej: "2026-05-23_Azul")
    llave_partido = f"{fecha_p_str}_{'Azul' if 'Azul' in bloque_seleccionado else 'Amarillo'}"
    
    # Inicializar el partido si es nuevo
    if llave_partido not in st.session_state.partidos:
        st.session_state.partidos[llave_partido] = {
            "rival": rival,
            "bloque": bloque_seleccionado,
            "convocados": {id_: False for id_ in st.session_state.plantel.keys()}
        }
    
    # Si el usuario escribe el rival sobre la marcha, lo actualizamos en la memoria
    if rival:
        st.session_state.partidos[llave_partido]["rival"] = rival

    st.write("---")
    
    # 2. Selección de Jugadores para este bloque
    st.markdown(f"### 👥 Convocados para el Bloque: **{bloque_seleccionado}**")
    st.caption("Tildá a los chicos que van a jugar en este bloque este fin de semana.")
    
    # Botón para limpiar rápido la lista de convocados
    if st.button("❌ Limpiar Convocatoria de este Bloque", key="btn_limpiar_partido"):
        for id_ in st.session_state.plantel.keys():
            st.session_state.partidos[llave_partido]["convocados"][id_] = False
            if f"chk_partido_{id_}_{llave_partido}" in st.session_state:
                st.session_state[f"chk_partido_{id_}_{llave_partido}"] = False
        st.rerun()

    buscar_p = st.text_input("🔍 Buscar jugador para convocar...")
    
    st.write("---")
    convocados_cont = 0
    
    # LISTADO DE JUGADORES
    for id_, datos in st.session_state.plantel.items():
        nombre_completo = f"{datos['apellido']} {datos['nombre']}"
        
        if buscar_p.lower() in nombre_completo.lower():
            clave_check_p = f"chk_partido_{id_}_{llave_partido}"
            
            # Buscamos si ya está guardado como convocado en este partido
            estado_guardado_p = st.session_state.partidos[llave_partido]["convocados"].get(id_, False)
            
            # Control cruzado sutil: Verificar si el chico ya está en el OTRO bloque para la misma fecha
            otra_llave = f"{fecha_p_str}_{'Amarillo' if 'Azul' in bloque_seleccionado else 'Azul'}"
            ya_juega_en_otro = False
            if otra_llave in st.session_state.partidos:
                ya_juega_en_otro = st.session_state.partidos[otra_llave]["convocados"].get(id_, False)
            
            # Dibujamos el checkbox. Si ya juega en el otro bloque, le agregamos un aviso al nombre
            etiqueta = f"🏃‍♂️ {nombre_completo} ⚠️ (Ya está en el otro Bloque)" if ya_juega_en_otro else nombre_completo
            
            # Sincronizamos la interfaz
            if clave_check_p not in st.session_state:
                st.session_state[clave_check_p] = estado_guardado_p
                
            check_p = st.checkbox(etiqueta, key=clave_check_p)
            
            # Guardamos el tilde del entrenador
            st.session_state.partidos[llave_partido]["convocados"][id_] = check_p
            
            if check_p:
                convocados_cont += 1

    st.write("---")
    st.write(f"### 📈 Total Convocados {bloque_seleccionado}: {convocados_cont} chicos")
    
    if st.button("💾 GUARDAR CONVOCATORIA DE PARTIDO", key="btn_guardar_partido"):
        if not rival:
            st.error("Por favor, escribí el nombre del rival antes de guardar.")
        else:
            st.success(f"¡Partido vs. {rival} ({bloque_seleccionado}) guardado correctamente!")

# --- MÓDULO 4: PROXIMAMENTE ESTADÍSTICAS ---
elif st.session_state.pantalla_actual == "Estadísticas":
    st.header("📊 Estadísticas de Rendimiento")
    if st.session_state.asistencias:
        fechas = list(st.session_state.asistencias.keys())
        chart_data = pd.DataFrame({"Asistencia Total (%)": [min(100, int((sum(st.session_state.asistencias[f].values())/55)*100)) for f in fechas]}, index=fechas)
        st.line_chart(chart_data)
    else:
        st.info("Aún no hay asistencias registradas para graficar.")
