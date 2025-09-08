from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.frames import Frame
from datetime import datetime
from typing import List
import os

from app.schemas.pdf_epp import PDFEppRequest, EppDeliveryItem


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

    def _create_table(self, elementos: List[EppDeliveryItem]) -> List:
        # Headers de la tabla
        data = [['N°', 'ELEMENTO DE PROTECCIÓN PERSONAL', 'CANTIDAD', 'FECHA DE ENTREGA']]
        
        # Agregar elementos
        for i, elemento in enumerate(elementos, 1):
            data.append([str(i), elemento.elemento_proteccion, '', ''])
        
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

