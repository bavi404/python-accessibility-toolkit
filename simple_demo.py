#!/usr/bin/env python3
"""
Simple demo script for testing basic accessibility functionality.
This version doesn't require the headless browser, so it's perfect for testing
the core accessibility checks.
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from accessibility_toolkit.checks import (
    AltTextCheck, HeadingHierarchyCheck, ColorContrastCheck,
    FormAccessibilityCheck, LinkAccessibilityCheck, AriaCheck,
    LandmarkCheck, KeyboardNavigationCheck
)
from bs4 import BeautifulSoup

# Test HTML content with various accessibility issues
TEST_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Test Page</title>
</head>
<body>
    <h1>Main Heading</h1>
    
    <!-- Missing alt text -->
    <img src="logo.png">
    <img src="banner.jpg">
    
    <!-- Poor heading hierarchy -->
    <h1>Another H1</h1>
    <h4>Skipped H3</h4>
    
    <!-- Form without labels -->
    <form>
        <input type="text" placeholder="Name">
        <input type="email" placeholder="Email">
        <button type="submit">Submit</button>
    </form>
    
    <!-- Non-descriptive links -->
    <a href="/page1">Click here</a>
    <a href="/page2">More</a>
    
    <!-- Invalid ARIA -->
    <div role="invalid-role">Invalid role</div>
    <button aria-label="">Empty label</button>
    
    <!-- Missing landmarks -->
    <div>Content without semantic structure</div>
    
    <!-- Keyboard navigation issues -->
    <div onclick="alert('clicked')">No keyboard support</div>
</body>
</html>
"""

async def test_individual_checks():
    """Test each accessibility check individually."""
    print("🧪 Testing Individual Accessibility Checks")
    print("=" * 50)
    
    # Parse HTML to BeautifulSoup
    soup = BeautifulSoup(TEST_HTML, 'html.parser')
    test_url = "https://example.com"
    
    # Test Alt Text Check
    print("\n🔍 Testing Alt Text Check...")
    alt_check = AltTextCheck({})
    alt_issues = alt_check.check(soup, test_url)
    print(f"   Found {len(alt_issues)} alt text issues")
    for issue in alt_issues:
        print(f"   - {issue.description}")
    
    # Test Heading Hierarchy Check
    print("\n🔍 Testing Heading Hierarchy Check...")
    heading_check = HeadingHierarchyCheck({})
    heading_issues = heading_check.check(soup, test_url)
    print(f"   Found {len(heading_issues)} heading issues")
    for issue in heading_issues:
        print(f"   - {issue.description}")
    
    # Test Form Accessibility Check
    print("\n🔍 Testing Form Accessibility Check...")
    form_check = FormAccessibilityCheck({})
    form_issues = form_check.check(soup, test_url)
    print(f"   Found {len(form_issues)} form issues")
    for issue in form_issues:
        print(f"   - {issue.description}")
    
    # Test Link Accessibility Check
    print("\n🔍 Testing Link Accessibility Check...")
    link_check = LinkAccessibilityCheck({})
    link_issues = link_check.check(soup, test_url)
    print(f"   Found {len(link_issues)} link issues")
    for issue in link_issues:
        print(f"   - {issue.description}")
    
    # Test ARIA Check
    print("\n🔍 Testing ARIA Check...")
    aria_check = AriaCheck({})
    aria_issues = aria_check.check(soup, test_url)
    print(f"   Found {len(aria_issues)} ARIA issues")
    for issue in aria_issues:
        print(f"   - {issue.description}")
    
    # Test Landmark Check
    print("\n🔍 Testing Landmark Check...")
    landmark_check = LandmarkCheck({})
    landmark_issues = landmark_check.check(soup, test_url)
    print(f"   Found {len(landmark_issues)} landmark issues")
    for issue in landmark_issues:
        print(f"   - {issue.description}")
    
    # Test Keyboard Navigation Check
    print("\n🔍 Testing Keyboard Navigation Check...")
    keyboard_check = KeyboardNavigationCheck({})
    keyboard_issues = keyboard_check.check(soup, test_url)
    print(f"   Found {len(keyboard_issues)} keyboard navigation issues")
    for issue in keyboard_issues:
        print(f"   - {issue.description}")

async def test_with_real_html_file():
    """Test with the actual test HTML file."""
    print("\n🧪 Testing with Real HTML File")
    print("=" * 50)
    
    test_file = Path("browser-extension/test-page.html")
    if test_file.exists():
        print(f"📄 Reading test file: {test_file}")
        content = test_file.read_text(encoding='utf-8')
        
        # Test all checks
        soup = BeautifulSoup(content, 'html.parser')
        test_url = "file://test-page.html"
        
        checks = [
            AltTextCheck({}),
            HeadingHierarchyCheck({}),
            FormAccessibilityCheck({}),
            LinkAccessibilityCheck({}),
            AriaCheck({}),
            LandmarkCheck({}),
            KeyboardNavigationCheck({})
        ]
        
        total_issues = 0
        for check in checks:
            issues = check.check(soup, test_url)
            total_issues += len(issues)
            print(f"   {check.check_name}: {len(issues)} issues")
        
        print(f"\n📊 Total issues found: {total_issues}")
        
    else:
        print("❌ Test HTML file not found. Run this from the project root directory.")

def test_models():
    """Test the data models."""
    print("\n🧪 Testing Data Models")
    print("=" * 50)
    
    try:
        from accessibility_toolkit.models import (
            SeverityLevel, IssueType, AccessibilityIssue, ScanResult
        )
        
        # Test enum values
        print(f"   Severity levels: {[level.value for level in SeverityLevel]}")
        print(f"   Issue types: {[issue_type.value for issue_type in IssueType]}")
        
        # Test creating an issue
        issue = AccessibilityIssue(
            issue_type=IssueType.MISSING_ALT_TEXT,
            severity=SeverityLevel.CRITICAL,
            description="Test issue",
            element="<img src='test.jpg'>",
            context="test context",
            suggested_fix="Add alt text"
        )
        print(f"   Created issue: {issue.description}")
        
        # Test creating a scan result
        result = ScanResult(
            url="https://example.com",
            timestamp=None,
            status="completed",
            issues=[issue]
        )
        print(f"   Created scan result with {len(result.issues)} issues")
        print(f"   Accessibility score: {result.accessibility_score}")
        
        print("✅ All model tests passed!")
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")

async def main():
    """Main demo function."""
    print("🚀 Accessibility Toolkit - Simple Demo")
    print("=" * 50)
    print("This demo tests the core functionality without requiring a headless browser.")
    print()
    
    try:
        # Test data models first
        test_models()
        
        # Test individual checks
        await test_individual_checks()
        
        # Test with real HTML file
        await test_with_real_html_file()
        
        print("\n🎉 Demo completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Install Google Chrome if you haven't already")
        print("   2. Try the full demo: python demo.py")
        print("   3. Test the browser extension")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("   2. Check that you're running from the project root directory")
        print("   3. Verify the accessibility_toolkit package is properly installed")

if __name__ == "__main__":
    asyncio.run(main())
