# Sample Resume and Job Description for testing

SAMPLE_RESUME = """Senior Software Engineer

Summary:
Experienced software engineer with 5+ years building scalable web applications.
Led cross-functional teams to deliver high-quality products on time.

Experience:
- Developed REST APIs serving 1M+ daily requests using Python and Flask
- Led team of 4 engineers to deliver e-commerce platform on time
- Reduced deployment time by 40% using CI/CD pipelines with Jenkins
- Implemented microservices architecture using Docker and Kubernetes
- Mentored junior developers and conducted code reviews

Skills:
Python, JavaScript, Flask, Django, React, Docker, Kubernetes, AWS, SQL, Git

Education:
BS Computer Science, University of Tech, 2018"""

SAMPLE_JD = """Senior Software Engineer

Requirements:
- 3+ years experience with Python and REST APIs
- Experience with AWS, Kubernetes, and microservices architecture
- Strong problem-solving and communication skills
- Experience with CI/CD pipelines (Jenkins, GitLab CI)
- Bachelor's degree in Computer Science or related field
- Experience with Agile/Scrum methodology

Preferred:
- Experience with React and modern JavaScript
- Knowledge of database design and SQL
- Experience leading technical teams

Responsibilities:
- Design and implement scalable backend services
- Collaborate with product and design teams
- Mentor junior engineers
- Participate in code reviews and architecture discussions"""

# Run analysis on these samples
if __name__ == '__main__':
    import spacy
    from nlp.analyzer import Analyzer
    from nlp.optimizer import Optimizer

    nlp = spacy.load('en_core_web_sm')
    analyzer = Analyzer(nlp)
    optimizer = Optimizer(nlp, analyzer)

    print("=== JD Analysis ===")
    jd_analysis = analyzer.analyze_jd(SAMPLE_JD)
    print(f"Keywords: {jd_analysis['keywords'][:10]}")
    print(f"Skills: {jd_analysis['skills']}")
    print(f"Experience Level: {jd_analysis['experience_level']}")

    print("\n=== Optimization Result ===")
    result = optimizer.optimize_resume(SAMPLE_RESUME, jd_analysis)
    print(f"Segments: {result['statistics']['total_segments']}")
    print(f"Confidence: {result['statistics']['confidence_score']}%")
    print(f"\nMapping:")
    for original, optimized in result['mapping'].items():
        print(f"\nOriginal: {original[:80]}...")
        print(f"Optimized: {optimized[:80]}...")