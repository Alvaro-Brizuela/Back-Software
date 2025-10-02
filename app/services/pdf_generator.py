from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.frames import Frame
from datetime import datetime
from typing import List
from collections import defaultdict
import os


from app.schemas.pdf_epp import PDFEppRequest
from app.schemas.pdf_odi import PDFOdiRequest


class PDFEppGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.create_custom_styles()

    def create_custom_styles(self):
        # Estilo para el título principal
        self.title_style = ParagraphStyle(
            'TitleStyle',
            parent=self.styles['Normal'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=18,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para el encabezado (más pequeño)
        self.header_style = ParagraphStyle(
            'HeaderStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=3
        )
        
        # Estilo para el texto legal
        self.legal_style = ParagraphStyle(
            'LegalStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        )
        
        # Estilo para certificación
        self.cert_style = ParagraphStyle(
            'CertStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceBefore=12,
            spaceAfter=20
        )
        
        # Estilo para firmas
        self.signature_style = ParagraphStyle(
            'SignatureStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=6
        )

    def generate_pdf(self, data: PDFEppRequest) -> str:
        # Crear directorio para PDFs si no existe
        pdf_dir = "generated_pdfs"
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Nombre del archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"epp_delivery_{data.rut}_{timestamp}.pdf"
        filepath = os.path.join(pdf_dir, filename)
        
        # Crear el documento
        doc = SimpleDocTemplate(filepath, pagesize=A4, 
                              rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=72)
        
        def create_footer(canvas, doc, data):
            # Footer con firmas en la parte inferior
            canvas.saveState()
            
            # Posición del footer (desde abajo)
            footer_y = 120
            
            # Líneas para firmas
            canvas.line(100, footer_y + 20, 280, footer_y + 20)  # Línea empresa
            canvas.line(320, footer_y + 20, 500, footer_y + 20)  # Línea trabajador
            
            # Textos de firma - empresa
            canvas.setFont("Helvetica-Bold", 10)
            canvas.drawCentredString(190, footer_y, data.empresa_nombre)
            canvas.drawCentredString(190, footer_y - 12, f"RUT: {data.empresa_rut}")
            canvas.drawCentredString(190, footer_y - 24, "EMPLEADOR")
            
            # Textos de firma - trabajador  
            canvas.drawCentredString(410, footer_y, data.nombre)
            canvas.drawCentredString(410, footer_y - 12, f"RUT: {data.rut}")
            canvas.drawCentredString(410, footer_y - 24, "TRABAJADOR")
            
            canvas.restoreState()
        
        story = []
        
        # Título principal
        story.append(Paragraph("REGISTRO DE ENTREGA", self.title_style))
        story.append(Paragraph("ELEMENTOS DE PROTECCIÓN PERSONAL", self.title_style))
        
        # Encabezado
        story.extend(self._create_header(data))
        
        # Texto legal
        story.extend(self._create_legal_text())
        
        # Tabla de elementos
        story.extend(self._create_table(data.elementos))
        
        # Certificación
        story.extend(self._create_certification())
        
        # Construir el PDF con footer personalizado
        doc.build(story, onFirstPage=lambda c, d: create_footer(c, d, data), 
                 onLaterPages=lambda c, d: create_footer(c, d, data))
        
        return filepath

    def _create_header(self, data: PDFEppRequest) -> List:
        elements = []
        fecha_actual = datetime.now().strftime("%d de %B de %Y")
        
        elements.append(Paragraph(f"<b>NOMBRE:</b> {data.nombre}", self.header_style))
        elements.append(Paragraph(f"<b>RUT:</b> {data.rut}", self.header_style))
        elements.append(Paragraph(f"<b>CARGO:</b> {data.cargo}", self.header_style))
        elements.append(Paragraph(f"<b>FECHA:</b> {fecha_actual}", self.header_style))
        elements.append(Spacer(1, 15))
        
        return elements

    def _create_legal_text(self) -> List:
        legal_text = """Con el propósito de promover y mantener el nivel de seguridad y cumplimiento en lo establecido en la Ley Nº 16.744.- y sus Decretos Reglamentarios en lo relacionado al suministro de equipos de protección personal, por intermedio de la presente, se deja constancia de la provisión u entrega de los siguientes elementos de protección personal:"""
        
        return [
            Paragraph(legal_text, self.legal_style),
            Spacer(1, 12)
        ]

    def _create_table(self, elementos: List) -> List:
        # Headers de la tabla
        data = [['N°', 'ELEMENTO DE PROTECCIÓN PERSONAL', 'CANTIDAD', 'FECHA DE ENTREGA']]

        # Agregar elementos
        for i, elemento in enumerate(elementos, 1):
            cantidad = str(elemento.cantidad) if elemento.cantidad is not None else ''
            fecha = elemento.fecha_entrega.strftime('%d/%m/%Y') if elemento.fecha_entrega is not None else ''
            data.append([str(i), elemento.elemento_proteccion, cantidad, fecha])

        # Crear la tabla
        table = Table(data, colWidths=[0.5*inch, 3.5*inch, 1*inch, 1.5*inch])
        
        # Estilo de la tabla
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            
            # Body
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Altura de filas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white]),
        ]))
        
        return [table, Spacer(1, 20)]

    def _create_certification(self) -> List:
        cert_text = """Certifico haber recibido los elementos de protección personal, como así también instrucciones para su correcto uso y reconozco la OBLIGACIÓN DE USAR, conservar y cuidar los mismos, e informar del deterioro o extravío, conforme a lo indicado anteriormente."""
        
        return [
            Paragraph(cert_text, self.cert_style),
            Spacer(1, 30)
        ]

class PDFOdiGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.create_custom_styles()

    def create_custom_styles(self):
        # Estilo para el título principal
        self.title_style = ParagraphStyle(
            'TitleStyle',
            parent=self.styles['Normal'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=18,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para el encabezado (más pequeño)
        self.header_style = ParagraphStyle(
            'HeaderStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=3
        )
        
        # Estilo para el texto legal
        self.legal_style = ParagraphStyle(
            'LegalStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        )
        
        # Estilo para Titulo de tabla (tabla tarea)
        self.table_title_style = ParagraphStyle(
            'TableTitleStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_JUSTIFY,
            spaceAfter=6
        )

        # Estilo para celdas de tabla (texto envuelve)
        self.table_cell_style = ParagraphStyle(
            'TableCell',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11,
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=0
        )

        # Estilo para certificación
        self.cert_style = ParagraphStyle(
            'CertStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceBefore=12,
            spaceAfter=20
        )
        
        # Estilo para firmas
        self.signature_style = ParagraphStyle(
            'SignatureStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=6
        )

    def _p(self, text: str) -> Paragraph:
        # Envuelve texto en Paragraph y escapa HTML para evitar errores con '<', '&', etc.
        from xml.sax.saxutils import escape as xml_escape
        return Paragraph(xml_escape(text or ""), self.table_cell_style)

    def generate_pdf(self, data: PDFOdiRequest) -> str:
        # Crear directorio para PDFs si no existe
        pdf_dir = "generated_pdfs"
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Nombre del archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"odi_{data.cargo}_{data.rut}_{timestamp}.pdf"
        filepath = os.path.join(pdf_dir, filename)
        
        # Crear el documento
        doc = SimpleDocTemplate(filepath, pagesize=A4, 
                                rightMargin=72, leftMargin=72, 
                                topMargin=72, bottomMargin=72)
        content_width = doc.width  # ancho disponible dentro de márgenes
        
        def create_footer(canvas, doc, data):
            # Footer con firmas en la parte inferior
            canvas.saveState()
            footer_y = 120
            canvas.line(100, footer_y + 20, 280, footer_y + 20)  # Empresa
            canvas.line(320, footer_y + 20, 500, footer_y + 20)  # Trabajador
            canvas.setFont("Helvetica-Bold", 10)
            canvas.drawCentredString(190, footer_y, data.empresa_nombre)
            canvas.drawCentredString(190, footer_y - 12, f"RUT: {data.empresa_rut}")
            canvas.drawCentredString(190, footer_y - 24, "EMPLEADOR")
            canvas.drawCentredString(410, footer_y, data.nombre)
            canvas.drawCentredString(410, footer_y - 12, f"RUT: {data.rut}")
            canvas.drawCentredString(410, footer_y - 24, "TRABAJADOR")
            canvas.restoreState()
        
        story = []
        story.append(Paragraph("OBLIGACIÓN DE INFORMAR LOS RIESGOS LABORALES", self.title_style))
        story.extend(self._create_header(data))
        story.extend(self._create_legal_text())
        story.extend(self._create_table_by_task(data.elementos, content_width))
        story.extend(self._create_certification())
        
        doc.build(story, onFirstPage=lambda c, d: create_footer(c, d, data), 
                  onLaterPages=lambda c, d: create_footer(c, d, data))
        return filepath

    def _create_header(self, data: PDFOdiRequest) -> List:
        elements = []
        fecha_actual = datetime.now().strftime("%d de %B de %Y")
        elements.append(Paragraph(f"<b>NOMBRE:</b> {data.nombre}", self.header_style))
        elements.append(Paragraph(f"<b>RUT:</b> {data.rut}", self.header_style))
        elements.append(Paragraph(f"<b>CARGO:</b> {data.cargo}", self.header_style))
        elements.append(Paragraph(f"<b>FECHA:</b> {fecha_actual}", self.header_style))
        elements.append(Spacer(1, 15))
        return elements

    def _create_legal_text(self) -> List:
        legal_text = """De acuerdo a lo establecido en el artículo 8 del Decreto N°18, de 23 de abril de 2020, se informa sobre el riesgo que entrañan las actividades asociadas a su trabajo, indicando las instrucciones, métodos de trabajo y medidas preventivas necesarias para evitar los potenciales accidentes del trabajo y/o enfermedades profesionales, las cuales se le solicita leer y cumplir con todo esmero en beneficio de su propia salud."""
        legal_text2 = """Los trabajadores tienen el derecho a desistir realizar un trabajo, si éste pone en peligro su vida, por falta de medidas de seguridad. A su vez los trabajadores se comprometen a informar toda acción o condición subestándar y cumplir todas las instrucciones recibidas para evitar accidentes en el trabajo y disminuir o evitar los impactos al medio ambiente."""
        return [
            Paragraph(legal_text, self.legal_style),
            Paragraph(legal_text2, self.legal_style),
            Spacer(1, 12)
        ]

    def _create_table(self, elementos: List, content_width: float) -> Table:
        # Headers de la tabla
        data = [['RIESGOS', 'CONSECUENCIAS', 'MEDIDAS DE PREVENCIÓN']]
        # Filas con Paragraph para que el texto envuelva
        for elemento in elementos:
            data.append([
                self._p(getattr(elemento, "riesgo", "")),
                self._p(getattr(elemento, "consecuencias", "")),
                self._p(getattr(elemento, "precaucion", "")),
            ])

        w1 = content_width * 0.33
        w2 = content_width * 0.33
        w3 = content_width * 0.34
        table = Table(data, colWidths=[w1, w2, w3], repeatRows=1)

        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),

            # Body
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),

            # Padding para que el texto no pegue al borde
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),

            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white]),

            ('WORDWRAP', (0, 1), (-1, -1), 'CJK'),
        ]))

        return table

    def _create_table_by_task(self, elementos: List, content_width: float):
        from collections import defaultdict
        groups = defaultdict(list)
        for e in elementos:
            groups[e.tarea].append(e)
        
        story = []
        for tarea in sorted(groups.keys()):
            rows = groups[tarea]
            heading = Paragraph(f"TAREA: {self._p(tarea).getPlainText()}", self.table_title_style)
            table = self._create_table(rows, content_width)
            # No usamos KeepTogether para permitir que la tabla se parta entre páginas
            story.extend([heading, Spacer(1, 6), table, Spacer(1, 12)])
        return story

    def _create_certification(self) -> List:
        cert_text = """Declaro que he sido informado y he comprendido acerca de todos los riesgos asociados a mi área de trabajo, cómo también de las medidas preventivas y procedimientos de trabajo seguro que deberé aplicar y respetar en el desempeño de mis funciones."""
        return [
            Paragraph(cert_text, self.cert_style),
            Spacer(1, 30)
        ]
