# JDAlign - Resume Optimization Tool

## Project Overview

- **Project Name**: JDAlign
- **Type**: Web Application (Flask + Python)
- **Core Functionality**: Analyze resume against job description, optimize text to match JD keywords while maintaining character constraints (±5%), support multiple input formats, generate PDF reports and themed resumes
- **Target Users**: Job seekers wanting ATS-optimized resume modifications

---

## UI/UX Specification

### Layout Structure

**Single Page Application**
- Header with app branding + theme toggle (light/dark)
- Resume input section with multiple input options (text, PDF, camera)
- Job Description input section
- Theme selector for final resume
- Action button area
- Results section with analysis report + PDF download
- Footer

**Responsive Breakpoints**
- Desktop: Two-column layout (50/50)
- Tablet (< 992px): Stacked columns
- Mobile (< 576px): Full-width stacked

### Visual Design - Light Mode (Default)

**Color Palette - Light Mode**
- Background: `#f8f9fa` (light gray)
- Card Background: `#ffffff` (white)
- Primary Accent: `#2563eb` (bright blue)
- Secondary Accent: `#16a34a` (green for success)
- Warning: `#d97706` (amber)
- Text Primary: `#1f2937` (dark gray)
- Text Secondary: `#6b7280` (muted gray)
- Border: `#e5e7eb`

**Color Palette - Dark Mode**
- Background: `#0d1117` (dark charcoal)
- Card Background: `#161b22` (slate)
- Primary Accent: `#58a6ff` (bright blue)
- Secondary Accent: `#238636` (green)
- Warning: `#d29922` (amber)
- Text Primary: `#c9d1d9` (light gray)
- Text Secondary: `#8b949e` (muted gray)
- Border: `#30363d`

**Typography**
- Font Family: `'JetBrains Mono', 'Fira Code', monospace` for code/output
- Font Family: `'Inter', sans-serif` for UI text
- Heading: 24px bold
- Body: 14px regular
- Code/JSON: 13px monospace

**Components**

1. **Theme Toggle**
   - Pill-shaped toggle button in header
   - Sun icon for light mode, Moon icon for dark mode
   - Smooth transition animation

2. **Resume Input Options**
   - Tab navigation: Text | Upload PDF | Camera
   - Text tab: Large textarea with character count
   - PDF tab: Drag & drop zone with file picker
   - Camera tab: Live camera preview with capture button

3. **Theme Selector**
   - Dropdown with preview thumbnails
   - Themes: Modern Blue, Classic Gray, Executive Black, Minimalist White, Creative Colorful
   - "Keep Original" option to preserve uploaded PDF styling

4. **Analysis Report Panel**
   - Confidence score gauge
   - Matched keywords list
   - Skill gaps identified
   - Optimized resume preview
   - Download as PDF button

5. **PDF Download Button**
   - Generates comprehensive report with:
     - Analysis summary
     - Matched keywords
     - Identified gaps
     - Optimized resume text
   - Uses selected theme styling

---

## Functionality Specification

### Core Features

1. **Multiple Resume Input Methods**
   - Plain text paste
   - PDF file upload (extract text using pdfplumber)
   - Camera capture (use browser getUserMedia, capture as image for OCR or manual review)

2. **Theme System**
   - 5 predefined themes for output PDF
   - "Keep Original" option - extracts text, optimizes, re-applies original PDF styling
   - Theme selection stored in session

3. **Analysis Report**
   - Confidence score (0-100%)
   - Matched keywords count and list
   - Identified skill gaps
   - Before/after text comparison

4. **PDF Generation**
   - Generate analysis report as PDF
   - Generate optimized resume as themed PDF
   - Use FPDF (free, no watermark)

5. **Light/Dark Mode**
   - CSS custom properties for theming
   - Toggle persisted in localStorage
   - Default: Light mode

### User Interactions

1. User selects input method (text/PDF/camera)
2. User uploads/pastes resume
3. User pastes job description
4. User selects output theme
5. User clicks "Analyze & Optimize"
6. System displays analysis report with stats
7. User can download PDF report
8. User can download optimized resume (selected theme)

### Edge Cases

- Empty inputs: Show validation error
- Very short text (< 50 chars): Show warning
- PDF with no extractable text: Show error, suggest camera option
- Camera not available: Hide camera option, show error message
- No common keywords found: Show informational message
- Character overflow detected: Highlight with warning color

---

## Technical Architecture

### Project Structure

```
JDAlign/
├── app.py                 # Flask application
├── requirements.txt       # Dependencies
├── nlp/
│   ├── __init__.py
│   ├── analyzer.py       # Analysis functions
│   ├── optimizer.py      # Text optimization logic
│   └── keywords.py       # Keyword extraction
├── static/
│   ├── style.css         # Styling with CSS variables
│   └── script.js         # Frontend logic
├── templates/
│   └── index.html        # Main HTML template
├── data/
│   └── sample_data.py    # Example data
├── themes/
│   └── __init__.py       # Theme definitions and PDF generation
└── utils/
    ├── __init__.py
    └── pdf_handler.py    # PDF text extraction
```

### Dependencies

- Flask==3.0.0
- pdfplumber (free PDF text extraction)
- fpdf (free PDF generation)

---

## Acceptance Criteria

1. ✅ Flask server runs without errors
2. ✅ Light mode is default, dark mode switchable
3. ✅ Theme toggle button works with smooth transition
4. ✅ Text input with character count
5. ✅ PDF upload extracts text correctly
6. ✅ Camera capture works (where supported)
7. ✅ Analysis report shows confidence, keywords, gaps
8. ✅ PDF report downloadable
9. ✅ Theme selector with 5 themes + Keep Original
10. ✅ Optimized resume downloadable as themed PDF
11. ✅ Character count constraint ±5% enforced
12. ✅ Responsive layout works on mobile/tablet
13. ✅ No external paid services required