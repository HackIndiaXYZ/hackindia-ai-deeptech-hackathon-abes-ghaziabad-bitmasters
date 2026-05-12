# JDAlign - Resume Optimizer

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

JDAlign is a web-based tool that analyzes your resume against a job description (JD), identifies skill gaps, and provides detailed comparison analysis to help you optimize your resume for ATS (Applicant Tracking Systems).

## Features

- **Resume Analysis**: Upload or paste your resume (PDF or text)
- **Job Description Input**: Paste the job description you're targeting
- **Detailed Comparison**: See exactly how your resume matches the JD
  - Skills gap analysis
  - Requirements matching
  - Experience level comparison
  - Keywords density
  - Action verbs analysis
- **Dark/Light Mode**: Toggle between themes for comfortable viewing
- **PDF Reports**: Download detailed analysis reports

## Getting Started

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/JDAlign.git
cd JDAlign
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. **Upload Resume**: Either paste your resume text or upload a PDF
2. **Enter Job Description**: Paste the job description you're targeting
3. **Analyze**: Click "Analyze & Optimize Resume" to get your results
4. **Review**: See detailed analysis including:
   - Match score percentage
   - Skills you have vs. skills needed
   - Requirements matched and missing
   - Experience level comparison
   - Keywords found

## Project Structure

```
JDAlign/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── nlp/
│   ├── analyzer.py    # JD and resume analysis
│   └── optimizer.py   # Resume optimization logic
├── utils/
│   └── pdf_handler.py # PDF text extraction
├── themes/
│   └── __init__.py   # PDF report generation
├── templates/
│   └── index.html    # Frontend HTML
└── static/
    ├── style.css     # Styling
    └── script.js     # Frontend JavaScript
```

## Technologies Used

- **Backend**: Flask (Python)
- **PDF Processing**: pdfplumber, pdfme, fpdf
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Ready for cloud deployment (Render, Railway, etc.)

## Deployment

### Deploy to Render (Recommended - Free Tier)

1. Push your code to GitHub
2. Create a free account at [render.com](https://render.com)
3. Create a new Web Service:
   - Connect your GitHub repository
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `python app.py`
   - Choose free tier

### Deploy to Railway

1. Push your code to GitHub
2. Create a free account at [railway.app](https://railway.app)
3. Deploy from GitHub and select your repository

## Version

**Current Version: 1.0.0**

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Built with ❤️ for job seekers