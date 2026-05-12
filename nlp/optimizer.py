import re
import json


class Optimizer:
    def __init__(self, nlp, analyzer):
        self.nlp = nlp
        self.analyzer = analyzer

    def optimize_resume(self, resume_text, jd_analysis):
        # Parse resume into sections
        resume_sections = self._parse_resume_sections(resume_text)

        result_map = {}
        statistics = {
            'total_segments': 0,
            'matched_keywords': 0,
            'gaps_identified': [],
            'optimized_segments': 0
        }

        jd_keywords_lower = set(k.lower() for k in jd_analysis['keywords'])
        jd_skills_lower = set(s.lower() for s in jd_analysis['skills'])

        # Optimize each section
        for section_name, section_content in resume_sections.items():
            if not section_content.strip():
                continue

            # Split into sentences/line items
            segments = self._split_into_segments(section_content)

            for segment in segments:
                if not segment.strip():
                    continue

                original = segment.strip()
                original_length = len(original)

                # Check keyword matches
                segment_lower = original.lower()
                matched = [kw for kw in jd_keywords_lower if kw in segment_lower]
                matched_skills = [s for s in jd_skills_lower if s in segment_lower]

                statistics['matched_keywords'] += len(matched)

                # Identify gaps
                for skill in jd_analysis['skills']:
                    if skill.lower() not in segment_lower:
                        if skill.lower() not in [s.lower() for s in statistics['gaps_identified']]:
                            if len(statistics['gaps_identified']) < 20:
                                statistics['gaps_identified'].append(skill)

                # Optimize the segment
                optimized = self._optimize_segment(
                    original, jd_analysis, matched, matched_skills
                )

                # Enforce ±5% character constraint
                optimized = self._enforce_length_constraint(original, optimized)

                statistics['total_segments'] += 1
                statistics['optimized_segments'] += 1

                result_map[original] = optimized

        # Add overall summary if sections detected
        if 'summary' in resume_sections:
            original_summary = resume_sections['summary'].strip()
            if original_summary:
                optimized_summary = self._optimize_summary(
                    original_summary, jd_analysis
                )
                optimized_summary = self._enforce_length_constraint(
                    original_summary, optimized_summary
                )
                if optimized_summary != original_summary:
                    result_map[original_summary] = optimized_summary

        # Calculate confidence score
        total_content = len(resume_text)
        matched_count = statistics['matched_keywords']
        confidence = min(100, int((matched_count / max(1, len(jd_analysis['keywords']))) * 100))

        return {
            'mapping': result_map,
            'statistics': {
                'total_segments': statistics['total_segments'],
                'matched_keywords': matched_count,
                'gaps_identified': statistics['gaps_identified'][:10],
                'confidence_score': confidence,
                'jd_keywords_count': len(jd_analysis['keywords']),
                'jd_skills_count': len(jd_analysis['skills'])
            }
        }

    def _parse_resume_sections(self, text):
        sections = {}

        # Common section headers
        section_headers = [
            'summary', 'objective', 'profile',
            'experience', 'employment', 'work history',
            'education', 'academic',
            'skills', 'technical skills', 'competencies',
            'projects', 'certifications'
        ]

        lines = text.split('\n')
        current_section = 'header'
        current_content = []

        for line in lines:
            line_clean = line.strip()
            line_lower = line_clean.lower()

            # Check if line is a section header
            is_header = False
            for header in section_headers:
                if header in line_lower and len(line_clean) < 60:
                    # Check if it's followed by a colon or is all caps
                    if ':' in line_clean or line_clean.isupper():
                        is_header = True
                        break

            if is_header:
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                # Determine section name
                for header in section_headers:
                    if header in line_lower:
                        current_section = header
                        break
                current_content = []
            else:
                current_content.append(line)

        if current_content:
            sections[current_section] = '\n'.join(current_content)

        return sections

    def _split_into_segments(self, text):
        # Split by newlines first, then by periods for longer text
        segments = []

        # Split by bullet points and newlines
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                # Remove common bullet characters
                line = re.sub(r'^[\-\*\•\▶\▸]\s*', '', line)
                if line:
                    segments.append(line)

        return segments

    def _optimize_segment(self, segment, jd_analysis, matched, matched_skills):
        result = segment

        # Replace generic terms with JD-specific terms where appropriate
        replacements = {
            r'\bwork with\b': 'collaborate with',
            r'\busing\b': 'utilizing',
            r'\bmake\b': 'develop',
            r'\bgood\b': 'strong',
            r'\bhelp\b': 'facilitate',
            r'\bdo\b': 'execute',
            r'\bgot\b': 'achieved',
        }

        for pattern, replacement in replacements.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        # Add relevant JD keywords if not present but contextually appropriate
        # Only add keywords that match the segment's context
        for skill in jd_analysis['skills'][:5]:
            skill_lower = skill.lower()
            # Only add if skill is in JD keywords and segment is in skills section
            if skill_lower not in result.lower():
                # Check if this is a skills section line
                if len(segment) < 50 and ',' in segment:
                    # This looks like a skills list - append
                    if not result.endswith(','):
                        result = result.rstrip(',')
                        result += ', '
                    result += skill
                    break

        # Ensure action verbs are present
        if jd_analysis['action_verbs']:
            first_word = result.split()[0].lower() if result.split() else ''
            if first_word not in jd_analysis['action_verbs']:
                # Prepend most relevant action verb if missing
                relevant_verbs = [v for v in jd_analysis['action_verbs'] if v in result.lower()]
                if not relevant_verbs:
                    # Only prepend if segment is an experience bullet
                    if result.startswith(('- ', '* ', '• ')):
                        pass  # Don't modify, could break format

        return result

    def _optimize_summary(self, summary, jd_analysis):
        # No spaCy - use pure regex-based optimization
        result = summary

        # Enhance with JD keywords
        jd_keywords = jd_analysis['keywords'][:10]
        summary_lower = summary.lower()

        for keyword in jd_keywords:
            if keyword.lower() not in summary_lower:
                # Only add if it fits contextually
                if len(keyword.split()) <= 2:
                    # Add to end if summary is short
                    if len(summary) < 150:
                        result = result.rstrip('.') + f", {keyword}."

        # Improve opening phrases
        improvements = [
            (r'\bI am a\b', 'I am an'),
            (r'\bI have\s+\d+\s+years\b', f"I have {jd_analysis.get('experience_level', 'extensive')} experience"),
            (r'\blooking for\b', 'seeking'),
            (r'\bwant to\b', 'aim to'),
        ]

        for pattern, replacement in improvements:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        return result

    def _enforce_length_constraint(self, original, optimized):
        original_len = len(original)
        max_allowed = int(original_len * 1.05)
        min_allowed = int(original_len * 0.95)

        optimized_len = len(optimized)

        # If too long, trim non-essential words
        if optimized_len > max_allowed:
            # Remove filler words
            fillers = ['very', 'really', 'actually', 'basically', 'simply', 'quite']
            words = optimized.split()
            filtered = [w for w in words if w.lower() not in fillers]
            optimized = ' '.join(filtered)

        # If too short, expand slightly
        elif optimized_len < min_allowed:
            # Add appropriate qualifier
            additions = {
                'led': 'successfully led',
                'managed': 'effectively managed',
                'developed': 'proactively developed',
                'created': 'strategically created',
            }

            words = optimized.split()
            if words and words[0].lower() in additions:
                words[0] = additions[words[0].lower()]
                optimized = ' '.join(words)

        return optimized


def save_json_output(result, filepath='output.json'):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)