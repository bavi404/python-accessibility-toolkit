"""
Unit tests for the accessibility toolkit models.
"""

import pytest
from datetime import datetime
from accessibility_toolkit.models import (
    SeverityLevel, IssueType, AccessibilityIssue, 
    ScanResult, ScanSummary
)


class TestSeverityLevel:
    """Test SeverityLevel enum."""
    
    def test_severity_levels(self):
        """Test that all severity levels are defined."""
        assert SeverityLevel.CRITICAL == "critical"
        assert SeverityLevel.MODERATE == "moderate"
        assert SeverityLevel.LOW == "low"
    
    def test_severity_values(self):
        """Test severity level values."""
        levels = [level.value for level in SeverityLevel]
        assert "critical" in levels
        assert "moderate" in levels
        assert "low" in levels


class TestIssueType:
    """Test IssueType enum."""
    
    def test_issue_types(self):
        """Test that all issue types are defined."""
        expected_types = [
            "missing_alt_text", "poor_color_contrast", "improper_heading_hierarchy",
            "missing_form_labels", "non_descriptive_links", "missing_aria_labels",
            "keyboard_navigation", "missing_landmarks", "inaccessible_forms",
            "missing_skip_links", "other"
        ]
        
        for expected_type in expected_types:
            assert hasattr(IssueType, expected_type.upper())


class TestAccessibilityIssue:
    """Test AccessibilityIssue class."""
    
    def test_create_issue(self):
        """Test creating a basic accessibility issue."""
        issue = AccessibilityIssue(
            issue_type=IssueType.MISSING_ALT_TEXT,
            severity=SeverityLevel.CRITICAL,
            description="Image missing alt text",
            element="<img src='test.jpg'>",
            context="Main content area"
        )
        
        assert issue.issue_type == IssueType.MISSING_ALT_TEXT
        assert issue.severity == SeverityLevel.CRITICAL
        assert issue.description == "Image missing alt text"
        assert issue.element == "<img src='test.jpg'>"
        assert issue.context == "Main content area"
        assert issue.line_number is None
        assert issue.column_number is None
        assert issue.suggested_fix == ""
        assert issue.wcag_criteria == []
        assert issue.additional_info == {}
    
    def test_create_issue_with_all_fields(self):
        """Test creating an issue with all fields populated."""
        issue = AccessibilityIssue(
            issue_type=IssueType.POOR_COLOR_CONTRAST,
            severity=SeverityLevel.MODERATE,
            description="Insufficient color contrast",
            element="<p style='color: #666;'>",
            context="Article text",
            line_number=42,
            column_number=15,
            suggested_fix="Increase contrast ratio to 4.5:1",
            wcag_criteria=["1.4.3"],
            additional_info={"current_ratio": 2.1, "required_ratio": 4.5}
        )
        
        assert issue.line_number == 42
        assert issue.column_number == 15
        assert issue.suggested_fix == "Increase contrast ratio to 4.5:1"
        assert issue.wcag_criteria == ["1.4.3"]
        assert issue.additional_info["current_ratio"] == 2.1
    
    def test_issue_validation(self):
        """Test that issues validate required fields."""
        with pytest.raises(ValueError, match="Issue description cannot be empty"):
            AccessibilityIssue(
                issue_type=IssueType.MISSING_ALT_TEXT,
                severity=SeverityLevel.CRITICAL,
                description="",
                element="<img>",
                context="Test"
            )
        
        with pytest.raises(ValueError, match="Element information cannot be empty"):
            AccessibilityIssue(
                issue_type=IssueType.MISSING_ALT_TEXT,
                severity=SeverityLevel.CRITICAL,
                description="Test issue",
                element="",
                context="Test"
            )
    
    def test_issue_to_dict(self):
        """Test converting issue to dictionary."""
        issue = AccessibilityIssue(
            issue_type=IssueType.MISSING_ALT_TEXT,
            severity=SeverityLevel.CRITICAL,
            description="Test issue",
            element="<img>",
            context="Test context"
        )
        
        issue_dict = issue.to_dict()
        
        assert issue_dict["issue_type"] == "missing_alt_text"
        assert issue_dict["severity"] == "critical"
        assert issue_dict["description"] == "Test issue"
        assert issue_dict["element"] == "<img>"
        assert issue_dict["context"] == "Test context"
    
    def test_issue_string_representation(self):
        """Test string representation of issue."""
        issue = AccessibilityIssue(
            issue_type=IssueType.MISSING_ALT_TEXT,
            severity=SeverityLevel.CRITICAL,
            description="Test issue",
            element="<img>",
            context="Test context"
        )
        
        issue_str = str(issue)
        assert "[CRITICAL]" in issue_str
        assert "missing_alt_text" in issue_str
        assert "Test issue" in issue_str


class TestScanResult:
    """Test ScanResult class."""
    
    def test_create_scan_result(self):
        """Test creating a basic scan result."""
        result = ScanResult(
            url="https://example.com",
            timestamp=datetime.now(),
            issues=[],
            page_title="Example Page",
            page_description="A test page",
            scan_duration=1.5,
            status="completed"
        )
        
        assert result.url == "https://example.com"
        assert result.page_title == "Example Page"
        assert result.page_description == "A test page"
        assert result.scan_duration == 1.5
        assert result.status == "completed"
        assert result.total_issues == 0
        assert result.accessibility_score == 100.0
    
    def test_scan_result_with_issues(self):
        """Test scan result with accessibility issues."""
        issues = [
            AccessibilityIssue(
                issue_type=IssueType.MISSING_ALT_TEXT,
                severity=SeverityLevel.CRITICAL,
                description="Missing alt text",
                element="<img>",
                context="Test"
            ),
            AccessibilityIssue(
                issue_type=IssueType.POOR_COLOR_CONTRAST,
                severity=SeverityLevel.MODERATE,
                description="Poor contrast",
                element="<p>",
                context="Test"
            )
        ]
        
        result = ScanResult(
            url="https://example.com",
            timestamp=datetime.now(),
            issues=issues,
            page_title="Test Page",
            scan_duration=2.0,
            status="completed"
        )
        
        assert result.total_issues == 2
        assert result.critical_issues_count == 1
        assert result.moderate_issues_count == 1
        assert result.low_issues_count == 0
        assert result.accessibility_score < 100.0
    
    def test_scan_result_properties(self):
        """Test computed properties of scan result."""
        result = ScanResult(
            url="https://example.com",
            timestamp=datetime.now(),
            issues=[],
            page_title="Test Page"
        )
        
        assert result.domain == "example.com"
        assert result.total_issues == 0
        assert result.accessibility_score == 100.0
    
    def test_scan_result_filtering(self):
        """Test filtering issues by severity and type."""
        issues = [
            AccessibilityIssue(
                issue_type=IssueType.MISSING_ALT_TEXT,
                severity=SeverityLevel.CRITICAL,
                description="Critical issue",
                element="<img>",
                context="Test"
            ),
            AccessibilityIssue(
                issue_type=IssueType.POOR_COLOR_CONTRAST,
                severity=SeverityLevel.MODERATE,
                description="Moderate issue",
                element="<p>",
                context="Test"
            ),
            AccessibilityIssue(
                issue_type=IssueType.MISSING_ALT_TEXT,
                severity=SeverityLevel.LOW,
                description="Low issue",
                element="<img>",
                context="Test"
            )
        ]
        
        result = ScanResult(
            url="https://example.com",
            timestamp=datetime.now(),
            issues=issues,
            page_title="Test Page"
        )
        
        # Test filtering by severity
        critical_issues = result.get_issues_by_severity(SeverityLevel.CRITICAL)
        assert len(critical_issues) == 1
        assert critical_issues[0].severity == SeverityLevel.CRITICAL
        
        # Test filtering by type
        alt_text_issues = result.get_issues_by_type(IssueType.MISSING_ALT_TEXT)
        assert len(alt_text_issues) == 2
    
    def test_scan_result_to_dict(self):
        """Test converting scan result to dictionary."""
        result = ScanResult(
            url="https://example.com",
            timestamp=datetime.now(),
            issues=[],
            page_title="Test Page"
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["url"] == "https://example.com"
        assert result_dict["page_title"] == "Test Page"
        assert "summary" in result_dict
        assert result_dict["summary"]["total_issues"] == 0
        assert result_dict["summary"]["accessibility_score"] == 100.0
    
    def test_scan_result_string_representation(self):
        """Test string representation of scan result."""
        result = ScanResult(
            url="https://example.com",
            timestamp=datetime.now(),
            issues=[],
            page_title="Test Page"
        )
        
        result_str = str(result)
        assert "✅" in result_str
        assert "https://example.com" in result_str
        assert "0 issues" in result_str
        assert "Score: 100.0" in result_str


class TestScanSummary:
    """Test ScanSummary class."""
    
    def test_create_scan_summary(self):
        """Test creating a scan summary."""
        summary = ScanSummary(
            total_urls_scanned=5,
            successful_scans=4,
            failed_scans=1,
            total_issues=10,
            critical_issues=3,
            moderate_issues=5,
            low_issues=2,
            average_accessibility_score=85.5,
            scan_duration=15.2
        )
        
        assert summary.total_urls_scanned == 5
        assert summary.successful_scans == 4
        assert summary.failed_scans == 1
        assert summary.total_issues == 10
        assert summary.critical_issues == 3
        assert summary.moderate_issues == 5
        assert summary.low_issues == 2
        assert summary.average_accessibility_score == 85.5
        assert summary.scan_duration == 15.2
    
    def test_scan_summary_from_results(self):
        """Test creating summary from scan results."""
        # Create mock scan results
        successful_result = ScanResult(
            url="https://example.com",
            timestamp=datetime.now(),
            issues=[
                AccessibilityIssue(
                    issue_type=IssueType.MISSING_ALT_TEXT,
                    severity=SeverityLevel.CRITICAL,
                    description="Test issue",
                    element="<img>",
                    context="Test"
                )
            ],
            page_title="Test Page",
            scan_duration=2.0,
            status="completed"
        )
        
        failed_result = ScanResult(
            url="https://failed.com",
            timestamp=datetime.now(),
            issues=[],
            page_title="",
            scan_duration=1.0,
            status="failed",
            error_message="Connection timeout"
        )
        
        scan_results = [successful_result, failed_result]
        summary = ScanSummary.from_scan_results(scan_results)
        
        assert summary.total_urls_scanned == 2
        assert summary.successful_scans == 1
        assert summary.failed_scans == 1
        assert summary.total_issues == 1
        assert summary.critical_issues == 1
        assert summary.moderate_issues == 0
        assert summary.low_issues == 0
        assert summary.average_accessibility_score < 100.0
        assert summary.scan_duration == 3.0
    
    def test_scan_summary_to_dict(self):
        """Test converting scan summary to dictionary."""
        summary = ScanSummary(
            total_urls_scanned=3,
            successful_scans=3,
            failed_scans=0,
            total_issues=5,
            critical_issues=2,
            moderate_issues=2,
            low_issues=1,
            average_accessibility_score=90.0,
            scan_duration=10.0
        )
        
        summary_dict = summary.to_dict()
        
        assert summary_dict["total_urls_scanned"] == 3
        assert summary_dict["successful_scans"] == 3
        assert summary_dict["failed_scans"] == 0
        assert summary_dict["total_issues"] == 5
        assert summary_dict["critical_issues"] == 2
        assert summary_dict["moderate_issues"] == 2
        assert summary_dict["low_issues"] == 1
        assert summary_dict["average_accessibility_score"] == 90.0
        assert summary_dict["scan_duration"] == 10.0


if __name__ == "__main__":
    pytest.main([__file__])
