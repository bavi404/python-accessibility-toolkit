# 🚀 Quick Start Guide - Accessibility Toolkit

Get up and running with the Accessibility Toolkit in minutes! This guide will walk you through installation, basic usage, and advanced features.

## ⚡ Installation (2 minutes)

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Internet connection for testing

### Install the Toolkit
```bash
# Clone the repository
git clone https://github.com/yourusername/pythonic-accessibility-toolkit.git
cd pythonic-accessibility-toolkit

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright for browser automation
playwright install
```

## 🎯 Your First Scan (1 minute)

### Basic Usage
```python
from accessibility_toolkit import AccessibilityScanner

# Quick scan
async with AccessibilityScanner() as scanner:
    result = await scanner.scan_url("https://example.com")
    print(f"Found {len(result.issues)} accessibility issues")
```

### Command Line
```bash
# Scan a website
python -m accessibility_toolkit scan https://example.com

# Generate HTML report
python -m accessibility_toolkit scan https://example.com --output html
```

## 🌟 Enhanced Features Demo

### Run the Enhanced Demo
```bash
# Showcase all features
python examples/enhanced_features_demo.py

# Basic demo
python demo.py
```

### What You'll See
- **Enhanced Link Detection**: Advanced vague label detection
- **Smart Deduplication**: Consolidated issue reporting
- **Beautiful Reports**: Professional HTML reports with categories
- **Comprehensive Coverage**: 20+ accessibility checks

## 📊 Understanding Reports

### Report Categories
Our enhanced reports organize issues by accessibility category:

- **👁️ Visual**: Alt text, color contrast, focus indicators
- **🔊 Auditory**: Captions, transcripts, media controls  
- **🧠 Cognitive**: Navigation, consistency, reduced motion
- **⌨️ Keyboard**: Focus management, no keyboard traps
- **📝 Forms**: Labels, error handling, validation
- **🔗 Content**: Descriptive text, heading structure

### Sample Report
```
🚨 Critical Issues (2)
├── Missing alt text for logo image
└── Insufficient color contrast: 2.1:1

⚠️  Moderate Issues (3)  
├── Non-descriptive link: "Click here"
├── Missing form label for email input
└── Improper heading hierarchy: H1 → H3
```

## 🔧 Advanced Configuration

### Custom Configuration
```yaml
# config/accessibility_config.yaml
checks:
  links:
    enabled: true
    check_context_awareness: true
    vague_patterns:
      - "click here"
      - "read more"
      - "learn more"

reporting:
  html:
    include_guidance: true
    dark_mode: true
    collapsible_sections: true
```

### Use Custom Config
```python
from accessibility_toolkit import AccessibilityScanner

scanner = AccessibilityScanner(config_file="config/accessibility_config.yaml")
```

## 🌐 Browser Extension

### Install Extension
1. Open `browser-extension/` folder
2. Load unpacked extension in Chrome/Edge
3. Click extension icon on any webpage
4. Scan for accessibility issues instantly

### Features
- **Real-time scanning** on any webpage
- **Auto-fixes** for common issues
- **Floating toolbar** with accessibility controls
- **Export reports** for team review

## 🧪 Testing & Development

### Run Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_models.py
```

### Create Custom Checks
```python
from accessibility_toolkit.checks import BaseCheck

class CustomCheck(BaseCheck):
    def check(self, page_content, url):
        issues = []
        # Your custom logic here
        return issues
```

## 📈 CI/CD Integration

### GitHub Actions
```yaml
- name: Accessibility Check
  run: |
    python -m accessibility_toolkit scan ${{ github.event.inputs.url }}
    python -m accessibility_toolkit generate-report --format html
```

### Jenkins Pipeline
```groovy
stage('Accessibility Test') {
    steps {
        sh 'python -m accessibility_toolkit scan ${WEBSITE_URL}'
        sh 'python -m accessibility_toolkit generate-report --format html'
    }
}
```

## 🎨 Customization Examples

### Custom Report Templates
```python
from accessibility_toolkit import ReportGenerator

generator = ReportGenerator()
generator.custom_template = "my_template.html"
report = generator.generate_report(results, "html")
```

### Filter Specific Issues
```python
# Only critical issues
critical_issues = [issue for issue in result.issues 
                   if issue.severity.value == "critical"]

# Issues by category
visual_issues = [issue for issue in result.issues 
                 if issue.issue_type in ["missing_alt_text", "poor_color_contrast"]]
```

## 🚨 Troubleshooting

### Common Issues

**"No module named 'accessibility_toolkit'"**
```bash
# Make sure you're in the right directory
cd pythonic-accessibility-toolkit
pip install -e .
```

**Browser automation fails**
```bash
# Install Playwright browsers
playwright install

# Or use HTTP-only mode
scanner = AccessibilityScanner(browser_mode="http_only")
```

**Memory issues with large sites**
```yaml
# config/accessibility_config.yaml
performance:
  memory_limit: "1GB"
  max_page_size: "20MB"
```

## 📚 Next Steps

### Learn More
1. **Read the full README.md** for comprehensive documentation
2. **Explore examples/** directory for usage patterns
3. **Check config/** for configuration options
4. **Review tests/** for implementation details

### Get Help
- **Issues**: Report bugs on GitHub
- **Discussions**: Join community conversations
- **Contributing**: Submit pull requests

### Advanced Topics
- **Custom accessibility checks**
- **Report template customization**
- **Performance optimization**
- **Integration with other tools**

---

## 🎉 You're Ready!

You now have a powerful accessibility toolkit that can:
- ✅ Scan any website for accessibility issues
- ✅ Generate professional reports with guidance
- ✅ Detect advanced issues like vague links
- ✅ Provide actionable fixes for developers
- ✅ Integrate into your development workflow

**Start making the web more accessible today!** 🌐♿

---

*Need help? Check the [main README.md](README.md) or open an issue on GitHub.*
