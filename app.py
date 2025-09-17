from flask import Flask, render_template, request, session, Response, send_file, make_response
from modules.scraper import find_policy_links, get_text_from_url
from modules.analyzer import analyze_policy_text
from modules.pdf_generator import create_report
from gtts import gTTS, gTTSError
from io import BytesIO
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_very_secret_key_for_development'

def setup_fonts():
    """Set up the fonts directory with a default system font"""
    fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    os.makedirs(fonts_dir, exist_ok=True)
    
    # Use Arial or a system font instead of downloading DejaVu
    font_path = os.path.join(fonts_dir, "arial.ttf")
    
    # If font doesn't exist, create a symlink to system Arial font
    if not os.path.exists(font_path):
        try:
            # Windows path to Arial
            system_font = "C:\\Windows\\Fonts\\arial.ttf"
            if os.path.exists(system_font):
                if os.name == 'nt':  # Windows
                    import shutil
                    shutil.copy2(system_font, font_path)
                else:  # Unix-like
                    os.symlink(system_font, font_path)
            else:
                print("Warning: Arial font not found. Text rendering might be affected.")
        except Exception as e:
            print(f"Warning: Could not set up font: {e}")
            print("Continuing without custom font...")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        language = request.form['language']
        
        try:
            print(f"Finding policy links for: {url}")
            policy_links = find_policy_links(url)
            print(f"Found policy links: {policy_links}")
            
            if not policy_links:
                print("No policy links found, using provided URL")
                policy_links = [url]
                
            print(f"Extracting text from: {policy_links[0]}")
            policy_text = get_text_from_url(policy_links[0])
            
            if not policy_text:
                return render_template('index.html', 
                    error="Could not extract policy text from the website. Please make sure the URL is correct.")
            
            print(f"Analyzing text of length: {len(policy_text)}")
            analysis_result = analyze_policy_text(policy_text, language)
            
            if 'error' in analysis_result:
                return render_template('index.html', error=analysis_result['error'])
            
            # Store ALL necessary data in session
            session['url'] = url
            session['language'] = language
            session['analysis'] = {
                'risk_category': analysis_result.get('risk_category', ''),
                'translated_summary': analysis_result.get('translated_summary', ''),
                'translated_key_risks': analysis_result.get('translated_key_risks', [])
            }
            
            result_data = {
                "url": url,
                "language": language,
                "analysis": analysis_result
            }
            
            return render_template('index.html', result=result_data)
            
        except Exception as e:
            print(f"Error processing request: {str(e)}")
            return render_template('index.html', error="An error occurred while processing your request. Please try again.")

    return render_template('index.html', result=None)

@app.route('/download_pdf')
def download_pdf():
    try:
        # Get data from session with better error handling
        url = session.get('url')
        language = session.get('language')
        analysis = session.get('analysis')
        
        if not url or not language or not analysis:
            print("Missing session data:", {
                'url': bool(url),
                'language': bool(language),
                'analysis': bool(analysis)
            })
            return "No analysis data available. Please analyze a policy first.", 400
            
        # Generate PDF
        pdf_bytes = create_report(analysis, url, language)
        
        if not pdf_bytes:
            print("PDF generation failed")
            return "Failed to generate PDF report.", 500
            
        # Create response
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=policy_analysis.pdf'
        
        return response
        
    except Exception as e:
        print(f"Error in download_pdf: {str(e)}")
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
        print(f"TTS Error: {str(e)}")
        return {'error': str(e)}, 500

if __name__ == '__main__':
    setup_fonts()  # Set up fonts before running the app
    app.run(debug=True)
