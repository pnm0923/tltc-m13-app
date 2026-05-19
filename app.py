import streamlit as st
import datetime
import pandas as pd
import io
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
from unidecode import unidecode
from supabase import create_client, Client

# CONFIGURACIÓN DE LA PÁGINA (Estilo TLTC)
st.set_page_config(page_title="TLTC M-13", page_icon="🏉", layout="centered")

# Inyección de CSS para diseño responsivo en tu Xiaomi y Placa Estilo Pro
st.markdown("""
    <style>
    .stApp { backgroundColor: #1E1E1E; color: white; }
    h1, h2, h3 { color: #F4C430 !important; font-family: 'Arial', sans-serif; text-align: center; }
    
    /* Botones grandes de la pantalla principal */
    .menu-card {
        background-color: #2B3E75; border: 2px solid #F4C430; border-radius: 12px;
        padding: 20px; text-align: center; margin-bottom: 15px; cursor: pointer;
    }
    .menu-card h4 { margin: 0; color: white !important; font-size: 18px; }
    .menu-card p { margin: 5px 0 0 0; color: #CCCCCC; font-size: 13px; }
    
    /* Botones del sistema de Streamlit */
    .stButton>button { 
        background-color: #2B3E75 !important; color: white !important; 
        border: 2px solid #F4C430 !important; border-radius: 10px; width: 100%; font-weight: bold;
    }
    .stButton>button:hover { background-color: #F4C430 !important; color: #2B3E75 !important; }
    div[data-testid="stExpander"] { background-color: #2A2A2A !important; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# CONEXIÓN CON SUPABASE
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase: Client = init_supabase()
except Exception as e:
    st.error("Error al conectar con la base de datos. Verifica los Secrets.")

# Lista de puestos oficiales
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
            "apellido": nombre.split()[0], "nombre": " ".join(nombre.split()[1:]),
            "nacimiento": datetime.date(2013, 1, 1), "puesto": "Sin Puesto", "foto": None,
            "notas_tecnicas": "", "notas_actitud": ""
        } for i, nombre in enumerate(nombres_crudos)
    }

    # Cargar Puestos y Notas guardados en Supabase al iniciar la app
    try:
        res_plantel = supabase.table("datos_plantel").select("*").execute()
        for row in res_plantel.data:
            j_id = str(row["jugador_id"])
            if j_id in st.session_state.plantel:
                st.session_state.plantel[j_id]["puesto"] = row["puesto"]
                st.session_state.plantel[j_id]["notas_actitud"] = row["notas_actitud"] if row["notas_actitud"] else ""
                st.session_state.plantel[j_id]["notas_tecnicas"] = row["notas_tecnicas"] if row["notas_tecnicas"] else ""
    except:
        pass

if 'pantalla_actual' not in st.session_state:
    st.session_state.pantalla_actual = "Inicio"

# --- PANTALLA PRINCIPAL (HOME) ---
if st.session_state.pantalla_actual == "Inicio":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try: st.image("escudo.png", use_container_width=True)
        except: st.markdown("<h3 style='text-align:center;'>🟨 TLTC M-13 🟦</h3>", unsafe_allow_html=True)
    
    st.title("TLTC M-13")
    st.write("Panel de Control del Entrenador")
    st.write("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="menu-card"><h4>👥 Plantel Actual</h4><p>Lista, puestos y fotos de perfil</p></div>', unsafe_allow_html=True)
        if st.button("Ir a Plantel", key="btn_plantel"):
            st.session_state.pantalla_actual = "Plantel"; st.rerun()
            
        st.markdown('<div class="menu-card"><h4>📋 Asistencia Entr.</h4><p>Cargar fecha y presentes</p></div>', unsafe_allow_html=True)
        if st.button("Ir a Asistencia", key="btn_asistencia"):
            st.session_state.pantalla_actual = "Asistencia"; st.rerun()
    with col_b:
        st.markdown('<div class="menu-card"><h4>🏉 Partidos y Placas</h4><p>Selección por Bloques y Placas</p></div>', unsafe_allow_html=True)
        if st.button("Ir a Partidos", key="btn_partidos"):
            st.session_state.pantalla_actual = "Partidos"; st.rerun()
            
        st.markdown('<div class="menu-card"><h4>📊 Estadísticas</h4><p>Ver evolución del jugador</p></div>', unsafe_allow_html=True)
        if st.button("Ir a Estadísticas", key="btn_stats"):
            st.session_state.pantalla_actual = "Estadísticas"; st.rerun()

# --- MÓDULO 1: ASISTENCIA A ENTRENAMIENTO ---
elif st.session_state.pantalla_actual == "Asistencia":
    if st.button("⬅️ Volver al Menú Principal", key="back_asist"):
        st.session_state.pantalla_actual = "Inicio"; st.rerun()
        
    st.header("📋 Asistencia a Entrenamiento")
    fecha = st.date_input("Fecha del Entrenamiento", datetime.date.today(), key="selector_fecha_entr")
    fecha_str = fecha.strftime("%Y-%m-%d")
    
    # Descargar desde la nube SOLO UNA VEZ al cambiar de fecha
    if f"last_loaded_date" not in st.session_state or st.session_state.last_loaded_date != fecha_str:
        try:
            res = supabase.table("asistencias_entrenamiento").select("*").eq("fecha", fecha_str).execute()
            mapa_nube = {row["jugador_id"]: row["presente"] for row in res.data}
            for id_ in st.session_state.plantel.keys():
                st.session_state[f"chk_asist_{id_}_{fecha_str}"] = mapa_nube.get(id_, False)
        except:
            for id_ in st.session_state.plantel.keys(): st.session_state[f"chk_asist_{id_}_{fecha_str}"] = False
        st.session_state.last_loaded_date = fecha_str

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("✔️ Todos Presentes", key="btn_todos_pres"):
            for id_ in st.session_state.plantel.keys():
                st.session_state[f"chk_asist_{id_}_{fecha_str}"] = True
            st.rerun()
    with col_btn2:
        if st.button("❌ Reiniciar (Todos Ausentes)", key="btn_todos_aus"):
            for id_ in st.session_state.plantel.keys():
                st.session_state[f"chk_asist_{id_}_{fecha_str}"] = False
            st.rerun()
            
    buscar = st.text_input("🔍 Buscar jugador en esta fecha...")
    st.write("---")
    
    presentes_cont = 0
    for id_, datos in st.session_state.plantel.items():
        nombre_completo = f"{datos['apellido']} {datos['nombre']}"
        clave_check = f"chk_asist_{id_}_{fecha_str}"
        
        if clave_check not in st.session_state:
            st.session_state[clave_check] = False
            
        if buscar.lower() in nombre_completo.lower():
            check = st.checkbox(nombre_completo, key=clave_check)
            if st.session_state[clave_check]: presentes_cont += 1
        else:
            if st.session_state[clave_check]: presentes_cont += 1
                
    st.write(f"### 🏃‍♂️ Presentes en esta fecha: {presentes_cont} / 55")
    
    if st.button("💾 GUARDAR ENTRENAMIENTO EN LA NUBE", key="btn_guardar_asist"):
        with st.spinner("Sincronizando con Supabase..."):
            # [ELIMINACIÓN ABSOLUTA DE DELETE] Hacemos un upsert limpio y directo de toda la lista
            filas_asistencia = []
            for id_ in st.session_state.plantel.keys():
                val_presente = st.session_state.get(f"chk_asist_{id_}_{fecha_str}", False)
                filas_asistencia.append({"fecha": fecha_str, "jugador_id": str(id_), "presente": val_presente})
            
            # Se ejecuta de forma nativa por lote sin on_conflict problemáticos
            supabase.table("asistencias_entrenamiento").upsert(filas_asistencia).execute()
            st.success("¡Asistencia guardada permanentemente con éxito!")

# --- MÓDULO 2: PLANTEL ACTUAL ---
elif st.session_state.pantalla_actual == "Plantel":
    if st.button("⬅️ Volver al Menú Principal", key="back_plantel"):
        st.session_state.pantalla_actual = "Inicio"; st.rerun()
        
    st.header("👥 Plantel Completo M-13")
    buscar_p = st.text_input("🔍 Buscar en el plantel...")
    
    for id_, datos in st.session_state.plantel.items():
        nombre_completo = f"{datos['apellido']}, {datos['nombre']}"
        puesto_actual = datos.get("puesto", "Sin Puesto")
        
        if buscar_p.lower() in nombre_completo.lower():
            with st.expander(f"🏃‍♂️ {nombre_completo} | 🏷️ {puesto_actual}"):
                indice_puesto = LISTA_PUESTOS.index(puesto_actual) if puesto_actual in LISTA_PUESTOS else 0
                
                nuevo_puesto = st.selectbox(f"Asignar Puesto:", LISTA_PUESTOS, index=indice_puesto, key=f"puesto_{id_}")
                nota_act = st.text_area("🌟 Notas Actitudinales:", datos["notas_actitud"], key=f"act_{id_}")
                nota_tec = st.text_area("🏉 Notas Técnicas:", datos["notas_tecnicas"], key=f"tec_{id_}")
                
                st.session_state.plantel[id_]["puesto"] = nuevo_puesto
                st.session_state.plantel[id_]["notas_actitud"] = nota_act
                st.session_state.plantel[id_]["notas_tecnicas"] = nota_tec

    st.write("---")
    if st.button("💾 GUARDAR MODIFICACIONES DEL PLANTEL", key="btn_guardar_fichas_nube"):
        with st.spinner("Sincronizando puestos y notas con la nube..."):
            filas_plantel = []
            for id_, datos in st.session_state.plantel.items():
                filas_plantel.append({
                    "jugador_id": str(id_), 
                    "puesto": datos["puesto"], 
                    "notas_actitud": datos["notas_actitud"], 
                    "notas_tecnicas": datos["notas_tecnicas"]
                })
            supabase.table("datos_plantel").upsert(filas_plantel).execute()
            st.success("¡Todos los puestos y notas técnicas se guardaron correctamente!")
            st.rerun()

# --- MÓDULO 3: PARTIDOS Y CONVOCATORIAS ---
elif st.session_state.pantalla_actual == "Partidos":
    if st.button("⬅️ Volver al Menú Principal", key="back_partidos"):
        st.session_state.pantalla_actual = "Inicio"; st.rerun()
        
    st.header("🏉 Carga de Partidos y Bloques")
    lista_rivales = ["Seleccionar rival...", "Tucumán Rugby", "Universitario", "Jockey Club", "Cardenales", "Natación y Gimnasia", "Los Tarcos", "Lince", "Huirapuca", "Aguará Guazú", "San Martín/Liceo/Corsarios"]
    
    col_p1, col_p2 = st.columns(2)
    with col_p1: bloque_seleccionado = st.selectbox("Seleccionar Bloque del TLTC", ["Tucumán Lawn Tennis Azul", "Tucumán Lawn Tennis Amarillo"], key="sb_bloque")
    with col_p2: rival_seleccionado = st.selectbox("Rival de la Fecha", lista_rivales, key="sb_rival")
        
    fecha_partido = st.date_input("Fecha del Partido", datetime.date.today(), key="di_fecha_partido")
    fecha_p_str = fecha_partido.strftime("%Y-%m-%d")
    bloque_corto = 'Azul' if 'Azul' in bloque_seleccionado else 'Amarillo'
    llave_partido = f"{fecha_p_str}_{bloque_corto}"
    
    if f"last_loaded_match" not in st.session_state or st.session_state.last_loaded_match != llave_partido:
        try:
            res = supabase.table("convocados_partidos").select("*").eq("fecha", fecha_p_str).eq("bloque", bloque_corto).execute()
            mapa_partido_nube = {row["jugador_id"]: row["convocado"] for row in res.data}
            for id_ in st.session_state.plantel.keys():
                st.session_state[f"chk_p_visual_{id_}_{llave_partido}"] = mapa_partido_nube.get(id_, False)
        except:
            for id_ in st.session_state.plantel.keys(): st.session_state[f"chk_p_visual_{id_}_{llave_partido}"] = False
        st.session_state.last_loaded_match = llave_partido

    st.write("---")
    tab_carga, tab_placa = st.tabs(["📝 Cargar Convocados", "🖼️ Ver Placa de Matchday"])
    
    with tab_carga:
        if st.button("❌ Limpiar Convocatoria", key="btn_limpiar_partido"):
            for id_ in st.session_state.plantel.keys(): 
                st.session_state[f"chk_p_visual_{id_}_{llave_partido}"] = False
            st.rerun()

        buscar_p = st.text_input("🔍 Buscar jugador para convocar...")
        st.write("---")
        
        convocados_cont = 0
        for id_, datos in st.session_state.plantel.items():
            nombre_completo = f"{datos['apellido']} {datos['nombre']} ({datos['puesto']})"
            clave_check_p = f"chk_p_visual_{id_}_{llave_partido}"
            
            if clave_check_p not in st.session_state:
                st.session_state[clave_check_p] = False
                
            if buscar_p.lower() in nombre_completo.lower():
                check_p = st.checkbox(nombre_completo, key=clave_check_p)
                if st.session_state[clave_check_p]: convocados_cont += 1
            else:
                if st.session_state[clave_check_p]: convocados_cont += 1

        st.write(f"### 📈 Total Convocados: {convocados_cont} chicos")
        if st.button("💾 GUARDAR PARTIDO EN LA NUBE", key="btn_guardar_partido"):
            if rival_seleccionado == "Seleccionar rival...": st.error("Por favor, elegí un rival.")
            else:
                with st.spinner("Subiendo lista de convocados..."):
                    filas_partidos = []
                    for id_ in st.session_state.plantel.keys():
                        val_convocado = st.session_state.get(f"chk_p_visual_{id_}_{llave_partido}", False)
                        filas_partidos.append({
                            "fecha": fecha_p_str, "bloque": bloque_corto, "rival": rival_seleccionado,
                            "jugador_id": str(id_), "convocado": val_convocado
                        })
                    supabase.table("convocados_partidos").upsert(filas_partidos).execute()
                    st.success("¡Convocatoria guardada permanentemente!")

    with tab_placa:
        total_tildados_placa = sum([st.session_state.get(f"chk_p_visual_{id_}_{llave_partido}", False) for id_ in st.session_state.plantel.keys()])
        
        if rival_seleccionado == "Seleccionar rival..." or total_tildados_placa == 0:
            st.warning("⚠️ Selecciona un rival y tilda convocados para generar la placa.")
        else:
            if st.button("🖼️ GENERAR PLACA COMPLETA"):
                fig, ax = plt.subplots(figsize=(8, 14), dpi=100)
                ax.set_facecolor('#111111'); ax.set_xlim(0, 10); ax.set_ylim(0, 20); ax.axis('off')
                try: ax.imshow(plt.imread("escudo.png"), extent=[4, 6, 17.5, 19.5], zorder=1)
                except: pass

                ax.text(5, 17.2, "CONVOCADOS M-13", color='#F4C430', fontsize=28, fontweight='bold', ha='center')
                ax.text(5, 16.4, f"TLTC {bloque_corto.upper()} vs {unidecode(rival_seleccionado).upper()}", color='white', fontsize=16, fontweight='bold', ha='center')
                ax.text(5, 15.9, f"📅 {fecha_p_str}", color='#AAAAAA', fontsize=11, ha='center')
                
                y_text = 14.9
                for puesto in LISTA_PUESTOS:
                    chicos_en_puesto = []
                    for id_ in st.session_state.plantel.keys():
                        if st.session_state.get(f"chk_p_visual_{id_}_{llave_partido}", False) and st.session_state.plantel[id_]["puesto"] == puesto:
                            chicos_en_puesto.append(f"{unidecode(st.session_state.plantel[id_]['apellido']).upper()} {unidecode(st.session_state.plantel[id_]['nombre']).upper()}")
                    
                    if chicos_en_puesto:
                        y_text -= 0.6
                        ax.add_patch(patches.Rectangle((1, y_text - 0.2), 8, 0.6, facecolor='#2B3E75', edgecolor='#F4C430', linewidth=1.5, zorder=0))
                        ax.text(1.3, y_text + 0.1, f"{puesto.upper()}", color='#F4C430', fontsize=13, fontweight='bold', ha='left', va='center')
                        y_text -= 0.5
                        for chico in chicos_en_puesto:
                            txt = ax.text(1.5, y_text, chico, color='white', fontsize=12, ha='left', va='center')
                            txt.set_path_effects([path_effects.withStroke(linewidth=2, foreground='#000000')])
                            y_text -= 0.4
                            
                ax.text(5, 1.0, f"“RESPETO • COMPAÑERISMO • PASIÓN” • TLTC", color='#AAAAAA', fontsize=11, ha='center')
                buf = io.BytesIO(); plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1); buf.seek(0); plt.close()
                st.image(buf, use_container_width=True)
                st.sidebar.download_button(label="📥 DESCARGAR PLACA", data=buf, file_name=f"convocados_{fecha_p_str}.png", mime="image/png")

# --- MÓDULO 4: ESTADÍSTICAS ---
elif st.session_state.pantalla_actual == "Estadísticas":
    if st.button("⬅️ Volver al Menú Principal", key="back_stats"):
        st.session_state.pantalla_actual = "Inicio"; st.rerun()
    st.header("📊 Estadísticas de Rendimiento")
    st.info("Módulo conectado a Supabase. Próximamente gráficos detallados de asistencia.")
