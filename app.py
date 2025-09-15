from flask import Flask, render_template, request, session, Response
from modules.scraper import find_policy_links, get_text_from_url
from modules.analyzer import analyze_policy_text
from modules.pdf_generator import create_report

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

        # 1. Find policy links from the base URL
        policy_links = find_policy_links(url)
        
        if not policy_links:
            # If no links found, maybe the provided URL is the policy page itself
            policy_links = [url]
            
        # 2. Extract text from the first found policy link (or the provided URL)
        # For a full implementation, you could analyze all found links.
        policy_text = get_text_from_url(policy_links[0]) if policy_links else None

        analysis_result = None
        if policy_text:
            # 3. Analyze the text using the LLM
            analysis_result = analyze_policy_text(policy_text, language)

        # Store analysis in session
        session['analysis'] = analysis_result
        
        result_data = {
            "url": url,
            "language": language,
            "analysis": analysis_result
        }
        
        return render_template('index.html', result=result_data)

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


if __name__ == '__main__':
    app.run(debug=True)
