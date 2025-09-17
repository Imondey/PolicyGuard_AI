# PolicyGuard_AI

PolicyGuard AI is an intelligent web application that helps users understand complex legal policies, terms of service, and privacy agreements. It uses advanced AI to analyze, summarize, and translate policy documents into multiple languages while identifying potential risks.

## Features

- **Policy Analysis**: Automatically detects and analyzes privacy policies and terms of service from websites
- **Risk Assessment**: Classifies policies into risk categories (Safe, Medium Risk, High Risk)
- **Multi-language Support**: Translates summaries and key risks into multiple languages:
  - English
  - Hindi
  - Bengali
  - Tamil
  - Telugu
  - Malayalam
  - Urdu
  - French
  - Russian
  - Spanish
  - German
- **Text-to-Speech**: Listen to summaries and key risks in your preferred language
- **PDF Reports**: Generate and download detailed analysis reports

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to `http://127.0.0.1:5000`

3. Enter a website URL and select your preferred language

4. Click "Analyze Policy" to get:
   - Easy-to-understand summary
   - Risk assessment
   - Key potential risks
   - Audio playback options
   - Downloadable PDF report

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, TailwindCSS, JavaScript
- **AI/ML**: Google Gemini AI
- **Text-to-Speech**: gTTS (Google Text-to-Speech)
- **PDF Generation**: FPDF
- **Web Scraping**: BeautifulSoup4, Requests

## Project Structure

```
PolicyGuard_AI/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (not tracked)
├── .gitignore            # Git ignore rules
├── modules/
│   ├── __init__.py
│   ├── analyzer.py        # AI analysis module
│   ├── pdf_generator.py   # PDF report generation
│   └── scraper.py        # Web scraping utilities
└── templates/
    └── index.html        # Frontend template
```