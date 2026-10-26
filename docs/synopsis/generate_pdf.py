import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(45, 805, "Otterlook AI: Project Synopsis & Technical Specification")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.75)
            self.line(45, 800, 550, 800)
            
        # Footer
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(45, 42, 550, 42)
        
        self.drawString(45, 30, "Otterlook AI &copy; 2026 &bull; Engineering & Research Documentation")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(550, 30, page_str)
        self.restoreState()

def build_pdf(filename="Otterlook_Project_Synopsis.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=45,
        rightMargin=45,
        topMargin=48,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A")
    )
    
    tagline_style = ParagraphStyle(
        'Tagline',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0284C7"),
        textTransform='uppercase',
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#475569")
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=11,
        spaceAfter=5,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=12.5,
        textColor=colors.HexColor("#334155")
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A")
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.0,
        leading=11,
        textColor=colors.HexColor("#334155")
    )

    problem_title_style = ParagraphStyle(
        'ProblemTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#9F1239")
    )

    problem_text_style = ParagraphStyle(
        'ProblemText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=11.5,
        textColor=colors.HexColor("#4C0519")
    )

    story = []

    # Title & Header
    story.append(Paragraph("PROJECT SYNOPSIS &amp; TECHNICAL BLUEPRINT", tagline_style))
    story.append(Paragraph("Otterlook AI: Personal Colour Analysis &amp; Palette Recommendation", title_style))
    story.append(Paragraph("AI-Driven Dermatological Colorimetry, Multi-Region Mesh Segmentation &amp; Probabilistic Styling Engine", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284C7"), spaceAfter=10))

    # SECTION 1: PROJECT IDEA
    story.append(Paragraph("1. PROJECT IDEA", h1_style))
    idea_text = (
        "<b>Otterlook AI</b> is an engineering platform that fuses computer vision, dermatological colorimetry, "
        "and machine learning to analyze front-facing facial portraits, isolate anatomically stable skin regions, "
        "extract multi-space colorimetric feature moments (sRGB, HSV, CIELAB, and Individual Typology Angle), "
        "predict biological skin undertones (<b>Warm</b>, <b>Cool</b>, or <b>Neutral</b>), and dynamically generate "
        "tailored styling recommendations spanning wardrobe, cosmetics, accessories, and seasonal harmonies."
    )
    story.append(Paragraph(idea_text, body_style))
    story.append(Spacer(1, 6))

    # SECTION 2: PROBLEM STATEMENT
    story.append(Paragraph("2. PROBLEM STATEMENT", h1_style))
    
    problems = [
        ("1. Subjectivity & Prohibitive Cost of In-Person Consultation",
         "Traditional personal color analysis relies on in-person fabric draping by human stylists, which is expensive, geographically inaccessible, subjective, and highly prone to ambient lighting variations and human bias."),
        ("2. Failure Across Diverse Global Skin Phototypes",
         "Automated smartphone tools and camera filters routinely sample single arbitrary pixels or use hardcoded RGB threshold heuristics. These techniques fail across global demographic skin diversity (Fitzpatrick phototypes I–VI)."),
        ("3. Contamination by Non-Skin Artifacts & Glare",
         "Unfiltered facial sampling is severely distorted by facial hair, makeup, lips, eyes, specular flash glare, and shadows. Without anatomical landmark isolation, this leads to erroneous classifications and mismatched recommendations.")
    ]
    
    prob_data = []
    for title, desc in problems:
        p_cell = [
            Paragraph(f"<b>{title}</b>", problem_title_style),
            Spacer(1, 2),
            Paragraph(desc, problem_text_style)
        ]
        prob_data.append([p_cell])

    prob_table = Table(prob_data, colWidths=[505])
    prob_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFF1F2")),
        ('LINEBEFORE', (0,0), (0,-1), 3.5, colors.HexColor("#F43F5E")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-2), 3, colors.HexColor("#FFFFFF")),
    ]))
    story.append(prob_table)
    story.append(Spacer(1, 7))

    # SECTION 3: PROPOSED AI/ML & CS SOLUTION
    story.append(Paragraph("3. PROPOSED AI/ML &amp; CS SOLUTION", h1_style))
    solutions = [
        "<b>Rigorous Automated Quality Control:</b> Validates input dimensions, exposure/contrast clipping, and applies the Laplacian variance operator to automatically flag and reject blurry uploads.",
        "<b>Anatomical Multi-Region Extraction:</b> MediaPipe FaceMesh (468 landmarks) with OpenCV Haar cascade fallback segments 4 anatomically consistent regions (Forehead, Cheeks, Jaw/Chin) while eliminating lips, eyes, and hair.",
        "<b>Dual-Space Glare & Outlier Filtering:</b> Gated skin thresholds across YCrCb and HSV combined with 20% upper/lower Interquartile Range (IQR) luminance trimming strip specular flash highlights and deep shadows.",
        "<b>Multi-Space Dermatological Colorimetry:</b> Computes feature moments across sRGB, HSV, and CIELAB (L*a*b*), formulating the Individual Typology Angle (ITA&deg;) and yellow-to-erythema chromatic balance (b*/a*).",
        "<b>Supervised Ensemble Inference:</b> Serialized <code>RandomForestClassifier</code> pipeline predicts Warm, Cool, and Neutral undertones with calibrated, quantitative probability scores.",
        "<b>Styling & Palette Knowledge Engine:</b> Algorithmic mapping translates predicted undertone and seasonal subtype into clothing palettes, cosmetic shades, metal compatibility, and colors to avoid.",
        "<b>Privacy-First Full-Stack Service:</b> Asynchronous FastAPI backend delivering sub-1.5s latency with zero persistent facial storage (pure in-memory RAM processing)."
    ]

    sol_data = [[Paragraph(f"&bull;&nbsp;&nbsp;{s}", bullet_style)] for s in solutions]
    sol_table = Table(sol_data, colWidths=[505])
    sol_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(sol_table)
    story.append(Spacer(1, 8))

    # SECTION 4: KEY MODULES
    story.append(Paragraph("4. KEY MODULES", h1_style))
    modules = [
        ("Module 1: Image Quality Assessment", "Validates resolution, contrast clipping, and uses Laplacian variance to detect/reject blurry uploads."),
        ("Module 2: Landmark & Anatomical Segmenter", "Deploys 468-point MediaPipe FaceMesh to construct sub-orbital cheek patches, forehead, and chin."),
        ("Module 3: Glare, Shadow & Outlier Filter", "Executes YCrCb/HSV skin masks & 20% IQR luminance trimming to ensure unadulterated skin pixels."),
        ("Module 4: Colorimetric Feature Extractor", "Extracts 20+ descriptors: sRGB moments, HSV hue/sat, CIELAB (L*a*b*), ITA&deg;, and b*/a* chromatic ratios."),
        ("Module 5: ML Undertone Classifier", "StandardScaler normalized Random Forest ensemble outputting Warm/Cool/Neutral class probabilities."),
        ("Module 6: Styling & Palette Engine", "Translates undertones to wardrobe hex swatches, cosmetic foundation/lip/blush, jewelry, and colors to avoid."),
        ("Module 7: Interactive API & Presentation Layer", "FastAPI asynchronous REST endpoints with HTML5 Canvas live ROI overlay and copyable color hex cards.")
    ]

    mod_data = []
    # 2-column format for modules
    for i in range(0, len(modules), 2):
        row = []
        for j in range(2):
            if i + j < len(modules):
                m_title, m_desc = modules[i+j]
                cell = [
                    Paragraph(f"<b>{m_title}</b>", ParagraphStyle('MTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.2, leading=10, textColor=colors.HexColor("#0369A1"))),
                    Spacer(1, 2),
                    Paragraph(m_desc, ParagraphStyle('MDesc', parent=styles['Normal'], fontName='Helvetica', fontSize=7.6, leading=9.8, textColor=colors.HexColor("#475569")))
                ]
                row.append(cell)
            else:
                row.append([])
        mod_data.append(row)

    mod_table = Table(mod_data, colWidths=[248, 248])
    mod_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFFFF")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(mod_table)
    story.append(Spacer(1, 8))

    # SECTION 5: ALGORITHMS / TECHNIQUES
    story.append(Paragraph("5. ALGORITHMS / TECHNIQUES", h1_style))
    algo_headers = [
        Paragraph("<b>Domain / Step</b>", table_header_style),
        Paragraph("<b>Algorithms / Methodologies</b>", table_header_style),
        Paragraph("<b>Operational Role &amp; Impact</b>", table_header_style)
    ]
    algo_rows = [
        algo_headers,
        [Paragraph("<b>Facial Landmark Mesh</b>", table_cell_style),
         Paragraph("MediaPipe FaceMesh (468 points) + OpenCV Haar fallback", table_cell_style),
         Paragraph("Sub-millimeter anatomical skin ROI isolation avoiding facial features.", table_cell_style)],
        [Paragraph("<b>Filtering &amp; Quality</b>", table_cell_style),
         Paragraph("Laplacian Variance + YCrCb/HSV Skin Masks + IQR 20% Trimming", table_cell_style),
         Paragraph("Rejects blurry portraits; purges specular flash glare and deep shadow tails.", table_cell_style)],
        [Paragraph("<b>Colorimetry &amp; Descriptors</b>", table_cell_style),
         Paragraph("CIELAB (L*a*b*), ITA&deg; = arctan((L*-50)/b*)*180/&pi;, b*/a* ratio", table_cell_style),
         Paragraph("Measures biological pigmentation and yellow-red balance invariant to brightness.", table_cell_style)],
        [Paragraph("<b>Champion ML Model</b>", table_cell_style),
         Paragraph("<b>Random Forest Classifier</b> (150 trees, max depth 10)", table_cell_style),
         Paragraph("Captures non-linear boundaries; achieved <b>90.74% test accuracy</b> &amp; 0.907 Macro F1.", table_cell_style)],
        [Paragraph("<b>Evaluated Baselines</b>", table_cell_style),
         Paragraph("Support Vector Machines (Linear/RBF), Multinomial Logistic Regression", table_cell_style),
         Paragraph("Benchmarked across 5-fold stratified cross-validation for empirical rigor.", table_cell_style)]
    ]
    algo_table = Table(algo_rows, colWidths=[120, 195, 190])
    algo_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(algo_table)
    story.append(Spacer(1, 8))

    # SECTION 6: DATASETS
    story.append(Paragraph("6. DATASETS", h1_style))
    datasets = [
        "<b>Personal Color Face Dataset:</b> Real facial portraits with Korean 4-season personal color labels (Spring Warm, Autumn Warm, Summer Cool, Winter Cool) for real-world facial and landmark testing.",
        "<b>The Pudding / TidyTuesday Global Complexion &amp; Undertone Dataset:</b> 6,800+ real commercial foundation formulations mapped across worldwide skin tones (Fitzpatrick I–VI) and verified Warm/Cool/Neutral undertones.",
        "<b>Google Monk Skin Tone (MST) Scale &amp; Fitzpatrick Index:</b> 10-shade inclusive dermatological scale ensuring balanced calibration and eliminating demographic bias.",
        "<b>Extracted Colorimetric Feature Matrix (<code>data/training.csv</code>):</b> Multi-space numerical statistical moments (sRGB, HSV, L*a*b*, ITA&deg;, and ratios) mapped to verified undertone labels."
    ]
    ds_data = [[Paragraph(f"&bull;&nbsp;&nbsp;{d}", bullet_style)] for d in datasets]
    ds_table = Table(ds_data, colWidths=[505])
    ds_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(ds_table)
    story.append(Spacer(1, 8))

    # SECTION 7: EXPECTED OUTCOME
    story.append(Paragraph("7. EXPECTED OUTCOME", h1_style))
    outcomes = [
        ("Objective Undertone Classification", "Automated, high-accuracy determination of Warm, Cool, or Neutral undertone with calibrated class probabilities (>90% accuracy)."),
        ("Dermatological Color Profile", "Real-time extraction of representative skin hex code, CIELAB coordinates (L*, a*, b*), and Individual Typology Angle (ITA&deg;)."),
        ("Personalized Styling Palettes", "Curated clothing swatches, cosmetic guidance (foundation, lip, blush), jewelry metals (Gold vs. Silver), and clashing colors to avoid."),
        ("Interactive Feedback & Privacy", "Live portrait preview with Canvas ROI patch overlays; sub-1.5s latency with zero persistent facial storage in RAM.")
    ]
    out_data = []
    for i in range(0, len(outcomes), 2):
        row = []
        for j in range(2):
            if i + j < len(outcomes):
                o_title, o_desc = outcomes[i+j]
                cell = [
                    Paragraph(f"<b>{o_title}</b>", ParagraphStyle('OTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.2, leading=10, textColor=colors.HexColor("#15803D"))),
                    Spacer(1, 2),
                    Paragraph(o_desc, ParagraphStyle('ODesc', parent=styles['Normal'], fontName='Helvetica', fontSize=7.6, leading=9.8, textColor=colors.HexColor("#166534")))
                ]
                row.append(cell)
            else:
                row.append([])
        out_data.append(row)

    out_table = Table(out_data, colWidths=[248, 248])
    out_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0FDF4")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#BBF7D0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BBF7D0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(out_table)

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {filename}")

if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Otterlook_Project_Synopsis.pdf")
    build_pdf(out_path)
