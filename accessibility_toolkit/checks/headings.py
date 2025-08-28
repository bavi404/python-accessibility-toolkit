"""
Heading hierarchy accessibility check implementation.
"""

from typing import List, Dict
from bs4 import BeautifulSoup
from .base import BaseCheck
from ..models import AccessibilityIssue, IssueType, SeverityLevel


class HeadingHierarchyCheck(BaseCheck):
    """Check for proper heading hierarchy and structure."""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.require_h1 = config.get("require_h1", True)
        self.max_heading_level = config.get("max_heading_level", 6)
        self.check_skip_levels = config.get("check_skip_levels", True)
    
    def check(self, soup: BeautifulSoup, url: str) -> List[AccessibilityIssue]:
        """
        Check for heading hierarchy issues.
        
        Args:
            soup: BeautifulSoup object of the parsed HTML
            url: URL of the page being checked
            
        Returns:
            List of AccessibilityIssue objects found
        """
        self.log_check_start(url)
        issues = []
        
        # Find all heading elements
        headings = self.find_elements_by_tag(soup, ["h1", "h2", "h3", "h4", "h5", "h6"])
        
        if not headings:
            if self.require_h1:
                issues.append(self._create_no_headings_issue(soup))
            return issues
        
        # Check for missing H1
        if self.require_h1 and not self._has_h1(headings):
            issues.append(self._create_missing_h1_issue(soup))
        
        # Check heading hierarchy
        issues.extend(self._check_heading_hierarchy(headings))
        
        # Check for skipped heading levels
        if self.check_skip_levels:
            issues.extend(self._check_skipped_levels(headings))
        
        # Check for multiple H1s (should only be one per page)
        h1_count = len([h for h in headings if h.name == "h1"])
        if h1_count > 1:
            issues.append(self._create_multiple_h1_issue(h1_count))
        
        self.log_check_complete(url, len(issues))
        return issues
    
    def _has_h1(self, headings: List) -> bool:
        """Check if there's at least one H1 heading."""
        return any(h.name == "h1" for h in headings)
    
    def _check_heading_hierarchy(self, headings: List) -> List[AccessibilityIssue]:
        """Check for proper heading hierarchy."""
        issues = []
        
        # Sort headings by their position in the document
        sorted_headings = sorted(headings, key=lambda h: self.get_line_number(h))
        
        current_level = 0
        for heading in sorted_headings:
            heading_level = int(heading.name[1])
            
            # Check if heading level is too deep
            if heading_level > self.max_heading_level:
                issues.append(self._create_deep_heading_issue(heading, heading_level))
            
            # Check for proper nesting (shouldn't skip more than one level)
            if heading_level > current_level + 1:
                issues.append(self._create_skip_level_issue(heading, current_level, heading_level))
            
            current_level = heading_level
        
        return issues
    
    def _check_skipped_levels(self, headings: List) -> List[AccessibilityIssue]:
        """Check for skipped heading levels."""
        issues = []
        
        # Group headings by level
        heading_levels = {}
        for heading in headings:
            level = int(heading.name[1])
            if level not in heading_levels:
                heading_levels[level] = []
            heading_levels[level].append(heading)
        
        # Check for gaps in heading levels
        expected_levels = set(range(1, max(heading_levels.keys()) + 1))
        actual_levels = set(heading_levels.keys())
        missing_levels = expected_levels - actual_levels
        
        for missing_level in missing_levels:
            if missing_level > 1:  # Don't require H1 if page doesn't have one
                issues.append(self._create_missing_level_issue(missing_level))
        
        return issues
    
    def _create_no_headings_issue(self, soup: BeautifulSoup) -> AccessibilityIssue:
        """Create an issue for pages with no headings."""
        return self.create_issue(
            issue_type=IssueType.IMPROPER_HEADING_HIERARCHY,
            severity=SeverityLevel.MODERATE,
            description="Page has no heading elements",
            element="<body>",
            context="Entire page",
            suggested_fix=(
                "Add heading elements (h1, h2, h3, etc.) to structure your content. "
                "Start with an h1 that describes the main topic of the page, "
                "then use h2, h3, etc. for subsections."
            ),
            wcag_criteria=["1.3.1", "2.4.6"],
            additional_info={"page_title": soup.title.string if soup.title else "No title"}
        )
    
    def _create_missing_h1_issue(self, soup: BeautifulSoup) -> AccessibilityIssue:
        """Create an issue for missing H1 heading."""
        return self.create_issue(
            issue_type=IssueType.IMPROPER_HEADING_HIERARCHY,
            severity=SeverityLevel.MODERATE,
            description="Page is missing an H1 heading",
            element="<body>",
            context="Entire page",
            suggested_fix=(
                "Add an H1 heading that clearly describes the main topic or purpose of the page. "
                "This helps users understand what the page is about and provides proper document structure."
            ),
            wcag_criteria=["1.3.1", "2.4.6"],
            additional_info={"page_title": soup.title.string if soup.title else "No title"}
        )
    
    def _create_multiple_h1_issue(self, h1_count: int) -> AccessibilityIssue:
        """Create an issue for multiple H1 headings."""
        return self.create_issue(
            issue_type=IssueType.IMPROPER_HEADING_HIERARCHY,
            severity=SeverityLevel.MODERATE,
            description=f"Page has {h1_count} H1 headings (should have only one)",
            element="Multiple <h1> elements",
            context="Entire page",
            suggested_fix=(
                "A page should have only one H1 heading that represents the main topic. "
                "Convert additional H1 headings to H2 or H3 as appropriate for your content hierarchy."
            ),
            wcag_criteria=["1.3.1", "2.4.6"],
            additional_info={"h1_count": h1_count}
        )
    
    def _create_deep_heading_issue(self, heading, heading_level: int) -> AccessibilityIssue:
        """Create an issue for headings that are too deep."""
        element_info = self.get_element_info(heading)
        context = self.get_parent_context(heading)
        
        return self.create_issue(
            issue_type=IssueType.IMPROPER_HEADING_HIERARCHY,
            severity=SeverityLevel.LOW,
            description=f"Heading level {heading_level} is too deep (max recommended: {self.max_heading_level})",
            element=f"<{heading.name}>{heading.get_text(strip=True)[:50]}...</{heading.name}>",
            context=context,
            line_number=self.get_line_number(heading),
            column_number=self.get_column_number(heading),
            suggested_fix=(
                f"Consider restructuring your content to use heading levels 1-{self.max_heading_level}. "
                "Very deep heading levels can make content difficult to navigate and understand."
            ),
            wcag_criteria=["1.3.1", "2.4.6"],
            additional_info=element_info
        )
    
    def _create_skip_level_issue(self, heading, current_level: int, heading_level: int) -> AccessibilityIssue:
        """Create an issue for skipped heading levels."""
        element_info = self.get_element_info(heading)
        context = self.get_parent_context(heading)
        
        return self.create_issue(
            issue_type=IssueType.IMPROPER_HEADING_HIERARCHY,
            severity=SeverityLevel.MODERATE,
            description=f"Heading level jumps from {current_level} to {heading_level} (skipping levels)",
            element=f"<{heading.name}>{heading.get_text(strip=True)[:50]}...</{heading.name}>",
            context=context,
            line_number=self.get_line_number(heading),
            column_number=self.get_column_number(heading),
            suggested_fix=(
                f"Don't skip heading levels. If the previous heading was level {current_level}, "
                f"the next heading should be level {current_level + 1}. "
                "This creates a logical and navigable document structure."
            ),
            wcag_criteria=["1.3.1", "2.4.6"],
            additional_info=element_info
        )
    
    def _create_missing_level_issue(self, missing_level: int) -> AccessibilityIssue:
        """Create an issue for missing heading levels."""
        return self.create_issue(
            issue_type=IssueType.IMPROPER_HEADING_HIERARCHY,
            severity=SeverityLevel.LOW,
            description=f"Heading level {missing_level} is missing from the page",
            element="Page structure",
            context="Entire page",
            suggested_fix=(
                f"Consider adding H{missing_level} headings to create a more complete "
                "and logical document structure. This helps users navigate and understand your content."
            ),
            wcag_criteria=["1.3.1", "2.4.6"],
            additional_info={"missing_level": missing_level}
        )
