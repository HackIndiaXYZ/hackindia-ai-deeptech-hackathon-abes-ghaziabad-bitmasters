import re
from collections import Counter


class Analyzer:
    """Keyword-based resume/JD analyzer - no spaCy dependency"""

    def __init__(self, nlp=None):
        # nlp parameter kept for compatibility but not used
        self.tech_keywords = self._load_tech_keywords()
        self.action_verbs = self._load_action_verbs()
        self.cert_patterns = self._load_cert_patterns()

    def _load_tech_keywords(self):
        return {
            'programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#',
                           'go', 'golang', 'rust', 'ruby', 'php', 'swift', 'kotlin'],
            'frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'spring',
                         'express', 'next.js', 'node.js', 'node', 'rails', '.net'],
            'cloud': ['aws', 'azure', 'gcp', 'google cloud', 'heroku', 'ec2', 's3'],
            'devops': ['docker', 'kubernetes', 'k8s', 'jenkins', 'terraform', 'ansible',
                      'ci/cd', 'git', 'gitlab', 'jira'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
                         'oracle', 'sqlite', 'cassandra', 'dynamodb'],
            'data': ['machine learning', 'ml', 'ai', 'tensorflow', 'pytorch', 'pandas',
                    'numpy', 'analytics', 'etl', 'data pipeline']
        }

    def _load_action_verbs(self):
        return ['managed', 'led', 'developed', 'created', 'designed', 'implemented',
                'optimized', 'improved', 'increased', 'reduced', 'automated', 'integrated',
                'built', 'launched', 'delivered', 'spearheaded', 'executed', 'coordinated',
                'analyzed', 'generated', 'monitored', 'maintained', 'trained', 'mentored',
                'collaborated', 'facilitated', 'orchestrated', 'engineered']

    def _load_cert_patterns(self):
        return [
            r'(?:aws|azure|gcp)\s+(?:certified|certification)',
            r'\b(pmp|cissp|cism|comptia)\b',
            r'scrum\s*master',
            r'certified\s+(?:software|cloud|security|data)'
        ]

    def analyze_jd(self, jd_text):
        text_lower = jd_text.lower()

        keywords = self._extract_keywords(jd_text)
        skills = self._extract_skills(text_lower)
        certifications = self._extract_certifications(text_lower)
        action_verbs = self._find_action_verbs(text_lower)
        experience_level = self._detect_experience_level(text_lower)

        return {
            'keywords': keywords,
            'skills': skills,
            'certifications': certifications,
            'action_verbs': action_verbs,
            'experience_level': experience_level,
            'jd_text': jd_text
        }

    def _extract_keywords(self, text):
        keywords = set()

        # Extract capitalized multi-word phrases (likely technical terms)
        pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b'
        matches = re.findall(pattern, text)
        keywords.update(matches)

        # Extract technical terms
        for category, terms in self.tech_keywords.items():
            for term in terms:
                if term in text.lower():
                    keywords.add(term)

        # Extract skill-like patterns
        skill_pattern = r'\b(?:proficient|experienced|skilled|knowledge)\s+(?:in|with)\s+([A-Za-z\s,]+?)(?:\.|,|\s+and)'
        matches = re.findall(skill_pattern, text, re.IGNORECASE)
        for match in matches:
            keywords.update([w.strip() for w in match.split(',')])

        # Extract bullet point items (likely requirements)
        bullet_pattern = r'^\s*[-•\*]\s*([^:\n]+)'
        matches = re.findall(bullet_pattern, text, re.MULTILINE)
        for match in matches:
            words = match.strip().split()
            if 1 < len(words) < 5:
                keywords.add(match.strip())

        return list(keywords)[:50]

    def _extract_skills(self, text):
        skills = []

        for category, terms in self.tech_keywords.items():
            for term in terms:
                if term in text:
                    skills.append(term)

        # Extract "X+ years" patterns
        exp_pattern = r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|exp)'
        matches = re.findall(exp_pattern, text, re.IGNORECASE)

        return list(set(skills))[:30]

    def _extract_certifications(self, text):
        certifications = []

        for pattern in self.cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            certifications.extend(matches)

        return list(set(certifications))[:10]

    def _find_action_verbs(self, text):
        found = []
        for verb in self.action_verbs:
            if verb in text:
                found.append(verb)
        return list(set(found))

    def _detect_experience_level(self, text):
        senior_indicators = ['senior', 'sr', 'lead', 'principal', 'staff', 'expert',
                           '5+', '6+', '7+', '8+', '10+']
        junior_indicators = ['junior', 'jr', 'entry', 'intern', 'graduate', '0-2', '1-3']

        if any(ind in text for ind in senior_indicators):
            return 'senior'
        elif any(ind in text for ind in junior_indicators):
            return 'junior'
        return 'mid'

    def analyze_resume(self, resume_text):
        text_lower = resume_text.lower()

        sections = self._extract_sections(resume_text)
        verbs = self._find_action_verbs(text_lower)
        metrics = self._extract_metrics(resume_text)

        return {
            'sections': sections,
            'action_verbs': verbs,
            'metrics': metrics
        }

    def _extract_sections(self, text):
        sections = {}
        lines = text.split('\n')

        section_patterns = {
            'summary': ['summary', 'objective', 'profile', 'about'],
            'experience': ['experience', 'employment', 'work history', 'professional experience'],
            'education': ['education', 'academic', 'qualification'],
            'skills': ['skills', 'technical skills', 'competencies', 'expertise'],
        }

        current_section = 'header'
        current_content = []

        for line in lines:
            line_lower = line.lower().strip()

            matched_section = None
            for section, patterns in section_patterns.items():
                if any(p in line_lower for p in patterns) and len(line) < 50:
                    matched_section = section
                    break

            if matched_section:
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = matched_section
                current_content = []
            else:
                current_content.append(line)

        if current_content:
            sections[current_section] = '\n'.join(current_content)

        return sections

    def _extract_metrics(self, text):
        metrics = []

        # Find percentages
        percent_pattern = r'\b(\d+(?:\.\d+)?%)\b'
        metrics.extend(re.findall(percent_pattern, text))

        # Find numbers with context
        number_pattern = r'\b(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:million|billion|percent|users|customers|requests|servers|nodes)\b'
        metrics.extend(re.findall(number_pattern, text, re.IGNORECASE))

        return metrics[:10]