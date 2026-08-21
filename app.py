import streamlit as st
from datetime import datetime, timedelta, time
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm
import pandas as pd
import os
import tempfile

st.set_page_config(
    page_title="Control de Tardanzas - CupoApp",
    page_icon="⏰",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items=None
)

MOBILE_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 100%;
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }
    
    @media (min-width: 768px) {
        .block-container {
            max-width: 720px;
            padding-left: 1.5rem;
            padding-right: 1.5rem;
        }
    }
    
    .main-header {
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        margin-bottom: 16px;
        text-align: center;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 1.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .main-header p {
        margin: 8px 0 0 0;
        color: #64748b;
        font-size: 0.85rem;
    }
    
    .info-card {
        background: white;
        border-radius: 14px;
        padding: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 14px;
        border-left: 4px solid #667eea;
    }
    
    .info-card.success {
        border-left-color: #10b981;
    }
    
    .info-card.warning {
        border-left-color: #f59e0b;
    }
    
    .info-card.danger {
        border-left-color: #ef4444;
    }
    
    .info-card h3 {
        margin: 0 0 8px 0;
        font-size: 1rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    .info-card p {
        margin: 0;
        color: #475569;
        font-size: 0.88rem;
        line-height: 1.5;
    }
    
    .student-card {
        background: white;
        border-radius: 14px;
        padding: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 14px;
        border: 2px solid #e2e8f0;
        transition: all 0.2s ease;
    }
    
    .student-card:hover {
        border-color: #667eea;
        transform: translateY(-2px);
    }
    
    .student-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    
    .student-number {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    
    .penalty-display {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-radius: 10px;
        padding: 12px;
        margin-top: 12px;
        border: 1px solid #f59e0b;
    }
    
    .penalty-display h4 {
        margin: 0 0 6px 0;
        font-size: 0.85rem;
        color: #92400e;
        font-weight: 700;
    }
    
    .penalty-amount {
        font-size: 1.4rem;
        font-weight: 800;
        color: #b45309;
    }
    
    .penalty-exercise {
        font-size: 1.1rem;
        font-weight: 700;
        color: #78350f;
    }
    
    div.stButton > button {
        border-radius: 12px;
        font-weight: 700;
        transition: all 0.2s ease;
        width: 100%;
        padding: 12px 20px;
        border: none;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    div.stButton > button[data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        color: white;
    }
    
    div.stButton > button[data-testid="baseButton-secondary"]:hover {
        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
    }
    
    .btn-add-more {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
    }
    
    .btn-save {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        color: white;
        font-size: 1.05rem;
        padding: 16px !important;
    }
    
    .btn-pdf {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }
    
    .total-card {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        border-radius: 16px;
        padding: 20px;
        color: white;
        text-align: center;
        margin-bottom: 14px;
        box-shadow: 0 8px 30px rgba(16, 185, 129, 0.3);
    }
    
    .total-card h2 {
        margin: 0;
        font-size: 0.95rem;
        font-weight: 600;
        opacity: 0.95;
    }
    
    .total-amount {
        font-size: 2.5rem;
        font-weight: 800;
        margin-top: 4px;
    }
    
    .debt-card {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        border-radius: 16px;
        padding: 20px;
        color: white;
        text-align: center;
        margin-bottom: 14px;
        box-shadow: 0 8px 30px rgba(239, 68, 68, 0.3);
    }
    
    .remove-btn {
        background: #fee2e2;
        color: #dc2626;
        border: none;
        border-radius: 50%;
        width: 28px;
        height: 28px;
        cursor: pointer;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .remove-btn:hover {
        background: #fecaca;
    }
    
    [data-testid="stTextInput"] input,
    [data-testid="stTimeInput"] input,
    [data-testid="stSelectbox"] select {
        border-radius: 10px;
        border: 1.5px solid #e2e8f0;
        padding: 8px 12px;
    }
    
    [data-testid="stTextInput"] input:focus,
    [data-testid="stTimeInput"] input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        padding: 8px;
        border-radius: 12px;
        margin-bottom: 16px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        background-color: #f1f5f9;
        color: #64748b;
        font-weight: 600;
        padding: 8px 16px;
        height: auto;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    section[data-testid="stSidebar"] {
        display: none;
    }
    
    .status-tag {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
    }
    
    .status-pagado {
        background: #dcfce7;
        color: #166534;
    }
    
    .status-ejercicio {
        background: #dbeafe;
        color: #1e40af;
    }
    
    .status-deuda {
        background: #fee2e2;
        color: #991b1b;
    }
    
    .empty-state {
        text-align: center;
        padding: 40px 20px;
        color: #94a3b8;
    }
    
    .empty-state h3 {
        margin: 16px 0 8px 0;
        color: #64748b;
    }
</style>
"""

st.markdown(MOBILE_CSS, unsafe_allow_html=True)


def get_google_credentials():
    creds_dict = {
        "type": st.secrets.get("google_service_account", {}).get("type", ""),
        "project_id": st.secrets.get("google_service_account", {}).get("project_id", ""),
        "private_key_id": st.secrets.get("google_service_account", {}).get("private_key_id", ""),
        "private_key": st.secrets.get("google_service_account", {}).get("private_key", "").replace("\\n", "\n"),
        "client_email": st.secrets.get("google_service_account", {}).get("client_email", ""),
        "client_id": st.secrets.get("google_service_account", {}).get("client_id", ""),
        "auth_uri": st.secrets.get("google_service_account", {}).get("auth_uri", ""),
        "token_uri": st.secrets.get("google_service_account", {}).get("token_uri", ""),
        "auth_provider_x509_cert_url": st.secrets.get("google_service_account", {}).get("auth_provider_x509_cert_url", ""),
        "client_x509_cert_url": st.secrets.get("google_service_account", {}).get("client_x509_cert_url", ""),
        "universe_domain": st.secrets.get("google_service_account", {}).get("universe_domain", "googleapis.com"),
    }
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.file",
    ]
    return Credentials.from_service_account_info(creds_dict, scopes=scopes)


def get_spreadsheet():
    creds = get_google_credentials()
    gc = gspread.authorize(creds)
    sheet_key = st.secrets.get("sheet_key", "")
    if sheet_key:
        return gc.open_by_key(sheet_key)
    sheet_name = st.secrets.get("sheet_name", "ControlTardanzas")
    return gc.open(sheet_name)


def get_or_create_worksheet(date_str):
    sh = get_spreadsheet()
    try:
        ws = sh.worksheet(date_str)
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=date_str, rows=100, cols=10)
        headers = [
            "Nombres y Apellidos",
            "Fecha",
            "Hora de Ingreso",
            "Horario de Control",
            "Tiempo de Tardanza (min)",
            "Monto Calculado (S/)",
            "Ejercicio (repeticiones)",
            "Tipo de Pago",
            "Estado",
            "Monto Final (S/)",
        ]
        ws.insert_row(headers, 1)
        ws.format("A1:J1", {
            "backgroundColor": {"red": 0.4, "green": 0.49, "blue": 0.92},
            "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True},
            "horizontalAlignment": "CENTER",
        })
    return ws


def get_drive_service():
    creds = get_google_credentials()
    return build("drive", "v3", credentials=creds)


def detect_day_and_schedule():
    now = datetime.now()
    weekday = now.weekday()
    schedules = {
        0: ("Lunes", time(19, 10), time(20, 30)),
        2: ("Miércoles", time(17, 30), time(20, 30)),
    }
    if weekday in schedules:
        return schedules[weekday][0], schedules[weekday][1], schedules[weekday][2], True
    return None, None, None, False


def calculate_penalty(arrival_time, start_time, end_time):
    arrival_dt = datetime.combine(datetime.now().date(), arrival_time)
    start_dt = datetime.combine(datetime.now().date(), start_time)
    end_dt = datetime.combine(datetime.now().date(), end_time)
    
    if arrival_time <= start_time:
        return 0, 0.0, 0
    
    if arrival_time > end_time:
        effective_arrival = end_dt
    else:
        effective_arrival = arrival_dt
    
    delay_minutes = max(0, int((effective_arrival - start_dt).total_seconds() / 60))
    
    if delay_minutes > 0:
        money_blocks = (delay_minutes + 9) // 10
        money_amount = money_blocks * 0.50
    else:
        money_amount = 0.0
    
    exercise_reps = delay_minutes
    
    return delay_minutes, money_amount, exercise_reps


def generate_pdf(date_str, records, schedule_name):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf_path = tmp.name
    
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=20,
        textColor=colors.HexColor("#4f46e5"),
        alignment=1,
        spaceAfter=6,
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#64748b"),
        alignment=1,
        spaceAfter=20,
    )
    h4_style = ParagraphStyle(
        "H4",
        parent=styles["Heading4"],
        fontSize=12,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=8,
        spaceAfter=6,
        fontName="Helvetica-Bold",
    )
    
    story = []
    story.append(Paragraph("REPORTE DE TARDANZAS", title_style))
    story.append(Paragraph(f"Fecha: {date_str} | Horario: {schedule_name}", subtitle_style))
    
    total_money = 0.0
    total_debt = 0.0
    paid_count = 0
    exercise_count = 0
    debt_count = 0
    
    table_data = [["#", "Nombres y Apellidos", "Horario Ingreso", "Tardanza", "Monto S/", "Ejercicio", "Estado"]]
    
    for i, r in enumerate(records, 1):
        row = [
            str(i),
            r.get("Nombre", ""),
            r.get("Hora Ingreso", ""),
            f"{r.get('Tiempo Tardanza (min)', 0)} min",
            f"S/ {r.get('Monto Final (S/)', 0.0):.2f}",
            f"{r.get('Ejercicio (repeticiones)', 0)} reps",
            r.get("Estado", ""),
        ]
        table_data.append(row)
        
        monto_final = float(r.get("Monto Final (S/)", 0.0))
        estado = r.get("Estado", "")
        tipo_pago = r.get("Tipo de Pago", "")
        
        if tipo_pago == "Pagar Dinero":
            total_money += monto_final
            paid_count += 1
        elif tipo_pago == "Realizar Ejercicio":
            exercise_count += 1
        elif "Deuda" in estado:
            total_debt += float(r.get("Monto Calculado (S/)", 0.0))
            debt_count += 1
    
    col_widths = [0.8 * cm, 6 * cm, 2.5 * cm, 2 * cm, 2 * cm, 2 * cm, 2.8 * cm]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    table_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("FONTSIZE", (0, 1), (-1, -1), 7.5),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ALIGN", (1, 1), (1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    
    for i, r in enumerate(records, 1):
        estado = r.get("Estado", "")
        if "Deuda" in estado:
            table_style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#fef2f2")))
        elif r.get("Tipo de Pago") == "Realizar Ejercicio":
            table_style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#eff6ff")))
    
    table.setStyle(TableStyle(table_style))
    story.append(table)
    
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph("RESUMEN", h4_style))
    
    summary_data = [
        ["Detalle", "Cantidad / Monto"],
        ["Total Alumnos Registrados", str(len(records))],
        ["Alumnos que Pagaron", str(paid_count)],
        ["Alumnos que Hicieron Ejercicio", str(exercise_count)],
        ["Alumnos con Deuda", str(debt_count)],
        ["Dinero Recaudado (S/)", f"S/ {total_money:.2f}"],
        ["Deuda Pendiente (S/)", f"S/ {total_debt:.2f}"],
    ]
    
    summary_table = Table(summary_data, colWidths=[8 * cm, 6 * cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("ALIGN", (1, 1), (1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 5), (1, 5), colors.HexColor("#dcfce7")),
        ("BACKGROUND", (0, 6), (1, 6), colors.HexColor("#fef2f2")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)
    
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph("___________________________", ParagraphStyle("sig", parent=styles["Normal"], alignment=1, textColor=colors.HexColor("#475569"))))
    story.append(Paragraph("Firma y Sello del Encargado", ParagraphStyle("sig-label", parent=styles["Normal"], alignment=1, textColor=colors.HexColor("#64748b"), fontSize=10)))
    
    doc.build(story)
    return pdf_path, total_money, total_debt


def upload_to_drive(pdf_path, file_name):
    drive_service = get_drive_service()
    folder_id = st.secrets.get("drive_folder_id", "")
    
    file_metadata = {
        "name": file_name,
        "mimeType": "application/pdf",
    }
    if folder_id:
        file_metadata["parents"] = [folder_id]
    
    media = MediaFileUpload(pdf_path, mimetype="application/pdf")
    file = drive_service.files().create(body=file_metadata, media_body=media, fields="id,webViewLink").execute()
    return file.get("webViewLink", "")


def main():
    st.markdown("""
        <div class="main-header">
            <h1>⏰ Control de Tardanzas</h1>
            <p>CupoApp - Registro y gestión de puntualidad</p>
        </div>
    """, unsafe_allow_html=True)
    
    bot_email = st.secrets.get("google_service_account", {}).get("client_email", "bot-tardanzas@true-ion-506204-h6.iam.gserviceaccount.com")
    has_sheet_key = bool(st.secrets.get("sheet_key", ""))
    has_drive_folder = bool(st.secrets.get("drive_folder_id", ""))
    
    if has_sheet_key and has_drive_folder:
        st.markdown(f"""
            <div class="info-card success">
                <h3>🔗 Configuración Detectada</h3>
                <p>✅ Sheet ID y Drive Folder ID están configurados.</p>
                <p>⚠️ Asegúrate de <strong>compartir</strong> tu hoja de Google Sheet <strong>y</strong> tu carpeta de Drive con este correo (permiso Editor):</p>
                <p style="background:#f1f5f9;padding:8px 12px;border-radius:8px;margin-top:6px;font-family:monospace;font-weight:600;">{bot_email}</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="info-card warning">
                <h3>⚠️ Verifica tu Configuración</h3>
                <p>Antes de usar la app, revisa tu archivo <code>.streamlit/secrets.toml</code>.</p>
                <p>Comparte el Sheet y la carpeta Drive con:</p>
                <p style="background:#f1f5f9;padding:8px 12px;border-radius:8px;margin-top:6px;font-family:monospace;font-weight:600;">{bot_email}</p>
            </div>
        """, unsafe_allow_html=True)
    
    today = datetime.now()
    date_str = today.strftime("%d/%m/%Y")
    date_iso = today.strftime("%Y-%m-%d")
    
    day_name, default_start, default_end, is_scheduled_day = detect_day_and_schedule()
    
    if is_scheduled_day:
        schedule_name = f"{day_name} ({default_start.strftime('%H:%M')} - {default_end.strftime('%H:%M')})"
        start_time = default_start
        end_time = default_end
        st.markdown(f"""
            <div class="info-card success">
                <h3>📅 Día de Control Automático Detectado</h3>
                <p><strong>{day_name}</strong> | Horario: <strong>{default_start.strftime('%I:%M %p')} - {default_end.strftime('%I:%M %p')}</strong></p>
                <p>Fecha: <strong>{date_str}</strong></p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="info-card warning">
                <h3>📅 Selección Manual de Horario</h3>
                <p>Hoy no es día de control programado. Selecciona el horario a utilizar:</p>
            </div>
        """, unsafe_allow_html=True)
        schedule_options = {
            "Lunes (19:10 - 20:30)": (time(19, 10), time(20, 30)),
            "Miércoles (17:30 - 20:30)": (time(17, 30), time(20, 30)),
        }
        selected = st.selectbox("Selecciona el horario:", list(schedule_options.keys()))
        schedule_name = selected
        start_time, end_time = schedule_options[selected]
    
    if "num_students" not in st.session_state:
        st.session_state.num_students = 1
    
    st.markdown('<div style="margin-bottom: 12px;"></div>', unsafe_allow_html=True)
    
    records = []
    
    total_collected = 0.0
    total_debt = 0.0
    
    for idx in range(st.session_state.num_students):
        with st.container():
            st.markdown(f"""
                <div class="student-card">
                    <div class="student-header">
                        <span class="student-number">👤 Alumno #{idx + 1}</span>
                    </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                name_key = f"name_{idx}"
                if name_key not in st.session_state:
                    st.session_state[name_key] = ""
                name = st.text_input("Nombres y Apellidos:", placeholder="Ej: Juan Pérez", key=name_key, label_visibility="visible")
            
            with col2:
                time_key = f"time_{idx}"
                if time_key not in st.session_state:
                    st.session_state[time_key] = datetime.now().time()
                arrival = st.time_input("Hora de Ingreso:", value=st.session_state[time_key], key=time_key, label_visibility="visible")
                if isinstance(arrival, datetime):
                    arrival_time_val = arrival.time()
                else:
                    arrival_time_val = arrival
            
            delay_min, money_amt, exercise_reps = calculate_penalty(arrival_time_val, start_time, end_time)
            
            pay_key = f"pay_{idx}"
            if pay_key not in st.session_state:
                st.session_state[pay_key] = "Sin Pago / Deuda" if money_amt > 0 else "Pagar Dinero"
            pay_options = ["Pagar Dinero", "Realizar Ejercicio", "Sin Pago / Deuda"]
            payment_type = st.selectbox("Tipo de Pago / Resolución:", pay_options, key=pay_key, label_visibility="visible")
            
            final_amount = 0.0
            estado = ""
            
            if payment_type == "Pagar Dinero":
                final_amount = money_amt
                estado = f"Pagado (S/ {money_amt:.2f})"
                total_collected += money_amt
            elif payment_type == "Realizar Ejercicio":
                final_amount = 0.0
                estado = f"Ejercicio Realizado ({exercise_reps} reps)"
            else:
                final_amount = 0.0
                if money_amt > 0:
                    estado = f"Con Deuda (S/ {money_amt:.2f})"
                    total_debt += money_amt
                else:
                    estado = "A Tiempo"
            
            if delay_min > 0:
                st.markdown(f"""
                    <div class="penalty-display">
                        <h4>⚠️ Penalidad Calculada</h4>
                        <div class="penalty-amount">Tardanza: {delay_min} min</div>
                        <div class="penalty-amount">S/ {money_amt:.2f}</div>
                        <div class="penalty-exercise">ó {exercise_reps} repeticiones</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="penalty-display" style="background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); border-color: #22c55e;">
                        <h4 style="color: #166534;">✅ Alumno a Tiempo</h4>
                        <div class="penalty-amount" style="color: #15803d;">Sin penalidad</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            records.append({
                "idx": idx,
                "Nombre": name,
                "Fecha": date_str,
                "Hora Ingreso": arrival_time_val.strftime("%H:%M:%S"),
                "Horario": schedule_name,
                "Tiempo Tardanza (min)": delay_min,
                "Monto Calculado (S/)": money_amt,
                "Ejercicio (repeticiones)": exercise_reps,
                "Tipo de Pago": payment_type,
                "Estado": estado,
                "Monto Final (S/)": final_amount,
            })
    
    col_add, col_remove = st.columns([3, 1])
    with col_add:
        if st.button("➕ Agregar Tardón", key="add_more", type="secondary"):
            st.session_state.num_students += 1
            st.rerun()
    
    with col_remove:
        if st.session_state.num_students > 1:
            if st.button("🗑️", key="remove_last", type="secondary"):
                for key in [f"name_{st.session_state.num_students - 1}", 
                            f"time_{st.session_state.num_students - 1}",
                            f"pay_{st.session_state.num_students - 1}"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.num_students -= 1
                st.rerun()
    
    st.markdown('<div style="margin: 16px 0;"></div>', unsafe_allow_html=True)
    
    if total_collected > 0:
        st.markdown(f"""
            <div class="total-card">
                <h2>💰 TOTAL RECAUDADO HOY</h2>
                <div class="total-amount">S/ {total_collected:.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    if total_debt > 0:
        st.markdown(f"""
            <div class="debt-card">
                <h2>⚠️ DEUDA PENDIENTE</h2>
                <div class="total-amount">S/ {total_debt:.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    save_btn = st.button("💾 Guardar Registros en Google Sheets", key="save_btn", type="primary")
    
    if save_btn:
        valid_records = [r for r in records if r["Nombre"].strip()]
        if not valid_records:
            st.error("❌ No hay registros válidos. Ingresa al menos un nombre.")
        else:
            try:
                with st.spinner("Guardando en Google Sheets..."):
                    ws = get_or_create_worksheet(date_iso)
                    
                    existing_rows = ws.get_all_values()
                    start_row = len(existing_rows) + 1
                    
                    rows_to_append = []
                    for r in valid_records:
                        rows_to_append.append([
                            r["Nombre"],
                            r["Fecha"],
                            r["Hora Ingreso"],
                            r["Horario"],
                            r["Tiempo Tardanza (min)"],
                            r["Monto Calculado (S/)"],
                            r["Ejercicio (repeticiones)"],
                            r["Tipo de Pago"],
                            r["Estado"],
                            r["Monto Final (S/)"],
                        ])
                    
                    ws.insert_rows(rows_to_append, start_row)
                    
                    recaudado = sum(r["Monto Final (S/)"] for r in valid_records)
                    st.success(f"✅ {len(valid_records)} registro(s) guardado(s) correctamente. Total recaudado: S/ {recaudado:.2f}")
                    
                    st.balloons()
            except Exception as e:
                st.error(f"❌ Error al guardar: {str(e)}")
                st.info("💡 Verifica las credenciales de Google en st.secrets y que el bot tenga acceso al sheet.")
    
    st.markdown('<div style="margin: 12px 0;"></div>', unsafe_allow_html=True)
    
    pdf_btn = st.button("📄 Generar Reporte PDF del Día", key="pdf_btn", type="secondary")
    
    if pdf_btn:
        try:
            with st.spinner("Cargando datos y generando PDF..."):
                ws = get_or_create_worksheet(date_iso)
                data = ws.get_all_records()
                
                if not data:
                    st.warning("⚠️ No hay registros guardados para este día. Guarda primero los registros.")
                else:
                    pdf_path, pdf_total, pdf_debt = generate_pdf(date_str, data, schedule_name)
                    file_name = f"Reporte_Tardanzas_{date_iso}.pdf"
                    
                    drive_link = upload_to_drive(pdf_path, file_name)
                    
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="⬇️ Descargar PDF",
                            data=pdf_bytes,
                            file_name=file_name,
                            mime="application/pdf",
                            key="download_pdf",
                            type="primary"
                        )
                    with col2:
                        if drive_link:
                            st.markdown(f"[☁️ Ver en Google Drive]({drive_link})")
                    
                    st.success(f"✅ PDF generado y subido a Google Drive correctamente.")
                    
                    try:
                        os.unlink(pdf_path)
                    except:
                        pass
        except Exception as e:
            st.error(f"❌ Error al generar PDF: {str(e)}")
            st.info("💡 Verifica la configuración de Google Drive en st.secrets.")
    
    st.markdown('<div style="margin: 24px 0;"></div>', unsafe_allow_html=True)
    
    with st.expander("ℹ️ Instrucciones de Configuración"):
        st.markdown("""
### 📋 Estructura de Google Sheets

1. **Crea una hoja de cálculo** en Google Sheets con el nombre: **`ControlTardanzas`**
2. **Comparte la hoja** con el correo de la cuenta de servicio (lo encontrarás en el JSON de credenciales como `client_email`), dándole permisos de **Editor**.
3. La aplicación creará automáticamente una pestaña por cada día con formato `YYYY-MM-DD` y estos encabezados:
   - Nombres y Apellidos
   - Fecha
   - Hora de Ingreso
   - Horario de Control
   - Tiempo de Tardanza (min)
   - Monto Calculado (S/)
   - Ejercicio (repeticiones)
   - Tipo de Pago
   - Estado
   - Monto Final (S/)

### 🔐 Configuración de Secrets en Streamlit Cloud

Crea un archivo `.streamlit/secrets.toml` en local o configura los Secrets en Streamlit Cloud:

```toml
[google_service_account]
type = "service_account"
project_id = "tu-project-id"
private_key_id = "tu-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nTU_KEY_AQUI\n-----END PRIVATE KEY-----\n"
client_email = "tu-cuenta@tu-project.iam.gserviceaccount.com"
client_id = "tu-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/tu-cuenta%40tu-project.iam.gserviceaccount.com"
universe_domain = "googleapis.com"

sheet_name = "ControlTardanzas"
drive_folder_id = "1aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890"
```

### 🛠️ Pasos para obtener credenciales de Google:

1. Ve a **Google Cloud Console** → https://console.cloud.google.com/
2. Crea un nuevo proyecto o usa uno existente
3. Activa las APIs: **Google Sheets API** y **Google Drive API**
4. Ve a **Credenciales** → **Crear credenciales** → **Cuenta de servicio**
5. Crea la cuenta, descarga el JSON de credenciales
6. Copia los valores del JSON al `secrets.toml`
7. Crea una carpeta en Google Drive, copia su ID (de la URL) y ponlo en `drive_folder_id`
8. Comparte la carpeta con el `client_email` de la cuenta de servicio
        """)


if __name__ == "__main__":
    main()
