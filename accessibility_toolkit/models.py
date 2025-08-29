"""
Data models for the accessibility toolkit.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse


class SeverityLevel(Enum):
    """Severity levels for accessibility issues."""
    CRITICAL = "critical"
    MODERATE = "moderate"
    LOW = "low"


class IssueType(Enum):
    """Types of accessibility issues."""
    MISSING_ALT_TEXT = "missing_alt_text"
    POOR_COLOR_CONTRAST = "poor_color_contrast"
    IMPROPER_HEADING_HIERARCHY = "improper_heading_hierarchy"
    MISSING_FORM_LABELS = "missing_form_labels"
    NON_DESCRIPTIVE_LINKS = "non_descriptive_links"
    MISSING_ARIA_LABELS = "missing_aria_labels"
    KEYBOARD_NAVIGATION = "keyboard_navigation"
    MISSING_LANDMARKS = "missing_landmarks"
    INACCESSIBLE_FORMS = "inaccessible_forms"
    MISSING_SKIP_LINKS = "missing_skip_links"
    OTHER = "other"


@dataclass
class AccessibilityIssue:
    """Represents a single accessibility issue found on a webpage."""
    
    issue_type: IssueType
    severity: SeverityLevel
    description: str
    element: str
    context: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    suggested_fix: str = ""
    wcag_criteria: List[str] = field(default_factory=list)
    additional_info: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate the issue data after initialization."""
        if not self.description.strip():
            raise ValueError("Issue description cannot be empty")
        if not self.element.strip():
            raise ValueError("Element information cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the issue to a dictionary representation."""
        return {
            "issue_type": self.issue_type.value,
            "severity": self.severity.value,
            "description": self.description,
            "element": self.element,
            "context": self.context,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "suggested_fix": self.suggested_fix,
            "wcag_criteria": self.wcag_criteria,
            "additional_info": self.additional_info,
        }
    
    def __str__(self) -> str:
        """String representation of the issue."""
        return f"[{self.severity.value.upper()}] {self.issue_type.value}: {self.description}"


@dataclass
class ScanResult:
    """Represents the results of scanning a single webpage."""
    
    url: str
    timestamp: datetime
    issues: List[AccessibilityIssue] = field(default_factory=list)
    page_title: str = ""
    page_description: str = ""
    scan_duration: float = 0.0
    status: str = "completed"
    error_message: Optional[str] = None
    message: Optional[str] = None  # Success message or additional info
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set default timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now()
    
    @property
    def domain(self) -> str:
        """Extract domain from URL."""
        return urlparse(self.url).netloc
    
    @property
    def critical_issues_count(self) -> int:
        """Count of critical issues."""
        return len([issue for issue in self.issues if issue.severity == SeverityLevel.CRITICAL])
    
    @property
    def moderate_issues_count(self) -> int:
        """Count of moderate issues."""
        return len([issue for issue in self.issues if issue.severity == SeverityLevel.MODERATE])
    
    @property
    def low_issues_count(self) -> int:
        """Count of low priority issues."""
        return len([issue for issue in self.issues if issue.severity == SeverityLevel.LOW])
    
    @property
    def total_issues(self) -> int:
        """Total number of issues found."""
        return len(self.issues)
    
    @property
    def accessibility_score(self) -> float:
        """Calculate accessibility score (0-100)."""
        if self.total_issues == 0:
            return 100.0
        
        # Weight issues by severity
        critical_weight = 3
        moderate_weight = 2
        low_weight = 1
        
        weighted_issues = (
            self.critical_issues_count * critical_weight +
            self.moderate_issues_count * moderate_weight +
            self.low_issues_count * low_weight
        )
        
        # Calculate score (higher is better)
        max_possible_weight = (self.total_issues * critical_weight)
        score = max(0, 100 - (weighted_issues / max_possible_weight) * 100)
        
        return round(score, 1)
    
    def get_issues_by_severity(self, severity: SeverityLevel) -> List[AccessibilityIssue]:
        """Get all issues of a specific severity level."""
        return [issue for issue in self.issues if issue.severity == severity]
    
    def get_issues_by_type(self, issue_type: IssueType) -> List[AccessibilityIssue]:
        """Get all issues of a specific type."""
        return [issue for issue in self.issues if issue.issue_type == issue_type]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the scan result to a dictionary representation."""
        return {
            "url": self.url,
            "timestamp": self.timestamp.isoformat(),
            "issues": [issue.to_dict() for issue in self.issues],
            "page_title": self.page_title,
            "page_description": self.page_description,
            "scan_duration": self.scan_duration,
            "status": self.status,
            "error_message": self.error_message,
            "message": self.message,
            "metadata": self.metadata,
            "summary": {
                "total_issues": self.total_issues,
                "critical_issues": self.critical_issues_count,
                "moderate_issues": self.moderate_issues_count,
                "low_issues": self.low_issues_count,
                "accessibility_score": self.accessibility_score,
            }
        }
    
    def __str__(self) -> str:
        """String representation of the scan result."""
        status_emoji = "✅" if self.status == "completed" else "❌"
        return f"{status_emoji} {self.url} - {self.total_issues} issues (Score: {self.accessibility_score})"


@dataclass
class ScanSummary:
    """Summary of multiple scan results."""
    
    total_urls_scanned: int
    successful_scans: int
    failed_scans: int
    total_issues: int
    critical_issues: int
    moderate_issues: int
    low_issues: int
    average_accessibility_score: float
    scan_duration: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def from_scan_results(cls, scan_results: List[ScanResult]) -> 'ScanSummary':
        """Create a summary from a list of scan results."""
        successful = [r for r in scan_results if r.status == "completed"]
        failed = [r for r in scan_results if r.status != "completed"]
        
        total_issues = sum(r.total_issues for r in successful)
        critical_issues = sum(r.critical_issues_count for r in successful)
        moderate_issues = sum(r.moderate_issues_count for r in successful)
        low_issues = sum(r.low_issues_count for r in successful)
        
        avg_score = sum(r.accessibility_score for r in successful) / len(successful) if successful else 0
        total_duration = sum(r.scan_duration for r in scan_results)
        
        return cls(
            total_urls_scanned=len(scan_results),
            successful_scans=len(successful),
            failed_scans=len(failed),
            total_issues=total_issues,
            critical_issues=critical_issues,
            moderate_issues=moderate_issues,
            low_issues=low_issues,
            average_accessibility_score=round(avg_score, 1),
            scan_duration=total_duration,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the summary to a dictionary representation."""
        return {
            "total_urls_scanned": self.total_urls_scanned,
            "successful_scans": self.successful_scans,
            "failed_scans": self.failed_scans,
            "total_issues": self.total_issues,
            "critical_issues": self.critical_issues,
            "moderate_issues": self.moderate_issues,
            "low_issues": self.low_issues,
            "average_accessibility_score": self.average_accessibility_score,
            "scan_duration": self.scan_duration,
            "timestamp": self.timestamp.isoformat(),
        }
