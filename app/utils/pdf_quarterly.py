# pdf_quarterly.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from flask import send_file
from datetime import datetime

class QuarterlyPDFGenerator:
    def __init__(self, appraisal):
        self.appraisal = appraisal
        self.buffer = BytesIO()
        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        self.styles = getSampleStyleSheet()
        self.setup_styles()
        
    def setup_styles(self):
        # Custom styles
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=30,
            textColor=colors.HexColor('#008751')
        ))
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=12,
            spaceBefore=12,
            textColor=colors.HexColor('#008751')
        ))
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=6
        ))
        
    def generate(self):
        story = []
        
        # Title
        title = Paragraph("EDO STATE GOVERNMENT", self.styles['CustomTitle'])
        story.append(title)
        title2 = Paragraph("CIVIL SERVICE COMMISSION", self.styles['CustomTitle'])
        story.append(title2)
        title3 = Paragraph("QUARTERLY PERFORMANCE APPRAISAL REPORT", self.styles['CustomTitle'])
        story.append(title3)
        story.append(Spacer(1, 20))
        
        # Appraisal details
        officer_name = self.appraisal.user.full_name if hasattr(self.appraisal.user, 'full_name') and self.appraisal.user.full_name else self.appraisal.user.username
            
        details_data = [
            ["Officer Name:", officer_name],
            ["Appraisal Year:", str(self.appraisal.appraisal_year)],
            ["Date:", datetime.now().strftime("%d %B %Y")],
            ["Status:", self.appraisal.status]
        ]
        
        details_table = Table(details_data, colWidths=[150, 350])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#008751')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 20))
        
        # Section A Scores
        story.append(Paragraph("SECTION A: AUTOMATED ASSESSMENTS", self.styles['CustomHeading']))
        story.append(Spacer(1, 10))
        
        section_a_total = (self.appraisal.training_attendance_score or 0) + \
                         (self.appraisal.clock_in_score or 0) + \
                         (self.appraisal.peer_review_score or 0)
        
        section_a_data = [
            ["Criteria", "Score", "Maximum"],
            ["Training Attendance Score", str(self.appraisal.training_attendance_score or 0), "10"],
            ["Clock-in Report Score", str(self.appraisal.clock_in_score or 0), "5"],
            ["360 Review Score", str(self.appraisal.peer_review_score or 0), "5"],
            ["", "", ""],
            ["TOTAL", str(section_a_total), "20"]
        ]
        
        section_a_table = Table(section_a_data, colWidths=[300, 80, 80])
        section_a_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#008751')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 0), (2, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f5e9')),
        ]))
        story.append(section_a_table)
        story.append(Spacer(1, 20))
        
        # Section B Scores (RO Assessment)
        story.append(Paragraph("SECTION B: REPORTING OFFICER'S ASSESSMENT", self.styles['CustomHeading']))
        story.append(Spacer(1, 10))
        
        # Calculate section B total from ratings (each rating 1-5, max 40)
        ratings = [
            self.appraisal.diligently_executed or 3,
            self.appraisal.delivered_timelines or 3,
            self.appraisal.punctuality_effectiveness or 3,
            self.appraisal.decency_presentability or 3,
            self.appraisal.productivity or 3,
            self.appraisal.communication_skills or 3,
            self.appraisal.team_collaboration or 3,
            self.appraisal.independent_work or 3,
            self.appraisal.openness_to_learning or 3,
            self.appraisal.proactivity_initiative or 3
        ]
        section_b_total = sum([r - 1 for r in ratings])  # Convert 1-5 to 0-4 scale, max 40
        
        section_b_data = [
            ["Criteria", "Rating (1-5)"],
            ["Diligently executed all tasks", str(self.appraisal.diligently_executed or 3)],
            ["Delivered tasks within timelines", str(self.appraisal.delivered_timelines or 3)],
            ["Punctuality and effectiveness", str(self.appraisal.punctuality_effectiveness or 3)],
            ["Decency and presentability", str(self.appraisal.decency_presentability or 3)],
            ["Productivity", str(self.appraisal.productivity or 3)],
            ["Communication skills", str(self.appraisal.communication_skills or 3)],
            ["Team collaboration", str(self.appraisal.team_collaboration or 3)],
            ["Independent work", str(self.appraisal.independent_work or 3)],
            ["Openness to learning", str(self.appraisal.openness_to_learning or 3)],
            ["Proactivity and initiative", str(self.appraisal.proactivity_initiative or 3)],
            ["", ""],
            ["TOTAL", f"{section_b_total}/40"]
        ]
        
        section_b_table = Table(section_b_data, colWidths=[350, 150])
        section_b_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#008751')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f5e9')),
        ]))
        story.append(section_b_table)
        story.append(Spacer(1, 20))
        
        # Total Score
        total_score = section_a_total + section_b_total
        
        # Determine rating
        if total_score >= 70:
            rating = 'Outstanding'
        elif total_score >= 60:
            rating = 'Very Good'
        elif total_score >= 50:
            rating = 'Good'
        elif total_score >= 40:
            rating = 'Satisfactory'
        elif total_score >= 30:
            rating = 'Fair'
        else:
            rating = 'Poor'
        
        score_data = [
            ["Section A Total", f"{section_a_total}/20"],
            ["Section B Total", f"{section_b_total}/40"],
            ["", ""],
            ["GRAND TOTAL", f"{total_score}/80"],
            ["RATING", rating]
        ]
        
        score_table = Table(score_data, colWidths=[200, 200])
        score_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BACKGROUND', (0, 0), (-1, -3), colors.HexColor('#f5f5f5')),
            ('BACKGROUND', (0, -2), (-1, -1), colors.HexColor('#e8f5e9')),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#008751')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 20))
        
        # Comments (only use attributes that exist)
        if hasattr(self.appraisal, 'reporting_officer_comments') and self.appraisal.reporting_officer_comments:
            story.append(Paragraph("Reporting Officer's Comments:", self.styles['CustomHeading']))
            story.append(Paragraph(self.appraisal.reporting_officer_comments, self.styles['CustomNormal']))
            story.append(Spacer(1, 10))
        
        if hasattr(self.appraisal, 'ps_comments') and self.appraisal.ps_comments:
            story.append(Paragraph("Permanent Secretary's Comments:", self.styles['CustomHeading']))
            story.append(Paragraph(self.appraisal.ps_comments, self.styles['CustomNormal']))
            story.append(Spacer(1, 10))
        
        # Officer's agreement status
        if hasattr(self.appraisal, 'officer_agrees') and self.appraisal.officer_agrees is not None:
            if self.appraisal.officer_agrees:
                story.append(Paragraph("Officer's Response:", self.styles['CustomHeading']))
                story.append(Paragraph("The officer has ACCEPTED the assessment.", self.styles['CustomNormal']))
            else:
                story.append(Paragraph("Officer's Response:", self.styles['CustomHeading']))
                story.append(Paragraph("The officer has DISAGREED with the assessment.", self.styles['CustomNormal']))
            story.append(Spacer(1, 10))
        
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#008751')))
        story.append(Spacer(1, 10))
        
        # Footer
        footer_text = Paragraph("This is a computer-generated document. No signature is required.", 
                               ParagraphStyle(name='Footer', fontSize=8, alignment=TA_CENTER))
        story.append(footer_text)
        
        # Build PDF
        self.doc.build(story)
        self.buffer.seek(0)
        return self.buffer
    
    def download(self, filename="appraisal_report.pdf"):
        buffer = self.generate()
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )