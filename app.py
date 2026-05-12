from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import io
from nlp.analyzer import Analyzer
from nlp.optimizer import Optimizer
from utils.pdf_handler import extract_text_from_pdf
from themes import generate_analysis_report, generate_resume_pdf

app = Flask(__name__)
CORS(app, resources={r"/download/*": {"origins": "*"}})

analyzer = Analyzer()
optimizer = Optimizer(None, analyzer)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_resume():
    """Handle PDF upload and extract text"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are supported'}), 400

    try:
        file_bytes = file.read()
        text = extract_text_from_pdf(file_bytes)

        if not text or len(text.strip()) < 50:
            return jsonify({'error': 'Could not extract text from PDF. Try using the text input instead.'}), 400

        return jsonify({
            'success': True,
            'text': text,
            'filename': file.filename
        })

    except Exception as e:
        return jsonify({'error': f'Error processing PDF: {str(e)}'}), 400


@app.route('/analyze', methods=['POST'])
def analyze():
    """Main analysis endpoint with detailed comparison"""
    data = request.get_json()
    resume_text = data.get('resume', '').strip()
    jd_text = data.get('jd', '').strip()

    if not resume_text or not jd_text:
        return jsonify({'error': 'Both resume and job description are required'}), 400

    if len(resume_text) < 50:
        return jsonify({'error': 'Resume text is too short (minimum 50 characters)'}), 400

    # Analyze JD
    jd_analysis = analyzer.analyze_jd(jd_text)

    # Optimize resume
    result = optimizer.optimize_resume(resume_text, jd_analysis)

    # Build detailed comparison
    comparison = build_detailed_comparison(resume_text, jd_analysis, result)
    result['comparison'] = comparison

    # Add matched keywords list
    mapping = result['mapping']
    matched_kw = []
    jd_keywords_lower = set(k.lower() for k in jd_analysis['keywords'])

    for original in mapping.keys():
        for kw in jd_keywords_lower:
            if kw in original.lower():
                matched_kw.append(kw)

    result['matched_keywords_list'] = list(set(matched_kw))[:20]
    result['optimized_resume_text'] = build_optimized_resume(resume_text, mapping)

    return jsonify(result)


def build_detailed_comparison(resume_text, jd_analysis, result):
    """Build comprehensive comparison between resume and JD"""
    resume_lower = resume_text.lower()
    jd_text = jd_analysis['jd_text']
    jd_lower = jd_text.lower()

    # === 1. REQUIREMENTS MATCHING ===
    # Extract requirements from JD
    jd_requirements = extract_jd_requirements(jd_text)

    matched_requirements = []
    missing_requirements = []
    partial_matches = []

    for req in jd_requirements:
        req_words = req.lower().split()
        req_key_words = [w for w in req_words if len(w) > 3][:5]  # Get key words

        # Check if resume has these keywords
        match_count = sum(1 for kw in req_key_words if kw in resume_lower)

        if match_count >= len(req_key_words) * 0.7:
            matched_requirements.append(req)
        elif match_count >= 1:
            partial_matches.append(f"{req} (partial match)")
        else:
            if len(req) > 10:
                missing_requirements.append(req)

    # === 2. SKILLS ANALYSIS ===
    # Extract skills from resume
    resume_skills = extract_skills_from_resume(resume_text)

    # JD skills
    jd_skills = [s.lower() for s in jd_analysis['skills']]

    # Categorize skills
    technical_skills = ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'ruby', 'php', 'swift', 'kotlin']
    frameworks = ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'node', 'next', 'nuxt']
    cloud_devops = ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible', 'git', 'ci/cd']
    databases = ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle']

    resume_skill_lower = [s.lower() for s in resume_skills]

    # Categorize what resume has
    have_technical = [s for s in resume_skills if s.lower() in technical_skills]
    have_frameworks = [s for s in resume_skills if s.lower() in frameworks]
    have_cloud = [s for s in resume_skills if s.lower() in cloud_devops]
    have_databases = [s for s in resume_skills if s.lower() in databases]

    # What JD requires
    need_technical = [s for s in jd_skills if s in technical_skills]
    need_frameworks = [s for s in jd_skills if s in frameworks]
    need_cloud = [s for s in jd_skills if s in cloud_devops]
    need_databases = [s for s in jd_skills if s in databases]

    # Skills gap
    skills_have = resume_skills[:15]
    skills_need = [s for s in jd_skills if s.lower() not in resume_skill_lower][:15]

    # === 3. EXPERIENCE ANALYSIS ===
    jd_level = jd_analysis.get('experience_level', 'mid')
    resume_level = detect_resume_experience_level(resume_text)

    # Analyze years of experience
    jd_years = extract_years_from_jd(jd_text)
    resume_years = extract_years_from_resume(resume_text)

    if jd_years and resume_years:
        if resume_years >= jd_years:
            exp_verdict = f"You have {resume_years}+ years, meets {jd_years}+ years requirement"
        else:
            exp_verdict = f"You have {resume_years} years, JD requires {jd_years}+ years"
    else:
        exp_verdict = "Experience level appears to match"

    # Check for key action verbs in JD vs resume
    jd_action_verbs = jd_analysis.get('action_verbs', [])
    resume_action_verbs = extract_action_verbs_from_resume(resume_text)

    matched_verbs = [v for v in jd_action_verbs if v in resume_action_verbs]
    missing_verbs = [v for v in jd_action_verbs if v not in resume_action_verbs]

    # === 4. EDUCATION & CERTIFICATIONS ===
    edu_match = check_education_match(resume_text, jd_text)
    cert_match = check_certifications_match(resume_text, jd_text)

    # === 5. KEYWORDS DENSITY ===
    jd_keywords = [k.lower() for k in jd_analysis.get('keywords', [])]
    keyword_density = calculate_keyword_density(resume_lower, jd_keywords)

    return {
        # Requirements
        'matched_requirements': matched_requirements[:8],
        'partial_matches': partial_matches[:5],
        'missing_requirements': missing_requirements[:8],

        # Skills breakdown
        'skills_have': skills_have,
        'skills_need': skills_need,
        'have_technical': have_technical,
        'have_frameworks': have_frameworks,
        'have_cloud': have_cloud,
        'have_databases': have_databases,
        'need_technical': need_technical,
        'need_frameworks': need_frameworks,
        'need_cloud': need_cloud,
        'need_databases': need_databases,

        # Experience
        'experience_analysis': {
            'jd_level': jd_level,
            'resume_level': resume_level,
            'jd_years': jd_years,
            'resume_years': resume_years,
            'verdict': exp_verdict,
            'matched_verbs': matched_verbs[:5],
            'missing_verbs': missing_verbs[:5]
        },

        # Education & Certs
        'education_match': edu_match,
        'certification_match': cert_match,

        # Summary score
        'overall': {
            'requirements_match_pct': int((len(matched_requirements) / max(1, len(matched_requirements) + len(missing_requirements))) * 100),
            'skills_match_pct': int((len(skills_have) / max(1, len(skills_have) + len(skills_need))) * 100),
            'keyword_density': keyword_density
        }
    }


def extract_jd_requirements(jd_text):
    """Extract requirement items from JD"""
    requirements = []
    lines = jd_text.split('\n')

    in_requirements_section = False
    for line in lines:
        line = line.strip()
        line_lower = line.lower()

        # Detect requirements section
        if any(x in line_lower for x in ['requirement', 'qualification', 'responsibility', 'duty', 'skill', 'must have', 'expected']):
            in_requirements_section = True
            if ':' in line:
                req = line.split(':', 1)[1].strip()
                if len(req) > 5:
                    requirements.append(req)
            continue

        if in_requirements_section:
            if line.startswith('-') or line.startswith('*') or line.startswith('•'):
                req = line.lstrip('-*•').strip()
                if len(req) > 5:
                    requirements.append(req)
            elif line and len(line) < 80 and not line.endswith(':'):
                requirements.append(line)

    return requirements


def extract_skills_from_resume(resume_text):
    """Extract skills mentioned in resume"""
    skills = []
    tech_keywords = [
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'golang', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'r',
        'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring', 'express', 'next', 'nuxt', 'rails', '.net',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'k8s', 'jenkins', 'git', 'terraform', 'ansible', 'ci/cd', 'gitlab',
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sqlite', 'cassandra',
        'machine learning', 'ml', 'ai', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit',
        'html', 'css', 'sass', 'rest', 'graphql', 'api', 'microservices', 'agile', 'scrum', 'jira'
    ]

    resume_lower = resume_text.lower()
    for skill in tech_keywords:
        if skill in resume_lower:
            skills.append(skill.title() if len(skill) > 3 else skill.upper())

    return list(set(skills))


def detect_resume_experience_level(resume_text):
    """Detect experience level from resume"""
    text_lower = resume_text.lower()

    senior_keywords = ['senior', 'sr.', 'sr ', 'lead', 'principal', 'staff', 'architect', 'manager', 'director', 'head of']
    junior_keywords = ['junior', 'jr.', 'jr ', 'intern', 'trainee', 'entry', 'entry-level', 'graduate']

    if any(word in text_lower for word in senior_keywords):
        return 'senior'
    elif any(word in text_lower for word in junior_keywords):
        return 'junior'
    return 'mid-level'


def extract_years_from_jd(jd_text):
    """Extract years of experience required from JD"""
    import re
    pattern = r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)'
    match = re.search(pattern, jd_text.lower())
    return int(match.group(1)) if match else None


def extract_years_from_resume(resume_text):
    """Extract years of experience from resume"""
    import re
    pattern = r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)'
    match = re.search(pattern, resume_text.lower())
    return int(match.group(1)) if match else None


def extract_action_verbs_from_resume(resume_text):
    """Extract action verbs used in resume"""
    action_verbs = [
        'managed', 'led', 'developed', 'created', 'designed', 'implemented', 'optimized', 'improved',
        'increased', 'reduced', 'automated', 'integrated', 'built', 'launched', 'delivered', 'spearheaded',
        'executed', 'coordinated', 'analyzed', 'generated', 'monitored', 'maintained', 'trained', 'mentored'
    ]
    resume_lower = resume_text.lower()
    return [v for v in action_verbs if v in resume_lower]


def check_education_match(resume_text, jd_text):
    """Check if education requirements are met"""
    edu_keywords = ['bachelor', 'master', 'phd', 'm.sc', 'b.sc', 'bscs', 'mcs', 'btech', 'mtech', 'degree']

    resume_has_degree = any(word in resume_text.lower() for word in edu_keywords)
    jd_requires_degree = any(word in jd_text.lower() for word in edu_keywords)

    if jd_requires_degree:
        if resume_has_degree:
            return "Education requirement: MET"
        else:
            return "Education requirement: NOT SPECIFIED IN RESUME"
    return "No specific degree required"


def check_certifications_match(resume_text, jd_text):
    """Check certification requirements"""
    cert_keywords = ['aws', 'azure', 'gcp', 'pmp', 'comptia', 'cissp', 'scrum', 'certified']

    jd_certs = [c for c in cert_keywords if c in jd_text.lower()]
    resume_certs = [c for c in cert_keywords if c in resume_text.lower()]

    if jd_certs:
        matched = [c for c in jd_certs if c in resume_certs]
        missing = [c for c in jd_certs if c not in resume_certs]
        return f"Certifications: {', '.join(matched) if matched else 'None'} | Missing: {', '.join(missing) if missing else 'None'}"
    return "No specific certifications required"


def calculate_keyword_density(resume_lower, jd_keywords):
    """Calculate keyword density percentage"""
    if not jd_keywords:
        return 0
    matches = sum(1 for kw in jd_keywords if kw in resume_lower)
    return int((matches / len(jd_keywords)) * 100)


def build_optimized_resume(original_text, mapping):
    """Build the complete optimized resume text"""
    result = original_text
    for original, optimized in mapping.items():
        result = result.replace(original, optimized, 1)
    return result


@app.route('/download/report', methods=['POST', 'OPTIONS'])
def download_report():
    """Generate and download analysis report PDF"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json(silent=True)

        analysis_data = {
            'confidence_score': data.get('confidence_score', 0) if data else 0,
            'statistics': data.get('statistics', {}) if data else {},
            'matched_keywords_list': data.get('matched_keywords_list', []) if data else [],
            'gaps_identified': data.get('gaps_identified', []) if data else [],
            'mapping': data.get('mapping', {}) if data else {},
            'comparison': data.get('comparison', {}) if data else {}
        }

        pdf_bytes = generate_analysis_report(analysis_data, 'modern')

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='jdalgin-analysis-report.pdf'
        )
    except Exception as e:
        print(f"Error in download_report: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/download/resume', methods=['POST', 'OPTIONS'])
def download_resume():
    """Generate and download optimized resume PDF"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        resume_text = data.get('optimized_resume_text', '') if data else ''

        if not resume_text:
            return jsonify({'error': 'No optimized resume available'}), 400

        pdf_bytes = generate_resume_pdf(resume_text, 'modern')

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='optimized-resume.pdf'
        )
    except Exception as e:
        print(f"Error in download_resume: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)