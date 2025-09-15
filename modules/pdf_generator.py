from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'PolicyGuard AI Analysis Report', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_report(analysis_data, url, language):
    """
    Generates a PDF report from the analysis data.
    """
    pdf = PDF()
    pdf.add_page()
    
    # Add DejaVu font for UTF-8 support (for multiple languages)
    # You might need to provide the path to the font file on your system
    # Or place the .ttf file in your project directory.
    # We will try to add it, but fallback to Arial if it fails.
    try:
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        pdf.set_font('DejaVu', '', 12)
    except RuntimeError:
        print("DejaVuSans.ttf not found. Falling back to Arial. Non-ASCII characters may not render correctly.")
        pdf.set_font('Arial', '', 12)

    # Report Title
    pdf.set_font_size(16)
    pdf.cell(0, 10, f"Analysis for: {url}", 0, 1, 'L')
    pdf.ln(5)

    # Risk Category
    risk = analysis_data.get('risk_category', 'N/A')
    pdf.set_font_size(14)
    if risk == 'Safe':
        pdf.set_text_color(0, 128, 0) # Green
    elif risk == 'Medium Risk':
        pdf.set_text_color(255, 165, 0) # Orange
    elif risk == 'High Risk':
        pdf.set_text_color(255, 0, 0) # Red
    pdf.cell(0, 10, f"Overall Risk: {risk}", 0, 1, 'L')
    pdf.set_text_color(0, 0, 0) # Reset color
    pdf.ln(10)

    # Summary
    pdf.set_font_size(12)
    pdf.cell(0, 10, f"Summary ({language}):", 0, 1, 'L')
    summary = analysis_data.get('translated_summary', 'No summary available.')
    pdf.multi_cell(0, 10, summary)
    pdf.ln(10)

    # Key Risks
    pdf.cell(0, 10, f"Key Risks ({language}):", 0, 1, 'L')
    risks = analysis_data.get('translated_key_risks', [])
    if risks:
        for item in risks:
            pdf.multi_cell(0, 10, f"- {item}")
    else:
        pdf.multi_cell(0, 10, "No significant risks were identified.")

    # Save the PDF to a byte stream
    return pdf.output(dest='S').encode('latin-1')
