from fpdf import FPDF
from datetime import datetime
from pdfme import PDF
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
    """Generate a full A4 page resume with comprehensive formatting"""
    resume_text = sanitize_text(resume_text)

    # Use smaller margins for more content space
    pdf = PDF(
        page_size='a4',
        margin=40,  # Smaller margin for more space
        font_family='Helvetica',
        font_size=10,  # Smaller base font
        font_color='#1f2937',
        text_align='l',
        line_height=1.4
    )
    pdf.add_page()

    sections = parse_resume_sections(resume_text)

    # === HEADER (Name, Title, Contact) ===
    render_full_header(pdf, sections)
    pdf.text('')  # Space

    # === PROFESSIONAL SUMMARY ===
    if 'summary' in sections:
        render_full_section(pdf, 'PROFESSIONAL SUMMARY', sections['summary'])
        pdf.text('')

    # === TECHNICAL SKILLS ===
    if 'skills' in sections:
        render_full_skills(pdf, sections['skills'])
        pdf.text('')

    # === PROFESSIONAL EXPERIENCE ===
    if 'experience' in sections:
        render_full_experience(pdf, sections['experience'])
        pdf.text('')

    # === PROJECTS ===
    if 'projects' in sections:
        render_full_projects(pdf, sections['projects'])
        pdf.text('')

    # === EDUCATION ===
    if 'education' in sections:
        render_full_education(pdf, sections['education'])
        pdf.text('')

    # === CERTIFICATIONS & ACHIEVEMENTS ===
    if 'certifications' in sections:
        render_full_certifications(pdf, sections['certifications'])

    # Output to bytes
    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()


def render_full_header(pdf, sections):
    """Render full professional header"""
    header_text = sections.get('header', '')
    lines = [l.strip() for l in header_text.split('\n') if l.strip()]

    # Name - Bold and larger
    name = lines[0] if lines else 'Your Name'
    pdf.text({
        '.': name.upper(),
        'b': True,
        's': 14
    }, text_align='c')

    # Title
    if len(lines) > 1:
        title = lines[1]
        if '@' not in title and '(' not in title:
            pdf.text({
                '.': title,
                's': 11
            }, text_align='c')

    # Contact info on one line
    contact_parts = []
    for line in lines[1:]:
        line_clean = line.strip()
        if '@' in line_clean or '(' in line_clean or 'linkedin' in line_clean.lower() or any(c.isdigit() for c in line_clean):
            contact_parts.append(line_clean)

    if contact_parts:
        pdf.text(' | '.join(contact_parts), text_align='c')

    # Separator line
    pdf.text('')
    pdf.text('=' * 80, text_align='c')
    pdf.text('')


def render_full_section(pdf, title, content):
    """Render section with proper formatting"""
    # Section title - uppercase, bold
    pdf.text({
        '.': title,
        'b': True,
        's': 11,
        'c': '#2563eb'
    })

    # Underline
    pdf.text('-' * 60)
    pdf.text('')

    # Content - multiple lines
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            pdf.text('')
            continue

        # Clean bullets
        for bullet in ['- ', '* ', '• ', '● ']:
            if line.startswith(bullet):
                line = '  ' + bullet.strip() + ' ' + line[len(bullet):]
                break

        pdf.text({
            '.': line,
            's': 10
        })


def render_full_skills(pdf, content):
    """Render skills as categorized list"""
    pdf.text({
        '.': 'TECHNICAL SKILLS',
        'b': True,
        's': 11,
        'c': '#2563eb'
    })
    pdf.text('-' * 60)
    pdf.text('')

    # Parse all skills
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

        # Split by comma
        parts = line.replace('•', ',').split(',')
        for part in parts:
            part = part.strip()
            if part:
                all_skills.append(part)

    # Display as multiple columns or wrapped list
    # Group into categories if possible
    if len(all_skills) > 8:
        # Split into two columns
        mid = len(all_skills) // 2
        col1 = all_skills[:mid]
        col2 = all_skills[mid:]

        # Print two columns
        for i in range(max(len(col1), len(col2))):
            left = col1[i] if i < len(col1) else ''
            right = col2[i] if i < len(col2) else ''
            if left or right:
                pdf.text(f'  {left:<35} {right}')
    else:
        # Single column
        for skill in all_skills:
            pdf.text(f'  - {skill}')


def render_full_experience(pdf, content):
    """Render comprehensive experience section"""
    pdf.text({
        '.': 'PROFESSIONAL EXPERIENCE',
        'b': True,
        's': 11,
        'c': '#2563eb'
    })
    pdf.text('-' * 60)
    pdf.text('')

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

        # Clean bullets
        for bullet in ['- ', '* ', '• ', '● ']:
            if line.startswith(bullet):
                line = line[len(bullet):].strip()
                break

        # First non-bullet line is job title
        if not current_title and not line.startswith(('-', '*', '•')):
            current_title = line
        else:
            current_job.append(line)

    if current_title and current_job:
        jobs.append((current_title, current_job))

    # Render each job with proper formatting
    for i, (title, responsibilities) in enumerate(jobs):
        # Parse title and company/date
        if '(' in title:
            parts = title.split('(')
            job_title = parts[0].strip()
            company_date = '(' + parts[1]
        else:
            job_title = title
            company_date = ''

        # Job title - bold
        pdf.text({
            '.': job_title,
            'b': True,
            's': 10
        })

        # Company and dates
        if company_date:
            pdf.text({
                '.': company_date,
                's': 9,
                'c': '#6b7280'
            })

        # Responsibilities as bullet points
        for resp in responsibilities:
            if resp:
                pdf.text(f'  - {resp}')

        # Space between jobs
        if i < len(jobs) - 1:
            pdf.text('')


def render_full_projects(pdf, content):
    """Render projects section"""
    pdf.text({
        '.': 'PROJECTS',
        'b': True,
        's': 11,
        'c': '#2563eb'
    })
    pdf.text('-' * 60)
    pdf.text('')

    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            pdf.text('')
            continue

        # Clean bullets
        for bullet in ['- ', '* ', '• ', '● ']:
            if line.startswith(bullet):
                line = line[len(bullet):].strip()
                break

        # Check if it's a project name (contains hyphen or is a header)
        if ' - ' in line or '–' in line:
            pdf.text({
                '.': line.split(' - ')[0].split('–')[0].strip(),
                'b': True,
                's': 10
            })
            if ' - ' in line:
                desc = line.split(' - ', 1)[1].strip()
                if desc:
                    pdf.text(f'    {desc}')
            elif '–' in line:
                desc = line.split('–', 1)[1].strip()
                if desc:
                    pdf.text(f'    {desc}')
        else:
            pdf.text(f'  - {line}')


def render_full_education(pdf, content):
    """Render education section"""
    pdf.text({
        '.': 'EDUCATION',
        'b': True,
        's': 11,
        'c': '#2563eb'
    })
    pdf.text('-' * 60)
    pdf.text('')

    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            pdf.text('')
            continue

        for bullet in ['- ', '* ', '• ', '● ']:
            if line.startswith(bullet):
                line = line[len(bullet):].strip()
                break

        # Parse degree and school
        if ',' in line:
            parts = line.rsplit(',', 1)
            degree = parts[0].strip()
            school_info = parts[1].strip() if len(parts) > 1 else ''

            pdf.text({
                '.': degree,
                'b': True,
                's': 10
            })
            if school_info:
                pdf.text({
                    '.': school_info,
                    's': 9,
                    'c': '#6b7280'
                })
        else:
            pdf.text(line)


def render_full_certifications(pdf, content):
    """Render certifications section"""
    pdf.text({
        '.': 'CERTIFICATIONS & ACHIEVEMENTS',
        'b': True,
        's': 11,
        'c': '#2563eb'
    })
    pdf.text('-' * 60)
    pdf.text('')

    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            pdf.text('')
            continue

        for bullet in ['- ', '* ', '• ', '● ']:
            if line.startswith(bullet):
                line = line[len(bullet):].strip()
                break

        pdf.text(f'  - {line}')


def render_professional_header(pdf, sections):
    """Render professional header with proper formatting"""
    header_text = sections.get('header', '')
    lines = [l.strip() for l in header_text.split('\n') if l.strip()]

    # Name - Bold, centered
    name = lines[0] if lines else 'Your Name'
    pdf.text(name, text_align='c')

    # Title
    if len(lines) > 1:
        title = lines[1]
        if '@' not in title and '(' not in title:
            pdf.text(title, text_align='c')

    # Contact info
    contact_parts = []
    for line in lines[1:]:
        line_clean = line.strip()
        if '@' in line_clean or '(' in line_clean or 'linkedin' in line_clean.lower():
            contact_parts.append(line_clean)

    if contact_parts:
        pdf.text(' | '.join(contact_parts), text_align='c')

    pdf.text('')
    # Separator line (ASCII)
    pdf.text('-' * 60, text_align='c')
    pdf.text('')


def render_professional_section(pdf, title, content):
    """Render a section with proper formatting"""
    # Section title - Bold
    pdf.text(title, text_align='l')

    # Content
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            pdf.text('')
            continue

        # Clean bullets
        for bullet in ['- ', '* ', '• ', '● ']:
            if line.startswith(bullet):
                line = line[len(bullet):].strip()
                break

        pdf.text(line)

    pdf.text('')


def render_professional_skills(pdf, content):
    """Render skills section with bullet points"""
    pdf.text('SKILLS')
    pdf.text('')

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

    # Display as bullet list
    for skill in all_skills[:25]:
        pdf.text(f'  - {skill}')

    pdf.text('')


def render_professional_experience(pdf, content):
    """Render experience with proper job formatting"""
    pdf.text('PROFESSIONAL EXPERIENCE')
    pdf.text('')

    lines = content.split('\n')
    jobs_html = []
    current_job = []
    current_title = ''

    for line in lines:
        line = line.strip()
        if not line:
            if current_title and current_job:
                jobs_html.append((current_title, current_job))
                current_job = []
                current_title = ''
            continue

        # Clean bullets
        for bullet in ['- ', '* ', '• ', '● ']:
            if line.startswith(bullet):
                line = line[len(bullet):].strip()
                break

        if not current_title and not line.startswith('•'):
            current_title = line
        else:
            current_job.append(line)

    if current_title and current_job:
        jobs_html.append((current_title, current_job))

    # Render jobs
    for title, responsibilities in jobs_html:
        # Parse title and company/dates
        if '(' in title:
            parts = title.split('(')
            job_title = parts[0].strip()
            company_dates = '(' + parts[1]
        else:
            job_title = title
            company_dates = ''

        # Job title bold
        pdf.text(job_title)
        if company_dates:
            pdf.text(company_dates)
        pdf.text('')

        # Responsibilities
        for r in responsibilities:
            pdf.text(f'  - {r}')
        pdf.text('')


def render_professional_education(pdf, content):
    """Render education with proper formatting"""
    pdf.text('EDUCATION')
    pdf.text('')

    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            pdf.text('')
            continue

        for bullet in ['- ', '* ', '• ', '● ']:
            if line.startswith(bullet):
                line = line[len(bullet):].strip()
                break

        # Format: Degree, School, Year
        pdf.text(line)

    pdf.text('')

# The following functions are unused but kept for reference
def _unused_build_resume_html():
    pass
    header_lines = [l.strip() for l in header_text.split('\n') if l.strip()]
    name = header_lines[0] if header_lines else 'Your Name'
    title = header_lines[1] if len(header_lines) > 1 else ''

    # Extract contact info
    contact_parts = []
    for line in header_lines[1:]:
        if '@' in line or '(' in line or 'linkedin' in line.lower():
            contact_parts.append(line.strip())

    # Build sections HTML
    sections_html = ''

    # Professional Summary
    if 'summary' in sections:
        sections_html += build_section_html('PROFESSIONAL SUMMARY', sections['summary'])

    # Skills
    if 'skills' in sections:
        sections_html += build_skills_html(sections['skills'])

    # Professional Experience
    if 'experience' in sections:
        sections_html += build_experience_html(sections['experience'])

    # Projects
    if 'projects' in sections:
        sections_html += build_section_html('PROJECTS', sections['projects'])

    # Education
    if 'education' in sections:
        sections_html += build_education_html(sections['education'])

    # Certifications
    if 'certifications' in sections:
        sections_html += build_section_html('CERTIFICATIONS', sections['certifications'])

    # Complete HTML document
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume</title>
    <style>
        @page {{
            size: A4;
            margin: 40px 50px;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 11px;
            line-height: 1.4;
            color: #1f2937;
            background: white;
        }}

        /* HEADER */
        .header {{
            text-align: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #2563eb;
        }}

        .header .name {{
            font-size: 24px;
            font-weight: bold;
            color: #1f2937;
            letter-spacing: 1px;
            margin-bottom: 4px;
        }}

        .header .title {{
            font-size: 14px;
            color: #6b7280;
            margin-bottom: 8px;
        }}

        .header .contact {{
            font-size: 10px;
            color: #6b7280;
        }}

        .header .contact span {{
            margin: 0 5px;
        }}

        /* SECTION TITLES */
        .section {{
            margin-bottom: 18px;
        }}

        .section-title {{
            font-size: 13px;
            font-weight: bold;
            color: #2563eb;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
            padding-bottom: 4px;
            border-bottom: 1px solid #e5e7eb;
        }}

        /* CONTENT */
        .content {{
            padding-left: 0;
        }}

        .content p {{
            margin-bottom: 4px;
            text-align: justify;
        }}

        /* LISTS */
        ul {{
            list-style: none;
            padding-left: 0;
        }}

        li {{
            margin-bottom: 3px;
            padding-left: 15px;
            position: relative;
        }}

        li::before {{
            content: "•";
            position: absolute;
            left: 0;
            color: #2563eb;
        }}

        /* SKILLS */
        .skills-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .skill-item {{
            background: #f3f4f6;
            padding: 4px 10px;
            border-radius: 3px;
            font-size: 10px;
            color: #374151;
        }}

        /* EXPERIENCE */
        .job {{
            margin-bottom: 12px;
        }}

        .job-header {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 4px;
        }}

        .job-title {{
            font-weight: bold;
            font-size: 11px;
            color: #1f2937;
        }}

        .job-date {{
            font-size: 10px;
            color: #6b7280;
            font-style: italic;
        }}

        .job-company {{
            font-size: 10px;
            color: #6b7280;
            margin-bottom: 4px;
        }}

        .job ul {{
            margin-top: 2px;
        }}

        /* EDUCATION */
        .edu-item {{
            margin-bottom: 8px;
        }}

        .edu-header {{
            display: flex;
            justify-content: space-between;
        }}

        .edu-degree {{
            font-weight: bold;
            font-size: 11px;
        }}

        .edu-date {{
            font-size: 10px;
            color: #6b7280;
        }}

        .edu-school {{
            font-size: 10px;
            color: #6b7280;
        }}

        /* PROJECTS & CERTIFICATIONS */
        .project-item, .cert-item {{
            margin-bottom: 6px;
        }}

        .project-name, .cert-name {{
            font-weight: bold;
            font-size: 11px;
        }}

        .project-desc, .cert-desc {{
            font-size: 10px;
            color: #4b5563;
            padding-left: 15px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="name">{name}</div>
        {f'<div class="title">{title}</div>' if title and '@' not in title else ''}
        {f'<div class="contact">{" <span>|</span> ".join(contact_parts)}</div>' if contact_parts else ''}
    </div>

    {sections_html}
</body>
</html>'''

    return html


def build_section_html(title, content):
    """Build a standard section with title and content"""
    lines = content.split('\n')
    items_html = ''

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Clean bullets
        for bullet in ['- ', '* ', '• ', '● ']:
            if line.startswith(bullet):
                line = '• ' + line[len(bullet):]
                break

        items_html += f'<li>{line}</li>'

    return f'''
    <div class="section">
        <div class="section-title">{title}</div>
        <ul class="content">
            {items_html}
        </ul>
    </div>
    '''


def build_skills_html(content):
    """Build skills section with styled badges"""
    lines = content.split('\n')
    skills = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Clean bullets
        for bullet in ['- ', '* ', '• ', '● ']:
            if line.startswith(bullet):
                line = line[len(bullet):].strip()
                break

        # Split by comma
        parts = line.replace('•', ',').split(',')
        for part in parts:
            part = part.strip()
            if part:
                skills.append(part)

    skills_html = ''.join([f'<span class="skill-item">{s}</span>' for s in skills[:25]])

    return f'''
    <div class="section">
        <div class="section-title">SKILLS</div>
        <div class="skills-list">
            {skills_html}
        </div>
    </div>
    '''


def build_experience_html(content):
    """Build professional experience section with proper job formatting"""
    lines = content.split('\n')
    jobs_html = ''
    current_job = []
    current_title = ''

    for line in lines:
        line = line.strip()
        if not line:
            if current_title and current_job:
                jobs_html += build_job_html(current_title, current_job)
                current_job = []
                current_title = ''
            continue

        # Clean bullets
        for bullet in ['- ', '* ', '• ', '● ']:
            if line.startswith(bullet):
                line = '• ' + line[len(bullet):]
                break

        # Check if it's a job title/company line (likely first non-bullet line)
        if not current_title and not line.startswith('•'):
            current_title = line
        else:
            current_job.append(line)

    # Add last job
    if current_title and current_job:
        jobs_html += build_job_html(current_title, current_job)

    return f'''
    <div class="section">
        <div class="section-title">PROFESSIONAL EXPERIENCE</div>
        {jobs_html}
    </div>
    '''


def build_job_html(title, responsibilities):
    """Build a single job entry"""
    # Parse title and company/dates
    parts = title.split('(')
    job_title = parts[0].strip()
    company_dates = parts[1].replace(')', '').strip() if len(parts) > 1 else ''

    resp_html = ''.join([f'<li>{r}</li>' for r in responsibilities if r])

    return f'''
    <div class="job">
        <div class="job-header">
            <span class="job-title">{job_title}</span>
            <span class="job-date">{company_dates}</span>
        </div>
        <ul class="content">
            {resp_html}
        </ul>
    </div>
    '''


def build_education_html(content):
    """Build education section"""
    lines = content.split('\n')
    edu_items = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Clean bullets
        for bullet in ['- ', '* ', '• ', '● ']:
            if line.startswith(bullet):
                line = line[len(bullet):].strip()
                break

        # Parse degree and school
        if ',' in line:
            parts = line.rsplit(',', 1)
            degree = parts[0].strip()
            school_date = parts[1].strip() if len(parts) > 1 else ''
        else:
            degree = line
            school_date = ''

        edu_items.append(f'''
        <div class="edu-item">
            <div class="edu-header">
                <span class="edu-degree">{degree}</span>
                <span class="edu-date">{school_date}</span>
            </div>
        </div>
        ''')

    return f'''
    <div class="section">
        <div class="section-title">EDUCATION</div>
        {''.join(edu_items)}
    </div>
    '''


def render_header_pdfme(pdf, sections):
    """Render resume header with name, title, and contact info"""
    header_text = sections.get('header', '')
    lines = [l.strip() for l in header_text.split('\n') if l.strip()]

    # Name - centered, bold, larger
    name = lines[0] if lines else 'Your Name'
    pdf.text({
        '.': name,
        'b': True,
        's': 18
    }, text_align='c')
    pdf.text('')

    # Title - centered
    if len(lines) > 1:
        title = lines[1]
        if '@' not in title and '(' not in title:
            pdf.text({
                '.': title,
                's': 12
            }, text_align='c')

    # Contact info - centered
    contact_parts = []
    for line in lines[1:]:
        line_clean = line.strip()
        if '@' in line_clean or '(' in line_clean or 'linkedin' in line_clean.lower():
            contact_parts.append(line_clean)

    if contact_parts:
        pdf.text({
            '.': ' | '.join(contact_parts),
            's': 10
        }, text_align='c')

    pdf.text('')


def render_section_pdfme(pdf, title, content):
    """Render a standard section with title and content"""
    # Section title - bold
    pdf.text({
        '.': title,
        'b': True,
        's': 12
    })

    # Content
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            pdf.text('')
            continue

        # Clean bullets
        for bullet in ['- ', '* ', '• ', '● ']:
            if line.startswith(bullet):
                line = '  - ' + line[len(bullet):]
                break

        pdf.text(line)

    pdf.text('')


def render_skills_pdfme(pdf, content):
    """Render skills as a categorized list"""
    # Section title
    pdf.text({
        '.': 'SKILLS',
        'b': True,
        's': 12
    })
    pdf.text('')

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

    # Display as bullet list
    if all_skills:
        for skill in all_skills[:25]:
            pdf.text('  - ' + skill)

    pdf.text('')


def render_experience_pdfme(pdf, content):
    """Render experience section with proper job formatting"""
    # Section title
    pdf.text({
        '.': 'PROFESSIONAL EXPERIENCE',
        'b': True,
        's': 12
    })
    pdf.text('')

    # Parse experience - group into job entries
    lines = content.split('\n')
    current_job = []
    jobs = []

    for line in lines:
        line = line.strip()
        if not line:
            if current_job:
                jobs.append(current_job)
                current_job = []
        else:
            # Clean bullets
            for bullet in ['- ', '* ', '• ', '● ']:
                if line.startswith(bullet):
                    line = '  - ' + line[len(bullet):]
                    break
            current_job.append(line)

    if current_job:
        jobs.append(current_job)

    # Render each job
    for job_lines in jobs:
        if not job_lines:
            continue

        # First line is usually job title/company
        first_line = job_lines[0]
        pdf.text({
            '.': first_line,
            'b': True,
            's': 11
        })

        # Rest are responsibilities
        for line in job_lines[1:]:
            if line.startswith('  -'):
                pdf.text(line)
            else:
                pdf.text(line)

        pdf.text('')

    pdf.text('')


def render_education_pdfme(pdf, content):
    """Render education section"""
    # Section title
    pdf.text({
        '.': 'EDUCATION',
        'b': True,
        's': 12
    })
    pdf.text('')

    # Content
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            pdf.text('')
            continue

        for bullet in ['- ', '* ', '• ', '● ']:
            if line.startswith(bullet):
                line = line[len(bullet):].strip()
                break

        if is_subheading(line):
            pdf.text({
                '.': line,
                'b': True,
                's': 11
            })
        else:
            pdf.text(line)

    pdf.text('')


def render_header(pdf, sections):
    """Render resume header with name, title, and contact info"""
    header_text = sections.get('header', '')

    # Extract name (first line)
    lines = [l.strip() for l in header_text.split('\n') if l.strip()]
    name = lines[0] if lines else 'Your Name'

    pdf.set_font('Helvetica', 'B', 24)
    pdf.set_text_color(31, 41, 55)
    pdf.cell(0, 14, name, 0, 1, 'C')

    # Extract title (usually second line, not an email/phone)
    if len(lines) > 1:
        title = lines[1]
        if '@' not in title and '(' not in title:
            pdf.set_font('Helvetica', '', 14)
            pdf.set_text_color(107, 114, 128)
            pdf.cell(0, 8, title, 0, 1, 'C')

    # Collect contact info (email, phone, location, LinkedIn)
    contact_parts = []
    for line in lines[1:]:
        line_clean = line.strip()
        if '@' in line_clean or '(' in line_clean or 'linkedin' in line_clean.lower():
            contact_parts.append(line_clean)

    if contact_parts:
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(107, 114, 128)
        pdf.cell(0, 6, ' | '.join(contact_parts), 0, 1, 'C')


def render_standard_section(pdf, title, content):
    """Render a standard section with title and content"""
    margin = pdf.l_margin
    # Section title with line
    pdf.set_draw_color(37, 99, 235)
    pdf.set_line_width(0.5)
    y = pdf.get_y()
    pdf.line(margin, y, margin + 60, y)
    pdf.ln(3)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 7, title, 0, 1)
    pdf.ln(2)

    # Content
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(31, 41, 55)

    for line in content.split('\n'):
        line = line.strip()
        if not line:
            pdf.ln(3)
            continue

        # Clean bullets
        for bullet in ['- ', '* ', '• ', '● ']:
            if line.startswith(bullet):
                line = '  - ' + line[len(bullet):]
                break

        # Check if it's a subheading (company name or date)
        if is_subheading(line):
            pdf.ln(2)
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(31, 41, 55)
            pdf.multi_cell(0, 6, line)
            pdf.set_font('Helvetica', '', 10)
        else:
            pdf.multi_cell(0, 5, line)
        pdf.ln(1)


def render_skills_section(pdf, content):
    """Render skills as a clean categorized list"""
    margin = pdf.l_margin
    pdf.set_draw_color(37, 99, 235)
    pdf.set_line_width(0.5)
    y = pdf.get_y()
    pdf.line(margin, y, margin + 60, y)
    pdf.ln(3)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 7, 'SKILLS', 0, 1)
    pdf.ln(2)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(31, 41, 55)

    # Parse skills - try to categorize or show as comma-separated
    lines = content.split('\n')
    all_skills = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Remove bullets
        for bullet in ['- ', '* ', '• ', '● ']:
            if line.startswith(bullet):
                line = line[len(bullet):].strip()
                break

        # Split by comma or new bullets
        parts = line.replace('•', ',').replace('•', ',').split(',')
        for part in parts:
            part = part.strip()
            if part:
                all_skills.append(part)

    # Display as wrapped line
    if all_skills:
        skill_text = ' - '.join(all_skills[:30])  # Limit to 30 skills
        pdf.multi_cell(0, 5, skill_text)


def render_experience_section(pdf, content):
    """Render experience with job entries"""
    margin = pdf.l_margin
    pdf.set_draw_color(37, 99, 235)
    pdf.set_line_width(0.5)
    y = pdf.get_y()
    pdf.line(margin, y, margin + 60, y)
    pdf.ln(3)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 7, 'EXPERIENCE', 0, 1)
    pdf.ln(2)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(31, 41, 55)

    # Split into job entries
    entries = split_into_entries(content)

    for entry in entries:
        parse_and_render_job(pdf, entry)
        pdf.ln(4)


def render_education_section(pdf, content):
    """Render education section"""
    margin = pdf.l_margin
    pdf.set_draw_color(37, 99, 235)
    pdf.set_line_width(0.5)
    y = pdf.get_y()
    pdf.line(margin, y, margin + 60, y)
    pdf.ln(3)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 7, 'EDUCATION', 0, 1)
    pdf.ln(2)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(31, 41, 55)

    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(2)
            continue
        # Clean bullets
        for bullet in ['- ', '* ', '• ', '● ']:
            if line.startswith(bullet):
                line = line[len(bullet):].strip()
                break

        if is_subheading(line):
            pdf.set_font('Helvetica', 'B', 10)
            pdf.multi_cell(0, 6, line)
            pdf.set_font('Helvetica', '', 10)
        else:
            pdf.multi_cell(0, 5, line)
        pdf.ln(1)


def is_subheading(text):
    """Check if a line looks like a subheading (company, date, degree)"""
    text_lower = text.lower()

    # Check for date patterns
    date_patterns = ['201', '202', '201', 'present', 'current', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    if any(p in text_lower for p in date_patterns) and ('-' in text or '–' in text):
        return True

    # Check for company or school
    if any(k in text_lower for k in ['inc', 'llc', 'corp', 'company', 'tech', 'solutions', 'systems', 'university', 'college', 'institute', 'school']):
        return True

    return len(text) < 60 and not text.startswith('•')


def split_into_entries(text):
    """Split content into separate job entries"""
    entries = []
    current_entry = []

    lines = text.split('\n')
    for line in lines:
        line = line.strip()

        # New entry might start with a company name or date
        if is_subheading(line) and len(current_entry) > 2:
            entries.append('\n'.join(current_entry))
            current_entry = [line]
        else:
            current_entry.append(line)

    if current_entry:
        entries.append('\n'.join(current_entry))

    return entries if entries else [text]


def parse_and_render_job(pdf, entry_text):
    """Parse and render a single job entry"""
    lines = entry_text.split('\n')
    first_line = True

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

        if first_line and is_subheading(line):
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(31, 41, 55)
            pdf.multi_cell(0, 6, line)
            pdf.set_font('Helvetica', '', 10)
            first_line = False
        else:
            pdf.multi_cell(0, 5, line)
        pdf.ln(1)


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