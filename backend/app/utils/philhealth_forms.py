"""
PhilHealth form generation utilities.
Generates official PhilHealth forms (CF2, etc.) for insurance claims.
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
from typing import Dict, Any, Optional


class PhilHealthCF2Generator:
    """
    Generate PhilHealth Claim Form 2 (CF2) - Member's Claim Form.
    
    This is the official form used for PhilHealth reimbursement claims.
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='CenterBold',
            parent=self.styles['Heading1'],
            alignment=TA_CENTER,
            fontSize=14,
            textColor=colors.HexColor('#1a5490'),
        ))
        
        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['Normal'],
            fontSize=8,
        ))
        
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#333333'),
        ))
    
    def generate(
        self,
        patient_data: Dict[str, Any],
        invoice_data: Dict[str, Any],
        hospital_data: Dict[str, Any],
    ) -> BytesIO:
        """
        Generate PhilHealth CF2 form.
        
        Args:
            patient_data: Patient information
            invoice_data: Invoice/billing information
            hospital_data: Hospital/clinic information
            
        Returns:
            BytesIO: PDF file buffer
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
        )
        
        elements = []
        
        # Header
        elements.extend(self._create_header())
        elements.append(Spacer(1, 0.2*inch))
        
        # Part I: Member Information
        elements.append(Paragraph("PART I: MEMBER INFORMATION", self.styles['CenterBold']))
        elements.append(Spacer(1, 0.1*inch))
        elements.extend(self._create_member_info(patient_data))
        elements.append(Spacer(1, 0.2*inch))
        
        # Part II: Confinement Information
        elements.append(Paragraph("PART II: CONFINEMENT INFORMATION", self.styles['CenterBold']))
        elements.append(Spacer(1, 0.1*inch))
        elements.extend(self._create_confinement_info(invoice_data))
        elements.append(Spacer(1, 0.2*inch))
        
        # Part III: Hospital/Clinic Information
        elements.append(Paragraph("PART III: HEALTH CARE INSTITUTION", self.styles['CenterBold']))
        elements.append(Spacer(1, 0.1*inch))
        elements.extend(self._create_hospital_info(hospital_data))
        elements.append(Spacer(1, 0.2*inch))
        
        # Part IV: Charges
        elements.append(Paragraph("PART IV: CHARGES", self.styles['CenterBold']))
        elements.append(Spacer(1, 0.1*inch))
        elements.extend(self._create_charges_table(invoice_data))
        elements.append(Spacer(1, 0.2*inch))
        
        # Signatures
        elements.extend(self._create_signature_section())
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def _create_header(self):
        """Create form header."""
        elements = []
        
        # PhilHealth logo and title
        header_text = Paragraph(
            "<b>PHILIPPINE HEALTH INSURANCE CORPORATION</b><br/>"
            "<font size=10>CLAIM FORM 2 (CF2)</font><br/>"
            "<font size=8>Member's Claim Form</font>",
            self.styles['CenterBold']
        )
        elements.append(header_text)
        
        return elements
    
    def _create_member_info(self, patient_data: Dict[str, Any]):
        """Create member information section."""
        elements = []
        
        data = [
            ['PhilHealth Number:', patient_data.get('philhealth_number', 'N/A')],
            ['Member Type:', patient_data.get('philhealth_member_type', 'N/A')],
            ['Last Name:', patient_data.get('last_name', '')],
            ['First Name:', patient_data.get('first_name', '')],
            ['Middle Name:', patient_data.get('middle_name', '')],
            ['Date of Birth:', patient_data.get('date_of_birth', '')],
            ['Gender:', patient_data.get('gender', '')],
            ['Address:', patient_data.get('address', '')],
            ['Contact Number:', patient_data.get('phone_number', '')],
        ]
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        elements.append(table)
        return elements
    
    def _create_confinement_info(self, invoice_data: Dict[str, Any]):
        """Create confinement information section."""
        elements = []
        
        data = [
            ['Admission Date:', invoice_data.get('admission_date', 'N/A')],
            ['Discharge Date:', invoice_data.get('discharge_date', 'N/A')],
            ['Diagnosis:', invoice_data.get('diagnosis', 'N/A')],
            ['Type of Accommodation:', invoice_data.get('room_type', 'N/A')],
        ]
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        return elements
    
    def _create_hospital_info(self, hospital_data: Dict[str, Any]):
        """Create hospital information section."""
        elements = []
        
        data = [
            ['Hospital/Clinic Name:', hospital_data.get('name', 'N/A')],
            ['PhilHealth Accreditation No.:', hospital_data.get('philhealth_accreditation', 'N/A')],
            ['Address:', hospital_data.get('address', 'N/A')],
            ['Contact Number:', hospital_data.get('phone', 'N/A')],
        ]
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        return elements
    
    def _create_charges_table(self, invoice_data: Dict[str, Any]):
        """Create charges breakdown table."""
        elements = []
        
        # Header
        data = [
            ['Description', 'Amount (₱)'],
        ]
        
        # Add line items
        items = invoice_data.get('items', [])
        total = 0
        for item in items:
            amount = item.get('amount', 0)
            data.append([
                item.get('description', ''),
                f"₱{amount:,.2f}"
            ])
            total += amount
        
        # Totals
        philhealth_coverage = invoice_data.get('philhealth_coverage', 0)
        patient_balance = total - philhealth_coverage
        
        data.extend([
            ['', ''],
            ['TOTAL CHARGES:', f"₱{total:,.2f}"],
            ['PhilHealth Coverage:', f"₱{philhealth_coverage:,.2f}"],
            ['PATIENT BALANCE:', f"₱{patient_balance:,.2f}"],
        ])
        
        table = Table(data, colWidths=[4*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('LINEABOVE', (0, -3), (-1, -3), 1, colors.black),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
            ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        return elements
    
    def _create_signature_section(self):
        """Create signature section."""
        elements = []
        
        elements.append(Spacer(1, 0.3*inch))
        
        sig_data = [
            ['Member/Patient Signature:', '', 'Date:'],
            ['', '', ''],
            ['', '', ''],
            ['Attending Physician:', '', 'PRC License No.:'],
            ['', '', ''],
        ]
        
        table = Table(sig_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('LINEBELOW', (1, 1), (1, 1), 1, colors.black),
            ('LINEBELOW', (2, 1), (2, 1), 1, colors.black),
            ('LINEBELOW', (1, 4), (1, 4), 1, colors.black),
            ('LINEBELOW', (2, 4), (2, 4), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        
        elements.append(table)
        
        return elements

