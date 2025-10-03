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
from app.schemas.pdf_contrato import PDFContratoRequest
from app.schemas.pdf_termino_contrato import PDFTerminoContratoRequest


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


class PDFContratoGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.create_custom_styles()

    def create_custom_styles(self):
        # Estilo para el título principal
        self.title_style = ParagraphStyle(
            'TitleStyle',
            parent=self.styles['Normal'],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )

        # Estilo para texto del contrato
        self.contrato_style = ParagraphStyle(
            'ContratoStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=14
        )

        # Estilo para firmas
        self.signature_style = ParagraphStyle(
            'SignatureStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=6
        )

    def generate_pdf(self, data: PDFContratoRequest) -> str:
        # Crear directorio para PDFs si no existe
        pdf_dir = "generated_pdfs"
        os.makedirs(pdf_dir, exist_ok=True)

        # Nombre del archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"contrato_{data.rut_trabajador}_{timestamp}.pdf"
        filepath = os.path.join(pdf_dir, filename)

        # Crear el documento
        doc = SimpleDocTemplate(filepath, pagesize=A4,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=120)

        def create_footer_first_page(canvas, doc, data):
            # Footer solo en la última página con firmas
            pass

        def create_footer_last_page(canvas, doc, data):
            # Footer con firmas solo en la última página
            canvas.saveState()
            footer_y = 80

            # Líneas para firmas
            canvas.line(100, footer_y + 20, 280, footer_y + 20)  # Empresa
            canvas.line(320, footer_y + 20, 500, footer_y + 20)  # Trabajador

            # Textos de firma - empresa
            canvas.setFont("Helvetica-Bold", 10)
            canvas.drawCentredString(190, footer_y, data.empresa_nombre)
            canvas.drawCentredString(190, footer_y - 12, f"{data.empresa_rut}")
            canvas.drawCentredString(190, footer_y - 24, "EMPLEADOR")

            # Textos de firma - trabajador
            canvas.drawCentredString(410, footer_y, data.nombre_trabajador)
            canvas.drawCentredString(410, footer_y - 12, f"{data.rut_trabajador}")
            canvas.drawCentredString(410, footer_y - 24, "TRABAJADOR")

            canvas.restoreState()

        story = []

        # Título
        story.append(Paragraph("CONTRATO DE TRABAJO POR OBRA O FAENA", self.title_style))
        story.append(Spacer(1, 12))

        # Fecha formateada
        meses = {
            1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
            5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
            9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
        }
        dias_semana = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
        fecha_obj = data.fecha_contrato
        dia_semana = dias_semana[fecha_obj.weekday()]
        mes_nombre = meses[fecha_obj.month]
        fecha_formateada = f"{dia_semana} {fecha_obj.day} de {mes_nombre} del {fecha_obj.year}"

        # Fecha de nacimiento
        fecha_nac = data.fecha_nacimiento_trabajador
        dia_nac = dias_semana[fecha_nac.weekday()]
        mes_nac = meses[fecha_nac.month]
        fecha_nac_formateada = f"{dia_nac} {fecha_nac.day} DE {mes_nac} DE {fecha_nac.year}"

        # Párrafo introductorio
        intro_text = f"""En {data.ciudad_firma} a {fecha_formateada}, entre la sociedad denominada {data.empresa_nombre} rol único tributario número {data.empresa_rut} Representada por Don {data.representante_legal}, cédula nacional de identidad número {data.rut_representante}, ambos domiciliados en {data.domicilio_representante}, por una parte y en adelante también "El Empleador" o "La Empresa"; y por la otra, don(a) {data.nombre_trabajador} de nacionalidad {data.nacionalidad_trabajador}, nacido el {fecha_nac_formateada}, cédula de identidad número {data.rut_trabajador}, estado civil {data.estado_civil_trabajador}, domiciliado en {data.domicilio_trabajador}, en adelante "El Trabajador", los comparecientes mayores de edad, quienes han convenido en celebrar el siguiente Contrato de Trabajo por Obra o Faena."""

        story.append(Paragraph(intro_text, self.contrato_style))
        story.append(Spacer(1, 20))

        # PRIMERA CLÁUSULA
        clausula1_text = f"""<b>PRIMERO:</b> {data.empresa_nombre}, representada del modo indicado en la comparecencia, contrata a don {data.nombre_trabajador}, quien se compromete y obliga a ejecutar el trabajo de {data.cargo_trabajador}, prestando estos servicios en {data.lugar_trabajo}."""
        story.append(Paragraph(clausula1_text, self.contrato_style))

        alteracion_text = """Con todo, el empleador podrá alterar la naturaleza de los servicios o el sitio o recinto en que ellos deban prestarse, a condición de que se trate de labores similares, que el nuevo sitio o recinto quede dentro del territorio nacional, sin que ello importe un menoscabo para el trabajador."""
        story.append(Paragraph(alteracion_text, self.contrato_style))
        story.append(Spacer(1, 12))

        # SEGUNDA CLÁUSULA
        clausula2_text = f"""<b>SEGUNDO:</b> La Jornada de Trabajo será de {data.jornada} de acuerdo a la siguiente distribución diaria: {data.descripcion_jornada} La jornada de trabajo será interrumpida con un descanso de 60 MINUTOS, destinados a la colación, tiempo que en ningún caso será imputable al tiempo de trabajo. Por circunstancias que afecten a todo el proceso de la empresa o establecimiento o alguna de sus unidades o conjuntos operativos, podrá el empleador alterar la distribución de la jornada de trabajo convenida hasta en sesenta minutos, sea anticipando o postergando la hora de ingreso al trabajo, debiendo dar el aviso correspondiente al trabajador con 30 días de anticipación a lo menos."""
        story.append(Paragraph(clausula2_text, self.contrato_style))
        story.append(Spacer(1, 12))

        # TERCERA CLÁUSULA
        sueldo_palabras = self._numero_a_palabras(data.sueldo)
        clausula3_text = f"""<b>TERCERO:</b> {data.empresa_nombre}, pagará a don(a) {data.nombre_trabajador} por su trabajo, una remuneración mensual de ${data.sueldo:,} ({sueldo_palabras} PESOS)."""
        story.append(Paragraph(clausula3_text, self.contrato_style))
        story.append(Spacer(1, 12))

        # CUARTA CLÁUSULA
        clausula4_text = f"""<b>CUARTO:</b> El Empleador se compromete a otorgar o suministrar al Trabajador los siguientes beneficios: Asignación de colación y movilización según lo establecido por la empresa. Se deja constancia que, para efectos de Gratificación Legal, las partes han acordado aplicar lo dispuesto en el Artículo 50 del Código del Trabajo, esto es, que se pagará el 25% sobre la remuneración base mensual con un tope de 4.75 ingresos mínimos mensuales. Cualquier otra prestación o beneficio, ocasional o periódico, que el Empleador conceda el trabajador, distinto al que le corresponde por este contrato y sus ajustes legales o contractuales, como pudieran ser entre otras, premios por rendimiento, asignaciones para Navidad o Fiestas Patrias, etcétera, se entenderá conferido a título de mera liberalidad, no dará derecho alguno, y el Empleador podrá modificarlo o suspenderlo a su arbitrio."""
        story.append(Paragraph(clausula4_text, self.contrato_style))

        # Salto de página
        story.append(PageBreak())

        # QUINTA CLÁUSULA
        clausula5_text = """<b>QUINTO:</b> El presente contrato tendrá una duración hasta una vez concluidos los trabajos que dieron origen al contrato y podrá ponérsele término cuando concurran para ello causas justificadas que, en conformidad a la Ley, puedan producir su caducidad, quedando permitido dar al trabajador el aviso de Desahucio que establece la Ley."""
        story.append(Paragraph(clausula5_text, self.contrato_style))
        story.append(Spacer(1, 12))

        # SEXTA CLÁUSULA
        clausula6_text = """<b>SEXTO:</b> Son obligaciones esenciales del Trabajador, cuya infracción las partes entienden como causa justificada de terminación del presente contrato, las siguientes: 1) Cumplir íntegramente la jornada de trabajo; 2) Cuidar y mantener en perfecto estado de conservación, las máquinas, útiles y otros bienes de la empresa; 3) Cumplir las instrucciones y ordenes que le impartan sus superiores directos, técnicos y ejecutivos del Empleador; 4) En caso de inasistencia al trabajo por enfermedad, el Trabajador deberá justificarla únicamente, con el correspondiente certificado médico, otorgado por un Facultativo especializado dentro del plazo de 24 horas, desde aquel que dejó de asistir al trabajo; 5) Utilizar los implementos de seguridad que correspondan dada la naturaleza del trabajo que se encuentre desempeñando, dando estricto cumplimiento a las normas de seguridad de aplicación general de la Empresa; 6) Mantener con el resto de los trabajadores, y en general con todo el personal, jefes y ejecutivos de la Empresa, relaciones de convivencia y respeto mutuos, que permita a cada uno el normal desempeño de sus labores: 7) El trabajador queda obligado a cumplir leal y correctamente con todos los deberes que le imponga este instrumento o aquéllos que se deriven de las funciones y cargo, debiendo ejecutar las instrucciones que le confieran sus superiores. Del mismo modo el trabajador se obliga a desempeñar en forma eficaz, las funciones y el cargo para el cual ha sido contratado, empleando para ello la mayor diligencia y dedicación."""
        story.append(Paragraph(clausula6_text, self.contrato_style))
        story.append(Spacer(1, 12))

        # SÉPTIMA CLÁUSULA
        clausula7_text = """<b>SÉPTIMO:</b> El Trabajador se obliga a desarrollar su trabajo con el debido cuidado, evitando comprometer la seguridad y la salud del resto de los trabajadores y el Medio Ambiente. La infracción o el incumplimiento grave de las obligaciones que impone el presente contrato y, cuando proceda, faculta a la empresa para poner término al contrato sin derecho a indemnización alguna."""
        story.append(Paragraph(clausula7_text, self.contrato_style))
        story.append(Spacer(1, 12))

        # OCTAVA CLÁUSULA
        clausula8_text = """<b>OCTAVO:</b> Las partes pueden ponerle término al presente contrato de común acuerdo, y cualquiera de ellas, en la forma, condiciones y por las causales previstas y sancionadas por los artículos 159, 160 y 161 del Código del Trabajo, las que en el futuro se establezcan, y las que a continuación se indican, las que tendrán el carácter de esenciales y determinantes, configurando por sí mismas causales de terminación del contrato: 1) Presentarse al trabajo en estado de ebriedad, ingerir bebidas alcohólicas durante las horas de trabajo o introducirlas al establecimiento, obras, faenas o lugar de trabajo; 2) Ejecutar, durante las horas de trabajo, y en el desempeño de sus funciones, actividades ajenas a su labor, o dedicarse a atender asuntos particulares; 3) Promover o provocar juegos de azar, riñas o alteraciones de cualquier especie con sus compañeros o jefes durante la jornada de trabajo y dentro del recinto de la obra, establecimiento o lugar de trabajo; 4) Fumar dentro de los lugares o recintos en donde exista prohibición expresa para ello, de acuerdo a las normas de seguridad implantadas previamente por la Gerencia; 5) Vender o enajenar elementos de seguridad proporcionados por la Empresa; 6) Ocultar inasistencias que no sean propias."""
        story.append(Paragraph(clausula8_text, self.contrato_style))
        story.append(Spacer(1, 12))

        # NOVENA CLÁUSULA
        clausula9_text = """<b>NOVENO:</b> Las partes convienen que la remuneración pactada y los demás beneficios que el trabajador tenga derecho a percibir en virtud del presente contrato, serán pagados en dinero en efectivo a más tardar dentro de los primeros 5 días del mes siguiente a cada periodo."""
        story.append(Paragraph(clausula9_text, self.contrato_style))
        story.append(Spacer(1, 12))

        # DÉCIMA CLÁUSULA
        fecha_inicio = data.fecha_contrato
        dia_inicio = dias_semana[fecha_inicio.weekday()]
        mes_inicio = meses[fecha_inicio.month]
        fecha_inicio_formateada = f"{dia_inicio} {fecha_inicio.day} de {mes_inicio} del {fecha_inicio.year}"

        clausula10_text = f"""<b>DÉCIMO:</b> Las partes comparecientes dejan expresa constancia que el presente contrato tendrá vigencia a contar del día {fecha_inicio_formateada}, fecha en la que el trabajador comenzó a prestar servicios para la empresa."""
        story.append(Paragraph(clausula10_text, self.contrato_style))

        # Salto de página para cláusulas finales
        story.append(PageBreak())

        # DÉCIMA PRIMERA CLÁUSULA
        clausula11_text = """<b>DÉCIMO PRIMERO:</b> "El Trabajador no podrá divulgar, publicar, hacer comentarios ni, en general, traspasar de cualquier forma, total o parcialmente, por cuenta propia o a través de terceros, durante la vigencia del presente contrato y aún después de expirado el mismo por cualquier causa, informaciones o antecedentes relativos a las materias sobre las cuales se ha obligado a guardar secreto y mantener reserva. Asimismo, el Trabajador se compromete a guardar absoluta reserva y confidencialidad acerca de toda la información, proyectos, ideas, creaciones, invenciones, diseños, procesos de venta, información comercial, derechos de autor, marcas o nombres comerciales, desarrollo de software o presentación de mercaderías y, en general de todo asuntos y negocios que haya tomado conocimiento en virtud del trabajo desarrollado para el Empleador. La obligación de guardar secreto y mantener reserva tiene el carácter de esencial para la formación del consentimiento del presente contrato." """
        story.append(Paragraph(clausula11_text, self.contrato_style))
        story.append(Spacer(1, 12))

        # DÉCIMA SEGUNDA CLÁUSULA
        clausula12_text = f"""<b>DÉCIMO SEGUNDO:</b> Para todos los efectos legales derivados del presente instrumento, las partes fijan su domicilio en la Ciudad de {data.ciudad_firma}, y se someten a la Competencia de los Tribunales Ordinarios del Trabajo."""
        story.append(Paragraph(clausula12_text, self.contrato_style))
        story.append(Spacer(1, 12))

        # DÉCIMA TERCERA CLÁUSULA
        clausula13_text = """<b>DÉCIMO TERCERO:</b> El presente contrato se firma en triplicado de igual fecha y tenor, de tres páginas cada uno, quedando dos en poder del Empleador y uno en poder del Trabajador."""
        story.append(Paragraph(clausula13_text, self.contrato_style))
        story.append(Spacer(1, 30))

        # Agregar cláusulas adicionales si existen
        if data.clausulas and len(data.clausulas) > 0:
            for clausula in data.clausulas:
                clausula_text = f"""<b>CLÁUSULA ADICIONAL:</b> {clausula}"""
                story.append(Paragraph(clausula_text, self.contrato_style))
                story.append(Spacer(1, 12))

        # Espacio antes de las firmas
        story.append(Spacer(1, 80))

        # Agregar las firmas directamente en el story
        from reportlab.platypus import Flowable

        class SignatureBlock(Flowable):
            def __init__(self, empresa_nombre, empresa_rut, trabajador_nombre, trabajador_rut):
                Flowable.__init__(self)
                self.empresa_nombre = empresa_nombre
                self.empresa_rut = empresa_rut
                self.trabajador_nombre = trabajador_nombre
                self.trabajador_rut = trabajador_rut
                self.width = 450
                self.height = 80

            def draw(self):
                canvas = self.canv

                # Líneas para firmas (alineadas igual que EPP)
                canvas.line(28, 60, 208, 60)  # Línea empresa
                canvas.line(248, 60, 428, 60)  # Línea trabajador

                # Textos de firma - empresa
                canvas.setFont("Helvetica-Bold", 10)
                canvas.drawCentredString(118, 45, self.empresa_nombre)
                canvas.drawCentredString(118, 33, self.empresa_rut)
                canvas.drawCentredString(118, 21, "EMPLEADOR")

                # Textos de firma - trabajador
                canvas.drawCentredString(338, 45, self.trabajador_nombre)
                canvas.drawCentredString(338, 33, self.trabajador_rut)
                canvas.drawCentredString(338, 21, "TRABAJADOR")

        signature_block = SignatureBlock(
            data.empresa_nombre,
            data.empresa_rut,
            data.nombre_trabajador,
            data.rut_trabajador
        )
        story.append(signature_block)

        # Construir el PDF
        doc.build(story)

        return filepath

    def _numero_a_palabras(self, numero: int) -> str:
        """Convierte un número a palabras (simplificado)"""
        # Simplificación básica
        if numero < 1000:
            return str(numero).upper()
        elif numero < 1000000:
            miles = numero // 1000
            resto = numero % 1000
            if resto == 0:
                return f"{miles} MIL"
            return f"{miles} MIL {resto}"
        else:
            millones = numero // 1000000
            resto = numero % 1000000
            if resto == 0:
                return f"{millones} MILLONES"
            return f"{millones} MILLONES {resto}"

    def _numero_a_romano(self, numero: int) -> str:
        """Convierte número a romano"""
        valores = [
            (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'),
            (5, 'V'), (4, 'IV'), (1, 'I')
        ]
        resultado = ''
        for valor, romano in valores:
            while numero >= valor:
                resultado += romano
                numero -= valor
        return f"DÉCIMO {resultado}" if resultado else "DÉCIMO"


class PDFTerminoContratoGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.create_custom_styles()

    def create_custom_styles(self):
        # Estilo para el título
        self.title_style = ParagraphStyle(
            'TitleStyle',
            parent=self.styles['Normal'],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )

        # Estilo para el nombre de empresa
        self.empresa_style = ParagraphStyle(
            'EmpresaStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=18,
            fontName='Helvetica-Bold'
        )

        # Estilo para fecha y lugar
        self.fecha_style = ParagraphStyle(
            'FechaStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=12
        )

        # Estilo normal
        self.normal_style = ParagraphStyle(
            'NormalStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=6
        )

        # Estilo justificado
        self.justify_style = ParagraphStyle(
            'JustifyStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=6
        )

    def _format_date(self, date_obj):
        """Formatea la fecha en español"""
        days = ['LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO', 'DOMINGO']
        months = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO',
                  'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']

        day_name = days[date_obj.weekday()]
        month_name = months[date_obj.month - 1]

        return f"{day_name} {date_obj.day} de {month_name} del {date_obj.year}"

    def generate_pdf(self, data):
        """Genera el PDF de carta de término de contrato"""
        # Crear directorio para PDFs si no existe
        pdf_dir = "generated_pdfs"
        os.makedirs(pdf_dir, exist_ok=True)

        # Nombre del archivo PDF
        filename = f"termino_contrato_{data.rut_trabajador.replace('-', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(pdf_dir, filename)

        # Crear el documento PDF
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Contenido del documento
        story = []

        # Título
        story.append(Paragraph("CARTA DE AVISO", self.title_style))
        story.append(Spacer(1, 12))

        # Nombre de la empresa
        story.append(Paragraph(data.empresa_nombre.upper(), self.empresa_style))
        story.append(Spacer(1, 12))

        # Fecha y lugar
        fecha_formateada = self._format_date(data.fecha_carta)
        story.append(Paragraph(f"En {data.ciudad.upper()} a {fecha_formateada}", self.fecha_style))
        story.append(Spacer(1, 12))

        # Datos del trabajador
        story.append(Paragraph(f"Señor\t{data.nombre_trabajador.upper()}", self.normal_style))
        story.append(Paragraph(f"Rut\t{data.rut_trabajador}", self.normal_style))
        story.append(Paragraph(f"Dirección\t{data.direccion_trabajador.upper()}", self.normal_style))
        story.append(Paragraph(f"Comuna\t{data.comuna_trabajador.upper()}", self.normal_style))
        story.append(Spacer(1, 12))

        # PRESENTE
        story.append(Paragraph("<b>PRESENTE</b>", self.normal_style))
        story.append(Spacer(1, 6))

        # Saludo
        story.append(Paragraph("De nuestra consideración:", self.normal_style))
        story.append(Spacer(1, 6))

        # Cuerpo principal
        fecha_termino_formateada = self._format_date(data.fecha_termino)
        texto_principal = f"Informamos a Usted que la Administración de la Empresa ha decidido poner termino a su contrato de trabajo a contar del día {fecha_termino_formateada}, en virtud a lo establecido en el {data.articulo_causal} del Código del Trabajo, esto es, {data.descripcion_causal.upper()}, causal señalada en el Código del Trabajo, artículo 159, inciso 5to."
        story.append(Paragraph(texto_principal, self.justify_style))
        story.append(Spacer(1, 12))

        # Fundamentación
        story.append(Paragraph(data.fundamentacion, self.justify_style))
        story.append(Spacer(1, 12))

        # Imposiciones
        texto_imposiciones = "Asi Mismo informamos a usted que sus imposiciones se encuentran canceladas oportuna y debidamente en las Instituciones Previsionales correspondientes. Además,  adjuntamos a la siguiente carta,  Certificado de la empresa Previred que da cuenta que las cotizaciones previsionales, de los meses trabajados, se encuentran pagadas."
        story.append(Paragraph(texto_imposiciones, self.justify_style))
        story.append(Spacer(1, 12))

        # Información de pago
        texto_pago = f"Su finiquito sera cancelado en diez dias habiles a partir de la fecha del finiquito en {data.lugar_pago_finiquito},  Llamar al {data.telefono_notaria} para confirmar Pago."
        story.append(Paragraph(texto_pago, self.justify_style))
        story.append(Spacer(1, 12))

        # Despedida
        story.append(Paragraph("Atentamente,", self.normal_style))
        story.append(Spacer(1, 36))

        # Firmas
        from reportlab.platypus.flowables import Flowable

        class SignatureBlock(Flowable):
            def __init__(self, empresa_nombre, empresa_rut, trabajador_nombre, trabajador_rut):
                Flowable.__init__(self)
                self.empresa_nombre = empresa_nombre
                self.empresa_rut = empresa_rut
                self.trabajador_nombre = trabajador_nombre
                self.trabajador_rut = trabajador_rut
                self.width = 450
                self.height = 100

            def draw(self):
                canvas = self.canv

                # Líneas para firmas
                canvas.line(28, 60, 208, 60)  # Línea empresa
                canvas.line(248, 60, 428, 60)  # Línea trabajador

                # Textos de firma - empresa
                canvas.setFont("Helvetica-Bold", 9)
                canvas.drawCentredString(118, 45, self.empresa_nombre.upper())
                canvas.setFont("Helvetica", 9)
                canvas.drawCentredString(118, 33, self.empresa_rut)
                canvas.drawCentredString(118, 21, "EMPLEADOR")

                # Textos de firma - trabajador
                canvas.setFont("Helvetica-Bold", 9)
                canvas.drawCentredString(338, 45, self.trabajador_nombre.upper())
                canvas.setFont("Helvetica", 9)
                canvas.drawCentredString(338, 33, self.trabajador_rut)
                canvas.drawCentredString(338, 21, "TRABAJADOR")
                canvas.setFont("Helvetica", 8)
                canvas.drawCentredString(338, 9, "Recibí Copia de la presente carta")

        signature_block = SignatureBlock(
            data.empresa_nombre,
            data.empresa_rut,
            data.nombre_trabajador,
            data.rut_trabajador
        )
        story.append(signature_block)

        # Construir el PDF
        doc.build(story)

        return filepath
