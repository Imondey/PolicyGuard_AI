from flask import Flask, render_template, request, session, Response, send_file
from modules.scraper import find_policy_links, get_text_from_url
from modules.analyzer import analyze_policy_text
from modules.pdf_generator import create_report
from gtts import gTTS
from io import BytesIO

app = Flask(__name__)
# Secret key is needed to use sessions
app.config['SECRET_KEY'] = 'a_very_secret_key_for_development' 

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        language = request.form['language']
        
        # Store data in session to be used for PDF download
        session['url'] = url
        session['language'] = language

        try:
            # 1. Find policy links from the base URL
            policy_links = find_policy_links(url)
            
            if not policy_links:
                # If no links found, maybe the provided URL is the policy page itself
                policy_links = [url]
                
            # 2. Extract text from the first found policy link (or the provided URL)
            policy_text = get_text_from_url(policy_links[0]) if policy_links else None

            analysis_result = None
            if policy_text:
                # 3. Analyze the text using the LLM
                analysis_result = analyze_policy_text(policy_text, language)
                
                # Convert analysis_result to a format that can be stored in session
                session_analysis = {
                    'risk_category': analysis_result.get('risk_category', ''),
                    'translated_summary': analysis_result.get('translated_summary', ''),
                    'translated_key_risks': analysis_result.get('translated_key_risks', [])
                }
                
                # Store analysis in session
                session['analysis'] = session_analysis
                
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
    # Retrieve data from session
    analysis_data = session.get('analysis')
    url = session.get('url', 'N/A')
    language = session.get('language', 'English')

    if not analysis_data:
        return "No analysis data found to generate PDF.", 404
        
    pdf_bytes = create_report(analysis_data, url, language)
    
    return Response(pdf_bytes,
                    mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=PolicyGuard_Report.pdf'})

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
        # Create audio file with optimized settings
        audio_io = BytesIO()
        tts = gTTS(text=text, lang=lang_code, slow=False)
        tts.write_to_fp(audio_io)
        audio_io.seek(0)
        
        response = send_file(
            audio_io,
            mimetype='audio/mp3',
            as_attachment=True,
            download_name='speech.mp3'
        )
        
        # Add headers to prevent caching
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
        
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)
