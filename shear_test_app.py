import streamlit as st
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 1. Page Configuration
st.set_page_config(page_title="G&G Direct Shear Suite", layout="wide", page_icon="🧪")

st.title("🪨 Direct Shear Test Calculator & Report Generator")
st.write("ASTM D3080 standard ke mutabiq Cohesion (c) aur Friction Angle (φ) calculate, plot aur PDF report me graph embedded karne ka platform.")

# 2. Sidebar: Metadata Details
st.sidebar.header("📋 Project Information")
company_name = st.sidebar.text_input("COMPANY NAME", "Geoscience & Geotechnical Engineers and Consultant Private Limited")
project_name = st.sidebar.text_input("PROJECT NAME", "Soil Investigation Project")
client_name = st.sidebar.text_input("CLIENT NAME", "M/s Alpha Developers")
location = st.sidebar.text_input("SITE LOCATION", "Karachi, Pakistan")
sample_id = st.sidebar.text_input("SAMPLE ID / DEPTH", "BH-02 @ 3.0m")

# UPDATED: Selectbox ko remove kar ke simple text_input lagaya hai taake aap soil/rock khud type kar sakein
sample_type = st.sidebar.text_input("SOIL / ROCK TYPE", "Silty Sand (SM)")

test_date = st.sidebar.date_input("TEST DATE", datetime.date.today())

st.sidebar.markdown("---")
st.sidebar.header("📐 Box Dimensions")
box_w = st.sidebar.number_input("Box Width (cm)", value=6.0, step=0.1)
box_l = st.sidebar.number_input("Box Length (cm)", value=6.0, step=0.1)

# Area calculation (cm²)
area_cm2 = box_w * box_l
st.sidebar.info(f"📐 Calculated Area: {area_cm2:.2f} cm²")

# 3. Main Data Input Matrix (3 Trials Standard)
st.header("📥 Laboratory Test Data Input")
st.write("Teeno (3) Trials ke liye Normal Load aur Peak Shear Load (kg) enter karein:")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🔬 Trial 1")
    normal_load_1 = st.number_input("Normal Load (kg) - T1", value=18.0, key="nl1")
    shear_load_1 = st.number_input("Peak Shear Load (kg) - T1", value=14.5, key="sl1")
    
    normal_stress_1 = normal_load_1 / area_cm2
    shear_stress_1 = shear_load_1 / area_cm2

with col2:
    st.subheader("🔬 Trial 2")
    normal_load_2 = st.number_input("Normal Load (kg) - T2", value=36.0, key="nl2")
    shear_load_2 = st.number_input("Peak Shear Load (kg) - T2", value=24.0, key="sl2")
    
    normal_stress_2 = normal_load_2 / area_cm2
    shear_stress_2 = shear_load_2 / area_cm2

with col3:
    st.subheader("🔬 Trial 3")
    normal_load_3 = st.number_input("Normal Load (kg) - T3", value=54.0, key="nl3")
    shear_load_3 = st.number_input("Peak Shear Load (kg) - T3", value=33.5, key="sl3")
    
    normal_stress_3 = normal_load_3 / area_cm2
    shear_stress_3 = shear_load_3 / area_cm2

# Arrays for calculation
normal_stresses = np.array([normal_stress_1, normal_stress_2, normal_stress_3])
shear_stresses = np.array([shear_stress_1, shear_stress_2, shear_stress_3])

# 4. Geotechnical Engineering Calculations (Linear Regression)
slope, intercept = np.polyfit(normal_stresses, shear_stresses, 1)

cohesion = max(0.0, intercept) # Cohesion negative nahi ho sakti
phi_radians = np.arctan(slope)
phi_degrees = np.degrees(phi_radians)

# Display Results Card
st.markdown("---")
st.header("📊 Calculated Shear Parameters")
res_c1, res_c2 = st.columns(2)
with res_c1:
    st.metric(label="Cohesion (c)", value=f"{cohesion:.3f} kg/cm²")
with res_c2:
    st.metric(label="Angle of Internal Friction (φ)", value=f"{phi_degrees:.1f}°")

# 5. Graph Plotting Function (Used for both Streamlit UI and PDF Report)
def generate_graph_image():
    fig, ax = plt.subplots(figsize=(7, 4.5))
    # Plot data points
    ax.scatter(normal_stresses, shear_stresses, color='red', s=80, zorder=5, label='Test Data Points')
    
    # Plot best-fit line
    x_fit = np.linspace(0, max(normal_stresses)*1.2, 100)
    y_fit = intercept + slope * x_fit
    ax.plot(x_fit, y_fit, color='#1a365d', linestyle='-', linewidth=2, label=f'Failure Envelope (c={cohesion:.2f}, φ={phi_degrees:.1f}°)')
    
    # Graph Formatting
    ax.set_xlabel("Normal Stress (σ) [kg/cm²]", fontsize=10, fontweight='bold', color="#1a365d")
    ax.set_ylabel("Shear Stress (τ) [kg/cm²]", fontsize=10, fontweight='bold', color="#1a365d")
    ax.set_title("DIRECT SHEAR TEST - FAILURE ENVELOPE", fontsize=11, fontweight='bold', pad=12, color="#1a365d")
    ax.set_xlim(0, max(normal_stresses)*1.2)
    ax.set_ylim(0, max(shear_stresses)*1.2)
    ax.grid(True, linestyle='--', alpha=0.6, color='#cbd5e0')
    ax.legend(loc='upper left', fontsize=9)
    plt.tight_layout()
    
    # Save plot to buffer
    img_buf = BytesIO()
    plt.savefig(img_buf, format='png', dpi=200)
    img_buf.seek(0)
    plt.close(fig)
    return img_buf

# Render graph on UI
st.markdown("---")
st.header("📈 Shear Strength Failure Envelope")
graph_img = generate_graph_image()
st.image(graph_img, caption="Generated Failure Envelope Plot", width=700)

# 6. Automated PDF Generation Engine with Embedded Graph
def generate_pdf(graph_buffer):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    comp_style = ParagraphStyle('CompStyle', parent=styles['Heading1'], fontSize=16, leading=18, textColor=colors.HexColor('#1a365d'), alignment=1)
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading2'], fontSize=12, leading=14, textColor=colors.HexColor('#2b6cb0'), alignment=1)
    meta_lbl = ParagraphStyle('MetaLbl', parent=styles['Normal'], fontSize=9, fontName="Helvetica-Bold", textColor=colors.HexColor('#1a365d'))
    meta_val = ParagraphStyle('MetaVal', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#2d3748'))
    cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontSize=9, fontName="Helvetica-Bold", alignment=1)
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=9, alignment=1)

    story = []
    
    # Header Banner
    story.append(Paragraph(f"<b>{company_name.upper()}</b>", comp_style))
    story.append(Paragraph("DIRECT SHEAR TEST REPORT (ASTM D3080)", title_style))
    story.append(Spacer(1, 15))
    
    # Metadata Table
    meta_data = [
        [Paragraph("PROJECT NAME:", meta_lbl), Paragraph(project_name, meta_val), Paragraph("SAMPLE ID:", meta_lbl), Paragraph(sample_id, meta_val)],
        [Paragraph("CLIENT NAME:", meta_lbl), Paragraph(client_name, meta_val), Paragraph("SOIL / ROCK TYPE:", meta_lbl), Paragraph(sample_type, meta_val)],
        [Paragraph("SITE LOCATION:", meta_lbl), Paragraph(location, meta_val), Paragraph("TEST DATE:", meta_lbl), Paragraph(test_date.strftime('%d-%m-%Y'), meta_val)],
        [Paragraph("BOX DIMENSIONS:", meta_lbl), Paragraph(f"{box_w}cm x {box_l}cm", meta_val), Paragraph("BOX AREA:", meta_lbl), Paragraph(f"{area_cm2:.2f} cm²", meta_val)]
    ]
    meta_table = Table(meta_data, colWidths=[110, 160, 110, 160])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#1a365d')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    # Test Data Table
    story.append(Paragraph("<b>LABORATORY TEST OBSERVATIONS & CALCULATIONS</b>", styles['Heading4']))
    story.append(Spacer(1, 5))
    
    table_content = [
        [Paragraph("Trial No.", cell_bold), Paragraph("Normal Load (kg)", cell_bold), Paragraph("Normal Stress (kg/cm²)", cell_bold), 
         Paragraph("Peak Shear Load (kg)", cell_bold), Paragraph("Peak Shear Stress (kg/cm²)", cell_bold)]
    ]
    
    for idx in range(3):
        table_content.append([
            Paragraph(str(idx+1), cell_style),
            Paragraph(f"{[normal_load_1, normal_load_2, normal_load_3][idx]:.1f}", cell_style),
            Paragraph(f"{normal_stresses[idx]:.3f}", cell_style),
            Paragraph(f"{[shear_load_1, shear_load_2, shear_load_3][idx]:.1f}", cell_style),
            Paragraph(f"{shear_stresses[idx]:.3f}", cell_style)
        ])
        
    data_table = Table(table_content, colWidths=[60, 110, 120, 110, 140])
    data_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a365d')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e0')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(data_table)
    story.append(Spacer(1, 15))
    
    # Interpretation Results Table
    story.append(Paragraph("<b>FINAL INTERPRETATION RESULTS</b>", styles['Heading4']))
    story.append(Spacer(1, 5))
    
    result_content = [
        [Paragraph("PARAMETER", cell_bold), Paragraph("VALUE (UNIT)", cell_bold)],
        [Paragraph("Cohesion (c)", cell_style), Paragraph(f"<b>{cohesion:.3f} kg/cm²</b>", cell_style)],
        [Paragraph("Angle of Internal Friction (φ)", cell_style), Paragraph(f"<b>{phi_degrees:.1f}°</b>", cell_style)]
    ]
    res_table = Table(result_content, colWidths=[270, 270])
    res_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2b6cb0')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(res_table)
    story.append(Spacer(1, 15))
    
    # ─── GRAPH INTEGRATION INSIDE PDF ───
    story.append(Paragraph("<b>SHEAR STRENGTH FAILURE ENVELOPE PLOT</b>", styles['Heading4']))
    story.append(Spacer(1, 5))
    
    # ReportLab Image flowable automatically reads from the graph buffer
    pdf_graph = Image(graph_buffer, width=420, height=270)
    pdf_graph.hAlign = 'CENTER'
    story.append(pdf_graph)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Download Button Trigger
st.markdown("---")
st.subheader("💾 Export & Download Laboratory Report")
# Regenerate fresh buffer data for PDF conversion safety
pdf_graph_buf = generate_graph_image()
pdf_file = generate_pdf(pdf_graph_buf)

st.download_button(
    label="📥 Download Direct Shear Test PDF Report (With Graph)",
    data=pdf_file,
    file_name=f"Direct_Shear_Report_{sample_id}.pdf",
    mime="application/pdf"
)
