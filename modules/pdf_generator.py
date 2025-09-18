from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 20)
        self.cell(0, 10, 'PolicyGuard AI Report', 0, 1, 'C')
        self.ln(10)

def create_report(analysis_data, url, language):
    try:
        pdf = PDF()
        pdf.add_page()
        
        # Ensure text is properly encoded
        def safe_text(text):
            if isinstance(text, str):
                return text.encode('latin-1', errors='replace').decode('latin-1')
            return str(text)
        
        # Use safer text handling
        url = safe_text(url)
        summary = safe_text(analysis_data.get('translated_summary', 'No summary available.'))
        risks = [safe_text(risk) for risk in analysis_data.get('translated_key_risks', [])]
        
        # Try different fonts in order of preference
        fonts = ['Arial', 'Helvetica', 'Courier']
        font_set = False
        
        for font in fonts:
            try:
                pdf.set_font(font, '', 12)
                font_set = True
                break
            except Exception:
                continue
        
        if not font_set:
            # If no preferred fonts work, use the default font
            pdf.set_font('Arial', '', 12)
        
        # URL Section
        pdf.set_font(pdf.font_family, 'B', 14)
        pdf.cell(0, 10, 'Website Analyzed:', 0, 1)
        pdf.set_font(pdf.font_family, '', 12)
        pdf.multi_cell(0, 10, url)
        pdf.ln(10)
        
        # Risk Level Section
        pdf.set_font(pdf.font_family, 'B', 14)
        pdf.cell(0, 10, 'Risk Level:', 0, 1)
        pdf.set_font(pdf.font_family, '', 12)
        pdf.cell(0, 10, analysis_data.get('risk_category', 'N/A'), 0, 1)
        pdf.ln(10)
        
        # Summary Section
        pdf.set_font(pdf.font_family, 'B', 14)
        pdf.cell(0, 10, f'Summary ({language}):', 0, 1)
        pdf.set_font(pdf.font_family, '', 12)
        pdf.multi_cell(0, 10, summary)
        pdf.ln(10)
        
        # Key Risks Section
        pdf.set_font(pdf.font_family, 'B', 14)
        pdf.cell(0, 10, f'Key Risks ({language}):', 0, 1)
        pdf.set_font(pdf.font_family, '', 12)
        for risk in risks:
            pdf.multi_cell(0, 10, f"• {risk}")
        
        # Return PDF as bytes
        return pdf.output(dest='S').encode('latin-1', errors='replace')
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return None
