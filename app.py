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

def crear_avatar(numero, size=150):
    img = Image.new("RGB", (size, size), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    draw.ellipse([6, 6, size-6, size-6], fill=(43, 62, 117), outline=(244, 196, 48), width=4)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size=52)
    except:
        font = ImageFont.load_default()
    text = str(numero)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.text(((size-tw)/2, (size-th)/2 - 4), text, fill=(244, 196, 48), font=font)
    return img

def generar_placa(titulares_ids, suplentes_ids, bloque_nombre, rival, fecha_str):
    W, H = 1100, 980
    CELL_W, CELL_H = 200, 235
    FOTO_SIZE = 148

    img = Image.new("RGB", (W, H), color=(12, 12, 12))
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        font_name  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 19)
        font_num   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
        font_sub   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except:
        font_title = font_name = font_num = font_sub = font_small = ImageFont.load_default()

    AMARILLO = (244, 196, 48)
    AZUL     = (43, 62, 117)
    BLANCO   = (255, 255, 255)
    GRIS     = (170, 170, 170)

    # Degradado superior
    for y in range(85):
        t = y / 85
        r = int(12 + (43-12)*t)
        g = int(12 + (62-12)*t)
        b = int(12 + (117-12)*t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Título
    titulo = "TUCUMÁN LAWN TENNIS CLUB"
    bb = draw.textbbox((0,0), titulo, font=font_title)
    draw.text(((W-(bb[2]-bb[0]))//2, 15), titulo, fill=AMARILLO, font=font_title)

    # Subtítulo
    sub = f"{bloque_nombre}  vs  {rival}  —  {fecha_str}"
    bb2 = draw.textbbox((0,0), sub, font=font_small)
    draw.text(((W-(bb2[2]-bb2[0]))//2, 52), sub, fill=GRIS, font=font_small)

    draw.line([(30, 80), (W-30, 80)], fill=AMARILLO, width=2)

    def dibujar_jugador(pos_x, pos_y, jugador_id, numero):
        datos = st.session_state.plantel.get(str(jugador_id), {})
        apellido = datos.get("apellido", "???").upper()

        foto_img = None
        url = get_foto_url(str(jugador_id))
        if url:
            foto_img = cargar_imagen_desde_url(url)
        foto_img = foto_img.resize((FOTO_SIZE, FOTO_SIZE)) if foto_img else crear_avatar(numero, FOTO_SIZE)

        # Recorte circular
        mask = Image.new("L", (FOTO_SIZE, FOTO_SIZE), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, FOTO_SIZE, FOTO_SIZE], fill=255)
        foto_rgba = foto_img.convert("RGBA")
        foto_rgba.putalpha(mask)

        fx = pos_x + (CELL_W - FOTO_SIZE) // 2
        img.paste(foto_rgba, (fx, pos_y + 8), foto_rgba)
        draw.ellipse([fx-3, pos_y+5, fx+FOTO_SIZE+3, pos_y+FOTO_SIZE+11], outline=AMARILLO, width=3)

        # Número
        nr = 17
        ncx = fx + FOTO_SIZE - 4
        ncy = pos_y + 11
        draw.ellipse([ncx-nr, ncy-nr, ncx+nr, ncy+nr], fill=(8,8,8), outline=AMARILLO, width=2)
        ns = str(numero)
        nb = draw.textbbox((0,0), ns, font=font_num)
        nw, nh = nb[2]-nb[0], nb[3]-nb[1]
        draw.text((ncx-nw//2, ncy-nh//2-1), ns, fill=AMARILLO, font=font_num)

        # Apellido
        ab = draw.textbbox((0,0), apellido, font=font_name)
        aw = ab[2]-ab[0]
        draw.text((pos_x+(CELL_W-aw)//2, pos_y+FOTO_SIZE+16), apellido, fill=BLANCO, font=font_name)

    filas = [titulares_ids[0:5], titulares_ids[5:10], titulares_ids[10:15]]
    y_start = 92
    for fi, fila in enumerate(filas):
        x_offset = (W - len(fila)*CELL_W) // 2
        for ci, jid in enumerate(fila):
            dibujar_jugador(x_offset + ci*CELL_W, y_start + fi*CELL_H, jid, fi*5+ci+1)

    y_sep = y_start + 3*CELL_H + 12
    draw.line([(30, y_sep), (W-30, y_sep)], fill=AMARILLO, width=1)

    if suplentes_ids:
        partes = [f"{16+i} {st.session_state.plantel.get(str(jid),{}).get('apellido','???').upper()}"
                  for i, jid in enumerate(suplentes_ids)]
        texto = "   ".join(partes)
        sb = draw.textbbox((0,0), texto, font=font_sub)
        draw.text(((W-(sb[2]-sb[0]))//2, y_sep+12), texto, fill=AMARILLO, font=font_sub)

    # Escudo placeholder
    draw.ellipse([18, H-68, 76, H-10], fill=AZUL, outline=AMARILLO, width=2)
    eb = draw.textbbox((0,0), "TLTC", font=font_small)
    draw.text((47-(eb[2]-eb[0])//2, H-44), "TLTC", fill=AMARILLO, font=font_small)

    return img

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
    lista_rivales = ["Seleccionar rival...", "Tucumán Rugby", "Universitario", "Jockey Club",
        "Cardenales", "Natación y Gimnasia", "Los Tarcos", "Lince",
        "Huirapuca", "Aguará Guazú", "San Martín/Liceo/Corsarios"]
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        bloque_seleccionado = st.selectbox("Bloque TLTC",
            ["Tucumán Lawn Tennis Azul", "Tucumán Lawn Tennis Amarillo"], key="sb_bloque")
    with col_p2:
        rival_seleccionado = st.selectbox("Rival", lista_rivales, key="sb_rival")
    fecha_partido = st.date_input("Fecha del Partido", datetime.date.today(), key="di_fecha_partido")
    fecha_p_str = fecha_partido.strftime("%Y-%m-%d")
    bloque_corto = 'Azul' if 'Azul' in bloque_seleccionado else 'Amarillo'
    llave_partido = f"{fecha_p_str}_{bloque_corto}"
    st.write("---")

    tab_conv, tab_stats, tab_placa = st.tabs(["📋 Convocatoria", "📊 Stats en Vivo", "🖼️ Generar Placa"])

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
            if st.button("✔️ Convocar a Todos", key="btn_conv_todos"):
                for id_ in st.session_state.plantel.keys():
                    st.session_state[f"chk_p_{id_}_{llave_partido}"] = True
                st.rerun()
        with col_c2:
            if st.button("❌ Limpiar Convocatoria", key="btn_conv_limpiar"):
                for id_ in st.session_state.plantel.keys():
                    st.session_state[f"chk_p_{id_}_{llave_partido}"] = False
                st.rerun()
        buscar_conv = st.text_input("🔍 Buscar jugador...")
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
            with st.spinner("Guardando..."):
                try:
                    filas_conv = [{"fecha": fecha_p_str, "bloque": bloque_corto,
                                   "jugador_id": str(id_),
                                   "convocado": st.session_state.get(f"chk_p_{id_}_{llave_partido}", False)}
                                  for id_ in st.session_state.plantel.keys()]
                    supabase.table("convocados_partidos").upsert(filas_conv, on_conflict="fecha,bloque,jugador_id").execute()
                    st.success("¡Convocatoria guardada!")
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

    with tab_placa:
        st.subheader("🖼️ Generador de Placa de Convocatoria")
        if rival_seleccionado == "Seleccionar rival...":
            st.info("Seleccioná un rival arriba para generar la placa.")
        else:
            convocados_ids = [id_ for id_ in st.session_state.plantel.keys()
                              if st.session_state.get(f"chk_p_{id_}_{llave_partido}", False)]
            opciones_nombres = {id_: f"{datos['apellido']} {datos['nombre']}"
                                for id_, datos in st.session_state.plantel.items()}
            st.write("**Seleccioná los 15 titulares en orden (1 al 15):**")
            titulares_sel = []
            for i in range(1, 16):
                default_id = convocados_ids[i-1] if i-1 < len(convocados_ids) else list(opciones_nombres.keys())[0]
                default_nombre = opciones_nombres.get(default_id, "")
                opciones_lista = list(opciones_nombres.values())
                idx_default = opciones_lista.index(default_nombre) if default_nombre in opciones_lista else 0
                sel = st.selectbox(f"#{i}", options=opciones_lista, index=idx_default, key=f"titular_sel_{i}")
                sel_id = [id_ for id_, nombre in opciones_nombres.items() if nombre == sel][0]
                titulares_sel.append(sel_id)
            titulares_set = set(titulares_sel)
            suplentes_sel = [id_ for id_ in convocados_ids if id_ not in titulares_set]
            st.write("**Suplentes:**")
            if suplentes_sel:
                for id_ in suplentes_sel:
                    st.write(f"• {opciones_nombres[id_]}")
            else:
                st.write("_Sin suplentes cargados_")
            st.write("---")
            if st.button("🖼️ GENERAR PLACA", key="btn_generar_placa"):
                with st.spinner("Generando placa..."):
                    fecha_display = fecha_partido.strftime("%d/%m/%Y")
                    placa_img = generar_placa(titulares_sel, suplentes_sel, bloque_seleccionado, rival_seleccionado, fecha_display)
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
