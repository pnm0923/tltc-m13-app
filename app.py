import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont
import io
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
BUCKET = "fotos-jugadores"

def get_foto_url(jugador_id):
    try:
        return supabase.storage.from_(BUCKET).get_public_url(f"{jugador_id}.jpg")
    except:
        return None

def subir_foto(jugador_id, archivo_bytes, content_type="image/jpeg"):
    try:
        path = f"{jugador_id}.jpg"
        try:
            supabase.storage.from_(BUCKET).remove([path])
        except:
            pass
        supabase.storage.from_(BUCKET).upload(
            path=path, file=archivo_bytes,
            file_options={"content-type": content_type, "upsert": "true"}
        )
        return True
    except Exception as e:
        st.error(f"Error al subir foto: {e}")
        return False

def cargar_imagen_desde_url(url):
    try:
        resp = requests.get(url, timeout=5)
        return Image.open(io.BytesIO(resp.content)).convert("RGB")
    except:
        return None

@st.cache_resource
def cargar_avatar_base():
    """Carga avatar_jugador.png una sola vez y recorta del pecho hacia arriba (mitad superior)."""
    try:
        avatar = Image.open("avatar_jugador.png").convert("RGB")
        w, h = avatar.size
        # Recortar solo la mitad superior (pecho hacia arriba)
        recorte = avatar.crop((0, 0, w, h // 2))
        return recorte
    except:
        return None

def crear_avatar(numero, size=150):
    """Devuelve el avatar del jugador recortado y redimensionado al tamaño pedido."""
    base = cargar_avatar_base()
    if base:
        return base.resize((size, size), Image.LANCZOS)
    # Fallback si no encuentra el archivo
    img = Image.new("RGB", (size, size), color=(43, 62, 117))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size=52)
    except:
        font = ImageFont.load_default()
    text = str(numero)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.text(((size-tw)/2, (size-th)/2 - 4), text, fill=(244, 196, 48), font=font)
    return img

def generar_placa(convocados_ids, bloque_nombre, rival, fecha_str):
    FORWARDS  = {"Pilar", "Hooker", "2° Linea", "3° Linea"}
    BACKS     = {"Medio scrum", "Apertura", "Centro", "Wing", "Fullback"}

    HEADER_H  = 225
    MARGEN_X  = 48
    ROW_H     = 46
    SECTION_H = 36
    W         = 720

    # Clasificar ANTES de crear la imagen para calcular altura exacta
    forwards, backs, sin_puesto = [], [], []
    for jid in convocados_ids:
        puesto = st.session_state.plantel.get(str(jid), {}).get("puesto", "Sin Puesto")
        if puesto in FORWARDS:
            forwards.append(jid)
        elif puesto in BACKS:
            backs.append(jid)
        else:
            sin_puesto.append(jid)

    secciones = []
    if forwards:   secciones.append(("Forwards", forwards))
    if backs:      secciones.append(("Backs", backs))
    if sin_puesto: secciones.append(("Sin Puesto Asignado", sin_puesto))

    total_filas = sum(len(j) for _, j in secciones)
    H = HEADER_H + 10 + len(secciones) * (SECTION_H + 14) + total_filas * ROW_H + 40

    img  = Image.new("RGB", (W, H), color=(12, 12, 12))
    draw = ImageDraw.Draw(img)

    try:
        font_title   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 27)
        font_sub     = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
        font_section = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
        font_jugador = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_puesto  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        font_small   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    except:
        font_title = font_sub = font_section = font_jugador = font_puesto = font_small = ImageFont.load_default()

    AMARILLO = (244, 196, 48)
    AZUL     = (43, 62, 117)
    BLANCO   = (255, 255, 255)
    GRIS     = (160, 160, 160)
    GRIS_OSC = (38, 38, 38)

    for y in range(HEADER_H):
        t = y / HEADER_H
        draw.line([(0, y), (W, y)], fill=(int(43+(12-43)*t), int(62+(12-62)*t), int(117+(12-117)*t)))

    escudo_size, escudo_y = 118, 16
    try:
        escudo = Image.open("escudo.png").convert("RGBA")
        escudo = escudo.resize((escudo_size, escudo_size), Image.LANCZOS)
        img.paste(escudo, ((W - escudo_size) // 2, escudo_y), escudo)
    except:
        cx, cy = W // 2, escudo_y + escudo_size // 2
        draw.ellipse([cx-50, cy-50, cx+50, cy+50], fill=AZUL, outline=AMARILLO, width=3)

    titulo = "TUCUMAN LAWN TENNIS CLUB"
    bb = draw.textbbox((0,0), titulo, font=font_title)
    draw.text(((W-(bb[2]-bb[0]))//2, escudo_y+escudo_size+6), titulo, fill=AMARILLO, font=font_title)

    sub = f"{bloque_nombre}  vs  {rival}  -  {fecha_str}"
    bb2 = draw.textbbox((0,0), sub, font=font_small)
    draw.text(((W-(bb2[2]-bb2[0]))//2, escudo_y+escudo_size+40), sub, fill=GRIS, font=font_small)
    draw.line([(30, HEADER_H-8), (W-30, HEADER_H-8)], fill=AMARILLO, width=2)

    y_cursor = HEADER_H + 10

    def dibujar_seccion(titulo_sec, jugadores):
        nonlocal y_cursor
        draw.rectangle([(MARGEN_X, y_cursor), (W-MARGEN_X, y_cursor+SECTION_H)], fill=AZUL)
        draw.line([(MARGEN_X, y_cursor+SECTION_H), (W-MARGEN_X, y_cursor+SECTION_H)], fill=AMARILLO, width=1)
        bbs = draw.textbbox((0,0), titulo_sec.upper(), font=font_section)
        draw.text(((W-(bbs[2]-bbs[0]))//2, y_cursor+8), titulo_sec.upper(), fill=AMARILLO, font=font_section)
        y_cursor += SECTION_H + 4
        for i, jid in enumerate(jugadores):
            datos = st.session_state.plantel.get(str(jid), {})
            nombre_completo = f"{datos.get('apellido', '???').upper()} {datos.get('nombre', '').upper()}".strip()
            puesto = datos.get("puesto", "")
            fondo  = (22, 22, 22) if i % 2 == 0 else GRIS_OSC
            draw.rectangle([(MARGEN_X, y_cursor), (W-MARGEN_X, y_cursor+ROW_H-2)], fill=fondo)
            draw.text((MARGEN_X+14, y_cursor+12), nombre_completo, fill=BLANCO, font=font_jugador)
            pb = draw.textbbox((0,0), puesto, font=font_puesto)
            draw.text((W-MARGEN_X-(pb[2]-pb[0])-10, y_cursor+16), puesto, fill=GRIS, font=font_puesto)
            y_cursor += ROW_H
        y_cursor += 10

    for titulo_sec, jugadores in secciones:
        dibujar_seccion(titulo_sec, jugadores)

    draw.line([(30, y_cursor+4), (W-30, y_cursor+4)], fill=AMARILLO, width=1)
    return img


# SEMILLA DEL PLANTEL
if 'plantel' not in st.session_state:
    nombres_crudos = [
        "ARGANARAZ BAUTISTA", "BANEGAS MAXIMO", "BELLIDO IVO", "BERTINI ANTONIO", "BERTINI DIEGO",
        "BUENO RISCO LISANDRO", "CANO PAOLETTI SALVADOR", "CARRASCO IGNACIO", "CISNEROS POSSE MAXIMO",
        "CORONEL BLAS", "CORONEL STEFANO", "CORROTO RODRIGO", "CRIPOVICH JUAN IGNACIO", "CRUZADO BAUTISTA",
        "DEL TOSO BENJAMIN", "FERNANDEZ CORREA JUAN MARTIN", "FERNANDEZ FELIPE IGNACIO", "GARCIA COLLADOS MAXIMO",
        "GIBILISCO MATEO", "GIJON BENJAMIN", "GUARDIA GERONIMO", "HERRERA BENJAMIN", "INGARAMO BAUTISTA",
        "JUAREZ COLLADO LUCAS", "LIZARRAGA PALACIOS BAUTISTA", "LOBO HERRERA VICENTE", "MAIZEL FACUNDO",
        "MARIGLIANO LORENZO", "MARQUESTO MARTIN", "MEJAIL FRANCISCO", "MOLINA FRANCISCO", "MOROF MAXIMILANO",
        "NELLA CASTRO ANTONIO", "NORES PONDAL LORENZO", "ORTIZ FELIPE", "PALAVECINO JOAQUIN", "PEIRO JUAN PABLO",
        "PEREZ FELIPE IGNACIO", "PEZZA ARQUEZ SOLANO", "PONCE DIAZ ELISEO", "PONCE MATEO", "RAIDEN RECUPERO BIEL",
        "RODRIGUEZ BELMONTE FRANCISCO", "RUIZ MENDILARZU MANUEL", "SALAZAR BENICIO", "SASSI BERNARDO",
        "SILVA SANTIAGO", "SOLBES FACUNDO", "SOSA LORENZO", "SOUBIE PEDRO", "TOMAS FELIPE", "VALLE PADUA FELIPE",
        "VELAZQUEZ FELIPE", "VIOLETTO OCTAVIO", "VIOTTI JUAN MARTIN"
    ]
    st.session_state.plantel = {
        str(i+1): {
            "apellido": nombre.split()[0], "nombre": " ".join(nombre.split()[1:]),
            "nacimiento": datetime.date(2013, 1, 1), "puesto": "Sin Puesto", "foto": None,
            "notas_tecnicas": "", "notas_actitud": ""
        } for i, nombre in enumerate(nombres_crudos)
    }
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

# PANTALLA PRINCIPAL
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
        st.markdown('<div class="menu-card"><h4>👥 Plantel Actual</h4><p>Lista, puestos, fotos y notas</p></div>', unsafe_allow_html=True)
        if st.button("Ir a Plantel", key="btn_plantel"):
            st.session_state.pantalla_actual = "Plantel"; st.rerun()
        st.markdown('<div class="menu-card"><h4>📋 Asistencia Entr.</h4><p>Cargar fecha y presentes</p></div>', unsafe_allow_html=True)
        if st.button("Ir a Asistencia", key="btn_asistencia"):
            st.session_state.pantalla_actual = "Asistencia"; st.rerun()
    with col_b:
        st.markdown('<div class="menu-card"><h4>🏉 Partidos</h4><p>Convocatoria, stats y placa</p></div>', unsafe_allow_html=True)
        if st.button("Ir a Partidos", key="btn_partidos"):
            st.session_state.pantalla_actual = "Partidos"; st.rerun()
        st.markdown('<div class="menu-card"><h4>📊 Estadísticas</h4><p>Ver evolución del jugador</p></div>', unsafe_allow_html=True)
        if st.button("Ir a Estadísticas", key="btn_stats"):
            st.session_state.pantalla_actual = "Estadísticas"; st.rerun()

# MÓDULO 1: ASISTENCIA
elif st.session_state.pantalla_actual == "Asistencia":
    if st.button("⬅️ Volver al Menú Principal", key="back_asist"):
        st.session_state.pantalla_actual = "Inicio"; st.rerun()
    st.header("📋 Asistencia a Entrenamiento")
    fecha = st.date_input("Fecha del Entrenamiento", datetime.date.today(), key="selector_fecha_entr")
    fecha_str = fecha.strftime("%Y-%m-%d")
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
                filas = [{"fecha": fecha_str, "jugador_id": str(id_),
                          "presente": st.session_state.get(f"chk_asist_{id_}_{fecha_str}", False)}
                         for id_ in st.session_state.plantel.keys()]
                supabase.table("asistencias_entrenamiento").upsert(filas, on_conflict="fecha,jugador_id").execute()
                st.success("¡Asistencia guardada con éxito!")
            except Exception as e:
                st.error(f"Error al guardar: {e}")

# MÓDULO 2: PLANTEL
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
                col_foto, col_datos = st.columns([1, 2])
                with col_foto:
                    url_foto = get_foto_url(id_)
                    if url_foto:
                        st.image(url_foto, width=120)
                    else:
                        st.markdown("📷 Sin foto")
                    archivo = st.file_uploader("Subir foto", type=["jpg","jpeg","png"], key=f"foto_upload_{id_}")
                    if archivo is not None:
                        if st.button("📤 Guardar foto", key=f"btn_foto_{id_}"):
                            img_pil = Image.open(archivo).convert("RGB")
                            buf = io.BytesIO()
                            img_pil.save(buf, format="JPEG", quality=85)
                            if subir_foto(id_, buf.getvalue(), "image/jpeg"):
                                st.success("Foto guardada.")
                                st.rerun()
                with col_datos:
                    indice_puesto = LISTA_PUESTOS.index(puesto_actual) if puesto_actual in LISTA_PUESTOS else 0
                    nuevo_puesto = st.selectbox("Asignar Puesto:", LISTA_PUESTOS, index=indice_puesto, key=f"puesto_{id_}")
                    nota_act = st.text_area("🌟 Notas Actitudinales:", datos["notas_actitud"], key=f"act_{id_}")
                    nota_tec = st.text_area("🏉 Notas Técnicas:", datos["notas_tecnicas"], key=f"tec_{id_}")
                    st.session_state.plantel[id_]["puesto"] = nuevo_puesto
                    st.session_state.plantel[id_]["notas_actitud"] = nota_act
                    st.session_state.plantel[id_]["notas_tecnicas"] = nota_tec

                # Estadistica de asistencia
                st.write("---")
                try:
                    res_asist = supabase.table("asistencias_entrenamiento").select("presente").eq("jugador_id", str(id_)).execute()
                    total     = len(res_asist.data)
                    presentes = sum(1 for r in res_asist.data if r["presente"])
                    ausentes  = total - presentes
                    porcentaje = int((presentes / total) * 100) if total > 0 else 0
                    col_p, col_a, col_pct = st.columns(3)
                    col_p.markdown(f"<span style=\'color:#4CAF50; font-weight:bold; font-size:15px\'>Entrenamiento: {presentes} presentes</span>", unsafe_allow_html=True)
                    col_a.markdown(f"<span style=\'color:#F44336; font-weight:bold; font-size:15px\'>{ausentes} ausentes</span>", unsafe_allow_html=True)
                    col_pct.markdown(f"<span style=\'color:#F4C430; font-weight:bold; font-size:15px\'>{porcentaje}%</span>", unsafe_allow_html=True)
                except Exception as e_asist:
                    st.caption(f"No se pudo cargar asistencia: {e_asist}")
    st.write("---")
    if st.button("💾 GUARDAR MODIFICACIONES DEL PLANTEL", key="btn_guardar_fichas_nube"):
        with st.spinner("Sincronizando puestos y notas con la nube..."):
            try:
                filas = [{"jugador_id": str(id_), "puesto": datos["puesto"],
                          "notas_actitud": datos["notas_actitud"], "notas_tecnicas": datos["notas_tecnicas"]}
                         for id_, datos in st.session_state.plantel.items()]
                supabase.table("datos_plantel").upsert(filas, on_conflict="jugador_id").execute()
                st.success("¡Plantel guardado correctamente!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")

# MÓDULO 3: PARTIDOS
elif st.session_state.pantalla_actual == "Partidos":
    if st.button("⬅️ Volver al Menú Principal", key="back_partidos"):
        st.session_state.pantalla_actual = "Inicio"; st.rerun()
    st.header("🏉 Partidos y Estadísticas en Vivo")
    lista_rivales = ["Seleccionar rival...", "Tucuman Rugby", "Universitario", "Jockey Club",
        "Cardenales", "Natacion y Gimnasia", "Los Tarcos", "Lince",
        "Huirapuca", "Aguara Guazu", "San Martin/Liceo/Corsarios"]
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        bloque_seleccionado = st.selectbox("Bloque TLTC",
            ["Tucuman Lawn Tennis Azul", "Tucuman Lawn Tennis Amarillo"], key="sb_bloque")
    with col_p2:
        rival_seleccionado = st.selectbox("Rival", lista_rivales, key="sb_rival")
    fecha_partido = st.date_input("Fecha del Partido", datetime.date.today(), key="di_fecha_partido")
    fecha_p_str = fecha_partido.strftime("%Y-%m-%d")
    bloque_corto = 'Azul' if 'Azul' in bloque_seleccionado else 'Amarillo'
    llave_partido = f"{fecha_p_str}_{bloque_corto}"
    st.write("---")

    tab_conv, tab_stats = st.tabs(["📋 Convocatoria", "📊 Stats en Vivo"])

    with tab_conv:
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
            if st.button("Convocar a Todos", key="btn_conv_todos"):
                for id_ in st.session_state.plantel.keys():
                    st.session_state[f"chk_p_{id_}_{llave_partido}"] = True
                st.rerun()
        with col_c2:
            if st.button("Limpiar Convocatoria", key="btn_conv_limpiar"):
                for id_ in st.session_state.plantel.keys():
                    st.session_state[f"chk_p_{id_}_{llave_partido}"] = False
                st.rerun()

        # Clasificar jugadores por sección
        FORWARDS_P = {"Pilar", "Hooker", "2° Linea", "3° Linea"}
        BACKS_P    = {"Medio scrum", "Apertura", "Centro", "Wing", "Fullback"}
        forwards_list, backs_list, sinpuesto_list = [], [], []
        for id_, datos in st.session_state.plantel.items():
            puesto = datos.get("puesto", "Sin Puesto")
            if puesto in FORWARDS_P:
                forwards_list.append((id_, datos))
            elif puesto in BACKS_P:
                backs_list.append((id_, datos))
            else:
                sinpuesto_list.append((id_, datos))

        # Inicializar claves faltantes
        for id_ in st.session_state.plantel.keys():
            clave = f"chk_p_{id_}_{llave_partido}"
            if clave not in st.session_state:
                st.session_state[clave] = False

        def seccion_convocatoria(titulo, jugadores):
            convocados_sec = sum(1 for id_, _ in jugadores if st.session_state.get(f"chk_p_{id_}_{llave_partido}", False))
            with st.expander(f"{titulo} ({convocados_sec}/{len(jugadores)} convocados)", expanded=False):
                for id_, datos in jugadores:
                    nombre_completo = f"{datos['apellido']} {datos['nombre']}"
                    puesto = datos.get("puesto", "Sin Puesto")
                    clave = f"chk_p_{id_}_{llave_partido}"
                    col_chk, col_pst = st.columns([3, 1])
                    with col_chk:
                        st.checkbox(nombre_completo, key=clave)
                    with col_pst:
                        st.caption(puesto)

        seccion_convocatoria("Forwards", forwards_list)
        seccion_convocatoria("Backs", backs_list)
        if sinpuesto_list:
            seccion_convocatoria("Sin Puesto Asignado", sinpuesto_list)

        convocados_count = sum(1 for id_ in st.session_state.plantel.keys()
                               if st.session_state.get(f"chk_p_{id_}_{llave_partido}", False))
        st.write(f"**Convocados: {convocados_count} jugadores**")
        if st.button("💾 GUARDAR CONVOCATORIA Y GENERAR PLACA", key="btn_guardar_conv"):
            with st.spinner("Guardando y generando placa..."):
                try:
                    filas_conv = [{"fecha": fecha_p_str, "bloque": bloque_corto,
                                   "jugador_id": str(id_),
                                   "convocado": st.session_state.get(f"chk_p_{id_}_{llave_partido}", False)}
                                  for id_ in st.session_state.plantel.keys()]
                    supabase.table("convocados_partidos").upsert(filas_conv, on_conflict="fecha,bloque,jugador_id").execute()
                    st.success("¡Convocatoria guardada!")
                    # Generar placa automáticamente
                    ids_conv = [id_ for id_ in st.session_state.plantel.keys()
                                if st.session_state.get(f"chk_p_{id_}_{llave_partido}", False)]
                    if ids_conv and rival_seleccionado != "Seleccionar rival...":
                        fecha_display = fecha_partido.strftime("%d/%m/%Y")
                        placa_img = generar_placa(ids_conv, bloque_seleccionado, rival_seleccionado, fecha_display)
                        buf = io.BytesIO()
                        placa_img.save(buf, format="PNG")
                        buf.seek(0)
                        st.image(placa_img, use_container_width=True)
                        st.download_button(
                            label="📥 Descargar placa para WhatsApp",
                            data=buf,
                            file_name=f"placa_{bloque_corto}_{fecha_p_str}.png",
                            mime="image/png",
                            key="btn_download_placa"
                        )
                except Exception as e:
                    st.error(f"Error: {e}")

    with tab_stats:
        if rival_seleccionado == "Seleccionar rival...":
            st.info("Seleccioná un rival arriba para cargar estadísticas.")
        else:
            convocados_ids = [id_ for id_ in st.session_state.plantel.keys()
                              if st.session_state.get(f"chk_p_{id_}_{llave_partido}", False)]
            if not convocados_ids:
                st.warning("No hay jugadores convocados. Guardá la convocatoria primero.")
            else:
                llave_stats = f"stats_loaded_{llave_partido}"
                if not st.session_state.get(llave_stats, False):
                    try:
                        res_stats = supabase.table("estadisticas_partido").select("*").eq("fecha", fecha_p_str).eq("bloque", bloque_corto).execute()
                        for row in res_stats.data:
                            j_id = str(row["jugador_id"])
                            for stat in ["tackles", "pases", "rucks", "apoyos"]:
                                st.session_state[f"stat_{stat}_{j_id}_{llave_partido}"] = row.get(stat, 0)
                        st.session_state[llave_stats] = True
                    except Exception as e:
                        st.warning(f"No se pudieron cargar stats previas: {e}")
                for id_ in convocados_ids:
                    for stat in ["tackles", "pases", "rucks", "apoyos"]:
                        key = f"stat_{stat}_{id_}_{llave_partido}"
                        if key not in st.session_state:
                            st.session_state[key] = 0
                st.write(f"**{bloque_seleccionado} vs {rival_seleccionado} — {fecha_partido.strftime('%d/%m/%Y')}**")
                for id_ in convocados_ids:
                    datos = st.session_state.plantel[id_]
                    nombre_completo = f"{datos['apellido']} {datos['nombre']}"
                    with st.expander(f"🏃 {nombre_completo} | {datos.get('puesto','Sin Puesto')}"):
                        for stat, label in {"tackles":"🛡️ Tackles","pases":"🤾 Pases","rucks":"💥 Rucks","apoyos":"🤝 Apoyos"}.items():
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
                            filas_stats = [{"fecha": fecha_p_str, "bloque": bloque_corto,
                                            "jugador_id": str(id_),
                                            "tackles": st.session_state.get(f"stat_tackles_{id_}_{llave_partido}", 0),
                                            "pases": st.session_state.get(f"stat_pases_{id_}_{llave_partido}", 0),
                                            "rucks": st.session_state.get(f"stat_rucks_{id_}_{llave_partido}", 0),
                                            "apoyos": st.session_state.get(f"stat_apoyos_{id_}_{llave_partido}", 0)}
                                           for id_ in convocados_ids]
                            supabase.table("estadisticas_partido").upsert(
                                filas_stats, on_conflict="fecha,bloque,jugador_id").execute()
                            st.success("¡Estadísticas guardadas!")
                        except Exception as e:
                            st.error(f"Error: {e}")


# MÓDULO 4: ESTADÍSTICAS
elif st.session_state.pantalla_actual == "Estadísticas":
    if st.button("⬅️ Volver al Menú Principal", key="back_stats"):
        st.session_state.pantalla_actual = "Inicio"; st.rerun()
    st.header("📊 Evolución del Jugador")
    opciones_jugadores = {id_: f"{datos['apellido']} {datos['nombre']}"
                          for id_, datos in st.session_state.plantel.items()}
    jugador_sel_nombre = st.selectbox("Seleccioná un jugador:",
                                      options=list(opciones_jugadores.values()), key="sel_jugador_stats")
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
                tabla = df[["fecha_label","tackles","pases","rucks","apoyos"]].rename(columns={
                    "fecha_label":"Partido","tackles":"🛡️ Tackles","pases":"🤾 Pases","rucks":"💥 Rucks","apoyos":"🤝 Apoyos"})
                st.dataframe(tabla, use_container_width=True, hide_index=True)
                st.write("**Totales acumulados:**")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("🛡️ Tackles", int(df["tackles"].sum()))
                col2.metric("🤾 Pases", int(df["pases"].sum()))
                col3.metric("💥 Rucks", int(df["rucks"].sum()))
                col4.metric("🤝 Apoyos", int(df["apoyos"].sum()))
                if len(df) > 1:
                    st.write("---")
                    fig, ax = plt.subplots(figsize=(8, 4))
                    fig.patch.set_facecolor('#1E1E1E')
                    ax.set_facecolor('#2A2A2A')
                    for stat, color, label in [
                        ("tackles","#F4C430","🛡️ Tackles"),("pases","#4FC3F7","🤾 Pases"),
                        ("rucks","#EF5350","💥 Rucks"),("apoyos","#66BB6A","🤝 Apoyos")]:
                        ax.plot(df["fecha_label"], df[stat], marker='o', label=label, color=color, linewidth=2)
                    ax.set_xlabel("Partido", color="white")
                    ax.set_ylabel("Cantidad", color="white")
                    ax.tick_params(colors="white")
                    ax.legend(facecolor="#2A2A2A", labelcolor="white")
                    plt.xticks(rotation=30, ha='right')
                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.info("Se necesitan al menos 2 partidos para el gráfico de evolución.")
        except Exception as e:
            st.error(f"Error al cargar estadísticas: {e}")
