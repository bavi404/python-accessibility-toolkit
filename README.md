# Pythonic Accessibility Toolkit

A Python-based accessibility toolkit that automatically scans websites for accessibility issues, flags problems such as missing alt text, poor color contrast, and broken heading structures, and provides actionable suggestions for fixes.

## Why Accessibility Matters

Accessible websites are crucial for users with disabilities including:
- **Visual impairments**: Screen readers, high contrast needs, color blindness
- **Auditory impairments**: Deaf or hard-of-hearing users
- **Cognitive impairments**: Learning disabilities, attention disorders
- **Motor impairments**: Limited mobility, tremors, paralysis

### Common Accessibility Pitfalls
- Missing alt text for images
- Poor color contrast ratios
- Improper heading hierarchy
- Inaccessible forms and navigation
- Non-descriptive link text
- Missing ARIA labels
- Keyboard navigation issues

### Legal and Ethical Implications
- **ADA Compliance**: Americans with Disabilities Act requirements
- **Section 508**: Federal accessibility standards
- **WCAG Guidelines**: Web Content Accessibility Guidelines
- **Inclusive Design**: Ensuring equal access for all users

## Toolkit Overview

The Pythonic Accessibility Toolkit provides an automated solution for developers to detect and fix accessibility issues before they reach production. It integrates seamlessly into development workflows:

- **Local Testing**: Scan during development
- **Pre-deployment Checks**: Validate before going live
- **CI/CD Pipelines**: Automated accessibility testing
- **Lightweight Design**: Python-first with minimal dependencies
- **Actionable Reports**: Clear issue descriptions and fix suggestions

## How It Works

### Technical Stack
- **Python**: Core logic and automation
- **Pyppeteer**: Headless browser control for page rendering
- **WAVE API**: Accessibility evaluation engine
- **BeautifulSoup**: HTML parsing and analysis
- **Requests**: HTTP communication

### Workflow
1. Accept URL(s) for scanning
2. Launch headless browser and render pages
3. Run automated accessibility checks via WAVE API
4. Parse and categorize issues by type and severity
5. Generate comprehensive reports with fix suggestions

## 🌟 Features

### **Python Toolkit**
- **Comprehensive Accessibility Checks**: Alt text, color contrast, heading structure, forms, links, ARIA, landmarks, and keyboard navigation
- **Multiple Output Formats**: HTML, JSON, CSV, and plain text reports
- **Extensible Architecture**: Easy to add custom accessibility checks
- **Async Support**: Efficient concurrent scanning of multiple URLs
- **Professional Reports**: Detailed findings with actionable suggestions
- **Command Line Interface**: Quick scanning from terminal
- **Configuration Management**: YAML-based settings
- **Unit Tests**: Reliable and maintainable code

### **Browser Extension**
- **Real-Time Scanning**: Instant accessibility analysis on any webpage
- **Smart Auto-Fixes**: Temporary improvements for common issues
- **Visual Indicators**: Clear highlighting of accessibility problems
- **User-Friendly Interface**: Intuitive popup with issue categorization
- **Export Functionality**: Generate reports for team review
- **Customizable Settings**: Personalized accessibility experience
- **Cross-Browser Support**: Works on Chrome, Edge, and Firefox
- **Privacy-First Design**: No data collection, local processing only

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/pythonic-accessibility-toolkit.git
cd pythonic-accessibility-toolkit

# Install dependencies
pip install -r requirements.txt

# Set up WAVE API key (optional, for enhanced features)
export WAVE_API_KEY="your_api_key_here"
```

## Quick Start

### **Python Toolkit**

```python
from accessibility_toolkit import AccessibilityScanner

# Initialize scanner
scanner = AccessibilityScanner()

# Scan a single URL
results = scanner.scan_url("https://example.com")

# Scan multiple URLs
urls = ["https://example.com", "https://test.com"]
results = scanner.scan_multiple(urls)

# Generate report
scanner.generate_report(results, output_format="html")
```

### **Browser Extension**

The project also includes a **browser extension** for real-time accessibility scanning:

1. **Install the extension** from the `browser-extension/` folder
2. **Click the extension icon** on any webpage
3. **Scan for issues** with one click
4. **Apply temporary fixes** to improve accessibility
5. **Export reports** for team review

See [Browser Extension Documentation](browser-extension/README.md) for detailed installation and usage instructions.

## Command Line Interface

```bash
# Scan a single URL
python -m accessibility_toolkit scan https://example.com

# Scan multiple URLs from file
python -m accessibility_toolkit scan --urls urls.txt

# Generate HTML report
python -m accessibility_toolkit scan https://example.com --output html

# Custom configuration
python -m accessibility_toolkit scan https://example.com --config config.yaml
```

## Understanding the Reports

Reports include:
- **Issue Type**: Specific accessibility problem identified
- **Severity Level**: Critical, Moderate, or Low priority
- **Location**: Page element and context
- **Suggested Fix**: Step-by-step guidance for developers
- **WCAG Reference**: Relevant accessibility guidelines

### Example Report Structure
```
🚨 Critical Issues (3)
├── Missing alt text for image: logo.png
├── Insufficient color contrast: 2.1:1 (requires 4.5:1)
└── Missing form label: email input

⚠️  Moderate Issues (5)
├── Improper heading hierarchy: H1 → H3
├── Non-descriptive link: "Click here"
└── Missing ARIA label: navigation menu
```

## Customizing the Toolkit

### Adding Custom Checks
```python
from accessibility_toolkit.checks import BaseCheck

class CustomCheck(BaseCheck):
    def check(self, page_content):
        # Your custom accessibility logic
        issues = []
        # ... implementation
        return issues
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Accessibility Check
  run: |
    python -m accessibility_toolkit scan ${{ github.event.inputs.url }}
    python -m accessibility_toolkit generate-report --format html
```

### Configuration Options
- Scan depth and page selection
- Output formats (JSON, CSV, HTML, PDF)
- Custom issue severity thresholds
- Team-specific reporting templates

## Open Source & Community

We welcome contributions from the community! Here's how you can help:

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Getting Help
- **Issues**: Report bugs or request features
- **Discussions**: Join accessibility conversations
- **Documentation**: Help improve guides and examples

### Impact
By contributing to this toolkit, you're helping:
- Make the web more accessible for millions of users
- Educate developers about accessibility best practices
- Create tools that benefit the entire development community
- Ensure equal access to digital content for everyone

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [WAVE Web Accessibility Evaluation Tool](https://wave.webaim.org/)
- [Web Content Accessibility Guidelines (WCAG)](https://www.w3.org/WAI/WCAG21/quickref/)
- The accessibility community for ongoing guidance and feedback

---

**Together, let's build a more accessible web for everyone!** 🌐♿
