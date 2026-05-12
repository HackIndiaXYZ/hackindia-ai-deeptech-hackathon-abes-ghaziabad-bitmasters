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
git clone https://github.com/HackIndiaXYZ/hackindia-ai-deeptech-hackathon-abes-ghaziabad-bitmasters.git
cd hackindia-ai-deeptech-hackathon-abes-ghaziabad-bitmasters
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
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

## Tech Stack

- **Backend**: Flask (Python)
- **PDF Processing**: pdfplumber, pdfme, fpdf
- **Frontend**: HTML, CSS, JavaScript

## Version

**Current Version: 1.0.0**

## License

This project is licensed under the MIT License.

---

Built with ❤️ for job seekers | HackIndia AI DeepTech Hackathon - BitMasters