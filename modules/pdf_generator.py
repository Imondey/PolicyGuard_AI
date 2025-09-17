from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        # Logo
        self.set_font('Arial', 'B', 20)
        self.cell(0, 10, 'PolicyGuard AI Report', 0, 1, 'C')
        self.ln(10)

def create_report(analysis_data, url, language):
    try:
        pdf = PDF()
        pdf.add_page()
        
        # Set Unicode font
        pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        pdf.set_font('DejaVu', '', 12)
        
        # URL Section
        pdf.set_font('DejaVu', 'B', 14)
        pdf.cell(0, 10, 'Website Analyzed:', 0, 1)
        pdf.set_font('DejaVu', '', 12)
        pdf.multi_cell(0, 10, url)
        pdf.ln(10)
        
        # Risk Level Section
        pdf.set_font('DejaVu', 'B', 14)
        pdf.cell(0, 10, 'Risk Level:', 0, 1)
        pdf.set_font('DejaVu', '', 12)
        pdf.cell(0, 10, analysis_data.get('risk_category', 'N/A'), 0, 1)
        pdf.ln(10)
        
        # Summary Section
        pdf.set_font('DejaVu', 'B', 14)
        pdf.cell(0, 10, f'Summary ({language}):', 0, 1)
        pdf.set_font('DejaVu', '', 12)
        pdf.multi_cell(0, 10, analysis_data.get('translated_summary', 'No summary available.'))
        pdf.ln(10)
        
        # Key Risks Section
        pdf.set_font('DejaVu', 'B', 14)
        pdf.cell(0, 10, f'Key Risks ({language}):', 0, 1)
        pdf.set_font('DejaVu', '', 12)
        risks = analysis_data.get('translated_key_risks', [])
        for risk in risks:
            pdf.multi_cell(0, 10, f"• {risk}")
        
        # Return PDF as bytes
        return pdf.output(dest='S').encode('latin-1', errors='replace')
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return None
