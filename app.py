from flask import Flask, render_template, request, session, Response, send_file, make_response
from modules.scraper import find_policy_links, get_text_from_url
from modules.analyzer import analyze_policy_text
from modules.pdf_generator import create_report
from gtts import gTTS, gTTSError
from io import BytesIO
import os
import logging
import requests
from urllib.parse import urlparse, urljoin

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_very_secret_key_for_development'

# Add session configuration
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=1800  # 30 minutes
)

def validate_url(url):
    """Validate and clean URL"""
    try:
        result = urlparse(url)
        if not result.scheme:
            url = 'https://' + url
        response = requests.head(url, allow_redirects=True)
        return response.url
    except Exception as e:
        logger.error(f"URL validation error: {e}")
        return None

def setup_fonts():
    """Set up the fonts directory with fallback options"""
    try:
        fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        os.makedirs(fonts_dir, exist_ok=True)
        
        # List of potential system fonts
        system_fonts = [
            "C:\\Windows\\Fonts\\arial.ttf",
            "C:\\Windows\\Fonts\\calibri.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        
        for system_font in system_fonts:
            if os.path.exists(system_font):
                dest_path = os.path.join(fonts_dir, os.path.basename(system_font))
                if not os.path.exists(dest_path):
                    import shutil
                    shutil.copy2(system_font, dest_path)
                return True
                
        logger.warning("No system fonts found. Using default font.")
        return False
    except Exception as e:
        logger.error(f"Font setup error: {e}")
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        language = request.form['language']
        
        try:
            # Validate and clean URL
            valid_url = validate_url(url)
            if not valid_url:
                return render_template('index.html', 
                    error="Invalid URL. Please enter a valid website address.")
            
            logger.info(f"Finding policy links for: {valid_url}")
            policy_links = find_policy_links(valid_url)
            logger.info(f"Found policy links: {policy_links}")
            
            if not policy_links:
                logger.warning("No policy links found, using provided URL")
                policy_links = [valid_url]
                
            policy_text = None
            for link in policy_links:
                logger.info(f"Trying to extract text from: {link}")
                policy_text = get_text_from_url(link)
                if policy_text:
                    break
            
            if not policy_text:
                return render_template('index.html', 
                    error="Could not extract policy text. Please check the website or try a different URL.")
            
            logger.info(f"Analyzing text of length: {len(policy_text)}")
            analysis_result = analyze_policy_text(policy_text, language)
            
            if 'error' in analysis_result:
                return render_template('index.html', error=analysis_result['error'])
            
            # Store complete analysis data in session
            session['analysis_data'] = {
                'url': valid_url,
                'language': language,
                'analysis': {
                    'risk_category': analysis_result.get('risk_category', ''),
                    'translated_summary': analysis_result.get('translated_summary', ''),
                    'translated_key_risks': analysis_result.get('translated_key_risks', [])
                }
            }
            
            return render_template('index.html', result=session['analysis_data'])
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            return render_template('index.html', 
                error="An error occurred while processing your request. Please try again.")

    return render_template('index.html', result=None)

@app.route('/download_pdf')
def download_pdf():
    try:
        # Get complete analysis data from session
        analysis_data = session.get('analysis_data')
        
        if not analysis_data:
            logger.error("No analysis data in session")
            return "Please analyze a policy first.", 400
            
        # Generate PDF with error handling
        try:
            pdf_bytes = create_report(
                analysis_data['analysis'],
                analysis_data['url'],
                analysis_data['language']
            )
            
            if not pdf_bytes:
                logger.error("PDF generation returned None")
                return "Failed to generate PDF report.", 500
                
            # Create response with PDF
            response = make_response(pdf_bytes)
            response.headers.update({
                'Content-Type': 'application/pdf',
                'Content-Disposition': 'attachment; filename=policy_analysis.pdf',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            })
            
            return response
            
        except Exception as e:
            logger.error(f"PDF generation error: {str(e)}", exc_info=True)
            return "Error generating PDF report.", 500
            
    except Exception as e:
        logger.error(f"Download PDF error: {str(e)}", exc_info=True)
        return "An error occurred while generating the PDF.", 500

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data.get('text', '')
    language = data.get('language', 'en')
    
    language_map = {
        'English': 'en',
        'Hindi': 'hi',
        'Bengali': 'bn',
        'Tamil': 'ta',
        'Telugu': 'te',
        'Malayalam': 'ml',
        'Urdu': 'ur',
        'French': 'fr',
        'Russian': 'ru',
        'Spanish': 'es',
        'German': 'de'
    }
    
    lang_code = language_map.get(language, 'en')
    
    try:
        # Create audio directly in memory for faster processing
        audio_io = BytesIO()
        tts = gTTS(
            text=text,
            lang=lang_code,
            slow=False,
            lang_check=False
        )
        tts.write_to_fp(audio_io)
        audio_io.seek(0)
        
        response = send_file(
            audio_io,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='speech.mp3'
        )
        
        # Add streaming headers
        response.headers.update({
            'Cache-Control': 'no-cache',
            'Accept-Ranges': 'bytes',
            'Content-Transfer-Encoding': 'binary'
        })
        
        return response
            
    except Exception as e:
        logger.error(f"TTS Error: {str(e)}")
        return {'error': str(e)}, 500

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.errorhandler(404)
def not_found_error(error):
    return render_template('index.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('index.html', error="An internal error occurred"), 500

if __name__ == '__main__':
    setup_fonts()
    app.run(debug=True)
