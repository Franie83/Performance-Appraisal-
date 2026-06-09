from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
from flask import send_file
import os

class ReportPDFGenerator:
    def __init__(self, report, staff_user, reporting_officer, countersigning_officer, assessment=None):
        self.report = report
        self.staff = staff_user
        self.reporting_officer = reporting_officer
        self.countersigning_officer = countersigning_officer
        self.assessment = assessment
        self.buffer = BytesIO()
    
    def _add_section_header(self, story, title):
        """Add a section header with green background and white, bold text."""
        p = Paragraph(title, self.section_title_style)
        header_table = Table([[p]], colWidths=[7.5*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#008751')),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#FFFFFF')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 14),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.1*inch))
    
    def generate(self):
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=0.6*inch,
            leftMargin=0.6*inch,
            topMargin=0.6*inch,
            bottomMargin=0.6*inch,
        )
        
        styles = getSampleStyleSheet()
        
        # Edo State Government Colors
        edo_green = colors.HexColor('#008751')
        edo_white = colors.HexColor('#FFFFFF')
        edo_dark_green = colors.HexColor('#00633E')
        edo_light_green = colors.HexColor('#E8F5E9')
        edo_gold = colors.HexColor('#D4AF37')
        
        # Section title style – white, bold, centered
        self.section_title_style = ParagraphStyle(
            name='SectionTitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=edo_white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Custom Styles
        styles.add(ParagraphStyle(
            name='HeaderStyle',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=edo_white,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=10,
            textColor=edo_green,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='SubTitleStyle',
            parent=styles['Heading2'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=15,
            textColor=edo_dark_green,
            fontName='Helvetica'
        ))
        
        styles.add(ParagraphStyle(
            name='SubSectionStyle',
            parent=styles['Heading3'],
            fontSize=11,
            textColor=edo_dark_green,
            spaceAfter=6,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='LabelStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#555555'),
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='ValueStyle',
            parent=styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            fontName='Helvetica'
        ))
        
        styles.add(ParagraphStyle(
            name='GreenBoxStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=edo_dark_green,
            fontName='Helvetica',
            backColor=edo_light_green,
            borderPadding=5
        ))
        
        # Footer style – white bold text for dark green background
        styles.add(ParagraphStyle(
            name='FooterStyle',
            parent=styles['Normal'],
            fontSize=8,
            textColor=edo_white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        story = []
        
        # ============ HEADER (green background, white bold text) ============
        header_data = [
            [Paragraph("EDO STATE GOVERNMENT", styles['HeaderStyle'])],   # fixed typo
            [Paragraph("MINISTRY OF ESTABLISHMENT AND TRAINING", styles['HeaderStyle'])],
            [Paragraph("PERFORMANCE MANAGEMENT DIRECTORATE", styles['HeaderStyle'])],
        ]
        
        header_table = Table(header_data, colWidths=[7.5*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), edo_green),
            ('TEXTCOLOR', (0,0), (-1,-1), edo_white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.1*inch))
        
        # Title
        story.append(Paragraph("ANNUAL PERFORMANCE EVALUATION REPORT", styles['TitleStyle']))
        story.append(Paragraph("Gen 79A Form - Civil Service Commission", styles['SubTitleStyle']))
        story.append(Spacer(1, 0.1*inch))
        
        # Decorative line
        story.append(Table([['']], colWidths=[7.5*inch], rowHeights=2))
        story[-1].setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), edo_green)]))
        story.append(Spacer(1, 0.2*inch))
        
        # ============ SECTION 1 ============
        self._add_section_header(story, "SECTION 1: OFFICER'S INFORMATION")
        
        staff_data = [
            [Paragraph("<b>Full Name:</b>", styles['LabelStyle']), Paragraph(self.staff.full_name or self.staff.username, styles['ValueStyle'])],
            [Paragraph("<b>Staff Number:</b>", styles['LabelStyle']), Paragraph(self.staff.staff_no or "N/A", styles['ValueStyle'])],
            [Paragraph("<b>Ministry/Department:</b>", styles['LabelStyle']), Paragraph(f"{self.staff.ministry or 'N/A'} / {self.staff.department or 'N/A'}", styles['ValueStyle'])],
            [Paragraph("<b>Role/Grade Level:</b>", styles['LabelStyle']), Paragraph(f"{self.staff.role} / {self.staff.salary_grade or 'N/A'}", styles['ValueStyle'])],
            [Paragraph("<b>Email:</b>", styles['LabelStyle']), Paragraph(self.staff.email, styles['ValueStyle'])],
        ]
        
        staff_table = Table(staff_data, colWidths=[2.2*inch, 5*inch])
        staff_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), edo_light_green),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ]))
        story.append(staff_table)
        story.append(Spacer(1, 0.15*inch))
        
        # ============ SECTION 2 ============
        self._add_section_header(story, "SECTION 2: REPORT DETAILS")
        
        period_text = f"{self.report.period_from.strftime('%d %B %Y') if self.report.period_from else 'N/A'} to {self.report.period_to.strftime('%d %B %Y') if self.report.period_to else 'N/A'}"
        
        report_data = [
            [Paragraph("<b>Report Year:</b>", styles['LabelStyle']), Paragraph(str(self.report.report_year), styles['ValueStyle'])],
            [Paragraph("<b>Review Period:</b>", styles['LabelStyle']), Paragraph(period_text, styles['ValueStyle'])],
            [Paragraph("<b>Verification Code:</b>", styles['LabelStyle']), Paragraph(self.report.verification_code or "N/A", styles['ValueStyle'])],
            [Paragraph("<b>Date Created:</b>", styles['LabelStyle']), Paragraph(self.report.created_at.strftime('%d %B %Y %H:%M') if self.report.created_at else "N/A", styles['ValueStyle'])],
            [Paragraph("<b>Date Submitted:</b>", styles['LabelStyle']), Paragraph(self.report.submitted_at.strftime('%d %B %Y %H:%M') if self.report.submitted_at else "Not submitted", styles['ValueStyle'])],
            [Paragraph("<b>Final Status:</b>", styles['LabelStyle']), Paragraph(self.report.final_status, styles['ValueStyle'])],
        ]
        
        report_table = Table(report_data, colWidths=[2.2*inch, 5*inch])
        report_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), edo_light_green),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ]))
        story.append(report_table)
        story.append(Spacer(1, 0.15*inch))
        
        # ============ SECTION 3 ============
        self._add_section_header(story, "SECTION 3: OFFICER'S TARGET SETTING")
        
        story.append(Paragraph("<b>4(A) Division/Branch/Section/Unit Targets</b>", styles['SubSectionStyle']))
        story.append(Paragraph(self.report.division_targets or "Not specified", styles['GreenBoxStyle']))
        story.append(Spacer(1, 0.1*inch))
        
        story.append(Paragraph("<b>4(B) Appraiser Targets</b>", styles['SubSectionStyle']))
        story.append(Paragraph(self.report.appraiser_targets or "Not specified", styles['GreenBoxStyle']))
        story.append(Spacer(1, 0.15*inch))
        
        # ============ SECTION 4 ============
        self._add_section_header(story, "SECTION 4: OFFICER'S JOB DESCRIPTION")
        
        story.append(Paragraph("<b>5(a) Main Duties Performed</b>", styles['SubSectionStyle']))
        story.append(Paragraph(self.report.main_duties or "Not specified", styles['GreenBoxStyle']))
        story.append(Spacer(1, 0.1*inch))
        
        story.append(Paragraph("<b>5(c) Constraints/Difficulties Encountered</b>", styles['SubSectionStyle']))
        story.append(Paragraph(self.report.constraints_difficulties or "None", styles['GreenBoxStyle']))
        story.append(Spacer(1, 0.15*inch))
        
        # ============ SECTION 5 ============
        story.append(PageBreak())
        self._add_section_header(story, "SECTION 5: REPORTING OFFICER'S ASSESSMENT")
        
        ro_info = [
            [Paragraph("<b>Reporting Officer:</b>", styles['LabelStyle']), Paragraph(self.reporting_officer.full_name or self.reporting_officer.username if self.reporting_officer else "Not assigned", styles['ValueStyle'])],
            [Paragraph("<b>Department:</b>", styles['LabelStyle']), Paragraph(self.reporting_officer.department if self.reporting_officer else "N/A", styles['ValueStyle'])],
            [Paragraph("<b>Approval Date:</b>", styles['LabelStyle']), Paragraph(self.report.reporting_approved_at.strftime('%d %B %Y %H:%M') if self.report.reporting_approved_at else "Pending", styles['ValueStyle'])],
            [Paragraph("<b>Comments:</b>", styles['LabelStyle']), Paragraph(self.report.reporting_comments or "No comments", styles['ValueStyle'])],
        ]
        
        ro_table = Table(ro_info, colWidths=[2.2*inch, 5*inch])
        ro_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), edo_light_green),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(ro_table)
        story.append(Spacer(1, 0.1*inch))
        
        if self.assessment:
            story.append(Paragraph("<b>Performance Grading Scale:</b> A=6, B=5, C=4, D=3, E=2, F=1", styles['LabelStyle']))
            story.append(Spacer(1, 0.05*inch))
            
            grade_data = [
                [Paragraph("<b>Aspect of Performance</b>", styles['LabelStyle']), Paragraph("<b>Grade</b>", styles['LabelStyle']), Paragraph("<b>Rating</b>", styles['LabelStyle'])],
                ["(i) Foresight", self.assessment.foresight or "-", self.get_grade_description(self.assessment.foresight) if self.assessment.foresight else "-"],
                ["(ii) Judgement", self.assessment.judgement or "-", self.get_grade_description(self.assessment.judgement) if self.assessment.judgement else "-"],
                ["(iii) Oral Expression", self.assessment.oral_expression or "-", self.get_grade_description(self.assessment.oral_expression) if self.assessment.oral_expression else "-"],
                ["(iv) Relations with Colleagues", self.assessment.relations or "-", self.get_grade_description(self.assessment.relations) if self.assessment.relations else "-"],
                ["(v) Punctuality", self.assessment.punctuality or "-", self.get_grade_description(self.assessment.punctuality) if self.assessment.punctuality else "-"],
                ["(vi) Attendance at Work", self.assessment.attendance or "-", self.get_grade_description(self.assessment.attendance) if self.assessment.attendance else "-"],
                ["(vii) Industry", self.assessment.industry or "-", self.get_grade_description(self.assessment.industry) if self.assessment.industry else "-"],
                ["(viii) Output of Work", self.assessment.output_work or "-", self.get_grade_description(self.assessment.output_work) if self.assessment.output_work else "-"],
                ["(ix) Quality of Work", self.assessment.quality_work or "-", self.get_grade_description(self.assessment.quality_work) if self.assessment.quality_work else "-"],
                ["(x) Honesty", self.assessment.honesty or "-", self.get_grade_description(self.assessment.honesty) if self.assessment.honesty else "-"],
            ]
            
            grade_table = Table(grade_data, colWidths=[3.5*inch, 1*inch, 2.5*inch])
            grade_table.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('BACKGROUND', (0,0), (-1,0), edo_green),
                ('TEXTCOLOR', (0,0), (-1,0), edo_white),
                ('ALIGN', (1,0), (2,0), 'CENTER'),
                ('ALIGN', (1,1), (2,-1), 'CENTER'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('BACKGROUND', (0,1), (-1,-1), edo_white),
            ]))
            story.append(grade_table)
            story.append(Spacer(1, 0.1*inch))
            
            if hasattr(self.assessment, 'calculate_total_score'):
                total_score = self.assessment.calculate_total_score()
                score_data = [
                    [Paragraph(f"<b>Total Score:</b> {total_score}%", styles['ValueStyle'])],
                    [Paragraph(f"<b>Overall Rating:</b> {self.get_rating_description(total_score)}", styles['ValueStyle'])],
                ]
                score_table = Table(score_data, colWidths=[7.5*inch])
                score_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), edo_gold),
                    ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 11),
                    ('TOPPADDING', (0,0), (-1,-1), 8),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ]))
                story.append(score_table)
                story.append(Spacer(1, 0.1*inch))
            
            if self.assessment.general_remarks:
                story.append(Paragraph("<b>General Remarks:</b>", styles['SubSectionStyle']))
                story.append(Paragraph(self.assessment.general_remarks, styles['GreenBoxStyle']))
                story.append(Spacer(1, 0.1*inch))
            
            if self.assessment.training_recommended:
                story.append(Paragraph("<b>Training Recommended:</b>", styles['SubSectionStyle']))
                story.append(Paragraph(self.assessment.training_recommended, styles['GreenBoxStyle']))
                story.append(Spacer(1, 0.1*inch))
            
            if self.assessment.promotability_rating:
                story.append(Paragraph("<b>Promotability Rating:</b>", styles['SubSectionStyle']))
                story.append(Paragraph(self.get_promotability_description(self.assessment.promotability_rating), styles['ValueStyle']))
                story.append(Spacer(1, 0.15*inch))
        
        # ============ SECTION 6 ============
        story.append(PageBreak())
        self._add_section_header(story, "SECTION 6: COUNTERSIGNING OFFICER'S REVIEW")
        
        cso_info = [
            [Paragraph("<b>Countersigning Officer:</b>", styles['LabelStyle']), Paragraph(self.countersigning_officer.full_name or self.countersigning_officer.username if self.countersigning_officer else "Not assigned", styles['ValueStyle'])],
            [Paragraph("<b>Ministry:</b>", styles['LabelStyle']), Paragraph(self.countersigning_officer.ministry if self.countersigning_officer else "N/A", styles['ValueStyle'])],
            [Paragraph("<b>Approval Date:</b>", styles['LabelStyle']), Paragraph(self.report.countersigning_approved_at.strftime('%d %B %Y %H:%M') if self.report.countersigning_approved_at else "Pending", styles['ValueStyle'])],
            [Paragraph("<b>Agrees with Assessment:</b>", styles['LabelStyle']), Paragraph("Yes" if self.report.countersigning_approved_at else "Pending", styles['ValueStyle'])],
            [Paragraph("<b>Comments/Remarks:</b>", styles['LabelStyle']), Paragraph(self.report.countersigning_comments or "No comments", styles['ValueStyle'])],
        ]
        
        cso_table = Table(cso_info, colWidths=[2.2*inch, 5*inch])
        cso_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), edo_light_green),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ]))
        story.append(cso_table)
        story.append(Spacer(1, 0.15*inch))
        
        # ============ SECTION 7 ============
        self._add_section_header(story, "SECTION 7: WORKFLOW SUMMARY")
        
        workflow_data = [
            [Paragraph("<b>Officer Created:</b>", styles['LabelStyle']), Paragraph(self.report.created_at.strftime('%d %B %Y %H:%M') if self.report.created_at else "N/A", styles['ValueStyle'])],
            [Paragraph("<b>Officer Submitted:</b>", styles['LabelStyle']), Paragraph(self.report.submitted_at.strftime('%d %B %Y %H:%M') if self.report.submitted_at else "Not submitted", styles['ValueStyle'])],
            [Paragraph("<b>Reporting Officer Approved:</b>", styles['LabelStyle']), Paragraph(self.report.reporting_approved_at.strftime('%d %B %Y %H:%M') if self.report.reporting_approved_at else "Pending", styles['ValueStyle'])],
            [Paragraph("<b>Countersigning Officer Approved:</b>", styles['LabelStyle']), Paragraph(self.report.countersigning_approved_at.strftime('%d %B %Y %H:%M') if self.report.countersigning_approved_at else "Pending", styles['ValueStyle'])],
        ]
        
        workflow_table = Table(workflow_data, colWidths=[2.5*inch, 5*inch])
        workflow_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), edo_light_green),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(workflow_table)
        story.append(Spacer(1, 0.2*inch))
        
        # ============ FOOTER (white bold on dark green) ============
        story.append(Spacer(1, 0.1*inch))
        
        footer_data = [
            [Paragraph("This is an electronically generated document. Valid without signature.", styles['FooterStyle'])],
            [Paragraph(f"Generated on: {datetime.now().strftime('%d %B %Y %H:%M:%S')}", styles['FooterStyle'])],
            [Paragraph("Edo State Government - Civil Service Commission", styles['FooterStyle'])],
            [Paragraph("Official Performance Appraisal Document - Gen 79A Form", styles['FooterStyle'])],
        ]
        
        footer_table = Table(footer_data, colWidths=[7.5*inch])
        footer_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), edo_dark_green),
            ('TEXTCOLOR', (0,0), (-1,-1), edo_white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(footer_table)
        
        # Build PDF
        doc.build(story)
        self.buffer.seek(0)
        return self.buffer
    
    def get_grade_description(self, grade):
        grades = {
            'A': 'Outstanding',
            'B': 'Very Good',
            'C': 'Good',
            'D': 'Fair',
            'E': 'Poor',
            'F': 'Very Poor'
        }
        return grades.get(grade, '-')
    
    def get_rating_description(self, score):
        if score >= 90:
            return "Outstanding (A) - Exceeds expectations"
        elif score >= 75:
            return "Very Good (B) - Above expectations"
        elif score >= 60:
            return "Good (C) - Meets expectations"
        elif score >= 45:
            return "Fair (D) - Below expectations"
        else:
            return "Poor (E/F) - Significantly below expectations"
    
    def get_promotability_description(self, rating):
        descriptions = {
            'A': 'A - Exceptionally well qualified, ready for higher responsibility',
            'B': 'B - Ready for promotion',
            'C': 'C - Has promotion potential',
            'D': 'D - Not yet entitled for promotion',
            'E': 'E - No evidence of promotion potential',
            'F': 'F - Unlikely to qualify, reached limit of capacity'
        }
        return descriptions.get(rating, rating or 'Not rated')
    
    def download(self, filename="edo_state_performance_report.pdf"):
        self.generate()
        return send_file(
            self.buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )