import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from supabase import create_client, Client

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="TLTC M-13", page_icon="🏉", layout="centered")

st.markdown("""
    <style>
    .stApp { backgroundColor: #1E1E1E; color: white; }
    h1, h2, h3 { color: #F4C430 !important; font-family: 'Arial', sans-serif; text-align: center; }
    .menu-card {
        background-color: #2B3E75; border: 2px solid #F4C430; border-radius: 12px;
        padding: 20px; text-align: center; margin-bottom: 15px; cursor: pointer;
    }
    .menu-card h4 { margin: 0; color: white !important; font-size: 18px; }
    .menu-card p { margin: 5px 0 0 0; color: #CCCCCC; font-size: 13px; }
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
    st.stop()

LISTA_PUESTOS = ["Sin Puesto", "Pilar", "Hooker", "2° Linea", "3° Linea", "Medio scrum", "Apertura", "Centro", "Wing", "Fullback"]

# SEMILLA DEL PLANTEL
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

    # Cargar datos persistidos desde Supabase
    try:
        res_plantel = supabase.table("datos_plantel").select("*").execute()
        for row in res_plantel.data:
            j_id = str(row["jugador_id"])
            if j_id in st.session_state.plantel:
                st.session_state.plantel[j_id]["puesto"] = row["puesto"] or "Sin Puesto"
                st.session_state.plantel[j_id]["notas_actitud"] = row["notas_actitud"] or ""
                st.session_state.plantel[j_id]["notas_tecnicas"] = row["notas_tecnicas"] or ""
    except Exception as e:
        st.warning(f"No se pudieron cargar los datos del plantel: {e}")

if 'pantalla_actual' not in st.session_state:
    st.session_state.pantalla_actual = "Inicio"

# ──────────────────────────────────────────────
# PANTALLA PRINCIPAL
# ──────────────────────────────────────────────
if st.session_state.pantalla_actual == "Inicio":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("escudo.png", use_container_width=True)
        except:
            st.markdown("<h3 style='text-align:center;'>🟨 TLTC M-13 🟦</h3>", unsafe_allow_html=True)

    st.title("TLTC M-13")
    st.write("Panel de Control del Entrenador")
    st.write("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="menu-card"><h4>👥 Plantel Actual</h4><p>Lista, puestos y notas</p></div>', unsafe_allow_html=True)
        if st.button("Ir a Plantel", key="btn_plantel"):
            st.session_state.pantalla_actual = "Plantel"; st.rerun()

        st.markdown('<div class="menu-card"><h4>📋 Asistencia Entr.</h4><p>Cargar fecha y presentes</p></div>', unsafe_allow_html=True)
        if st.button("Ir a Asistencia", key="btn_asistencia"):
            st.session_state.pantalla_actual = "Asistencia"; st.rerun()
    with col_b:
        st.markdown('<div class="menu-card"><h4>🏉 Partidos</h4><p>Convocatoria y stats en vivo</p></div>', unsafe_allow_html=True)
        if st.button("Ir a Partidos", key="btn_partidos"):
            st.session_state.pantalla_actual = "Partidos"; st.rerun()

        st.markdown('<div class="menu-card"><h4>📊 Estadísticas</h4><p>Ver evolución del jugador</p></div>', unsafe_allow_html=True)
        if st.button("Ir a Estadísticas", key="btn_stats"):
            st.session_state.pantalla_actual = "Estadísticas"; st.rerun()

# ──────────────────────────────────────────────
# MÓDULO 1: ASISTENCIA A ENTRENAMIENTO
# ──────────────────────────────────────────────
elif st.session_state.pantalla_actual == "Asistencia":
    if st.button("⬅️ Volver al Menú Principal", key="back_asist"):
        st.session_state.pantalla_actual = "Inicio"; st.rerun()

    st.header("📋 Asistencia a Entrenamiento")
    fecha = st.date_input("Fecha del Entrenamiento", datetime.date.today(), key="selector_fecha_entr")
    fecha_str = fecha.strftime("%Y-%m-%d")

    # Cargar desde Supabase solo al cambiar de fecha
    if st.session_state.get("last_loaded_date") != fecha_str:
        try:
            res = supabase.table("asistencias_entrenamiento").select("*").eq("fecha", fecha_str).execute()
            mapa_nube = {str(row["jugador_id"]): row["presente"] for row in res.data}
            for id_ in st.session_state.plantel.keys():
                st.session_state[f"chk_asist_{id_}_{fecha_str}"] = mapa_nube.get(id_, False)
        except:
            for id_ in st.session_state.plantel.keys():
                st.session_state[f"chk_asist_{id_}_{fecha_str}"] = False
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
            st.checkbox(nombre_completo, key=clave_check)
        if st.session_state[clave_check]:
            presentes_cont += 1

    st.write(f"### 🏃‍♂️ Presentes: {presentes_cont} / {len(st.session_state.plantel)}")

    if st.button("💾 GUARDAR ENTRENAMIENTO EN LA NUBE", key="btn_guardar_asist"):
        with st.spinner("Sincronizando con Supabase..."):
            try:
                filas = []
                for id_ in st.session_state.plantel.keys():
                    filas.append({
                        "fecha": fecha_str,
                        "jugador_id": str(id_),
                        "presente": st.session_state.get(f"chk_asist_{id_}_{fecha_str}", False)
                    })
                # UPSERT: inserta o actualiza si ya existe (requiere UNIQUE en fecha+jugador_id)
                supabase.table("asistencias_entrenamiento").upsert(filas, on_conflict="fecha,jugador_id").execute()
                st.success("¡Asistencia guardada con éxito!")
            except Exception as e:
                st.error(f"Error al guardar: {e}")

# ──────────────────────────────────────────────
# MÓDULO 2: PLANTEL
# ──────────────────────────────────────────────
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
                nuevo_puesto = st.selectbox("Asignar Puesto:", LISTA_PUESTOS, index=indice_puesto, key=f"puesto_{id_}")
                nota_act = st.text_area("🌟 Notas Actitudinales:", datos["notas_actitud"], key=f"act_{id_}")
                nota_tec = st.text_area("🏉 Notas Técnicas:", datos["notas_tecnicas"], key=f"tec_{id_}")

                st.session_state.plantel[id_]["puesto"] = nuevo_puesto
                st.session_state.plantel[id_]["notas_actitud"] = nota_act
                st.session_state.plantel[id_]["notas_tecnicas"] = nota_tec

    st.write("---")
    if st.button("💾 GUARDAR MODIFICACIONES DEL PLANTEL", key="btn_guardar_fichas_nube"):
        with st.spinner("Sincronizando puestos y notas con la nube..."):
            try:
                filas = []
                for id_, datos in st.session_state.plantel.items():
                    filas.append({
                        "jugador_id": str(id_),
                        "puesto": datos["puesto"],
                        "notas_actitud": datos["notas_actitud"],
                        "notas_tecnicas": datos["notas_tecnicas"]
                    })
                # UPSERT: requiere UNIQUE en jugador_id
                supabase.table("datos_plantel").upsert(filas, on_conflict="jugador_id").execute()
                st.success("¡Plantel guardado correctamente!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")

# ──────────────────────────────────────────────
# MÓDULO 3: PARTIDOS Y STATS EN VIVO
# ──────────────────────────────────────────────
elif st.session_state.pantalla_actual == "Partidos":
    if st.button("⬅️ Volver al Menú Principal", key="back_partidos"):
        st.session_state.pantalla_actual = "Inicio"; st.rerun()

    st.header("🏉 Partidos y Estadísticas en Vivo")

    lista_rivales = [
        "Seleccionar rival...", "Tucumán Rugby", "Universitario", "Jockey Club",
        "Cardenales", "Natación y Gimnasia", "Los Tarcos", "Lince",
        "Huirapuca", "Aguará Guazú", "San Martín/Liceo/Corsarios"
    ]

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        bloque_seleccionado = st.selectbox(
            "Bloque TLTC",
            ["Tucumán Lawn Tennis Azul", "Tucumán Lawn Tennis Amarillo"],
            key="sb_bloque"
        )
    with col_p2:
        rival_seleccionado = st.selectbox("Rival", lista_rivales, key="sb_rival")

    fecha_partido = st.date_input("Fecha del Partido", datetime.date.today(), key="di_fecha_partido")
    fecha_p_str = fecha_partido.strftime("%Y-%m-%d")
    bloque_corto = 'Azul' if 'Azul' in bloque_seleccionado else 'Amarillo'
    llave_partido = f"{fecha_p_str}_{bloque_corto}"

    st.write("---")

    # ── SECCIÓN A: CONVOCATORIA ──
    st.subheader("📋 Convocatoria al Partido")

    # Cargar convocatoria desde Supabase al cambiar de partido
    if st.session_state.get("last_loaded_match") != llave_partido:
        try:
            res = supabase.table("convocados_partidos").select("*").eq("fecha", fecha_p_str).eq("bloque", bloque_corto).execute()
            mapa_conv = {str(row["jugador_id"]): row["convocado"] for row in res.data}
            for id_ in st.session_state.plantel.keys():
                st.session_state[f"chk_p_{id_}_{llave_partido}"] = mapa_conv.get(id_, False)
        except:
            for id_ in st.session_state.plantel.keys():
                st.session_state[f"chk_p_{id_}_{llave_partido}"] = False
        st.session_state.last_loaded_match = llave_partido

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        if st.button("✔️ Convocar a Todos", key="btn_conv_todos"):
            for id_ in st.session_state.plantel.keys():
                st.session_state[f"chk_p_{id_}_{llave_partido}"] = True
            st.rerun()
    with col_c2:
        if st.button("❌ Limpiar Convocatoria", key="btn_conv_limpiar"):
            for id_ in st.session_state.plantel.keys():
                st.session_state[f"chk_p_{id_}_{llave_partido}"] = False
            st.rerun()

    buscar_conv = st.text_input("🔍 Buscar jugador para convocar...")
    convocados_count = 0
    for id_, datos in st.session_state.plantel.items():
        nombre_completo = f"{datos['apellido']} {datos['nombre']}"
        clave = f"chk_p_{id_}_{llave_partido}"
        if clave not in st.session_state:
            st.session_state[clave] = False
        if buscar_conv.lower() in nombre_completo.lower():
            st.checkbox(nombre_completo, key=clave)
        if st.session_state[clave]:
            convocados_count += 1

    st.write(f"**Convocados: {convocados_count} jugadores**")

    if st.button("💾 GUARDAR CONVOCATORIA", key="btn_guardar_conv"):
        with st.spinner("Guardando convocatoria..."):
            try:
                filas_conv = []
                for id_ in st.session_state.plantel.keys():
                    filas_conv.append({
                        "fecha": fecha_p_str,
                        "bloque": bloque_corto,
                        "jugador_id": str(id_),
                        "convocado": st.session_state.get(f"chk_p_{id_}_{llave_partido}", False)
                    })
                supabase.table("convocados_partidos").upsert(filas_conv, on_conflict="fecha,bloque,jugador_id").execute()
                st.success("¡Convocatoria guardada!")
            except Exception as e:
                st.error(f"Error al guardar convocatoria: {e}")

    st.write("---")

    # ── SECCIÓN B: ESTADÍSTICAS EN VIVO ──
    st.subheader("📊 Estadísticas en Vivo")

    if rival_seleccionado == "Seleccionar rival...":
        st.info("Seleccioná un rival para cargar estadísticas.")
    else:
        # Obtener solo los convocados para este partido
        convocados_ids = [
            id_ for id_ in st.session_state.plantel.keys()
            if st.session_state.get(f"chk_p_{id_}_{llave_partido}", False)
        ]

        if not convocados_ids:
            st.warning("No hay jugadores convocados para este partido. Guardá la convocatoria primero.")
        else:
            # Cargar stats existentes desde Supabase
            llave_stats = f"stats_loaded_{llave_partido}"
            if not st.session_state.get(llave_stats, False):
                try:
                    res_stats = supabase.table("estadisticas_partido").select("*").eq("fecha", fecha_p_str).eq("bloque", bloque_corto).execute()
                    for row in res_stats.data:
                        j_id = str(row["jugador_id"])
                        st.session_state[f"stat_tackles_{j_id}_{llave_partido}"] = row.get("tackles", 0)
                        st.session_state[f"stat_pases_{j_id}_{llave_partido}"] = row.get("pases", 0)
                        st.session_state[f"stat_rucks_{j_id}_{llave_partido}"] = row.get("rucks", 0)
                        st.session_state[f"stat_apoyos_{j_id}_{llave_partido}"] = row.get("apoyos", 0)
                    st.session_state[llave_stats] = True
                except Exception as e:
                    st.warning(f"No se pudieron cargar stats previas: {e}")

            # Inicializar en 0 si no están en session_state
            for id_ in convocados_ids:
                for stat in ["tackles", "pases", "rucks", "apoyos"]:
                    key = f"stat_{stat}_{id_}_{llave_partido}"
                    if key not in st.session_state:
                        st.session_state[key] = 0

            st.write(f"**{bloque_seleccionado} vs {rival_seleccionado} — {fecha_partido.strftime('%d/%m/%Y')}**")
            st.write("")

            # Tarjeta por jugador convocado
            for id_ in convocados_ids:
                datos = st.session_state.plantel[id_]
                nombre_completo = f"{datos['apellido']} {datos['nombre']}"

                with st.expander(f"🏃 {nombre_completo} | {datos.get('puesto','Sin Puesto')}"):
                    stats_labels = {
                        "tackles": "🛡️ Tackles",
                        "pases": "🤾 Pases",
                        "rucks": "💥 Rucks",
                        "apoyos": "🤝 Apoyos"
                    }
                    for stat, label in stats_labels.items():
                        key = f"stat_{stat}_{id_}_{llave_partido}"
                        col_label, col_val, col_btn = st.columns([3, 1, 1])
                        with col_label:
                            st.write(f"**{label}**")
                        with col_val:
                            st.write(f"### {st.session_state[key]}")
                        with col_btn:
                            if st.button("+1", key=f"btn_{stat}_{id_}_{llave_partido}"):
                                st.session_state[key] += 1
                                st.rerun()

            st.write("---")
            if st.button("💾 GUARDAR ESTADÍSTICAS EN LA NUBE", key="btn_guardar_stats"):
                with st.spinner("Guardando estadísticas..."):
                    try:
                        filas_stats = []
                        for id_ in convocados_ids:
                            filas_stats.append({
                                "fecha": fecha_p_str,
                                "bloque": bloque_corto,
                                "jugador_id": str(id_),
                                "tackles": st.session_state.get(f"stat_tackles_{id_}_{llave_partido}", 0),
                                "pases": st.session_state.get(f"stat_pases_{id_}_{llave_partido}", 0),
                                "rucks": st.session_state.get(f"stat_rucks_{id_}_{llave_partido}", 0),
                                "apoyos": st.session_state.get(f"stat_apoyos_{id_}_{llave_partido}", 0),
                            })
                        supabase.table("estadisticas_partido").upsert(
                            filas_stats, on_conflict="fecha,bloque,jugador_id"
                        ).execute()
                        st.success("¡Estadísticas guardadas correctamente!")
                    except Exception as e:
                        st.error(f"Error al guardar estadísticas: {e}")

# ──────────────────────────────────────────────
# MÓDULO 4: ESTADÍSTICAS — EVOLUCIÓN DEL JUGADOR
# ──────────────────────────────────────────────
elif st.session_state.pantalla_actual == "Estadísticas":
    if st.button("⬅️ Volver al Menú Principal", key="back_stats"):
        st.session_state.pantalla_actual = "Inicio"; st.rerun()

    st.header("📊 Evolución del Jugador")

    # Selector de jugador
    opciones_jugadores = {
        id_: f"{datos['apellido']} {datos['nombre']}"
        for id_, datos in st.session_state.plantel.items()
    }
    jugador_sel_nombre = st.selectbox(
        "Seleccioná un jugador:",
        options=list(opciones_jugadores.values()),
        key="sel_jugador_stats"
    )
    jugador_sel_id = [id_ for id_, nombre in opciones_jugadores.items() if nombre == jugador_sel_nombre][0]

    if st.button("🔍 Ver Estadísticas", key="btn_ver_stats"):
        try:
            res = supabase.table("estadisticas_partido").select("*").eq("jugador_id", jugador_sel_id).order("fecha").execute()
            datos_jugador = res.data

            if not datos_jugador:
                st.info("Este jugador aún no tiene estadísticas registradas.")
            else:
                df = pd.DataFrame(datos_jugador)
                df["fecha"] = pd.to_datetime(df["fecha"])
                df = df.sort_values("fecha")
                df["fecha_label"] = df["fecha"].dt.strftime("%d/%m") + " (" + df["bloque"] + ")"

                st.write(f"### {jugador_sel_nombre}")
                st.write(f"Puesto: **{st.session_state.plantel[jugador_sel_id].get('puesto','Sin Puesto')}**")
                st.write("---")

                # Tabla resumen
                tabla = df[["fecha_label", "tackles", "pases", "rucks", "apoyos"]].rename(columns={
                    "fecha_label": "Partido",
                    "tackles": "🛡️ Tackles",
                    "pases": "🤾 Pases",
                    "rucks": "💥 Rucks",
                    "apoyos": "🤝 Apoyos"
                })
                st.dataframe(tabla, use_container_width=True, hide_index=True)

                # Totales
                st.write("**Totales acumulados:**")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("🛡️ Tackles", int(df["tackles"].sum()))
                col2.metric("🤾 Pases", int(df["pases"].sum()))
                col3.metric("💥 Rucks", int(df["rucks"].sum()))
                col4.metric("🤝 Apoyos", int(df["apoyos"].sum()))

                st.write("---")

                # Gráfico de evolución
                if len(df) > 1:
                    fig, ax = plt.subplots(figsize=(8, 4))
                    fig.patch.set_facecolor('#1E1E1E')
                    ax.set_facecolor('#2A2A2A')
                    for stat, color, label in [
                        ("tackles", "#F4C430", "🛡️ Tackles"),
                        ("pases", "#4FC3F7", "🤾 Pases"),
                        ("rucks", "#EF5350", "💥 Rucks"),
                        ("apoyos", "#66BB6A", "🤝 Apoyos"),
                    ]:
                        ax.plot(df["fecha_label"], df[stat], marker='o', label=label, color=color, linewidth=2)
                    ax.set_xlabel("Partido", color="white")
                    ax.set_ylabel("Cantidad", color="white")
                    ax.tick_params(colors="white")
                    ax.legend(facecolor="#2A2A2A", labelcolor="white")
                    plt.xticks(rotation=30, ha='right')
                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.info("Se necesitan al menos 2 partidos para mostrar el gráfico de evolución.")

        except Exception as e:
            st.error(f"Error al cargar estadísticas: {e}")
