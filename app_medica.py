import streamlit as st
from google import genai
import sqlite3
import os
import hashlib
from PIL import Image
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN INICIAL
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="MedAssist Pro · Sistema Clínico",
    layout="wide",
    page_icon="🏥",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
# BASE DE DATOS DE MÉDICOS AUTORIZADOS (seed data)
# ═══════════════════════════════════════════════════════════════
MEDICOS = {
    "12345678": {"clave": "Pucallpa2026", "nombre": "Dra. Elsa María Gómez Vásquez", "especialidad": "Medicina Interna", "cmp": "012345"},
    "40451214": {"clave": "Pucallpa2026", "nombre": "Dr. Carlos Mendoza", "especialidad": "Medicina General", "cmp": "098765"},
    "73000000": {"clave": "Pucallpa2026", "nombre": "Dr. Paul Gómez", "especialidad": "Medicina General", "cmp": "054321"},
}

# ═══════════════════════════════════════════════════════════════
# CSS PROFESIONAL COMPLETO
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── RESET & GLOBALES ── */
.stApp [data-testid="stToolbar"] { display: none; }
header { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* ── FUENTES ── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

.stApp {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* ── LOGIN ── */
.login-wrapper {
    display: flex; justify-content: center; align-items: center;
    min-height: 80vh; padding: 20px;
}
.login-card {
    width: 100%; max-width: 420px;
    background: linear-gradient(145deg, #ffffff 0%, #f0f4f8 100%);
    border-radius: 24px; padding: 48px 40px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.05);
    border: 1px solid rgba(255,255,255,0.8);
    animation: fadeSlideUp 0.6s ease-out;
}
.login-logo {
    text-align: center; margin-bottom: 8px;
    font-size: 52px;
    animation: pulse-soft 2s infinite;
}
.login-title {
    text-align: center; font-size: 22px; font-weight: 700;
    color: #1a365d; margin-bottom: 4px; letter-spacing: -0.3px;
}
.login-subtitle {
    text-align: center; font-size: 13px; color: #718096;
    margin-bottom: 32px; font-weight: 400;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2027 0%, #203a43 50%, #2c5364 100%) !important;
}
section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
    transition: all 0.3s ease !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.15) !important;
    border-color: rgba(255,255,255,0.3) !important;
    transform: translateY(-1px) !important;
}

.sidebar-profile {
    background: rgba(255,255,255,0.06);
    border-radius: 16px; padding: 20px;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 20px;
}
.sidebar-profile-name {
    font-size: 17px; font-weight: 700; color: #fff !important;
    margin-bottom: 2px;
}
.sidebar-profile-spec {
    font-size: 12px; color: #81e6d9 !important;
    font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase;
    margin-bottom: 10px;
}
.sidebar-profile-cmp {
    font-size: 13px; color: #a0aec0 !important;
}
.sidebar-clock {
    text-align: center; padding: 12px;
    background: rgba(255,255,255,0.04);
    border-radius: 12px; margin-bottom: 16px;
    font-size: 13px; color: #a0aec0 !important;
}
.sidebar-divider {
    height: 1px; background: rgba(255,255,255,0.1);
    margin: 16px 0;
}

/* ── ENCABEZADO PRINCIPAL ── */
.main-header {
    background: linear-gradient(135deg, #1a365d 0%, #2c5282 60%, #2b6cb0 100%);
    border-radius: 20px; padding: 36px 40px;
    margin-bottom: 28px; position: relative; overflow: hidden;
    animation: fadeSlideUp 0.5s ease-out;
}
.main-header::before {
    content: ''; position: absolute; top: -50%; right: -20%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%);
    border-radius: 50%;
}
.main-header h1 {
    color: #fff; font-size: 28px; font-weight: 800;
    margin: 0 0 6px 0; letter-spacing: -0.5px;
    position: relative; z-index: 1;
}
.main-header p {
    color: #bee3f8; font-size: 14px; margin: 0;
    font-weight: 400; position: relative; z-index: 1;
}

/* ── TARJETAS / SECCIONES ── */
.section-card {
    background: #ffffff;
    border-radius: 16px; padding: 28px 32px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
    border: 1px solid #edf2f7;
    transition: box-shadow 0.3s ease;
    animation: fadeSlideUp 0.5s ease-out both;
}
.section-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.07);
}

.section-label {
    display: inline-flex; align-items: center; gap: 8px;
    font-size: 11px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1.2px;
    color: #718096; margin-bottom: 16px;
    padding: 6px 14px;
    background: #f7fafc; border-radius: 8px;
    border: 1px solid #e2e8f0;
}

/* ── TRIAJE ── */
.triaje-card {
    background: linear-gradient(135deg, #ebf8ff 0%, #ffffff 100%);
    border-radius: 16px; padding: 28px 32px;
    margin-bottom: 20px;
    border: 1px solid #bee3f8;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    animation: fadeSlideUp 0.5s ease-out 0.1s both;
}
.triaje-header {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 18px;
}
.triaje-badge {
    background: linear-gradient(135deg, #3182ce, #2b6cb0);
    color: white; padding: 6px 14px;
    border-radius: 8px; font-size: 12px;
    font-weight: 700; letter-spacing: 0.8px;
    text-transform: uppercase;
}
.triaje-title {
    font-size: 18px; font-weight: 700;
    color: #2d3748; margin: 0;
}

/* ── BOTÓN PRINCIPAL ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2b6cb0 0%, #3182ce 50%, #4299e1 100%) !important;
    border: none !important; border-radius: 14px !important;
    padding: 16px 32px !important; font-weight: 700 !important;
    font-size: 16px !important; letter-spacing: 0.3px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 14px rgba(49,130,206,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(49,130,206,0.45) !important;
}
.stButton > button[kind="primary"]:active {
    transform: translateY(0) !important;
}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    border-radius: 10px !important;
    border: 1.5px solid #e2e8f0 !important;
    padding: 10px 14px !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stNumberInput > div > div > input:focus {
    border-color: #3182ce !important;
    box-shadow: 0 0 0 3px rgba(49,130,206,0.1) !important;
}

/* ── ANIMACIÓN DE CARGA ── */
.loading-container {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 40px 20px;
    animation: fadeIn 0.3s ease;
}
.loading-ecg {
    width: 280px; height: 60px;
    margin-bottom: 20px;
}
.ecg-line {
    fill: none; stroke: #3182ce;
    stroke-width: 2.5;
    stroke-dasharray: 600;
    stroke-dashoffset: 600;
    animation: draw-ecg 2s linear infinite;
}
@keyframes draw-ecg {
    to { stroke-dashoffset: 0; }
}
.loading-text {
    font-size: 15px; font-weight: 600;
    color: #2d3748; margin-bottom: 6px;
}
.loading-sub {
    font-size: 13px; color: #718096;
    animation: pulse-soft 1.5s ease-in-out infinite;
}
.loading-dots::after {
    content: ''; animation: dots 1.5s steps(4, end) infinite;
}
@keyframes dots {
    0% { content: ''; }
    25% { content: '.'; }
    50% { content: '..'; }
    75% { content: '...'; }
}
.loading-bar-track {
    width: 260px; height: 4px;
    background: #e2e8f0; border-radius: 4px;
    overflow: hidden; margin-top: 16px;
}
.loading-bar-fill {
    width: 40%; height: 100%;
    background: linear-gradient(90deg, #3182ce, #63b3ed);
    border-radius: 4px;
    animation: loading-slide 1.2s ease-in-out infinite;
}
@keyframes loading-slide {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(350%); }
}

/* ── ANIMACIONES GENERALES ── */
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
@keyframes pulse-soft {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px; background: #f7fafc;
    border-radius: 12px; padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}
.stTabs [aria-selected="true"] {
    background: #fff !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
}

/* ── BADGE ESTADO ── */
.status-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px; border-radius: 20px;
    font-size: 12px; font-weight: 600;
}
.status-online {
    background: #c6f6d5; color: #22543d;
}
.status-dot {
    width: 7px; height: 7px;
    background: #38a169; border-radius: 50%;
    animation: pulse-soft 1.5s infinite;
}

/* ── IMAGEN UPLOAD ── */
.upload-zone {
    border: 2px dashed #cbd5e0; border-radius: 14px;
    padding: 24px; text-align: center;
    background: #f7fafc;
    transition: all 0.3s ease;
}
.upload-zone:hover {
    border-color: #3182ce;
    background: #ebf8ff;
}

/* ── SEPARADOR ── */
.custom-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #e2e8f0 20%, #e2e8f0 80%, transparent);
    margin: 28px 0;
}

/* ── RESULTADOS IA ── */
.resultado-wrapper {
    animation: fadeSlideUp 0.6s ease-out;
    margin-top: 20px;
}

/* ── IMPRESIÓN ── */
@media print {
    .stApp > header, .stSidebar, .stButton,
    [data-testid="stToolbar"], footer { display: none !important; }
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# BASE DE DATOS (inicializar ANTES del login)
# ═══════════════════════════════════════════════════════════════
conn = sqlite3.connect('historias_clinicas.db', check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS pacientes_v2 (
    dni TEXT PRIMARY KEY, nombres TEXT, apellidos TEXT,
    edad INTEGER, tipo_edad TEXT, triaje TEXT,
    antecedentes TEXT, sintomas TEXT, fecha_registro TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS medicos_db (
    dni TEXT PRIMARY KEY, nombre TEXT, especialidad TEXT,
    cmp TEXT, clave_hash TEXT, primera_vez INTEGER DEFAULT 1
)""")
c.execute("""CREATE TABLE IF NOT EXISTS admin_db (
    username TEXT PRIMARY KEY, clave_hash TEXT
)""")
conn.commit()


def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()


# Populate medicos_db from MEDICOS dict if empty
c.execute("SELECT COUNT(*) FROM medicos_db")
if c.fetchone()[0] == 0:
    for dni_m, info in MEDICOS.items():
        c.execute("INSERT INTO medicos_db VALUES (?,?,?,?,?,?)",
                  (dni_m, info["nombre"], info.get("especialidad", "Medicina General"),
                   info["cmp"], hash_pwd(info["clave"]), 0))
    conn.commit()

# Create default admin if not exists
c.execute("SELECT COUNT(*) FROM admin_db")
if c.fetchone()[0] == 0:
    c.execute("INSERT INTO admin_db VALUES (?,?)", ("admin", hash_pwd("Admin2026!")))
    conn.commit()


# ═══════════════════════════════════════════════════════════════
# INICIALIZAR ESTADO DE SESIÓN
# ═══════════════════════════════════════════════════════════════
defaults = {
    "authenticated": False,
    "is_admin": False,
    "medico_nombre": "",
    "medico_cmp": "",
    "medico_especialidad": "",
    "medico_dni": "",
    "primera_vez": False,
    "html_resultado": "",
    "mostrar_botones": False,
    "login_view": "seleccion",
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ═══════════════════════════════════════════════════════════════
# PANTALLA DE LOGIN
# ═══════════════════════════════════════════════════════════════
if not st.session_state["authenticated"] and not st.session_state["is_admin"]:
    st.markdown("<div style='height: 5vh'></div>", unsafe_allow_html=True)
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        st.markdown("""
            <div class="login-card">
                <div class="login-logo">
                    <svg width="70" height="70" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                      <rect x="15" y="35" width="70" height="55" rx="3" fill="#4299e1"/>
                      <rect x="35" y="10" width="30" height="30" rx="3" fill="#2b6cb0"/>
                      <rect x="44" y="15" width="12" height="20" fill="white"/>
                      <rect x="38" y="21" width="24" height="8" fill="white"/>
                      <rect x="20" y="55" width="15" height="15" rx="2" fill="white" opacity="0.8"/>
                      <rect x="65" y="55" width="15" height="15" rx="2" fill="white" opacity="0.8"/>
                      <rect x="38" y="55" width="24" height="35" rx="2" fill="white" opacity="0.9"/>
                      <rect x="44" y="62" width="12" height="10" fill="#4299e1"/>
                      <rect x="5" y="35" width="90" height="6" rx="2" fill="#2b6cb0"/>
                    </svg>
                </div>
                <div class="login-title">MedAssist Pro</div>
                <div class="login-subtitle">Sistema de Gestión Clínica · Seleccione tipo de acceso</div>
            </div>
        """, unsafe_allow_html=True)

        st.write("")
        tab_medico, tab_admin = st.tabs(["👨‍⚕️ Médico", "🔧 Administrador"])

        with tab_medico:
            with st.form("login_medico"):
                dni_login = st.text_input("🪪 DNI del Médico", max_chars=8, placeholder="8 dígitos numéricos")
                clave_login = st.text_input("🔑 Contraseña", type="password", placeholder="Ingrese su contraseña")
                st.write("")
                ingresar = st.form_submit_button("Ingresar al Sistema", use_container_width=True, type="primary")
                if ingresar:
                    if not dni_login.isdigit():
                        st.error("⚠️ El DNI solo debe contener números.")
                    else:
                        c.execute("SELECT nombre, especialidad, cmp, clave_hash, primera_vez FROM medicos_db WHERE dni=?", (dni_login,))
                        row = c.fetchone()
                        if row and row[3] == hash_pwd(clave_login):
                            st.session_state["authenticated"] = True
                            st.session_state["medico_nombre"] = row[0]
                            st.session_state["medico_especialidad"] = row[1]
                            st.session_state["medico_cmp"] = row[2]
                            st.session_state["medico_dni"] = dni_login
                            st.session_state["primera_vez"] = bool(row[4])
                            st.rerun()
                        else:
                            st.error("⚠️ DNI o contraseña incorrectos.")

        with tab_admin:
            with st.form("login_admin"):
                user_admin = st.text_input("👤 Usuario", placeholder="admin")
                clave_admin = st.text_input("🔑 Contraseña", type="password", placeholder="Contraseña de administrador")
                st.write("")
                ingresar_admin = st.form_submit_button("Acceder como Administrador", use_container_width=True)
                if ingresar_admin:
                    c.execute("SELECT clave_hash FROM admin_db WHERE username=?", (user_admin,))
                    row_a = c.fetchone()
                    if row_a and row_a[0] == hash_pwd(clave_admin):
                        st.session_state["is_admin"] = True
                        st.rerun()
                    else:
                        st.error("⚠️ Credenciales de administrador incorrectas.")
    st.stop()


# ═══════════════════════════════════════════════════════════════
# PRIMER LOGIN: CAMBIO DE CONTRASEÑA
# ═══════════════════════════════════════════════════════════════
if st.session_state.get("primera_vez") and st.session_state.get("authenticated"):
    st.markdown("<div style='height: 5vh'></div>", unsafe_allow_html=True)
    _, col_pwd, _ = st.columns([1, 1.2, 1])
    with col_pwd:
        st.markdown("""
            <div style="background:#fff; padding:32px; border-radius:16px;
                        box-shadow:0 4px 20px rgba(0,0,0,0.1); border-left:4px solid #e53e3e;">
                <h3 style="color:#c53030; margin-top:0;">🔐 Cambio de Contraseña Requerido</h3>
                <p style="color:#718096;">Es su primer inicio de sesión. Por seguridad, debe establecer una nueva contraseña.</p>
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        with st.form("cambiar_pwd"):
            nueva_pwd = st.text_input("Nueva contraseña", type="password", placeholder="Mínimo 6 caracteres")
            confirmar_pwd = st.text_input("Confirmar contraseña", type="password", placeholder="Repita la contraseña")
            cambiar = st.form_submit_button("Guardar nueva contraseña", use_container_width=True, type="primary")
            if cambiar:
                if len(nueva_pwd) < 6:
                    st.error("⚠️ La contraseña debe tener al menos 6 caracteres.")
                elif nueva_pwd != confirmar_pwd:
                    st.error("⚠️ Las contraseñas no coinciden.")
                else:
                    c.execute("UPDATE medicos_db SET clave_hash=?, primera_vez=0 WHERE dni=?",
                              (hash_pwd(nueva_pwd), st.session_state["medico_dni"]))
                    conn.commit()
                    st.session_state["primera_vez"] = False
                    st.success("✅ Contraseña actualizada. Redirigiendo...")
                    st.rerun()
    st.stop()


# ═══════════════════════════════════════════════════════════════
# PANEL DE ADMINISTRACIÓN
# ═══════════════════════════════════════════════════════════════
if st.session_state.get("is_admin"):
    st.markdown("""
        <div class="main-header">
            <h1>⚙️ Panel de Administración</h1>
            <p>Gestión de cuentas médicas · MedAssist Pro</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["➕ Agregar Médico", "👥 Lista de Médicos", "🗑️ Eliminar / Resetear"])

    with tab1:
        st.subheader("Registrar nuevo médico")
        with st.form("add_medico"):
            c1, c2 = st.columns(2)
            with c1:
                new_dni = st.text_input("DNI (8 dígitos)", max_chars=8, placeholder="Ej: 12345678")
                new_nombre = st.text_input("Nombre completo", placeholder="Nombres y Apellidos")
                new_esp = st.selectbox("Especialidad", ["Medicina General", "Medicina Interna", "Pediatría", "Cirugía", "Ginecología", "Cardiología", "Neurología", "Otro"])
            with c2:
                new_cmp = st.text_input("CMP", placeholder="Ej: 012345")
                new_pwd = st.text_input("Contraseña temporal", type="password", placeholder="Ej: P02@34m1")
                new_pwd2 = st.text_input("Confirmar contraseña", type="password")
            agregar = st.form_submit_button("✅ Registrar Médico", use_container_width=True, type="primary")
            if agregar:
                if not new_dni.isdigit() or len(new_dni) != 8:
                    st.error("⚠️ DNI debe tener 8 dígitos numéricos.")
                elif not new_nombre.strip():
                    st.error("⚠️ Ingrese el nombre completo.")
                elif not new_cmp.strip():
                    st.error("⚠️ Ingrese el CMP.")
                elif len(new_pwd) < 6:
                    st.error("⚠️ La contraseña debe tener al menos 6 caracteres.")
                elif new_pwd != new_pwd2:
                    st.error("⚠️ Las contraseñas no coinciden.")
                else:
                    try:
                        c.execute("INSERT INTO medicos_db VALUES (?,?,?,?,?,?)",
                                  (new_dni, new_nombre, new_esp, new_cmp, hash_pwd(new_pwd), 1))
                        conn.commit()
                        st.success(f"✅ Médico {new_nombre} registrado exitosamente. Deberá cambiar su contraseña al primer inicio de sesión.")
                    except Exception:
                        st.error("❌ Error: Ya existe un médico con ese DNI.")

    with tab2:
        st.subheader("Médicos registrados")
        c.execute("SELECT dni, nombre, especialidad, cmp, primera_vez FROM medicos_db ORDER BY nombre")
        medicos_list = c.fetchall()
        if medicos_list:
            for m in medicos_list:
                estado = "🔴 Primer ingreso pendiente" if m[4] else "🟢 Activo"
                st.markdown(f"""
                    <div style="background:#f7fafc; padding:12px 16px; border-radius:10px;
                                margin-bottom:8px; border-left:3px solid #4299e1;">
                        <strong>{m[1]}</strong> &nbsp;|&nbsp; DNI: {m[0]} &nbsp;|&nbsp;
                        {m[2]} &nbsp;|&nbsp; CMP: {m[3]} &nbsp;|&nbsp; {estado}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay médicos registrados.")

    with tab3:
        st.subheader("Eliminar cuenta o resetear contraseña")
        c.execute("SELECT dni, nombre FROM medicos_db ORDER BY nombre")
        opciones = c.fetchall()
        if opciones:
            opts_display = [f"{m[1]} (DNI: {m[0]})" for m in opciones]
            sel = st.selectbox("Seleccionar médico", opts_display)
            sel_dni = opciones[opts_display.index(sel)][0]

            col_del, col_reset = st.columns(2)
            with col_del:
                st.markdown("**Eliminar cuenta**")
                confirmar_del = st.checkbox("Confirmo que deseo eliminar esta cuenta")
                if st.button("🗑️ Eliminar cuenta", type="primary", disabled=not confirmar_del):
                    c.execute("DELETE FROM medicos_db WHERE dni=?", (sel_dni,))
                    conn.commit()
                    st.success("✅ Cuenta eliminada.")
                    st.rerun()
            with col_reset:
                st.markdown("**Resetear contraseña**")
                nueva_temp = st.text_input("Nueva contraseña temporal", type="password", key="reset_pwd")
                if st.button("🔄 Resetear contraseña"):
                    if len(nueva_temp) < 6:
                        st.error("⚠️ Mínimo 6 caracteres.")
                    else:
                        c.execute("UPDATE medicos_db SET clave_hash=?, primera_vez=1 WHERE dni=?",
                                  (hash_pwd(nueva_temp), sel_dni))
                        conn.commit()
                        st.success("✅ Contraseña reseteada. El médico deberá cambiarla al próximo inicio.")
        else:
            st.info("No hay médicos registrados.")

        st.divider()
        st.subheader("Cambiar contraseña de administrador")
        with st.form("change_admin_pwd"):
            pwd_actual = st.text_input("Contraseña actual", type="password")
            pwd_nueva = st.text_input("Nueva contraseña", type="password")
            pwd_conf = st.text_input("Confirmar nueva contraseña", type="password")
            cambiar_admin = st.form_submit_button("Cambiar contraseña admin")
            if cambiar_admin:
                c.execute("SELECT clave_hash FROM admin_db WHERE username='admin'")
                row_adm = c.fetchone()
                if not row_adm or row_adm[0] != hash_pwd(pwd_actual):
                    st.error("⚠️ Contraseña actual incorrecta.")
                elif len(pwd_nueva) < 6:
                    st.error("⚠️ Mínimo 6 caracteres.")
                elif pwd_nueva != pwd_conf:
                    st.error("⚠️ Las contraseñas no coinciden.")
                else:
                    c.execute("UPDATE admin_db SET clave_hash=? WHERE username='admin'", (hash_pwd(pwd_nueva),))
                    conn.commit()
                    st.success("✅ Contraseña de administrador actualizada.")

    st.write("")
    if st.button("🔓 Cerrar sesión de administrador", type="secondary"):
        st.session_state["is_admin"] = False
        st.rerun()
    st.stop()


# ═══════════════════════════════════════════════════════════════
# IA – CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════
API_KEY = (
    st.secrets.get("GEMINI_API_KEY", None)
    or os.environ.get("GEMINI_API_KEY", "AIzaSyCJTEPLPkzuJXd2ws1zsfJjfjKBHQgQwtA")
)
client = genai.Client(api_key=API_KEY)


# ═══════════════════════════════════════════════════════════════
# BARRA LATERAL
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
        <div style="text-align:center; margin-bottom: 10px;">
            <svg width="45" height="45" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
              <rect x="15" y="35" width="70" height="55" rx="3" fill="#4299e1"/>
              <rect x="35" y="10" width="30" height="30" rx="3" fill="#2b6cb0"/>
              <rect x="44" y="15" width="12" height="20" fill="white"/>
              <rect x="38" y="21" width="24" height="8" fill="white"/>
              <rect x="20" y="55" width="15" height="15" rx="2" fill="white" opacity="0.8"/>
              <rect x="65" y="55" width="15" height="15" rx="2" fill="white" opacity="0.8"/>
              <rect x="38" y="55" width="24" height="35" rx="2" fill="white" opacity="0.9"/>
              <rect x="44" y="62" width="12" height="10" fill="#4299e1"/>
              <rect x="5" y="35" width="90" height="6" rx="2" fill="#2b6cb0"/>
            </svg>
            <h2 style="margin: 4px 0 0 0; font-size: 20px; font-weight: 800; color: #fff !important; letter-spacing: -0.3px;">MedAssist Pro</h2>
            <span style="font-size: 11px; color: #81e6d9 !important; font-weight: 500; letter-spacing: 1px;">SISTEMA CLÍNICO v2.0</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    st.markdown(f"""
        <div class="sidebar-profile">
            <div class="sidebar-profile-name">{st.session_state['medico_nombre']}</div>
            <div class="sidebar-profile-spec">{st.session_state['medico_especialidad']}</div>
            <div class="sidebar-profile-cmp">CMP: {st.session_state['medico_cmp']}</div>
            <div style="margin-top: 10px;">
                <span class="status-badge status-online">
                    <span class="status-dot"></span> En servicio
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="sidebar-clock">
            📅 {datetime.now().strftime('%d de %B de %Y')}
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    st.markdown("""
        <p style="font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: #a0aec0 !important; margin-bottom: 8px;">
            Navegación
        </p>
    """, unsafe_allow_html=True)

    # Sección historial rápido
    with st.expander("📂 Buscar Historia Clínica"):
        buscar_dni = st.text_input("DNI del paciente", max_chars=8, key="buscar_dni", placeholder="Ej: 12345678")
        if st.button("🔍 Buscar", use_container_width=True):
            c.execute("SELECT * FROM pacientes_v2 WHERE dni = ?", (buscar_dni,))
            resultado = c.fetchone()
            if resultado:
                st.success(f"✅ {resultado[1]} {resultado[2]}")
                st.caption(f"Edad: {resultado[3]} {resultado[4]}")
                st.caption(f"Triaje: {resultado[5]}")
                st.caption(f"Antecedentes: {resultado[6]}")
                st.caption(f"Síntomas: {resultado[7]}")
            else:
                st.warning("No se encontró historia clínica.")

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    if st.button("🔓  Cerrar Sesión", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ═══════════════════════════════════════════════════════════════
# CONTENIDO PRINCIPAL
# ═══════════════════════════════════════════════════════════════

# — Encabezado —
st.markdown(f"""
    <div class="main-header">
        <h1>📋 Gestión de Historia Clínica y Diagnóstico</h1>
        <p>Evaluación clínica · {datetime.now().strftime('%d/%m/%Y')}</p>
    </div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# SECCIÓN 1: IDENTIFICACIÓN DEL PACIENTE
# ═══════════════════════════════════════════════════════════════
st.markdown("""
    <div class="section-card">
        <div class="section-label">👤 Identificación del Paciente</div>
    </div>
""", unsafe_allow_html=True)

col_dni, col_nom, col_ape = st.columns([1, 1.5, 1.5])
with col_dni:
    dni = st.text_input("DNI (8 dígitos)", max_chars=8, placeholder="Ej: 70123456")
    if dni and not dni.isdigit():
        st.error("⚠️ El DNI solo debe contener números.")
        dni = ""
with col_nom:
    nombres = st.text_input("Nombres", placeholder="Nombres completos")
with col_ape:
    apellidos = st.text_input("Apellidos", placeholder="Apellidos completos")

col_edad1, col_edad2, col_sexo, _ = st.columns([1, 1, 1, 2])
with col_edad1:
    edad = st.number_input("Edad", min_value=0, value=None, step=1, placeholder="Edad")
with col_edad2:
    tipo_edad = st.radio("Unidad", ["Años", "Meses"], horizontal=True)
with col_sexo:
    sexo = st.selectbox("Sexo", ["Seleccione...", "Masculino", "Femenino"], index=0)


# ═══════════════════════════════════════════════════════════════
# SECCIÓN 2: TRIAJE
# ═══════════════════════════════════════════════════════════════
st.markdown("""
    <div class="triaje-card">
        <div class="triaje-header">
            <span class="triaje-badge">Triaje</span>
            <h3 class="triaje-title">Signos Vitales y Antropometría</h3>
        </div>
    </div>
""", unsafe_allow_html=True)

t1, t2, t3, t4 = st.columns(4)
with t1:
    pa = st.text_input("Presión Arterial (PA)", placeholder="Ej: 120/80")
    temp = st.number_input("Temperatura (°C)", format="%.1f", value=None, placeholder="36.5")
with t2:
    fc = st.number_input("Frec. Cardíaca (lpm)", min_value=0, max_value=300, step=1, value=None, placeholder="80")
    sat = st.number_input("SatO₂ (%)", min_value=0, max_value=100, value=None, placeholder="98")
with t3:
    fr = st.number_input("Frec. Respiratoria (rpm)", min_value=0, max_value=60, step=1, value=None, placeholder="18")
    peso = st.number_input("Peso (kg)", min_value=0.0, value=None, format="%.1f", placeholder="70.0")
with t4:
    talla = st.number_input("Talla (m)", min_value=0.0, value=None, format="%.2f", placeholder="1.65")
    if peso and talla and talla > 0:
        imc = peso / (talla ** 2)
        if imc < 18.5:
            cat_imc = "Bajo peso"
        elif imc < 25:
            cat_imc = "Normal"
        elif imc < 30:
            cat_imc = "Sobrepeso"
        else:
            cat_imc = "Obesidad"
        st.metric("IMC", f"{imc:.1f}", cat_imc)


# ═══════════════════════════════════════════════════════════════
# SECCIÓN 3: ANTECEDENTES E IMAGEN
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

col_ant, col_foto = st.columns([1.5, 1])
with col_ant:
    st.markdown("""
        <div class="section-label">📁 Antecedentes Clínicos</div>
    """, unsafe_allow_html=True)
    antecedentes = st.text_area(
        "Antecedentes médicos relevantes",
        height=150,
        placeholder="Enfermedades previas, cirugías, alergias, medicación habitual, antecedentes familiares..."
    )
with col_foto:
    st.markdown("""
        <div class="section-label">📸 Imagen Clínica (Opcional)</div>
    """, unsafe_allow_html=True)
    foto = st.file_uploader(
        "Adjuntar imagen de lesión o estudio",
        type=['png', 'jpg', 'jpeg'],
        help="Suba una fotografía de la lesión o estudio si lo considera relevante para el diagnóstico."
    )
    if foto:
        img = Image.open(foto)
        st.image(img, use_container_width=True, caption="Imagen adjunta")


# ═══════════════════════════════════════════════════════════════
# SECCIÓN 4: MOTIVO DE CONSULTA + REEVALUACIÓN
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown("""
    <div class="section-label">📝 Evaluación Clínica</div>
""", unsafe_allow_html=True)

col_sint, col_exam = st.columns(2)
with col_sint:
    sintomas = st.text_area(
        "Motivo de consulta y síntomas principales",
        height=130,
        placeholder="Describa detalladamente: tiempo de enfermedad, características del síntoma, factores agravantes/atenuantes..."
    )
with col_exam:
    examen_fisico = st.text_area(
        "Reevaluación Médica (Hallazgos del examen físico)",
        height=130,
        placeholder="Registre aquí los hallazgos de auscultación, palpación, inspección y percusión tras la sugerencia de la IA..."
    )


# ═══════════════════════════════════════════════════════════════
# BOTÓN DE ANÁLISIS
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

if st.button("🔬  ANALIZAR CASO CLÍNICO", type="primary", use_container_width=True):

    # — Validaciones —
    errores = []
    if not dni or len(dni) != 8 or not dni.isdigit():
        errores.append("El DNI debe contener exactamente 8 dígitos numéricos.")
    if not nombres:
        errores.append("El campo Nombres es obligatorio.")
    if not apellidos:
        errores.append("El campo Apellidos es obligatorio.")
    if not sintomas:
        errores.append("Debe describir el motivo de consulta y los síntomas.")

    if errores:
        for e in errores:
            st.error(f"⚠️ {e}")
        st.stop()

    # — Animación de carga —
    contenedor_animacion = st.empty()
    contenedor_animacion.markdown("""
        <div class="loading-container">
            <svg class="loading-ecg" viewBox="0 0 280 60">
                <polyline class="ecg-line"
                    points="0,30 40,30 50,30 60,10 70,50 80,30 100,30 140,30 150,30 160,10 170,50 180,30 200,30 240,30 250,30 260,10 270,50 280,30"/>
            </svg>
            <div class="loading-text">Analizando información clínica</div>
            <div class="loading-sub">Evaluando calidad de los datos suministrados<span class="loading-dots"></span></div>
            <div class="loading-bar-track">
                <div class="loading-bar-fill"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # — Datos de triaje consolidados —
    datos_triaje = f"PA: {pa or 'N/R'}, FC: {fc or 'N/R'}, FR: {fr or 'N/R'}, Temp: {temp or 'N/R'}°C, SatO2: {sat or 'N/R'}%, Peso: {peso or 'N/R'}kg, Talla: {talla or 'N/R'}m"
    sexo_texto = sexo if sexo != "Seleccione..." else "No especificado"

    # — PROMPT CLÍNICO —
    prompt = f"""
    Actúa como un médico especialista e internista jefe. Genera SOLO CÓDIGO HTML PURO, sin bloques markdown, sin ```html ni ```.

    Paciente: {nombres} {apellidos}. Sexo: {sexo_texto}. Edad: {edad} {tipo_edad}.
    Signos vitales (Triaje): {datos_triaje}.
    Antecedentes: {antecedentes if antecedentes else 'No referidos'}.
    Motivo de consulta: {sintomas}.
    Reevaluación Médica (Examen Físico/Auscultación): {examen_fisico if examen_fisico else 'No realizada aún'}.

    REGLA DE ORO DE SEGURIDAD DEL PACIENTE:
    Primero, evalúa estrictamente si la información clínica es suficiente para un diagnóstico presuntivo seguro.

    ESCENARIO A: INFORMACIÓN INSUFICIENTE
    Si el motivo de consulta es muy vago (ej. solo "dolor", "fiebre", "malestar" sin más detalle) O faltan signos vitales clave, Y el campo "Reevaluación Médica" está vacío o no aclara el cuadro, DEBES DETENERTE.
    Genera ÚNICAMENTE este bloque y NADA MÁS (NO generes diagnósticos ni tratamientos):
    <div style="background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); padding: 24px; border-radius: 14px; border-left: 5px solid #f59e0b; font-family: 'Segoe UI', sans-serif; font-size: 15px; line-height: 1.7; text-align: justify;">
        <h3 style="color: #92400e; margin-top: 0; font-size: 18px;">⚠️ Información Clínica Insuficiente — Se requiere Reevaluación</h3>
        <p style="color: #78350f;">Doctor(a), para emitir un diagnóstico presuntivo seguro, la información actual es insuficiente. Por favor, evalúe lo siguiente en el paciente:</p>
        <ul style="color: #78350f; margin: 12px 0;">
            <li><strong>[Indica exactamente qué debe auscultar, palpar, inspeccionar o percutir]</strong></li>
            <li><strong>[Indica qué preguntas específicas debe hacerle al paciente]</strong></li>
            <li><strong>[Indica si necesita algún signo vital faltante]</strong></li>
        </ul>
        <p style="color: #78350f;">Una vez obtenidos estos hallazgos, ingréselos en el campo <strong>"Reevaluación Médica"</strong> y vuelva a procesar el caso.</p>
    </div>

    ESCENARIO B: INFORMACIÓN SUFICIENTE
    Si los datos iniciales son completos, O si el médico ya llenó la "Reevaluación Médica" con los hallazgos solicitados, genera el REPORTE COMPLETO con esta estructura:

    <div style="font-family: 'Segoe UI', sans-serif; line-height: 1.7;">

        <div style="background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); padding: 24px; border-radius: 14px; margin-bottom: 20px; border-left: 5px solid #10b981; font-size: 15px; text-align: justify;">
            <h3 style="color: #065f46; margin-top: 0; font-size: 18px;">✅ Datos Clínicos Adecuados</h3>
            <p style="color: #064e3b;">Se cuenta con información suficiente para emitir un diagnóstico presuntivo y plan de trabajo.</p>
        </div>

        <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); padding: 24px; border-radius: 14px; margin-bottom: 20px; border-left: 5px solid #3b82f6; font-size: 15px; text-align: justify;">
            <h3 style="color: #1e3a5f; margin-top: 0; font-size: 18px;">1. Evaluación Inicial y Fisiopatología</h3>
            <p style="color: #1e3a5f;">[Explica detalladamente la impresión clínica presuntiva con los diagnósticos diferenciales]</p>
        </div>

        <div style="background: #f8fafc; padding: 24px; border-radius: 14px; margin-bottom: 20px; border: 1px solid #e2e8f0; font-size: 15px; text-align: justify;">
            <h3 style="color: #1e293b; margin-top: 0; font-size: 18px;">2. Justificación de Exámenes (Laboratorio e Imágenes)</h3>
            <p style="color: #334155;">[Detalla qué exámenes solicitas y EXACTAMENTE POR QUÉ cada uno es necesario]</p>
        </div>

        <div style="background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%); padding: 24px; border-radius: 14px; margin-bottom: 20px; border-left: 5px solid #ef4444; font-size: 15px; text-align: justify;">
            <h3 style="color: #7f1d1d; margin-top: 0; font-size: 18px;">3. Tratamiento Inicial (Farmacia)</h3>
            <p style="color: #7f1d1d;">[Indica medicamentos, dosis, vía de administración, frecuencia y justificación farmacológica]</p>
        </div>

        <div style="background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%); padding: 24px; border-radius: 14px; margin-bottom: 20px; border-left: 5px solid #8b5cf6; font-size: 15px; text-align: justify;">
            <h3 style="color: #3b0764; margin-top: 0; font-size: 18px;">4. Cuidados de Enfermería</h3>
            <p style="color: #3b0764;">[Indica las intervenciones precisas de enfermería]</p>
        </div>

    </div>
    <hr style="border: none; height: 1px; background: #e2e8f0; margin: 30px 0;">

    <div id="impresion_orden" style="display: none;">
        <h2 style="text-align: center; font-family: Arial, sans-serif; color: #1a365d; margin-bottom: 4px;">ORDEN MÉDICA Y DE EXÁMENES</h2>
        <p style="text-align: center; font-family: Arial, sans-serif; font-size: 13px; color: #718096;">Documento generado con asistencia de IA — Requiere validación del médico tratante</p>
        <hr style="border: 1px solid #2d3748;">
        <p style="font-family: Arial, sans-serif; font-size: 14px;">
            <strong>Paciente:</strong> {nombres} {apellidos} &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong>DNI:</strong> {dni} &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong>Edad:</strong> {edad} {tipo_edad} &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong>Sexo:</strong> {sexo_texto} &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </p>
        <hr>

        <h3 style="font-family: Arial, sans-serif; color: #1a365d;">I. MEDIDAS INICIALES Y ENFERMERÍA</h3>
        <ol style="font-family: Arial, sans-serif; text-align: justify; font-size: 14px; line-height: 1.6;">
            [Lista enumerada de acciones]
        </ol>

        <h3 style="font-family: Arial, sans-serif; color: #1a365d;">II. ANÁLISIS DE LABORATORIO</h3>
        <ul style="column-count: 2; font-family: Arial, sans-serif; font-size: 14px;">
            [Lista con viñetas]
        </ul>

        <h3 style="font-family: Arial, sans-serif; color: #1a365d;">III. DIAGNÓSTICO POR IMÁGENES</h3>
        <ol style="font-family: Arial, sans-serif; font-size: 14px;">
            [Lista enumerada]
        </ol>

        <h3 style="font-family: Arial, sans-serif; color: #1a365d;">IV. FARMACIA (TERAPIA INICIAL)</h3>
        <ol style="font-family: Arial, sans-serif; text-align: justify; font-size: 14px; line-height: 1.6;">
            [Lista enumerada con dosis, vía, frecuencia]
        </ol>

        <br><br><br>
        <div style="text-align: center; font-family: Arial, sans-serif;">
            <p style="margin-bottom: 0;">_________________________________________</p>
            <p style="margin-top: 4px;"><strong>{st.session_state['medico_nombre']}</strong><br>
            CMP: {st.session_state['medico_cmp']}<br>
            <span style="font-size: 12px; color: #718096;">{st.session_state['medico_especialidad']}</span></p>
        </div>
    </div>
    """

    # — Llamada a la IA —
    try:
        if foto:
            img_pil = Image.open(foto)
            response = client.models.generate_content(model='gemini-2.5-flash', contents=[prompt, img_pil])
        else:
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)

        texto_limpio = response.text.replace("```html", "").replace("```", "").strip()

        st.session_state.html_resultado = texto_limpio
        st.session_state.mostrar_botones = 'id="impresion_orden"' in texto_limpio

        contenedor_animacion.empty()

    except Exception as e:
        contenedor_animacion.empty()
        st.error(f"❌ Error en el análisis: {e}")


# ═══════════════════════════════════════════════════════════════
# RESULTADOS
# ═══════════════════════════════════════════════════════════════
if st.session_state.html_resultado:
    st.html(f'<div class="resultado-wrapper">{st.session_state.html_resultado}</div>')
    st.write("")

    if st.session_state.mostrar_botones:
        script_impresion = """
        <script>
        function imprimirResumen() {
            var el = window.parent.document.getElementById('impresion_orden');
            if (!el) { alert('No se encontró la orden médica.'); return; }
            var contenido = el.innerHTML;
            var ventana = window.open('', '_blank');
            ventana.document.write('<html><head><title>Orden Médica</title>');
            ventana.document.write('<style>');
            ventana.document.write('body { padding: 40px 50px; font-family: Arial, sans-serif; text-align: justify; line-height: 1.6; color: #1a202c; }');
            ventana.document.write('h2 { color: #1a365d; } h3 { color: #2d3748; margin-top: 24px; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; }');
            ventana.document.write('ul { column-count: 2; } ol, ul { margin: 8px 0; }');
            ventana.document.write('@media print { body { padding: 20px 30px; } }');
            ventana.document.write('</style></head><body>');
            ventana.document.write(contenido);
            ventana.document.write('</body></html>');
            ventana.document.close();
            ventana.focus();
            setTimeout(function() { ventana.print(); ventana.close(); }, 600);
        }
        </script>
        <button onclick="imprimirResumen()" style="
            width: 100%; padding: 14px; font-size: 15px; font-weight: 700;
            background: linear-gradient(135deg, #e53e3e, #c53030);
            color: white; border: none; border-radius: 12px; cursor: pointer;
            box-shadow: 0 4px 14px rgba(229,62,62,0.3);
            transition: all 0.3s ease;
            font-family: 'Segoe UI', sans-serif;
        " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 20px rgba(229,62,62,0.4)'"
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 14px rgba(229,62,62,0.3)'">
            🖨️ IMPRIMIR ORDEN MÉDICA
        </button>
        """

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.iframe(script_impresion, height=65)
        with col_b2:
            if st.button("💾  Guardar en Historia Clínica", use_container_width=True, type="primary"):
                campos_vacios = []
                if not dni or not dni.isdigit() or len(dni) != 8:
                    campos_vacios.append("DNI (8 dígitos)")
                if not nombres or not nombres.strip():
                    campos_vacios.append("Nombres")
                if not apellidos or not apellidos.strip():
                    campos_vacios.append("Apellidos")
                if edad is None:
                    campos_vacios.append("Edad")
                if campos_vacios:
                    st.error(f"❌ Complete los siguientes campos obligatorios: {', '.join(campos_vacios)}")
                else:
                    try:
                        datos_t = f"PA: {pa}, FC: {fc}, FR: {fr}, Temp: {temp}, SatO2: {sat}, Peso: {peso}, Talla: {talla}"
                        sintomas_completos = f"Motivo: {sintomas} | Reevaluación: {examen_fisico}"
                        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        c.execute("REPLACE INTO pacientes_v2 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                  (dni, nombres, apellidos, edad, tipo_edad, datos_t, antecedentes, sintomas_completos, fecha))
                        conn.commit()
                        st.success("✅ Historia clínica guardada exitosamente.")
                    except Exception as e:
                        st.error(f"❌ Error al guardar: {e}")


# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; padding: 16px 0 8px 0; opacity: 0.5;">
        <p style="font-size: 12px; color: #a0aec0; margin: 0;">
            MedAssist Pro v2.0 · Sistema de apoyo al diagnóstico clínico · Uso exclusivo profesional médico<br>
            ⚠️ Este sistema es una herramienta de apoyo. El diagnóstico final es responsabilidad del médico tratante.
        </p>
    </div>
""", unsafe_allow_html=True)
