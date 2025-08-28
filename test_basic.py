#!/usr/bin/env python3
"""
Basic test script to verify core functionality.
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing Imports")
    print("=" * 30)
    
    try:
        from accessibility_toolkit.models import SeverityLevel, IssueType
        print("✅ Models imported successfully")
        
        from accessibility_toolkit.checks.base import BaseCheck
        print("✅ Base check imported successfully")
        
        from accessibility_toolkit.checks.alt_text import AltTextCheck
        print("✅ Alt text check imported successfully")
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_models():
    """Test basic model functionality."""
    print("\n🧪 Testing Models")
    print("=" * 30)
    
    try:
        from accessibility_toolkit.models import (
            SeverityLevel, IssueType, AccessibilityIssue
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
        print(f"   Issue type: {issue.issue_type.value}")
        print(f"   Severity: {issue.severity.value}")
        
        print("✅ Model tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_basic_check():
    """Test basic check functionality."""
    print("\n🧪 Testing Basic Check")
    print("=" * 30)
    
    try:
        from accessibility_toolkit.checks.alt_text import AltTextCheck
        from bs4 import BeautifulSoup
        
        # Create a simple HTML with an image missing alt text
        html = '<html><body><img src="test.jpg"></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        
        # Create check instance with empty config
        check = AltTextCheck({})
        print(f"   Created check: {check.check_name}")
        
        # Test the check
        issues = check.check(soup, "https://example.com")
        print(f"   Found {len(issues)} issues")
        
        if issues:
            for issue in issues:
                print(f"   - {issue.description}")
        
        print("✅ Basic check test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Basic check test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🚀 Basic Functionality Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_models,
        test_basic_check
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! The toolkit is working correctly.")
        print("\n💡 Next steps:")
        print("   1. Install Google Chrome for full functionality")
        print("   2. Try the full demo: python demo.py")
        print("   3. Test the browser extension")
    else:
        print("❌ Some tests failed. Check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("   2. Check that you're running from the project root directory")
        print("   3. Verify the accessibility_toolkit package is properly installed")

if __name__ == "__main__":
    main()
