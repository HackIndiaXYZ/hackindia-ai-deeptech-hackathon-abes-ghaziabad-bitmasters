from fpdf import FPDF
from datetime import datetime
import io


def sanitize_text(text):
    """Remove or replace non-latin-1 characters"""
    if not text:
        return text

    # Replace common Unicode bullets and symbols with ASCII equivalents
    replacements = {
        '•': '-',     # •
        '●': '-',     # ●
        '’': "'",     # '
        '‘': "'",     # '
        '“': '"',     # "
        '”': '"',     # "
        '–': '-',     # –
        '—': '-',     # —
        ' ': ' ',     # non-breaking space
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove any remaining non-latin-1 characters
    try:
        text = text.encode('latin-1', 'replace').decode('latin-1')
    except:
        # Fallback: keep only ASCII characters
        text = ''.join(c if ord(c) < 128 else '-' for c in text)

    return text


class ThemePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_font('Helvetica', '', 11)


def generate_analysis_report(analysis_data, format_name='modern'):
    """Generate detailed PDF report with comprehensive analysis"""
    # Sanitize all text data
    if 'matched_keywords_list' in analysis_data:
        analysis_data['matched_keywords_list'] = [sanitize_text(k) for k in analysis_data['matched_keywords_list']]

    pdf = ThemePDF()
    pdf.add_page()

    # ===== TITLE =====
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 16, 'JDAlign - Resume Analysis Report', 0, 1, 'C')
    pdf.ln(8)

    # ===== METADATA =====
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 6, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
    pdf.ln(12)

    # ===== OVERALL SCORE =====
    score = analysis_data.get('confidence_score', 0)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 10, f'Overall Match Score: {score}%', 0, 1)

    # Score interpretation
    if score >= 80:
        score_msg = "Excellent match - Your resume is well-aligned with this position."
    elif score >= 60:
        score_msg = "Good match - Some improvements recommended."
    elif score >= 40:
        score_msg = "Moderate match - Several areas need attention."
    else:
        score_msg = "Low match - Significant updates recommended."

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(31, 41, 55)
    pdf.multi_cell(0, 6, score_msg)
    pdf.ln(12)

    # ===== STATISTICS OVERVIEW =====
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 10, 'Statistics Overview', 0, 1)
    pdf.set_draw_color(37, 99, 235)
    pdf.set_line_width(0.5)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + 80, pdf.get_y())
    pdf.ln(4)

    stats = analysis_data.get('statistics', {})
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(31, 41, 55)

    stats_items = [
        ('Keywords Matched', stats.get('matched_keywords', 0)),
        ('Total Segments Analyzed', stats.get('total_segments', 0)),
        ('JD Keywords', stats.get('jd_keywords_count', 0)),
        ('JD Skills Required', stats.get('jd_skills_count', 0)),
    ]

    for label, value in stats_items:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(60, 7, f'{label}:', 0, 0)
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 7, str(value), 0, 1)

    pdf.ln(10)

    # ===== COMPARISON DATA =====
    comparison = analysis_data.get('comparison', {})
    overall = comparison.get('overall', {})

    # Requirements Match
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 10, 'Requirements Analysis', 0, 1)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + 80, pdf.get_y())
    pdf.ln(4)

    req_match_pct = overall.get('requirements_match_pct', 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(0, 7, f'Requirements Match: {req_match_pct}%', 0, 1)
    pdf.ln(5)

    # Matched Requirements
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(22, 163, 74)
    pdf.cell(0, 7, '[+] Requirements You Have:', 0, 1)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(31, 41, 55)

    matched = comparison.get('matched_requirements', [])
    if matched:
        for req in matched[:10]:
            pdf.cell(0, 6, f'  - {req}', 0, 1)
    else:
        pdf.cell(0, 6, '  No direct requirement matches found', 0, 1)

    pdf.ln(5)

    # Missing Requirements
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(220, 38, 38)
    pdf.cell(0, 7, '[-] Requirements Missing:', 0, 1)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(31, 41, 55)

    missing = comparison.get('missing_requirements', [])
    if missing:
        for req in missing[:10]:
            pdf.cell(0, 6, f'  - {req}', 0, 1)
    else:
        pdf.cell(0, 6, '  All key requirements are covered!', 0, 1)

    pdf.ln(12)

    # ===== SKILLS ANALYSIS =====
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 10, 'Skills Gap Analysis', 0, 1)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + 80, pdf.get_y())
    pdf.ln(4)

    skills_match_pct = overall.get('skills_match_pct', 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(0, 7, f'Skills Match: {skills_match_pct}%', 0, 1)
    pdf.ln(5)

    # Skills You Have
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(22, 163, 74)
    pdf.cell(0, 7, '[+] Skills in Your Resume:', 0, 1)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(31, 41, 55)

    skills_have = comparison.get('skills_have', [])
    if skills_have:
        pdf.cell(0, 6, f'  {", ".join(skills_have[:15])}', 0, 1)
    else:
        pdf.cell(0, 6, '  No skills detected', 0, 1)

    pdf.ln(5)

    # Skills You Need
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(220, 38, 38)
    pdf.cell(0, 7, '[-] Skills Required by JD:', 0, 1)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(31, 41, 55)

    skills_need = comparison.get('skills_need', [])
    if skills_need:
        pdf.cell(0, 6, f'  {", ".join(skills_need[:15])}', 0, 1)
    else:
        pdf.cell(0, 6, '  All required skills covered!', 0, 1)

    pdf.ln(12)

    # ===== EXPERIENCE ANALYSIS =====
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 10, 'Experience Analysis', 0, 1)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + 80, pdf.get_y())
    pdf.ln(4)

    exp = comparison.get('experience_analysis', {})

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(31, 41, 55)

    exp_data = [
        ('JD Required Level', exp.get('jd_level', 'Not specified')),
        ('Your Experience Level', exp.get('resume_level', 'Not detected')),
        ('JD Required Years', f"{exp.get('jd_years', 'Not specified')}+ years" if exp.get('jd_years') else 'Not specified'),
        ('Your Years of Experience', f"{exp.get('resume_years', 'Not detected')}+ years" if exp.get('resume_years') else 'Not detected'),
        ('Analysis', exp.get('verdict', 'Analyzing...')),
    ]

    for label, value in exp_data:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(50, 7, f'{label}:', 0, 0)
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 7, str(value), 0, 1)

    pdf.ln(8)

    # Action Verbs Analysis
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 7, 'Action Verbs Analysis:', 0, 1)

    matched_verbs = exp.get('matched_verbs', [])
    missing_verbs = exp.get('missing_verbs', [])

    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(31, 41, 55)

    if matched_verbs:
        pdf.cell(0, 6, f"  Verbs you use: {', '.join(matched_verbs)}", 0, 1)
    if missing_verbs:
        pdf.cell(0, 6, f"  Add these verbs: {', '.join(missing_verbs)}", 0, 1)

    pdf.ln(12)

    # ===== EDUCATION & CERTIFICATIONS =====
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 10, 'Education & Certifications', 0, 1)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + 80, pdf.get_y())
    pdf.ln(4)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(31, 41, 55)

    edu_match = comparison.get('education_match', 'Analyzing...')
    cert_match = comparison.get('certification_match', 'Analyzing...')

    pdf.cell(0, 7, f'Education: {edu_match}', 0, 1)
    pdf.cell(0, 7, f'Certifications: {cert_match}', 0, 1)

    pdf.ln(12)

    # ===== KEYWORDS =====
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 10, 'Keywords Found in Resume', 0, 1)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + 80, pdf.get_y())
    pdf.ln(4)

    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(31, 41, 55)

    kw_density = overall.get('keyword_density', 0)
    pdf.cell(0, 6, f'Keyword Density: {kw_density}%', 0, 1)
    pdf.ln(4)

    keywords = analysis_data.get('matched_keywords_list', [])
    if keywords:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(139, 92, 246)
        pdf.cell(0, 7, 'Detected Keywords:', 0, 1)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(31, 41, 55)
        pdf.multi_cell(0, 6, ', '.join(keywords[:20]))
    else:
        pdf.cell(0, 6, 'No keywords detected', 0, 1)

    pdf.ln(12)

    # ===== RECOMMENDATIONS =====
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 10, 'Recommendations', 0, 1)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + 80, pdf.get_y())
    pdf.ln(4)

    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(31, 41, 55)

    recommendations = []

    if skills_need:
        recommendations.append(f"- Add these missing skills: {', '.join(skills_need[:5])}")
    if missing_verbs:
        recommendations.append(f"- Use these action verbs: {', '.join(missing_verbs[:5])}")
    if missing:
        recommendations.append(f"- Address missing requirements: {', '.join(missing[:3])}")
    if req_match_pct < 60:
        recommendations.append("- Consider reformatting your resume to better highlight relevant experience")
    if kw_density < 40:
        recommendations.append("- Increase keyword density by incorporating more JD terminology")

    if not recommendations:
        recommendations.append("- Your resume is well-aligned! Keep applying.")

    for rec in recommendations:
        pdf.multi_cell(0, 6, rec)

    pdf.ln(10)

    # ===== FOOTER =====
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(156, 163, 175)
    pdf.cell(0, 10, 'Generated by JDAlign - Resume Optimization Tool', 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')


def generate_resume_pdf(resume_text, format_name='modern'):
    """Generate comprehensive A4 resume PDF optimized for JD"""
    return generate_full_resume(resume_text)


def generate_full_resume(resume_text):
    """Generate a full A4 page resume with comprehensive formatting using FPDF"""
    resume_text = sanitize_text(resume_text)

    pdf = ThemePDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    margin = 20
    pdf.set_left_margin(margin)
    pdf.set_right_margin(margin)

    sections = parse_resume_sections(resume_text)

    # === HEADER (Name, Title, Contact) ===
    render_fpdf_header(pdf, sections)
    pdf.ln(8)

    # === PROFESSIONAL SUMMARY ===
    if 'summary' in sections:
        render_fpdf_section(pdf, 'PROFESSIONAL SUMMARY', sections['summary'])
        pdf.ln(4)

    # === TECHNICAL SKILLS ===
    if 'skills' in sections:
        render_fpdf_skills(pdf, sections['skills'])
        pdf.ln(4)

    # === PROFESSIONAL EXPERIENCE ===
    if 'experience' in sections:
        render_fpdf_experience(pdf, sections['experience'])
        pdf.ln(4)

    # === PROJECTS ===
    if 'projects' in sections:
        render_fpdf_section(pdf, 'PROJECTS', sections['projects'])
        pdf.ln(4)

    # === EDUCATION ===
    if 'education' in sections:
        render_fpdf_section(pdf, 'EDUCATION', sections['education'])
        pdf.ln(4)

    # === CERTIFICATIONS & ACHIEVEMENTS ===
    if 'certifications' in sections:
        render_fpdf_section(pdf, 'CERTIFICATIONS', sections['certifications'])

    return pdf.output(dest='S').encode('latin-1')


def render_fpdf_header(pdf, sections):
    """Render header with FPDF"""
    header_text = sections.get('header', '')
    lines = [l.strip() for l in header_text.split('\n') if l.strip()]

    # Name - Bold and larger, centered
    name = lines[0] if lines else 'Your Name'
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(0, 10, name.upper(), 0, 1, 'C')
    pdf.ln(2)

    # Title
    if len(lines) > 1:
        title = lines[1]
        if '@' not in title and '(' not in title:
            pdf.set_font('Helvetica', '', 11)
            pdf.set_text_color(107, 114, 128)
            pdf.cell(0, 6, title, 0, 1, 'C')
            pdf.ln(2)

    # Contact info
    contact_parts = []
    for line in lines[1:]:
        line_clean = line.strip()
        if '@' in line_clean or '(' in line_clean or 'linkedin' in line_clean.lower() or any(c.isdigit() for c in line_clean):
            contact_parts.append(line_clean)

    if contact_parts:
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(107, 114, 128)
        pdf.cell(0, 5, ' | '.join(contact_parts), 0, 1, 'C')

    # Separator line
    pdf.ln(4)
    pdf.set_draw_color(37, 99, 235)
    pdf.set_line_width(0.5)
    pdf.line(margin, pdf.get_y(), pdf.get_x() + 150, pdf.get_y())
    pdf.ln(4)


def render_fpdf_section(pdf, title, content):
    """Render a section with FPDF"""
    # Section title - uppercase, bold, blue
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 7, title, 0, 1)
    pdf.ln(2)

    # Content
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(31, 41, 55)

    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(3)
            continue

        # Clean bullets
        for bullet in ['- ', '* ', '• ', '● ']:
            if line.startswith(bullet):
                line = '  - ' + line[len(bullet):]
                break

        pdf.multi_cell(0, 5, line)
        pdf.ln(1)


def render_fpdf_skills(pdf, content):
    """Render skills with FPDF"""
    # Section title
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 7, 'TECHNICAL SKILLS', 0, 1)
    pdf.ln(2)

    # Parse skills
    lines = content.split('\n')
    all_skills = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        for bullet in ['- ', '* ', '• ', '● ']:
            if line.startswith(bullet):
                line = line[len(bullet):].strip()
                break

        parts = line.replace('•', ',').split(',')
        for part in parts:
            part = part.strip()
            if part:
                all_skills.append(part)

    # Display as comma-separated
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(31, 41, 55)

    if all_skills:
        skill_text = ', '.join(all_skills[:30])
        pdf.multi_cell(0, 5, skill_text)


def render_fpdf_experience(pdf, content):
    """Render experience with FPDF"""
    # Section title
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 7, 'PROFESSIONAL EXPERIENCE', 0, 1)
    pdf.ln(2)

    # Parse experience entries
    lines = content.split('\n')
    jobs = []
    current_job = []
    current_title = ''

    for line in lines:
        line = line.strip()
        if not line:
            if current_title and current_job:
                jobs.append((current_title, current_job))
                current_job = []
                current_title = ''
            continue

        for bullet in ['- ', '* ', '• ', '● ']:
            if line.startswith(bullet):
                line = line[len(bullet):].strip()
                break

        if not current_title and not line.startswith(('-', '*', '•')):
            current_title = line
        else:
            current_job.append(line)

    if current_title and current_job:
        jobs.append((current_title, current_job))

    # Render each job
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(31, 41, 55)

    for i, (title, responsibilities) in enumerate(jobs):
        # Job title - bold
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(31, 41, 55)
        pdf.cell(0, 6, title, 0, 1)

        # Company/dates in grey
        if '(' in title:
            pdf.set_font('Helvetica', '', 9)
            pdf.set_text_color(107, 114, 128)
            pdf.cell(0, 5, title, 0, 1)

        # Responsibilities
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(31, 41, 55)
        for resp in responsibilities:
            if resp:
                pdf.multi_cell(0, 5, '  - ' + resp)

        if i < len(jobs) - 1:
            pdf.ln(2)

def parse_resume_sections(text):
    sections = {}
    lines = text.split('\n')

    section_patterns = {
        'header': [],
        'summary': ['summary', 'objective', 'profile', 'about me'],
        'skills': ['skills', 'technical skills', 'competencies', 'expertise', 'technologies'],
        'experience': ['experience', 'employment', 'work history'],
        'education': ['education', 'academic', 'qualification', 'degree'],
        'projects': ['projects', 'project'],
        'certifications': ['certifications', 'certificates', 'awards', 'credentials'],
    }

    current_section = 'header'
    current_content = []

    for line in lines:
        line_clean = line.strip()
        line_lower = line_clean.lower()

        is_section = False
        matched_section = None

        for section_name, patterns in section_patterns.items():
            if not patterns:
                continue
            for pattern in patterns:
                if pattern in line_lower and len(line_clean) < 60:
                    if ':' in line_clean or line_clean.isupper():
                        is_section = True
                        matched_section = section_name
                        break
            if is_section:
                break

        if is_section:
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = matched_section
            current_content = [line_clean]
        else:
            current_content.append(line_clean)

    if current_content:
        sections[current_section] = '\n'.join(current_content)

    return sections