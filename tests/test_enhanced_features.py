#!/usr/bin/env python3
"""
Enhanced Features Tests - Comprehensive testing of the latest accessibility toolkit capabilities.
"""

import pytest
from bs4 import BeautifulSoup
from accessibility_toolkit.checks.links import LinkAccessibilityCheck
from accessibility_toolkit.checks.forms import FormAccessibilityCheck
from accessibility_toolkit.utils import deduplicate_issues, filter_visible_elements
from accessibility_toolkit.models import AccessibilityIssue, Severity


class TestEnhancedLinkAccessibility:
    """Test enhanced link accessibility features."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.link_check = LinkAccessibilityCheck(config={
            "check_descriptive_text": True,
            "check_context_awareness": True
        })
    
    def test_vague_link_detection(self):
        """Test detection of various vague link patterns."""
        html = """
        <html>
        <body>
            <a href="/privacy">Click here</a>
            <a href="/terms">Read more</a>
            <a href="/contact">Here</a>
            <a href="/about">More info</a>
            <a href="/services">Learn more</a>
            <a href="/products">View more</a>
            <a href="/help">Find out</a>
            <a href="/support">Discover</a>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        issues = self.link_check.check(soup, "test://example.com")
        
        # Should detect vague links
        assert len(issues) > 0
        
        # Check specific vague patterns
        vague_texts = [issue.description for issue in issues]
        assert any("Click here" in text for text in vague_texts)
        assert any("Read more" in text for text in vague_texts)
        assert any("Here" in text for text in vague_texts)
    
    def test_context_aware_analysis(self):
        """Test context-aware link analysis."""
        html = """
        <html>
        <body>
            <h2>Privacy Policy</h2>
            <p>Read our privacy policy to understand how we protect your data.</p>
            <a href="/privacy">Read more</a>
            
            <h2>Terms of Service</h2>
            <p>Our terms outline the rules for using our service.</p>
            <a href="/terms">Read more</a>
            
            <a href="/contact">Contact us</a>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        issues = self.link_check.check(soup, "test://example.com")
        
        # "Read more" links with context should be flagged
        read_more_issues = [i for i in issues if "Read more" in i.description]
        assert len(read_more_issues) >= 2
    
    def test_enhanced_suggested_fixes(self):
        """Test enhanced suggested fixes for vague links."""
        html = """
        <html>
        <body>
            <a href="/privacy">Click here</a>
            <a href="/terms">Read more</a>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        issues = self.link_check.check(soup, "test://example.com")
        
        for issue in issues:
            assert issue.suggested_fix
            assert len(issue.suggested_fix) > 10  # Should be descriptive


class TestEnhancedFormAccessibility:
    """Test enhanced form accessibility features."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.form_check = FormAccessibilityCheck(config={
            "check_error_handling": True,
            "check_labels": True,
            "check_required_fields": True
        })
    
    def test_error_handling_detection(self):
        """Test detection of form error handling issues."""
        html = """
        <html>
        <body>
            <form>
                <input type="email" name="email" aria-invalid="true" required>
                <div class="error">Invalid email format</div>
                
                <input type="text" name="username" required>
                <div class="error">Username is required</div>
                
                <select name="country" required>
                    <option value="">Select country</option>
                </select>
                
                <button type="submit">Submit</button>
            </form>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        issues = self.form_check.check(soup, "test://example.com")
        
        # Should detect error handling issues
        assert len(issues) > 0
        
        # Check for specific error handling issues
        error_issues = [i for i in issues if "error" in i.issue_type.lower()]
        assert len(error_issues) > 0
    
    def test_required_field_indicators(self):
        """Test detection of missing required field indicators."""
        html = """
        <html>
        <body>
            <form>
                <input type="text" name="username" required>
                <input type="email" name="email" required>
                <select name="country" required>
                    <option value="">Select country</option>
                </select>
            </form>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        issues = self.form_check.check(soup, "test://example.com")
        
        # Should detect missing required field indicators
        required_issues = [i for i in issues if "required" in i.description.lower()]
        assert len(required_issues) > 0
    
    def test_form_label_association(self):
        """Test form label association detection."""
        html = """
        <html>
        <body>
            <form>
                <input type="text" name="username" id="username">
                <label for="username">Username</label>
                
                <input type="email" name="email" id="email">
                <!-- Missing label -->
                
                <input type="password" name="password">
                <!-- No id or label -->
            </form>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        issues = self.form_check.check(soup, "test://example.com")
        
        # Should detect missing labels
        label_issues = [i for i in issues if "label" in i.description.lower()]
        assert len(label_issues) > 0


class TestIssueDeduplication:
    """Test smart issue deduplication features."""
    
    def test_basic_deduplication(self):
        """Test basic issue deduplication."""
        issues = [
            AccessibilityIssue(
                issue_type="missing_alt_text",
                description="Missing alt text for image",
                element="img.logo",
                severity=Severity.CRITICAL,
                suggested_fix="Add descriptive alt text"
            ),
            AccessibilityIssue(
                issue_type="missing_alt_text",
                description="Missing alt text for image",
                element="img.banner",
                severity=Severity.CRITICAL,
                suggested_fix="Add descriptive alt text"
            ),
            AccessibilityIssue(
                issue_type="missing_alt_text",
                description="Missing alt text for image",
                element="img.icon",
                severity=Severity.CRITICAL,
                suggested_fix="Add descriptive alt text"
            )
        ]
        
        deduplicated = deduplicate_issues(issues)
        
        # Should consolidate similar issues
        assert len(deduplicated) < len(issues)
        
        # Should have a count in the description
        consolidated_issue = deduplicated[0]
        assert "3" in consolidated_issue.description or "multiple" in consolidated_issue.description.lower()
    
    def test_different_severity_deduplication(self):
        """Test deduplication with different severities."""
        issues = [
            AccessibilityIssue(
                issue_type="missing_alt_text",
                description="Missing alt text for image",
                element="img.logo",
                severity=Severity.CRITICAL,
                suggested_fix="Add descriptive alt text"
            ),
            AccessibilityIssue(
                issue_type="missing_alt_text",
                description="Missing alt text for image",
                element="img.banner",
                severity=Severity.MODERATE,
                suggested_fix="Add descriptive alt text"
            )
        ]
        
        deduplicated = deduplicate_issues(issues)
        
        # Should not deduplicate different severities
        assert len(deduplicated) == len(issues)
    
    def test_element_signature_deduplication(self):
        """Test deduplication based on element signatures."""
        issues = [
            AccessibilityIssue(
                issue_type="missing_form_label",
                description="Missing label for input field",
                element="input[name='username']",
                severity=Severity.MODERATE,
                suggested_fix="Add label element"
            ),
            AccessibilityIssue(
                issue_type="missing_form_label",
                description="Missing label for input field",
                element="input[name='email']",
                severity=Severity.MODERATE,
                suggested_fix="Add label element"
            )
        ]
        
        deduplicated = deduplicate_issues(issues)
        
        # Should deduplicate similar form label issues
        assert len(deduplicated) < len(issues)


class TestVisibleContentFiltering:
    """Test visible content filtering features."""
    
    def test_basic_visibility_filtering(self):
        """Test basic visibility filtering."""
        html = """
        <html>
        <body>
            <div class="visible">This is visible</div>
            <div class="hidden" style="display: none;">This is hidden</div>
            <div class="invisible" style="visibility: hidden;">This is invisible</div>
            <div class="offscreen" style="position: absolute; left: -9999px;">This is offscreen</div>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        
        visible_elements = filter_visible_elements(soup)
        
        # Should filter out hidden elements
        assert len(visible_elements.find_all()) < len(soup.find_all())
        
        # Should keep visible elements
        visible_div = visible_elements.find(class_="visible")
        assert visible_div is not None
        
        # Should filter hidden elements
        hidden_div = visible_elements.find(class_="hidden")
        assert hidden_div is None
    
    def test_complex_visibility_rules(self):
        """Test complex visibility filtering rules."""
        html = """
        <html>
        <body>
            <div class="parent">
                <div class="child" style="display: none;">Hidden child</div>
                <div class="visible-child">Visible child</div>
            </div>
            <div class="transparent" style="opacity: 0;">Transparent but takes space</div>
            <div class="zero-size" style="width: 0; height: 0;">Zero size element</div>
        </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        
        visible_elements = filter_visible_elements(soup)
        
        # Should handle nested visibility
        parent = visible_elements.find(class_="parent")
        assert parent is not None
        
        # Should filter hidden children
        hidden_child = visible_elements.find(class_="child")
        assert hidden_child is None
        
        # Should keep visible children
        visible_child = visible_elements.find(class_="visible-child")
        assert visible_child is not None


class TestEnhancedReportFeatures:
    """Test enhanced report generation features."""
    
    def test_issue_categorization(self):
        """Test issue categorization for reports."""
        from accessibility_toolkit.reports import ReportGenerator
        
        generator = ReportGenerator()
        
        # Test category mapping
        visual_category = generator._get_issue_category("missing_alt_text")
        assert visual_category == "visual"
        
        auditory_category = generator._get_issue_category("media_accessibility")
        assert auditory_category == "auditory"
        
        cognitive_category = generator._get_issue_category("heading_hierarchy")
        assert cognitive_category == "cognitive"
        
        navigation_category = generator._get_issue_category("keyboard_navigation")
        assert navigation_category == "navigation"
        
        forms_category = generator._get_issue_category("missing_form_labels")
        assert forms_category == "forms"
        
        general_category = generator._get_issue_category("non_descriptive_links")
        assert general_category == "general"
    
    def test_report_generation_with_categories(self):
        """Test report generation includes accessibility categories."""
        from accessibility_toolkit.reports import ReportGenerator
        
        # Create sample scan results
        issues = [
            AccessibilityIssue(
                issue_type="missing_alt_text",
                description="Missing alt text for logo",
                element="img.logo",
                severity=Severity.CRITICAL,
                suggested_fix="Add descriptive alt text"
            ),
            AccessibilityIssue(
                issue_type="non_descriptive_links",
                description="Vague link text: 'Click here'",
                element="a[href='/privacy']",
                severity=Severity.MODERATE,
                suggested_fix="Use descriptive link text"
            )
        ]
        
        # Mock scan result
        class MockScanResult:
            def __init__(self, url, issues):
                self.url = url
                self.issues = issues
                self.status = "completed"
                self.accessibility_score = 85
                self.total_issues = len(issues)
        
        scan_results = [MockScanResult("https://example.com", issues)]
        
        # Generate report
        generator = ReportGenerator()
        html_report = generator.generate_report(scan_results, "html")
        
        # Should include accessibility categories
        assert "Accessibility Categories" in html_report
        assert "Visual Accessibility" in html_report
        assert "Link & Content" in html_report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
