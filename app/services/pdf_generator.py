from typing import Dict, Any, List
from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class PDFGeneratorService:
    """Service for generating PDF credit assessment reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=10,
            spaceBefore=15
        )
        
        self.subheading_style = ParagraphStyle(
            'CustomSubheading',
            parent=self.styles['Heading3'],
            fontSize=11,
            textColor=colors.HexColor('#4a5568'),
            spaceAfter=8,
            spaceBefore=10
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=8,
            alignment=TA_LEFT
        )
        
        self.bold_style = ParagraphStyle(
            'CustomBold',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=8,
            alignment=TA_LEFT
        )
        self.bold_style.fontName = 'Helvetica-Bold'
    
    def generate_report(
        self,
        entity_data: Dict[str, Any],
        annual_report_data: Dict[str, Any],
        borrowing_profile_data: Dict[str, Any],
        recommendation_data: Dict[str, Any]
    ) -> bytes:
        """Generate complete PDF report"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Title
        title = Paragraph("Credit Assessment Report", self.title_style)
        story.append(title)
        story.append(Spacer(1, 10))
        
        # Report Date
        date_text = Paragraph(
            f"Generated: {datetime.now().strftime('%d %B %Y at %H:%M')}",
            self.normal_style
        )
        story.append(date_text)
        story.append(Spacer(1, 20))
        
        # Entity Details Section
        story.extend(self._create_entity_section(entity_data))
        
        # Financial Analysis Section
        story.extend(self._create_financial_section(annual_report_data))
        
        # Borrowing Profile Section
        if borrowing_profile_data:
            story.extend(self._create_borrowing_section(borrowing_profile_data))
        
        # Recommendation Section
        story.extend(self._create_recommendation_section(recommendation_data))
        
        # SWOT Analysis Section
        story.extend(self._create_swot_section(recommendation_data.get('swot_analysis', {})))
        
        # Footer disclaimer
        story.append(PageBreak())
        story.extend(self._create_disclaimer())
        
        # Build PDF
        doc.build(story)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def _create_entity_section(self, entity_data: Dict[str, Any]) -> List:
        """Create entity details section"""
        story = []
        
        story.append(Paragraph("Entity Details", self.heading_style))
        
        entity_table_data = [
            ['Field', 'Value'],
            ['Company Name', str(entity_data.get('name', 'N/A'))],
            ['CIN', str(entity_data.get('cin', 'N/A'))],
            ['PAN', str(entity_data.get('pan', 'N/A'))],
            ['Sector', str(entity_data.get('sector', 'N/A'))],
            ['Annual Turnover', f"₹{entity_data.get('turnover', 0):,.2f}"],
            ['Status', str(entity_data.get('status', 'N/A'))],
        ]
        
        table = Table(entity_table_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_financial_section(self, annual_report_data: Dict[str, Any]) -> List:
        """Create financial analysis section"""
        story = []
        
        story.append(Paragraph("Financial Analysis", self.heading_style))
        
        # Key Financial Metrics
        story.append(Paragraph("Key Financial Metrics", self.subheading_style))
        
        financial_table_data = [
            ['Metric', 'Value'],
            ['Fiscal Year', str(annual_report_data.get('year', 'N/A'))],
            ['Revenue', f"₹{annual_report_data.get('revenue', 0):,.2f}"],
            ['EBITDA', f"₹{annual_report_data.get('ebitda', 0):,.2f}"],
            ['Net Profit', f"₹{annual_report_data.get('net_profit', 0):,.2f}"],
            ['Cash Flow from Operations', f"₹{annual_report_data.get('cashflow_from_operations', 0):,.2f}"],
            ['Total Debt', f"₹{annual_report_data.get('total_debt', 0):,.2f}"],
            ['Total Equity', f"₹{annual_report_data.get('total_equity', 0):,.2f}"],
        ]
        
        table = Table(financial_table_data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 15))
        
        # Key Ratios
        story.append(Paragraph("Key Ratios", self.subheading_style))
        
        ratios_data = [
            ['Ratio', 'Value', 'Assessment'],
            ['Debt to Equity', f"{annual_report_data.get('debt_to_equity', 0):.2f}", self._assess_ratio('debt_to_equity', annual_report_data.get('debt_to_equity', 0))],
            ['Interest Coverage', f"{annual_report_data.get('interest_coverage', 0):.2f}x", self._assess_ratio('interest_coverage', annual_report_data.get('interest_coverage', 0))],
            ['Profit Margin', f"{annual_report_data.get('profit_margin', 0):.2f}%", self._assess_ratio('profit_margin', annual_report_data.get('profit_margin', 0))],
        ]
        
        ratios_table = Table(ratios_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        ratios_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ]))
        
        story.append(ratios_table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_borrowing_section(self, borrowing_data: Dict[str, Any]) -> List:
        """Create borrowing profile section"""
        story = []
        
        story.append(Paragraph("Borrowing Profile", self.heading_style))
        
        borrowing_table_data = [
            ['Field', 'Value'],
            ['Loan Amount', f"₹{borrowing_data.get('loan_amount', 0):,.2f}"],
            ['Tenure', f"{borrowing_data.get('tenure_months', 0)} months"],
            ['Interest Rate', f"{borrowing_data.get('interest_rate', 0):.2f}%"],
            ['EMI', f"₹{borrowing_data.get('emi', 0):,.2f}"],
            ['Purpose', str(borrowing_data.get('purpose', 'N/A'))],
            ['Lender', str(borrowing_data.get('lender_name', 'N/A'))],
        ]
        
        table = Table(borrowing_table_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_recommendation_section(self, recommendation_data: Dict[str, Any]) -> List:
        """Create recommendation section"""
        story = []
        
        story.append(Paragraph("Credit Recommendation", self.heading_style))
        
        status = recommendation_data.get('status', 'unknown')
        score = recommendation_data.get('score', 0)
        
        # Status color based on recommendation
        if status == 'approved':
            status_color = colors.HexColor('#38a169')
            status_text = 'APPROVED'
        elif status == 'flagged':
            status_color = colors.HexColor('#d69e2e')
            status_text = 'FLAGGED'
        else:
            status_color = colors.HexColor('#e53e3e')
            status_text = 'REJECTED'
        
        status_style = ParagraphStyle(
            'Status',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=status_color,
            spaceAfter=15,
            alignment=TA_CENTER
        )
        
        status_para = Paragraph(f"{status_text} (Score: {score}/100)", status_style)
        story.append(status_para)
        
        # Reasoning
        story.append(Paragraph("Analysis", self.subheading_style))
        reasoning = recommendation_data.get('reasoning', 'No analysis available')
        reasoning_para = Paragraph(reasoning, self.normal_style)
        story.append(reasoning_para)
        
        # Warnings
        warnings = recommendation_data.get('warnings', [])
        if warnings:
            story.append(Spacer(1, 10))
            story.append(Paragraph("Warnings", self.subheading_style))
            for warning in warnings:
                warning_para = Paragraph(f"• {warning}", self.normal_style)
                story.append(warning_para)
        
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_swot_section(self, swot: Dict[str, List[str]]) -> List:
        """Create SWOT analysis section"""
        story = []
        
        story.append(Paragraph("SWOT Analysis", self.heading_style))
        
        # Create SWOT grid
        swot_data = [
            ['Strengths', 'Weaknesses'],
            [self._format_swot_list(swot.get('strengths', [])), 
             self._format_swot_list(swot.get('weaknesses', []))],
            ['Opportunities', 'Threats'],
            [self._format_swot_list(swot.get('opportunities', [])), 
             self._format_swot_list(swot.get('threats', []))],
        ]
        
        swot_table = Table(swot_data, colWidths=[3*inch, 3*inch])
        swot_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#38a169')),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#3182ce')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('TEXTCOLOR', (0, 2), (-1, 2), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (-1, 1), colors.white),
            ('BACKGROUND', (0, 3), (-1, 3), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        story.append(swot_table)
        
        return story
    
    def _create_disclaimer(self) -> List:
        """Create disclaimer section"""
        story = []
        
        story.append(Paragraph("Disclaimer", self.heading_style))
        
        disclaimer_text = """
        This credit assessment report is generated based on the data provided and extracted from 
        submitted documents. The recommendation is based on automated rule-based analysis and should 
        be used as a guideline only. Final credit decisions should incorporate additional factors 
        including but not limited to market conditions, regulatory requirements, and detailed 
        credit evaluation by qualified professionals.
        
        The automated classification and data extraction may not be 100% accurate. Manual 
        verification of all extracted data is recommended before making any credit decisions.
        
        Generated by Credit Underwriting Platform MVP
        """
        
        disclaimer_para = Paragraph(disclaimer_text, self.normal_style)
        story.append(disclaimer_para)
        
        return story
    
    def _format_swot_list(self, items: List[str]) -> str:
        """Format SWOT items as HTML list"""
        if not items:
            return "<br/>- No items"
        
        html = "<br/>"
        for item in items:
            html += f"• {item}<br/>"
        return html
    
    def _assess_ratio(self, ratio_name: str, value: float) -> str:
        """Assess if a ratio is good, bad, or borderline"""
        if ratio_name == 'debt_to_equity':
            if value < 2.0:
                return "Good"
            elif value < 2.5:
                return "Borderline"
            else:
                return "High Risk"
        elif ratio_name == 'interest_coverage':
            if value >= 2.0:
                return "Good"
            elif value >= 1.5:
                return "Borderline"
            else:
                return "Low"
        elif ratio_name == 'profit_margin':
            if value >= 5.0:
                return "Good"
            elif value >= 2.0:
                return "Borderline"
            else:
                return "Low"
        return "N/A"


# Singleton instance
pdf_generator = PDFGeneratorService()
