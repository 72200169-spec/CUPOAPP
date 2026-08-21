import streamlit as st
from datetime import datetime, timedelta, time
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.units import cm
import pandas as pd
import os
import tempfile

st.set_page_config(
    page_title="CupoApp | Control de Tardanzas",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

PROFESSIONAL_UI = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

    * { font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4, h5, h6 { font-family: 'Plus Jakarta Sans', 'Inter', sans-serif; }

    .stApp {
        background: #f8fafc;
    }

    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { right: 2rem; }

    section[data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #e2e8f0;
        padding-top: 0 !important;
    }
    section[data-testid="stSidebar"] > div:first-child { padding-top: 0; }

    .brand-header {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        padding: 28px 24px 24px 24px;
        margin: -1rem -1rem 20px -1rem;
        color: white;
    }
    .brand-header h1 {
        margin: 0;
        font-size: 1.55rem;
        font-weight: 800;
        letter-spacing: -0.02em;
    }
    .brand-header .tagline {
        margin: 6px 0 0 0;
        font-size: 0.82rem;
        opacity: 0.9;
        font-weight: 500;
    }

    .stat-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        transition: all 0.2s ease;
    }
    .stat-card:hover {
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
        transform: translateY(-2px);
    }
    .stat-card .stat-icon {
        width: 42px;
        height: 42px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        margin-bottom: 10px;
    }
    .stat-card .stat-label {
        font-size: 0.78rem;
        color: #64748b;
        font-weight: 500;
        margin: 0;
    }
    .stat-card .stat-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #0f172a;
        margin: 4px 0 0 0;
        letter-spacing: -0.02em;
    }
    .stat-card.primary .stat-icon { background: #eef2ff; color: #4f46e5; }
    .stat-card.success .stat-icon { background: #dcfce7; color: #16a34a; }
    .stat-card.warning .stat-icon { background: #fef3c7; color: #d97706; }
    .stat-card.danger .stat-icon { background: #fee2e2; color: #dc2626; }

    .panel {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        margin-bottom: 20px;
    }
    .panel-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0 0 4px 0;
        letter-spacing: -0.01em;
    }
    .panel-subtitle {
        font-size: 0.82rem;
        color: #64748b;
        margin: 0 0 18px 0;
    }

    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.01em;
    }
    .badge-info    { background: #dbeafe; color: #1d4ed8; }
    .badge-success { background: #dcfce7; color: #15803d; }
    .badge-warning { background: #fef3c7; color: #92400e; }
    .badge-danger  { background: #fee2e2; color: #991b1b; }
    .badge-dark    { background: #e2e8f0; color: #1e293b; }

    .student-form-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        transition: all 0.2s ease;
    }
    .student-form-card:hover {
        border-color: #c7d2fe;
        box-shadow: 0 8px 24px rgba(79, 70, 229, 0.08);
    }
    .student-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 14px;
        padding-bottom: 10px;
        border-bottom: 1px solid #f1f5f9;
    }
    .student-card-header .tag {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 700;
    }

    .penalty-box {
        border-radius: 12px;
        padding: 14px 16px;
        margin-top: 14px;
        border: 1px solid;
    }
    .penalty-box.on-time {
        background: #f0fdf4;
        border-color: #bbf7d0;
    }
    .penalty-box.on-time h4 { color: #15803d; }
    .penalty-box.late {
        background: #fffbeb;
        border-color: #fde68a;
    }
    .penalty-box.late h4 { color: #92400e; }
    .penalty-box h4 {
        margin: 0 0 6px 0;
        font-size: 0.82rem;
        font-weight: 700;
    }
    .penalty-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-top: 6px;
    }
    .penalty-item {
        background: rgba(255,255,255,0.7);
        padding: 8px 10px;
        border-radius: 8px;
    }
    .penalty-item .pi-label {
        font-size: 0.7rem;
        color: #64748b;
        font-weight: 500;
    }
    .penalty-item .pi-value {
        font-size: 1.05rem;
        font-weight: 800;
        color: #0f172a;
    }

    [data-testid="stButton"] button,
    [data-testid="baseButton-secondary"],
    [data-testid="baseButton-primary"] {
        border-radius: 10px !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em !important;
        transition: all 0.2s ease !important;
        min-height: 42px;
        padding: 8px 18px !important;
        border: none !important;
    }
    [data-testid="stButton"] button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(15,23,42,0.12) !important;
    }
    [data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
    }
    [data-testid="baseButton-secondary"] {
        background: #f1f5f9 !important;
        color: #0f172a !important;
    }

    .locked-screen {
        text-align: center;
        padding: 60px 24px;
        max-width: 560px;
        margin: 40px auto;
        background: white;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 20px 60px rgba(15,23,42,0.08);
    }
    .locked-screen .icon {
        font-size: 4rem;
        margin-bottom: 12px;
    }
    .locked-screen h2 {
        margin: 0 0 8px 0;
        font-size: 1.6rem;
        color: #0f172a;
        font-weight: 800;
    }
    .locked-screen p {
        color: #64748b;
        font-size: 0.95rem;
        margin: 0 0 20px 0;
    }
    .lock-days-grid {
        display: flex;
        gap: 8px;
        justify-content: center;
        margin-bottom: 24px;
        flex-wrap: wrap;
    }
    .lock-day {
        padding: 10px 16px;
        border-radius: 10px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .lock-day.active { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
    .lock-day.inactive { background: #f1f5f9; color: #94a3b8; }

    [data-testid="stTextInput"] > label,
    [data-testid="stTimeInput"] > label,
    [data-testid="stSelectbox"] > label,
    [data-testid="stDateInput"] > label,
    [data-testid="stNumberInput"] > label,
    [data-testid="stCheckbox"] > label {
        font-weight: 600 !important;
        color: #334155 !important;
        font-size: 0.85rem !important;
    }
    [data-testid="stTextInput"] input,
    [data-testid="stTimeInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stDateInput"] input {
        border-radius: 10px !important;
        border: 1.5px solid #e2e8f0 !important;
        padding: 8px 12px !important;
        background: #f8fafc !important;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stTimeInput"] input:focus {
        border-color: #4f46e5 !important;
        background: white !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.12) !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] {
        border-radius: 10px !important;
        border: 1.5px solid #e2e8f0 !important;
        background: #f8fafc !important;
    }

    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 6px;
        background: #f1f5f9;
        padding: 6px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        border-radius: 8px !important;
        background-color: transparent !important;
        color: #475569 !important;
        font-weight: 600 !important;
        padding: 10px 18px !important;
        height: auto !important;
    }
    [data-testid="stTabs"] [aria-selected="true"] {
        background: #ffffff !important;
        color: #4f46e5 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    .dataframe-table {
        border-radius: 12px !important;
        overflow: hidden;
    }

    .footer-brand {
        text-align: center;
        padding: 24px 12px 0 12px;
        color: #94a3b8;
        font-size: 0.78rem;
        font-weight: 500;
    }
    .footer-brand strong { color: #64748b; }

    @media (max-width: 640px) {
        .panel { padding: 16px; border-radius: 12px; }
        .stat-card .stat-value { font-size: 1.35rem; }
        .penalty-grid { grid-template-columns: 1fr; }
    }
</style>
"""
st.markdown(PROFESSIONAL_UI, unsafe_allow_html=True)


SCHEDULES = {
    0: ("Lunes", time(19, 10), time(20, 30)),
    2: ("Miércoles", time(17, 30), time(20, 30)),
}
VALID_WEEKDAYS = set(SCHEDULES.keys())
DAY_NAMES = {0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"}


def get_google_credentials():
    account = st.secrets.get("google_service_account", {})
    creds_dict = {
        "type": account.get("type", ""),
        "project_id": account.get("project_id", ""),
        "private_key_id": account.get("private_key_id", ""),
        "private_key": account.get("private_key", ""),
        "client_email": account.get("client_email", ""),
        "client_id": account.get("client_id", ""),
        "auth_uri": account.get("auth_uri", ""),
        "token_uri": account.get("token_uri", ""),
        "auth_provider_x509_cert_url": account.get("auth_provider_x509_cert_url", ""),
        "client_x509_cert_url": account.get("client_x509_cert_url", ""),
        "universe_domain": account.get("universe_domain", "googleapis.com"),
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
    return gc.open(st.secrets.get("sheet_name", "ControlTardanzas"))


def get_or_create_worksheet(date_iso):
    sh = get_spreadsheet()
    try:
        ws = sh.worksheet(date_iso)
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=date_iso, rows=200, cols=10)
        headers = [
            "Nombres y Apellidos", "Fecha", "Hora de Ingreso", "Horario de Control",
            "Tiempo de Tardanza (min)", "Monto Calculado (S/)", "Ejercicio (repeticiones)",
            "Tipo de Pago", "Estado", "Monto Final (S/)",
        ]
        ws.insert_row(headers, 1)
        ws.format("A1:J1", {
            "backgroundColor": {"red": 0.31, "green": 0.27, "blue": 0.90},
            "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True},
            "horizontalAlignment": "CENTER",
        })
    return ws


def get_drive_service():
    creds = get_google_credentials()
    return build("drive", "v3", credentials=creds)


def detect_day_and_schedule(weekday):
    if weekday in SCHEDULES:
        name, start, end = SCHEDULES[weekday]
        return name, start, end, True
    return None, None, None, False


def calculate_penalty(arrival_time, start_time, end_time, ref_date):
    arrival_dt = datetime.combine(ref_date, arrival_time)
    start_dt = datetime.combine(ref_date, start_time)
    end_dt = datetime.combine(ref_date, end_time)

    if arrival_time <= start_time:
        return 0, 0.0, 0

    effective_arrival = end_dt if arrival_time > end_time else arrival_dt
    delay_minutes = max(0, int((effective_arrival - start_dt).total_seconds() / 60))

    money_blocks = (delay_minutes + 9) // 10 if delay_minutes > 0 else 0
    money_amount = money_blocks * 0.50
    exercise_reps = delay_minutes
    return delay_minutes, money_amount, exercise_reps


def generate_pdf(date_str, records, schedule_name):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf_path = tmp.name

    doc = SimpleDocTemplate(
        pdf_path, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("T", parent=styles["Heading1"], fontSize=20,
        textColor=colors.HexColor("#4f46e5"), alignment=1, spaceAfter=4, fontName="Helvetica-Bold")
    subtitle_style = ParagraphStyle("S", parent=styles["Normal"], fontSize=10.5,
        textColor=colors.HexColor("#64748b"), alignment=1, spaceAfter=18)
    h4_style = ParagraphStyle("H4", parent=styles["Heading4"], fontSize=12.5,
        textColor=colors.HexColor("#0f172a"), spaceBefore=10, spaceAfter=8, fontName="Helvetica-Bold")

    story = []
    story.append(Paragraph("REPORTE DE TARDANZAS", title_style))
    story.append(Paragraph(f"Fecha: {date_str}  |  Horario: {schedule_name}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0"),
        spaceBefore=2, spaceAfter=14))

    total_money = 0.0
    total_debt = 0.0
    paid_count = exercise_count = debt_count = ontime_count = 0

    table_data = [["#", "Nombres y Apellidos", "Ingreso", "Tardanza", "Monto S/", "Ejercicio", "Estado"]]
    for i, r in enumerate(records, 1):
        table_data.append([
            str(i), r.get("Nombres y Apellidos", ""), r.get("Hora de Ingreso", ""),
            f"{r.get('Tiempo de Tardanza (min)', 0)} min",
            f"S/ {float(r.get('Monto Final (S/)', 0.0)):.2f}",
            f"{r.get('Ejercicio (repeticiones)', 0)} reps",
            r.get("Estado", ""),
        ])
        mf = float(r.get("Monto Final (S/)", 0.0))
        mc = float(r.get("Monto Calculado (S/)", 0.0))
        tp = r.get("Tipo de Pago", "")
        est = r.get("Estado", "")
        if tp == "Pagar Dinero":
            total_money += mf; paid_count += 1
        elif tp == "Realizar Ejercicio":
            exercise_count += 1
        elif "Deuda" in est:
            total_debt += mc; debt_count += 1
        else:
            ontime_count += 1

    table = Table(table_data, repeatRows=1, hAlign="CENTER",
        colWidths=[0.9*cm, 6.2*cm, 2.3*cm, 2*cm, 2*cm, 2*cm, 2.6*cm])
    table_style = [
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#4f46e5")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 8.5),
        ("FONTSIZE", (0,1), (-1,-1), 7.8),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("ALIGN", (1,1), (1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.white]),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ]
    for i, r in enumerate(records, 1):
        est = r.get("Estado", "")
        tp = r.get("Tipo de Pago", "")
        if "Deuda" in est:
            table_style.append(("BACKGROUND", (0,i), (-1,i), colors.HexColor("#fef2f2")))
        elif tp == "Realizar Ejercicio":
            table_style.append(("BACKGROUND", (0,i), (-1,i), colors.HexColor("#eff6ff")))
        elif tp == "Pagar Dinero":
            table_style.append(("BACKGROUND", (0,i), (-1,i), colors.HexColor("#f0fdf4")))
    table.setStyle(TableStyle(table_style))
    story.append(table)

    story.append(Spacer(1, 0.8*cm))
    story.append(Paragraph("RESUMEN DEL DÍA", h4_style))

    summary_data = [
        ["Detalle", "Valor"],
        ["Total de Alumnos Registrados", str(len(records))],
        ["Alumnos a Tiempo", str(ontime_count)],
        ["Alumnos que Pagaron", f"{paid_count}  (S/ {total_money:.2f})"],
        ["Alumnos que Hicieron Ejercicio", str(exercise_count)],
        ["Alumnos con Deuda", f"{debt_count}  (S/ {total_debt:.2f} pendiente)"],
        ["Total Recaudado (S/)", f"S/ {total_money:.2f}"],
    ]
    summary_table = Table(summary_data, colWidths=[8.5*cm, 8.5*cm], hAlign="LEFT")
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME", (0,1), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9.5),
        ("ALIGN", (1,1), (1,-1), "CENTER"),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0,-1), (1,-1), colors.HexColor("#dcfce7")),
        ("BACKGROUND", (0,-2), (1,-2), colors.HexColor("#fee2e2")),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(summary_table)

    story.append(Spacer(1, 2*cm))
    story.append(HRFlowable(width="35%", thickness=0.8, color=colors.HexColor("#64748b"), hAlign="CENTER"))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Firma del Encargado", ParagraphStyle("sig",
        parent=styles["Normal"], alignment=1, textColor=colors.HexColor("#475569"), fontSize=9)))

    doc.build(story)
    return pdf_path, total_money, total_debt


def upload_to_drive(pdf_path, file_name):
    drive_service = get_drive_service()
    folder_id = st.secrets.get("drive_folder_id", "")
    file_metadata = {"name": file_name, "mimeType": "application/pdf"}
    if folder_id:
        file_metadata["parents"] = [folder_id]
    media = MediaFileUpload(pdf_path, mimetype="application/pdf")
    file = drive_service.files().create(body=file_metadata, media_body=media,
        fields="id,webViewLink").execute()
    return file.get("webViewLink", "")


def locked_view(bot_email, real_now):
    st.markdown("""
        <div class="brand-header">
            <h1>🎓 CupoApp</h1>
            <div class="tagline">Sistema de Control de Tardanzas · UC</div>
        </div>
    """, unsafe_allow_html=True)

    weekday = real_now.weekday()
    st.markdown(f"""
        <div class="locked-screen">
            <div class="icon">🔒</div>
            <h2>Sistema Bloqueado</h2>
            <p>Hoy es <strong>{DAY_NAMES[weekday]}</strong>. El sistema de control solo está disponible los días <strong>Lunes</strong> y <strong>Miércoles</strong>.</p>
            <div class="lock-days-grid">
                <div class="lock-day active">Lunes 19:10 – 20:30</div>
                <div class="lock-day active">Miércoles 17:30 – 20:30</div>
                <div class="lock-day inactive">Martes · Jueves · Viernes</div>
            </div>
            <p style="font-size:0.82rem;">Regresar en el día programado para habilitar el registro.</p>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("""
            <div class="brand-header" style="border-radius:0;">
                <h1>🎓 CupoApp</h1>
                <div class="tagline">Sistema de Control de Tardanzas</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
            <div style="padding:6px;">
                <p style="margin:0;font-size:0.8rem;color:#64748b;">Fecha actual:</p>
                <p style="margin:2px 0 14px 0;font-weight:700;color:#0f172a;">
                    {DAY_NAMES[weekday]}, {real_now.strftime('%d/%m/%Y %H:%M')}
                </p>
                <div class="badge badge-danger" style="margin-bottom:14px;">SISTEMA BLOQUEADO</div>
            </div>
        """, unsafe_allow_html=True)
        with st.expander("🛠️ Configuración Google", expanded=False):
            st.markdown("Comparte Sheet y carpeta Drive con:")
            st.code(bot_email, language=None)

    st.markdown('<div class="footer-brand">© 2026 <strong>CupoApp</strong> · Taller de Investigación UC</div>',
        unsafe_allow_html=True)


def main_view(ref_datetime, is_test_mode, real_now):
    with st.sidebar:
        st.markdown("""
            <div class="brand-header" style="border-radius:0;">
                <h1>🎓 CupoApp</h1>
                <div class="tagline">Sistema de Control de Tardanzas</div>
            </div>
        """, unsafe_allow_html=True)

        if is_test_mode:
            st.markdown("""
                <div class="badge badge-warning" style="margin-bottom:12px;display:block;text-align:center;">
                    🧪 MODO PRUEBAS ACTIVADO
                </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style="padding:6px;">
                <p style="margin:0;font-size:0.76rem;color:#64748b;font-weight:500;">
                    {"Fecha/Hora Simulada" if is_test_mode else "Fecha y Hora Actual"}
                </p>
                <p style="margin:2px 0 4px 0;font-weight:800;color:#0f172a;font-size:1.02rem;">
                    {DAY_NAMES[ref_datetime.weekday()]}, {ref_datetime.strftime('%d/%m/%Y')}
                </p>
                <p style="margin:0 0 14px 0;color:#4f46e5;font-weight:700;font-size:1.15rem;">
                    {ref_datetime.strftime('%H:%M')}
                </p>
            </div>
        """, unsafe_allow_html=True)

        with st.expander("📅 Horarios Oficiales"):
            st.markdown("""
                <div style="display:flex;flex-direction:column;gap:8px;padding:4px 0;">
                    <div style="display:flex;justify-content:space-between;align-items:center;background:#f1f5f9;padding:10px 12px;border-radius:8px;">
                        <span style="font-weight:700;">Lunes</span>
                        <span class="badge badge-info">19:10 – 20:30</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;background:#f1f5f9;padding:10px 12px;border-radius:8px;">
                        <span style="font-weight:700;">Miércoles</span>
                        <span class="badge badge-info">17:30 – 20:30</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with st.expander("💸 Reglas de Penalidad"):
            st.markdown("""
                <div style="padding:4px 0;font-size:0.82rem;color:#334155;line-height:1.55;">
                    <p style="margin:0 0 8px 0;"><strong>Dinero:</strong> S/ 0.50 por cada bloque de 10 min (o fracción).</p>
                    <p style="margin:0 0 8px 0;"><strong>Ejercicio:</strong> 1 min de tardanza = 1 repetición. Saldará la deuda monetaria total.</p>
                    <p style="margin:0;"><strong>Deuda:</strong> Si no paga ni hace ejercicio, queda deudor del monto calculado.</p>
                </div>
            """, unsafe_allow_html=True)

        with st.expander("🔗 Configuración Google"):
            bot_email = st.secrets.get("google_service_account", {}).get("client_email", "-")
            st.markdown("Comparte tu **Sheet** y **carpeta Drive** con este correo (Editor):")
            st.code(bot_email, language=None)
            sk = st.secrets.get("sheet_key", "-")
            df = st.secrets.get("drive_folder_id", "-")
            st.markdown(f"**Sheet ID:** `{sk[:12]}...`\n\n**Drive Folder ID:** `{df[:12]}...`")

    date_str = ref_datetime.strftime("%d/%m/%Y")
    date_iso = ref_datetime.strftime("%Y-%m-%d")
    weekday = ref_datetime.weekday()
    day_name, default_start, default_end, _ = detect_day_and_schedule(weekday)
    schedule_name = f"{day_name} ({default_start.strftime('%H:%M')} - {default_end.strftime('%H:%M')})"
    start_time, end_time = default_start, default_end

    st.markdown("""
        <div class="brand-header" style="margin-bottom:22px;">
            <h1>🎓 Control de Tardanzas</h1>
            <div class="tagline">CupoApp · Registro oficial de puntualidad</div>
        </div>
    """, unsafe_allow_html=True)

    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.markdown(f"""
            <div class="stat-card primary">
                <div class="stat-icon">📅</div>
                <p class="stat-label">Día de Control</p>
                <p class="stat-value">{day_name}</p>
            </div>
        """, unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""
            <div class="stat-card warning">
                <div class="stat-icon">⏰</div>
                <p class="stat-label">Horario</p>
                <p class="stat-value" style="font-size:1.1rem;margin-top:10px;">
                    {default_start.strftime('%H:%M')} – {default_end.strftime('%H:%M')}
                </p>
            </div>
        """, unsafe_allow_html=True)
    with sc3:
        st.markdown(f"""
            <div class="stat-card success">
                <div class="stat-icon">🗓️</div>
                <p class="stat-label">Fecha</p>
                <p class="stat-value" style="font-size:1.1rem;margin-top:10px;">{date_str}</p>
            </div>
        """, unsafe_allow_html=True)
    with sc4:
        badge_class = "badge-success" if is_test_mode else "badge-info"
        st.markdown(f"""
            <div class="stat-card danger">
                <div class="stat-icon">{"🧪" if is_test_mode else "⚡"}</div>
                <p class="stat-label">Estado</p>
                <p class="stat-value" style="font-size:1rem;margin-top:8px;">
                    <span class="badge {badge_class}" style="font-size:0.72rem;">
                        {"MODO PRUEBAS" if is_test_mode else "EN VIVO"}
                    </span>
                </p>
            </div>
        """, unsafe_allow_html=True)

    tab_reg, tab_hist, tab_info = st.tabs(["📝 Registro de Tardanzas", "📊 Historial del Día", "ℹ️ Información"])

    with tab_info:
        info1, info2 = st.columns([1.3, 1])
        with info1:
            st.markdown("""
                <div class="panel">
                    <h3 class="panel-title">📘 Guía Rápida</h3>
                    <p class="panel-subtitle">Pasos para registrar correctamente una tardanza</p>
                    <ol style="color:#334155;line-height:1.85;font-size:0.92rem;margin:0;padding-left:20px;">
                        <li>Ingresa los <strong>Nombres y Apellidos</strong> completos.</li>
                        <li>Verifica la <strong>Hora de Ingreso</strong> (se sugiere la hora actual).</li>
                        <li>Selecciona la <strong>forma de resolver</strong> la penalidad.</li>
                        <li>Agrega más alumnos con <strong>+ Agregar Tardón</strong> si llegaron varios a la vez.</li>
                        <li>Presiona <strong>Guardar Registros</strong> para enviar a Google Sheets.</li>
                        <li>Al finalizar genera el <strong>Reporte PDF</strong> y se subirá automáticamente a Drive.</li>
                    </ol>
                </div>
            """, unsafe_allow_html=True)
        with info2:
            st.markdown("""
                <div class="panel">
                    <h3 class="panel-title">💸 Tabla de Penalidades</h3>
                    <p class="panel-subtitle">Bloques de 10 minutos · S/ 0.50 cada uno</p>
            """, unsafe_allow_html=True)
            rows_df = pd.DataFrame([
                ["00 - 10 min", "S/ 0.50", "10 reps"],
                ["11 - 20 min", "S/ 1.00", "20 reps"],
                ["21 - 30 min", "S/ 1.50", "30 reps"],
                ["31 - 40 min", "S/ 2.00", "40 reps"],
                ["41 - 50 min", "S/ 2.50", "50 reps"],
                ["51 - 60 min", "S/ 3.00", "60 reps"],
            ], columns=["Tiempo Tardanza", "Monto (Dinero)", "Ejercicio (reps)"])
            st.dataframe(rows_df, use_container_width=True, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with tab_reg:
        st.markdown("""
            <div class="panel" style="margin-top:10px;">
                <h3 class="panel-title">📝 Registro de Alumnos</h3>
                <p class="panel-subtitle">Agrega a los alumnos que llegaron tarde. El sistema calcula la penalidad en tiempo real.</p>
            </div>
        """, unsafe_allow_html=True)

        if "num_students" not in st.session_state:
            st.session_state.num_students = 1

        records = []
        total_collected = 0.0
        total_debt = 0.0
        total_late = 0

        for idx in range(st.session_state.num_students):
            with st.container():
                st.markdown(f"""
                    <div class="student-form-card">
                        <div class="student-card-header">
                            <span class="tag">👤 Alumno #{idx + 1}</span>
                        </div>
                """, unsafe_allow_html=True)

                c1, c2 = st.columns([1.3, 1])
                with c1:
                    nk = f"name_{idx}"
                    if nk not in st.session_state:
                        st.session_state[nk] = ""
                    name = st.text_input("Nombres y Apellidos:", placeholder="Ej: Juan Pérez Gómez", key=nk)
                with c2:
                    tk = f"time_{idx}"
                    if tk not in st.session_state:
                        st.session_state[tk] = ref_datetime.time()
                    arrival = st.time_input("Hora de Ingreso:", value=st.session_state[tk], key=tk)
                    arrival_t = arrival.time() if isinstance(arrival, datetime) else arrival

                delay_min, money_amt, exercise_reps = calculate_penalty(
                    arrival_t, start_time, end_time, ref_datetime.date()
                )

                pk = f"pay_{idx}"
                if pk not in st.session_state:
                    if delay_min == 0:
                        st.session_state[pk] = "Pagar Dinero"
                    else:
                        st.session_state[pk] = "Sin Pago / Deuda"
                payment_type = st.selectbox("Tipo de Pago / Resolución:",
                    ["Pagar Dinero", "Realizar Ejercicio", "Sin Pago / Deuda"], key=pk,
                    disabled=(delay_min == 0))

                final_amount = 0.0
                estado = "A Tiempo"

                if delay_min > 0:
                    if payment_type == "Pagar Dinero":
                        final_amount = money_amt
                        estado = f"Pagado (S/ {money_amt:.2f})"
                        total_collected += money_amt
                    elif payment_type == "Realizar Ejercicio":
                        final_amount = 0.0
                        estado = f"Ejercicio Realizado ({exercise_reps} reps)"
                    else:
                        final_amount = 0.0
                        estado = f"Con Deuda (S/ {money_amt:.2f})"
                        total_debt += money_amt
                    total_late += 1

                if delay_min == 0:
                    st.markdown(f"""
                        <div class="penalty-box on-time">
                            <h4>✅ Alumno a Tiempo</h4>
                            <div class="penalty-grid">
                                <div class="penalty-item">
                                    <div class="pi-label">Estado</div>
                                    <div class="pi-value" style="color:#15803d;">A tiempo</div>
                                </div>
                                <div class="penalty-item">
                                    <div class="pi-label">Penalidad</div>
                                    <div class="pi-value" style="color:#15803d;">S/ 0.00</div>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="penalty-box late">
                            <h4>⚠️ Penalidad Calculada Automáticamente</h4>
                            <div class="penalty-grid">
                                <div class="penalty-item">
                                    <div class="pi-label">Tiempo de Tardanza</div>
                                    <div class="pi-value">{delay_min} min</div>
                                </div>
                                <div class="penalty-item">
                                    <div class="pi-label">Bloques</div>
                                    <div class="pi-value">{(delay_min + 9)//10} bloque(s)</div>
                                </div>
                                <div class="penalty-item">
                                    <div class="pi-label">Monto (Dinero)</div>
                                    <div class="pi-value" style="color:#b45309;">S/ {money_amt:.2f}</div>
                                </div>
                                <div class="penalty-item">
                                    <div class="pi-label">Ejercicio (repeticiones)</div>
                                    <div class="pi-value" style="color:#92400e;">{exercise_reps} reps</div>
                                </div>
                            </div>
                            <div style="margin-top:10px;">
                                <span class="badge {"badge-success" if final_amount > 0 else ("badge-info" if payment_type == "Realizar Ejercicio" else "badge-danger")}">
                                    {estado}
                                </span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

                records.append({
                    "idx": idx,
                    "Nombre": name.strip(),
                    "Fecha": date_str,
                    "Hora Ingreso": arrival_t.strftime("%H:%M:%S"),
                    "Horario": schedule_name,
                    "Tiempo Tardanza (min)": delay_min,
                    "Monto Calculado (S/)": money_amt,
                    "Ejercicio (repeticiones)": exercise_reps,
                    "Tipo de Pago": payment_type,
                    "Estado": estado,
                    "Monto Final (S/)": final_amount,
                })

        colA, colB, colC = st.columns([2, 1, 1])
        with colA:
            if st.button("➕ Agregar Tardón (nuevo alumno)", use_container_width=True):
                st.session_state.num_students += 1
                st.rerun()
        with colB:
            if st.session_state.num_students > 1 and st.button("🗑️ Quitar último", use_container_width=True):
                for k in [f"name_{st.session_state.num_students - 1}",
                          f"time_{st.session_state.num_students - 1}",
                          f"pay_{st.session_state.num_students - 1}"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.session_state.num_students -= 1
                st.rerun()
        with colC:
            if st.button("🔄 Resetear Formulario", use_container_width=True):
                for k in list(st.session_state.keys()):
                    if k.startswith(("name_", "time_", "pay_", "num_students")):
                        del st.session_state[k]
                st.rerun()

        st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)

        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            st.markdown(f"""
                <div class="stat-card success">
                    <div class="stat-icon">💰</div>
                    <p class="stat-label">Total Recaudado Hoy</p>
                    <p class="stat-value" style="color:#15803d;">S/ {total_collected:.2f}</p>
                </div>
            """, unsafe_allow_html=True)
        with rc2:
            st.markdown(f"""
                <div class="stat-card danger">
                    <div class="stat-icon">⚠️</div>
                    <p class="stat-label">Deuda Pendiente</p>
                    <p class="stat-value" style="color:#b91c1c;">S/ {total_debt:.2f}</p>
                </div>
            """, unsafe_allow_html=True)
        with rc3:
            st.markdown(f"""
                <div class="stat-card warning">
                    <div class="stat-icon">🚶</div>
                    <p class="stat-label">Alumnos Tarde</p>
                    <p class="stat-value">{total_late} / {len(records)}</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)

        if st.button("💾  Guardar Registros en Google Sheets", type="primary", use_container_width=True):
            valid = [r for r in records if r["Nombre"]]
            if not valid:
                st.error("❌ No hay registros válidos. Ingresa al menos un nombre.")
            else:
                try:
                    with st.spinner("Guardando registros en Google Sheets..."):
                        ws = get_or_create_worksheet(date_iso)
                        existing = ws.get_all_values()
                        start_row = len(existing) + 1
                        rows = [[
                            r["Nombre"], r["Fecha"], r["Hora Ingreso"], r["Horario"],
                            r["Tiempo Tardanza (min)"], r["Monto Calculado (S/)"],
                            r["Ejercicio (repeticiones)"], r["Tipo de Pago"],
                            r["Estado"], r["Monto Final (S/)"],
                        ] for r in valid]
                        ws.insert_rows(rows, start_row)
                    recaudado = sum(r["Monto Final (S/)"] for r in valid)
                    st.success(f"✅ {len(valid)} registro(s) guardado(s). Total recaudado: S/ {recaudado:.2f}")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Error al guardar: {str(e)}")
                    st.info("💡 Verifica: 1) Secrets en Streamlit, 2) Sheet compartido con bot, 3) APIs activadas.")

        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)

        if st.button("📄  Generar Reporte PDF del Día (y subir a Drive)", use_container_width=True):
            try:
                with st.spinner("Generando PDF y subiendo a Google Drive..."):
                    ws = get_or_create_worksheet(date_iso)
                    data = ws.get_all_records()
                    if not data:
                        st.warning("⚠️ No hay registros guardados para este día. Primero guarda los registros.")
                    else:
                        pdf_path, pdf_total, pdf_debt = generate_pdf(date_str, data, schedule_name)
                        file_name = f"Reporte_Tardanzas_{date_iso}.pdf"
                        link = upload_to_drive(pdf_path, file_name)
                        with open(pdf_path, "rb") as f:
                            pdf_bytes = f.read()
                        d1, d2 = st.columns(2)
                        with d1:
                            st.download_button("⬇️  Descargar PDF", pdf_bytes, file_name,
                                "application/pdf", use_container_width=True, type="primary")
                        with d2:
                            if link:
                                st.success("✅ PDF generado y subido a Google Drive.")
                                st.markdown(f"[☁️  Abrir PDF en Google Drive]({link})")
                        try: os.unlink(pdf_path)
                        except: pass
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    with tab_hist:
        try:
            with st.spinner("Cargando historial del día desde Google Sheets..."):
                ws = get_or_create_worksheet(date_iso)
                data = ws.get_all_records()
                if not data:
                    st.info("📭 No hay registros guardados para este día aún. Usa la pestaña de Registro.")
                else:
                    df = pd.DataFrame(data)
                    st.markdown(f"""
                        <div class="panel" style="margin-top:10px;">
                            <h3 class="panel-title">📊 Historial de Hoy ({date_str})</h3>
                            <p class="panel-subtitle">Total de {len(df)} registro(s) guardados en Google Sheets.</p>
                        </div>
                    """, unsafe_allow_html=True)

                    recaudado = sum(float(r.get("Monto Final (S/)", 0)) for r in data)
                    deuda = sum(float(r.get("Monto Calculado (S/)", 0)) for r in data
                                if isinstance(r.get("Estado", ""), str) and "Deuda" in r.get("Estado", ""))
                    t1, t2, t3 = st.columns(3)
                    t1.metric("Registros", len(df))
                    t2.metric("Recaudado Total", f"S/ {recaudado:.2f}")
                    t3.metric("Deuda Pendiente", f"S/ {deuda:.2f}")
                    st.dataframe(df, use_container_width=True, hide_index=True, height=420)
        except Exception as e:
            st.warning(f"No se pudo cargar el historial: {str(e)}")

    st.markdown('<div class="footer-brand">© 2026 <strong>CupoApp</strong> · Taller de Investigación UC · Desarrollado con Streamlit</div>',
        unsafe_allow_html=True)


def main():
    bot_email = st.secrets.get("google_service_account", {}).get("client_email",
        "bot-tardanzas@true-ion-506204-h6.iam.gserviceaccount.com")
    real_now = datetime.now()

    with st.sidebar:
        with st.expander("🧪 Modo Pruebas (Testing)", expanded=False):
            st.markdown("""
                <p style="font-size:0.8rem;color:#64748b;margin:0 0 8px 0;">
                    Activa este modo para simular otros días/horarios y probar el sistema sin esperar a Lunes o Miércoles.
                </p>
            """, unsafe_allow_html=True)
            test_mode = st.checkbox("Activar Modo Pruebas", value=False, key="_test_mode_toggle")

    is_test_mode = bool(test_mode)

    if not is_test_mode:
        real_weekday = real_now.weekday()
        if real_weekday not in VALID_WEEKDAYS:
            locked_view(bot_email, real_now)
            return
        ref_datetime = real_now
    else:
        with st.sidebar:
            st.markdown("""
                <div class="panel" style="padding:12px;border:1px dashed #f59e0b;margin-top:8px;">
                    <h3 class="panel-title" style="font-size:0.95rem;">🧪 Simular Fecha y Hora</h3>
                    <p class="panel-subtitle">Ajusta estos valores para probar escenarios de Lunes o Miércoles.</p>
            """, unsafe_allow_html=True)

            default_test_date = real_now.date()
            days_until_monday = (0 - real_now.weekday()) % 7
            if days_until_monday == 0 and real_now.weekday() != 0:
                days_until_monday = 7
            elif real_now.weekday() not in (0, 2):
                days_until_monday = (0 - real_now.weekday()) % 7
                if days_until_monday == 0:
                    days_until_monday = 2 if (2 - real_now.weekday()) > 0 else 7 - real_now.weekday() + 2

            suggested_date = real_now.date() + timedelta(days=days_until_monday if real_now.weekday() not in (0,2) else 0)
            if real_now.weekday() not in (0, 2):
                suggested_date = real_now.date() + timedelta(days=((0 - real_now.weekday()) % 7 or 7))

            t_date = st.date_input("Fecha a simular:", value=suggested_date,
                help="Escoge un Lunes o Miércoles", key="_test_date")
            t_time = st.time_input("Hora a simular:", value=time(19, 20),
                help="Ej: Lunes 19:20 para probar una tardanza de 10 min", key="_test_time")

            if t_date.weekday() not in VALID_WEEKDAYS:
                st.warning("⚠️ La fecha seleccionada NO es Lunes ni Miércoles. Elige otra fecha.")
            st.markdown("</div>", unsafe_allow_html=True)

        if t_date.weekday() not in VALID_WEEKDAYS:
            locked_view(bot_email, datetime.combine(t_date, t_time))
            return

        ref_datetime = datetime.combine(t_date, t_time)

    main_view(ref_datetime, is_test_mode, real_now)


if __name__ == "__main__":
    main()
