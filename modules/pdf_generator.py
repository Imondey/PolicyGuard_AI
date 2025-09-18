from fpdf import FPDF
import os
import logging

logger = logging.getLogger(__name__)

class PDF(FPDF):
    def header(self):
        try:
            self.set_font('Arial', 'B', 20)
            self.cell(0, 10, 'PolicyGuard AI Report', 0, 1, 'C')
            self.ln(10)
        except Exception as e:
            logger.error(f"Header error: {e}")

def create_report(analysis_data, url, language):
    try:
        pdf = PDF()
        pdf.add_page()
        
        # Try to set default font
        try:
            pdf.set_font('Arial', '', 12)
        except Exception:
            # Fallback to built-in font
            pdf.set_font('Helvetica', '', 12)
        
        # Function to safely handle text encoding
        def safe_text(text):
            if not text:
                return ''
            try:
                # First try UTF-8
                return text.encode('utf-8', errors='replace').decode('utf-8')
            except:
                # Fallback to latin-1
                return text.encode('latin-1', errors='replace').decode('latin-1')
        
        # URL Section
        pdf.set_font(pdf.font_family, 'B', 14)
        pdf.cell(0, 10, 'Website Analyzed:', 0, 1)
        pdf.set_font(pdf.font_family, '', 12)
        pdf.multi_cell(0, 10, safe_text(url))
        
        # Risk Level Section
        pdf.ln(5)
        pdf.set_font(pdf.font_family, 'B', 14)
        pdf.cell(0, 10, 'Risk Level:', 0, 1)
        pdf.set_font(pdf.font_family, '', 12)
        risk_category = analysis_data.get('risk_category', 'N/A')
        pdf.cell(0, 10, safe_text(risk_category), 0, 1)
        
        # Summary Section
        pdf.ln(5)
        pdf.set_font(pdf.font_family, 'B', 14)
        pdf.cell(0, 10, f'Summary ({language}):', 0, 1)
        pdf.set_font(pdf.font_family, '', 12)
        summary = analysis_data.get('translated_summary', 'No summary available.')
        pdf.multi_cell(0, 10, safe_text(summary))
        
        # Key Risks Section
        pdf.ln(5)
        pdf.set_font(pdf.font_family, 'B', 14)
        pdf.cell(0, 10, f'Key Risks ({language}):', 0, 1)
        pdf.set_font(pdf.font_family, '', 12)
        risks = analysis_data.get('translated_key_risks', [])
        for risk in risks:
            pdf.multi_cell(0, 10, f"• {safe_text(risk)}")
        
        # Generate PDF bytes
        try:
            return pdf.output(dest='S').encode('latin-1')
        except Exception as e:
            logger.error(f"PDF output error: {e}")
            # Try alternative output method
            pdf_buffer = bytes(pdf.output(dest='S'), 'latin-1')
            return pdf_buffer
            
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        return None
