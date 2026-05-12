// JDAlign Frontend Script

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const resumeInput = document.getElementById('resume-input');
    const jdInput = document.getElementById('jd-input');
    const resumeChars = document.getElementById('resume-chars');
    const jdChars = document.getElementById('jd-chars');
    const analyzeBtn = document.getElementById('analyze-btn');
    const errorMessage = document.getElementById('error-message');
    const resultsSection = document.getElementById('results-section');
    const toast = document.getElementById('toast');

    // Stats
    const statConfidence = document.getElementById('stat-confidence');
    const confidencePath = document.getElementById('confidence-path');
    const scoreMessage = document.getElementById('score-message');

    // Download buttons
    const downloadReportBtn = document.getElementById('download-report-btn');
    const downloadResumeBtn = document.getElementById('download-resume-btn');

    // Comparison elements
    const reqMatch = document.getElementById('req-match');
    const skillsMatch = document.getElementById('skills-match');
    const kwDensity = document.getElementById('kw-density');
    const skillsHave = document.getElementById('skills-have');
    const skillsNeed = document.getElementById('skills-need');
    const experienceInfo = document.getElementById('experience-info');
    const matchedReq = document.getElementById('matched-req');
    const missingReq = document.getElementById('missing-req');
    const verbsHave = document.getElementById('verbs-have');
    const verbsNeed = document.getElementById('verbs-need');
    const eduCertsInfo = document.getElementById('edu-certs-info');
    const keywordsList = document.getElementById('keywords-list');

    // Input type tabs
    const typeTabs = document.querySelectorAll('.type-tab');
    const inputTypes = document.querySelectorAll('.input-type');

    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    const lightIcon = document.querySelector('.light-icon');
    const darkIcon = document.querySelector('.dark-icon');

    // PDF elements
    const pdfUpload = document.getElementById('pdf-upload');
    const pdfPreviewBox = document.getElementById('pdf-preview-box');
    const pdfName = document.getElementById('pdf-name');
    const pdfSize = document.getElementById('pdf-size');
    const changePdfBtn = document.getElementById('change-pdf-btn');
    const removePdfBtn = document.getElementById('remove-pdf-btn');

    let lastAnalysisResult = null;

    // Theme management
    function initTheme() {
        const savedTheme = localStorage.getItem('jdalgin-theme') || 'light';
        applyTheme(savedTheme);
    }

    function applyTheme(theme) {
        if (theme === 'dark') {
            document.body.setAttribute('data-theme', 'dark');
            lightIcon.classList.add('hidden');
            darkIcon.classList.remove('hidden');
        } else {
            document.body.removeAttribute('data-theme');
            lightIcon.classList.remove('hidden');
            darkIcon.classList.add('hidden');
        }
        localStorage.setItem('jdalgin-theme', theme);
    }

    themeToggle.addEventListener('click', () => {
        const currentTheme = document.body.getAttribute('data-theme');
        applyTheme(currentTheme === 'dark' ? 'light' : 'dark');
    });

    // Input type switching
    typeTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const type = tab.dataset.type;
            typeTabs.forEach(t => t.classList.remove('active'));
            inputTypes.forEach(i => i.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(`${type}-input`).classList.add('active');
        });
    });

    // Character count
    resumeInput.addEventListener('input', () => {
        resumeChars.textContent = `${resumeInput.value.length} chars`;
    });
    jdInput.addEventListener('input', () => {
        jdChars.textContent = `${jdInput.value.length} chars`;
    });

    // PDF Upload
    pdfUpload.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handlePdfFile(file);
    });

    changePdfBtn.addEventListener('click', () => pdfUpload.click());
    removePdfBtn.addEventListener('click', () => {
        resumeInput.value = '';
        resumeChars.textContent = '0 chars';
        pdfPreviewBox.classList.add('hidden');
        pdfUpload.value = '';
    });

    async function handlePdfFile(file) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            showError('Please upload a PDF file');
            return;
        }
        if (file.size > 10 * 1024 * 1024) {
            showError('File too large. Maximum size is 10MB');
            return;
        }

        pdfName.textContent = file.name;
        pdfSize.textContent = formatFileSize(file.size);
        pdfPreviewBox.classList.remove('hidden');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload', { method: 'POST', body: formData });
            const data = await response.json();
            if (response.ok && data.success) {
                resumeInput.value = data.text;
                resumeChars.textContent = `${data.text.length} chars`;
                showToast('PDF uploaded successfully!');
            } else {
                showError(data.error || 'Failed to extract text from PDF');
            }
        } catch (err) {
            showError('Error uploading file');
        }
    }

    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    // Analyze button
    analyzeBtn.addEventListener('click', async () => {
        const resume = resumeInput.value.trim();
        const jd = jdInput.value.trim();

        hideError();
        resultsSection.classList.add('hidden');

        if (!resume || !jd) {
            showError('Please enter both resume and job description');
            return;
        }
        if (resume.length < 50) {
            showError('Resume text is too short (minimum 50 characters)');
            return;
        }

        setLoading(true);
        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ resume, jd })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Analysis failed');
            lastAnalysisResult = data;
            displayResults(data);
        } catch (err) {
            showError(err.message);
        } finally {
            setLoading(false);
        }
    });

    // Downloads
    downloadReportBtn.addEventListener('click', async () => {
        if (!lastAnalysisResult) return;
        try {
            const response = await fetch('/download/report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(lastAnalysisResult)
            });
            if (response.ok) {
                const blob = await response.blob();
                downloadBlob(blob, 'jdalgin-analysis-report.pdf');
                showToast('Report downloaded!');
            } else {
                const errData = await response.json();
                showError(errData.error || 'Failed to download report');
            }
        } catch (err) {
            showError('Failed to download report: ' + err.message);
        }
    });

    downloadResumeBtn.addEventListener('click', async () => {
        if (!lastAnalysisResult) {
            showError('Please analyze a resume first');
            return;
        }

        const resumeText = lastAnalysisResult.optimized_resume_text;
        if (!resumeText || resumeText.trim() === '') {
            showError('No optimized resume available. Please analyze first.');
            return;
        }

        try {
            console.log('Downloading resume, text length:', resumeText.length);
            const response = await fetch('/download/resume', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ optimized_resume_text: resumeText })
            });

            console.log('Response status:', response.status);
            console.log('Response type:', response.headers.get('content-type'));

            if (!response.ok) {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const errData = await response.json();
                    showError(errData.error || 'Failed to download resume');
                } else {
                    showError('Server error (status: ' + response.status + ')');
                }
                return;
            }

            const blob = await response.blob();
            if (blob.size === 0) {
                showError('Empty response from server');
                return;
            }

            downloadBlob(blob, 'optimized-resume.pdf');
            showToast('Resume downloaded!');
        } catch (err) {
            console.error('Download error:', err);
            showError('Failed to download resume: ' + err.message);
        }
    });

    function setLoading(loading) {
        analyzeBtn.disabled = loading;
        const btnText = analyzeBtn.querySelector('.btn-text');
        const btnLoader = analyzeBtn.querySelector('.btn-loader');
        if (loading) { btnText.textContent = 'Analyzing...'; btnLoader.classList.remove('hidden'); }
        else { btnText.textContent = 'Analyze & Optimize Resume'; btnLoader.classList.add('hidden'); }
    }

    function showError(msg) { errorMessage.textContent = msg; errorMessage.classList.remove('hidden'); }
    function hideError() { errorMessage.classList.add('hidden'); }

    function displayResults(data) {
        const confidence = data.statistics?.confidence_score || 0;
        statConfidence.textContent = `${confidence}%`;
        confidencePath.setAttribute('stroke-dasharray', `${confidence}, 100`);

        if (confidence >= 80) scoreMessage.textContent = 'Excellent match! Your resume aligns well with this job.';
        else if (confidence >= 60) scoreMessage.textContent = 'Good match. Some areas need improvement.';
        else if (confidence >= 40) scoreMessage.textContent = 'Moderate match. Consider adding more relevant skills.';
        else scoreMessage.textContent = 'Low match. Significant updates needed for this role.';

        const comp = data.comparison || {};
        const overall = comp.overall || {};
        reqMatch.textContent = `${overall.requirements_match_pct || 0}%`;
        skillsMatch.textContent = `${overall.skills_match_pct || 0}%`;
        kwDensity.textContent = `${overall.keyword_density || 0}%`;

        // Skills
        skillsHave.innerHTML = '';
        (comp.skills_have || []).forEach(s => {
            const tag = document.createElement('span');
            tag.className = 'skill-tag have';
            tag.textContent = s;
            skillsHave.appendChild(tag);
        });
        if (!(comp.skills_have || []).length) skillsHave.innerHTML = '<span style="color:var(--text-muted);font-size:12px">No skills detected</span>';

        skillsNeed.innerHTML = '';
        (comp.skills_need || []).forEach(s => {
            const tag = document.createElement('span');
            tag.className = 'skill-tag need';
            tag.textContent = s;
            skillsNeed.appendChild(tag);
        });
        if (!(comp.skills_need || []).length) skillsNeed.innerHTML = '<span style="color:var(--accent-secondary);font-size:12px">All required skills covered!</span>';

        // Experience
        const exp = comp.experience_analysis || {};
        experienceInfo.innerHTML = `
            <p><strong>JD Level:</strong> ${exp.jd_level || 'Not specified'} | <strong>Resume Level:</strong> ${exp.resume_level || 'Not detected'}</p>
            <p><strong>JD Requires:</strong> ${exp.jd_years ? exp.jd_years + '+ years' : 'Not specified'} | <strong>Your Experience:</strong> ${exp.resume_years ? exp.resume_years + '+ years' : 'Not detected'}</p>
            <p><strong>Analysis:</strong> ${exp.verdict || 'Analyzing...'}</p>
        `;

        // Requirements
        matchedReq.innerHTML = '';
        (comp.matched_requirements || []).forEach(r => {
            const item = document.createElement('div');
            item.className = 'req-item';
            item.textContent = r;
            matchedReq.appendChild(item);
        });
        if (!(comp.matched_requirements || []).length) matchedReq.innerHTML = '<span style="color:var(--text-muted);font-size:12px">No direct matches</span>';

        missingReq.innerHTML = '';
        (comp.missing_requirements || []).forEach(r => {
            const item = document.createElement('div');
            item.className = 'req-item';
            item.textContent = r;
            missingReq.appendChild(item);
        });
        if (!(comp.missing_requirements || []).length) missingReq.innerHTML = '<span style="color:var(--accent-secondary);font-size:12px">All requirements covered!</span>';

        // Action Verbs
        verbsHave.innerHTML = '';
        (exp.matched_verbs || []).forEach(v => {
            const tag = document.createElement('span');
            tag.className = 'verb-tag have';
            tag.textContent = v;
            verbsHave.appendChild(tag);
        });
        if (!(exp.matched_verbs || []).length) verbsHave.innerHTML = '<span style="color:var(--text-muted);font-size:12px">No action verbs detected</span>';

        verbsNeed.innerHTML = '';
        (exp.missing_verbs || []).forEach(v => {
            const tag = document.createElement('span');
            tag.className = 'verb-tag need';
            tag.textContent = v;
            verbsNeed.appendChild(tag);
        });
        if (!(exp.missing_verbs || []).length) verbsNeed.innerHTML = '<span style="color:var(--accent-secondary);font-size:12px">All key verbs present</span>';

        // Education & Certs
        eduCertsInfo.innerHTML = `
            <p>${comp.education_match || 'Analyzing...'}</p>
            <p>${comp.certification_match || 'Analyzing...'}</p>
        `;

        // Keywords
        keywordsList.innerHTML = '';
        (data.matched_keywords_list || []).forEach(kw => {
            const tag = document.createElement('span');
            tag.className = 'kw-tag';
            tag.textContent = kw;
            keywordsList.appendChild(tag);
        });
        if (!(data.matched_keywords_list || []).length) keywordsList.innerHTML = '<span style="color:var(--text-muted);font-size:13px">No keywords detected</span>';

        resultsSection.classList.remove('hidden');

        // Enable download buttons after successful analysis
        downloadReportBtn.disabled = false;
        downloadResumeBtn.disabled = false;
    }

    function downloadBlob(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function showToast(msg, isError = false) {
        toast.textContent = msg;
        toast.className = isError ? 'toast error' : 'toast';
        toast.classList.remove('hidden');

        // Add animation
        toast.style.animation = 'slideIn 0.3s ease, slideOut 0.3s ease 2.7s';
        setTimeout(() => toast.classList.add('hidden'), 3000);
    }

    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Enter to analyze
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            analyzeBtn.click();
        }
        // Escape to clear errors
        if (e.key === 'Escape') {
            hideError();
        }
    });

    // Add hover effects to stat minis
    document.querySelectorAll('.stat-mini').forEach(mini => {
        mini.addEventListener('mouseenter', () => {
            mini.style.transform = 'translateY(-4px)';
        });
        mini.addEventListener('mouseleave', () => {
            mini.style.transform = '';
        });
    });

    // Enhanced type tabs with click feedback
    typeTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove animation class and re-add for re-animation
            tab.classList.remove('active');
            setTimeout(() => tab.classList.add('active'), 10);
        });
    });

    // Add scroll reveal animation for results
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe comparison cards
    document.querySelectorAll('.comparison-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.5s ease';
        observer.observe(card);
    });

    // Add loading animation to analyze button
    analyzeBtn.addEventListener('click', () => {
        if (!analyzeBtn.disabled) {
            analyzeBtn.style.transform = 'scale(0.98)';
            setTimeout(() => analyzeBtn.style.transform = '', 200);
        }
    });

    // Tooltip for skill tags
    skillsHave.addEventListener('mouseover', (e) => {
        if (e.target.classList.contains('skill-tag')) {
            e.target.setAttribute('title', 'You have this skill');
        }
    });

    skillsNeed.addEventListener('mouseover', (e) => {
        if (e.target.classList.contains('skill-tag')) {
            e.target.setAttribute('title', 'Add this skill to match JD');
        }
    });

    initTheme();
});