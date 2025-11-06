"""
PDF Generation utilities for prescriptions, lab results, and invoices.
"""
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from typing import List, Dict, Any


def generate_prescription_pdf(prescription_data: Dict[str, Any]) -> BytesIO:
    """Generate a PDF for a prescription."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#4F46E5'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    story.append(Paragraph("MediFlow Lite", title_style))
    story.append(Paragraph("E-Prescription", styles['Heading2']))
    story.append(Spacer(1, 0.3*inch))
    
    # Prescription Info
    info_data = [
        ['Prescription #:', prescription_data.get('prescription_number', 'N/A')],
        ['Date:', datetime.now().strftime('%B %d, %Y')],
        ['Patient:', prescription_data.get('patient_name', 'N/A')],
        ['Doctor:', prescription_data.get('doctor_name', 'N/A')],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Diagnosis
    if prescription_data.get('diagnosis'):
        story.append(Paragraph("<b>Diagnosis:</b>", styles['Heading3']))
        story.append(Paragraph(prescription_data['diagnosis'], styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    # Medications
    story.append(Paragraph("<b>Medications:</b>", styles['Heading3']))
    story.append(Spacer(1, 0.1*inch))
    
    medications = prescription_data.get('medications', [])
    if medications:
        med_data = [['Medication', 'Dosage', 'Frequency', 'Duration']]
        for med in medications:
            med_data.append([
                med.get('medication_name', ''),
                med.get('dosage', ''),
                med.get('frequency', ''),
                med.get('duration', '')
            ])
        
        med_table = Table(med_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        med_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        story.append(med_table)
    
    # Instructions
    story.append(Spacer(1, 0.3*inch))
    if medications:
        story.append(Paragraph("<b>Instructions:</b>", styles['Heading3']))
        for i, med in enumerate(medications, 1):
            if med.get('instructions'):
                story.append(Paragraph(f"{i}. {med['instructions']}", styles['Normal']))
    
    # Notes
    if prescription_data.get('notes'):
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("<b>Additional Notes:</b>", styles['Heading3']))
        story.append(Paragraph(prescription_data['notes'], styles['Normal']))
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph("This is a computer-generated prescription.", footer_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_lab_result_pdf(lab_result_data: Dict[str, Any]) -> BytesIO:
    """Generate a PDF for a lab result."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#4F46E5'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    story.append(Paragraph("MediFlow Lite", title_style))
    story.append(Paragraph("Laboratory Test Results", styles['Heading2']))
    story.append(Spacer(1, 0.3*inch))
    
    # Lab Result Info
    info_data = [
        ['Result #:', lab_result_data.get('result_number', 'N/A')],
        ['Test Date:', lab_result_data.get('test_date', 'N/A')],
        ['Result Date:', lab_result_data.get('result_date', 'N/A')],
        ['Patient:', lab_result_data.get('patient_name', 'N/A')],
        ['Doctor:', lab_result_data.get('doctor_name', 'N/A')],
        ['Test Name:', lab_result_data.get('test_name', 'N/A')],
        ['Category:', lab_result_data.get('test_category', 'N/A')],
        ['Status:', lab_result_data.get('status', 'N/A').upper()],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Test Values
    story.append(Paragraph("<b>Test Results:</b>", styles['Heading3']))
    story.append(Spacer(1, 0.1*inch))
    
    test_values = lab_result_data.get('test_values', [])
    if test_values:
        test_data = [['Test Parameter', 'Result', 'Reference Range', 'Unit']]
        for val in test_values:
            test_data.append([
                val.get('parameter_name', ''),
                val.get('value', ''),
                val.get('reference_range', ''),
                val.get('unit', '')
            ])
        
        test_table = Table(test_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1*inch])
        test_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        story.append(test_table)
    
    # Notes
    if lab_result_data.get('notes'):
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("<b>Notes:</b>", styles['Heading3']))
        story.append(Paragraph(lab_result_data['notes'], styles['Normal']))
    
    # Doctor Comments
    if lab_result_data.get('doctor_comments'):
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("<b>Doctor's Comments:</b>", styles['Heading3']))
        story.append(Paragraph(lab_result_data['doctor_comments'], styles['Normal']))
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph("This is a computer-generated lab report.", footer_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_invoice_pdf(invoice_data: Dict[str, Any]) -> BytesIO:
    """Generate a PDF for an invoice."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#4F46E5'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    story.append(Paragraph("MediFlow Lite", title_style))
    story.append(Paragraph("INVOICE", styles['Heading2']))
    story.append(Spacer(1, 0.3*inch))
    
    # Invoice Info
    info_data = [
        ['Invoice #:', invoice_data.get('invoice_number', 'N/A')],
        ['Date:', datetime.now().strftime('%B %d, %Y')],
        ['Due Date:', invoice_data.get('due_date', 'N/A')],
        ['Patient:', invoice_data.get('patient_name', 'N/A')],
        ['Status:', invoice_data.get('status', 'N/A').upper()],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Invoice Items
    story.append(Paragraph("<b>Items:</b>", styles['Heading3']))
    story.append(Spacer(1, 0.1*inch))
    
    items = invoice_data.get('items', [])
    if items:
        item_data = [['Description', 'Quantity', 'Unit Price', 'Amount']]
        for item in items:
            item_data.append([
                item.get('description', ''),
                str(item.get('quantity', 0)),
                f"${item.get('unit_price', 0):.2f}",
                f"${item.get('amount', 0):.2f}"
            ])
        
        item_table = Table(item_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
        item_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        story.append(item_table)
    
    # Totals
    story.append(Spacer(1, 0.2*inch))
    total_data = [
        ['Subtotal:', f"${invoice_data.get('subtotal', 0):.2f}"],
        ['Tax:', f"${invoice_data.get('tax_amount', 0):.2f}"],
        ['Discount:', f"-${invoice_data.get('discount_amount', 0):.2f}"],
        ['TOTAL:', f"${invoice_data.get('total_amount', 0):.2f}"],
    ]
    
    total_table = Table(total_data, colWidths=[4.5*inch, 1.5*inch])
    total_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -2), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -2), 11),
        ('FONTSIZE', (0, -1), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
    ]))
    story.append(total_table)
    
    # Payment Info
    if invoice_data.get('payment_date'):
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"<b>Paid on:</b> {invoice_data['payment_date']}", styles['Normal']))
        if invoice_data.get('payment_method'):
            story.append(Paragraph(f"<b>Payment Method:</b> {invoice_data['payment_method']}", styles['Normal']))
    
    # Notes
    if invoice_data.get('notes'):
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("<b>Notes:</b>", styles['Heading3']))
        story.append(Paragraph(invoice_data['notes'], styles['Normal']))
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph("Thank you for your business!", footer_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

