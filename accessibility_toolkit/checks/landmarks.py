"""
Landmark accessibility check implementation.
"""

from typing import List
from bs4 import BeautifulSoup
from .base import BaseCheck
from ..models import AccessibilityIssue, IssueType, SeverityLevel


class LandmarkCheck(BaseCheck):
    """Check for landmark accessibility issues."""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.require_main = config.get("require_main", True)
        self.require_navigation = config.get("require_navigation", True)
        self.check_duplicate_landmarks = config.get("check_duplicate_landmarks", True)
    
    def check(self, soup: BeautifulSoup, url: str) -> List[AccessibilityIssue]:
        """
        Check for landmark accessibility issues.
        
        Args:
            soup: BeautifulSoup object of the parsed HTML
            url: URL of the page being checked
            
        Returns:
            List of AccessibilityIssue objects found
        """
        self.log_check_start(url)
        issues = []
        
        # Check for missing required landmarks
        if self.require_main:
            main_issues = self._check_main_landmark(soup)
            issues.extend(main_issues)
        
        if self.require_navigation:
            nav_issues = self._check_navigation_landmark(soup)
            issues.extend(nav_issues)
        
        # Check for duplicate landmarks
        if self.check_duplicate_landmarks:
            duplicate_issues = self._check_duplicate_landmarks(soup)
            issues.extend(duplicate_issues)
        
        # Check for landmark structure
        structure_issues = self._check_landmark_structure(soup)
        issues.extend(structure_issues)
        
        self.log_check_complete(url, len(issues))
        return issues
    
    def _check_main_landmark(self, soup: BeautifulSoup) -> List[AccessibilityIssue]:
        """Check for main landmark issues."""
        issues = []
        
        # Check for main element or role="main"
        main_elements = soup.find_all("main")
        main_roles = soup.find_all(attrs={"role": "main"})

        has_main_element = len(main_elements) > 0
        has_main_role = len(main_roles) > 0

        # Only one missing-main issue should be emitted if neither exists
        if not (has_main_element or has_main_role):
            issues.append(self._create_missing_main_landmark_issue(soup))
        elif len(main_elements) > 1:
            # If there are multiple <main> elements, report it once
            issues.append(self._create_multiple_main_landmarks_issue(len(main_elements)))
        
        return issues
    
    def _check_navigation_landmark(self, soup: BeautifulSoup) -> List[AccessibilityIssue]:
        """Check for navigation landmark issues."""
        issues = []
        
        # Check for nav elements
        nav_elements = soup.find_all("nav")
        nav_roles = soup.find_all(attrs={"role": "navigation"})
        
        if not nav_elements and not nav_roles:
            # Check if there are navigation-like elements
            if self._has_navigation_content(soup):
                issues.append(self._create_missing_navigation_landmark_issue(soup))
        
        return issues
    
    def _check_duplicate_landmarks(self, soup: BeautifulSoup) -> List[AccessibilityIssue]:
        """Check for duplicate landmark types."""
        issues = []
        
        # Check for duplicate navigation landmarks
        nav_elements = soup.find_all("nav")
        nav_roles = soup.find_all(attrs={"role": "navigation"})
        total_nav = len(nav_elements) + len(nav_roles)
        
        if total_nav > 1:
            issues.append(self._create_duplicate_navigation_landmark_issue(total_nav))
        
        # Check for duplicate banner landmarks
        header_elements = soup.find_all("header")
        banner_roles = soup.find_all(attrs={"role": "banner"})
        total_banner = len(header_elements) + len(banner_roles)
        
        if total_banner > 1:
            issues.append(self._create_duplicate_banner_landmark_issue(total_banner))
        
        # Check for duplicate contentinfo landmarks
        footer_elements = soup.find_all("footer")
        contentinfo_roles = soup.find_all(attrs={"role": "contentinfo"})
        total_contentinfo = len(footer_elements) + len(contentinfo_roles)
        
        if total_contentinfo > 1:
            issues.append(self._create_duplicate_contentinfo_landmark_issue(total_contentinfo))
        
        return issues
    
    def _check_landmark_structure(self, soup: BeautifulSoup) -> List[AccessibilityIssue]:
        """Check for landmark structure issues."""
        issues = []
        
        # Check for missing skip links
        if not self._has_skip_links(soup):
            issues.append(self._create_missing_skip_links_issue(soup))
        
        # Check for proper landmark hierarchy
        hierarchy_issues = self._check_landmark_hierarchy(soup)
        issues.extend(hierarchy_issues)
        
        return issues
    
    def _has_navigation_content(self, soup: BeautifulSoup) -> bool:
        """Check if the page has navigation-like content."""
        # Look for common navigation patterns
        nav_patterns = [
            soup.find("ul", class_=lambda x: x and "nav" in x.lower()),
            soup.find("ul", class_=lambda x: x and "menu" in x.lower()),
            soup.find("ul", class_=lambda x: x and "breadcrumb" in x.lower()),
            soup.find("ol", class_=lambda x: x and "breadcrumb" in x.lower()),
        ]
        
        return any(nav_patterns)
    
    def _has_skip_links(self, soup: BeautifulSoup) -> bool:
        """Check if the page has skip links."""
        # Look for skip links
        skip_links = soup.find_all("a", href="#main")
        skip_links.extend(soup.find_all("a", href="#content"))
        skip_links.extend(soup.find_all("a", class_=lambda x: x and "skip" in x.lower()))
        
        return len(skip_links) > 0
    
    def _check_landmark_hierarchy(self, soup: BeautifulSoup) -> List[AccessibilityIssue]:
        """Check for proper landmark hierarchy."""
        issues = []
        
        # Check if landmarks are properly nested
        main_elements = soup.find_all("main")
        for main in main_elements:
            # Main should not contain other main landmarks
            nested_main = main.find_all("main")
            if nested_main:
                issues.append(self._create_nested_main_landmark_issue(main))
            
            # Main should not contain navigation landmarks
            nested_nav = main.find_all("nav")
            if nested_nav:
                issues.append(self._create_main_contains_nav_issue(main))
        
        return issues
    
    def _create_missing_main_landmark_issue(self, soup: BeautifulSoup) -> AccessibilityIssue:
        """Create an issue for missing main landmark."""
        return self.create_issue(
            issue_type=IssueType.MISSING_LANDMARKS,
            severity=SeverityLevel.CRITICAL,
            description="Page missing main landmark",
            element="<body>",
            context="Entire page",
            suggested_fix=(
                "Add a <main> element or role='main' attribute to identify "
                "the main content area of the page. This helps screen readers "
                "navigate to the primary content."
            ),
            wcag_criteria=["1.3.1", "2.4.1"],
            additional_info={"page_title": soup.title.string if soup.title else "No title"}
        )
    
    def _create_multiple_main_landmarks_issue(self, count: int) -> AccessibilityIssue:
        """Create an issue for multiple main landmarks."""
        return self.create_issue(
            issue_type=IssueType.MISSING_LANDMARKS,
            severity=SeverityLevel.MODERATE,
            description=f"Page has {count} main landmarks (should have only one)",
            element="Multiple <main> elements",
            context="Entire page",
            suggested_fix=(
                f"Remove {count - 1} of the main landmarks. A page should have "
                "only one main landmark to identify the primary content area."
            ),
            wcag_criteria=["1.3.1", "2.4.1"],
            additional_info={"main_landmark_count": count}
        )
    
    def _create_missing_navigation_landmark_issue(self, soup: BeautifulSoup) -> AccessibilityIssue:
        """Create an issue for missing navigation landmark."""
        return self.create_issue(
            issue_type=IssueType.MISSING_LANDMARKS,
            severity=SeverityLevel.MODERATE,
            description="Page missing navigation landmark",
            element="<body>",
            context="Entire page",
            suggested_fix=(
                "Add <nav> elements or role='navigation' attributes to identify "
                "navigation sections. This helps screen readers identify and navigate "
                "through navigation menus."
            ),
            wcag_criteria=["1.3.1", "2.4.1"],
            additional_info={"page_title": soup.title.string if soup.title else "No title"}
        )
    
    def _create_duplicate_navigation_landmark_issue(self, count: int) -> AccessibilityIssue:
        """Create an issue for duplicate navigation landmarks."""
        return self.create_issue(
            issue_type=IssueType.MISSING_LANDMARKS,
            severity=SeverityLevel.LOW,
            description=f"Page has {count} navigation landmarks",
            element="Multiple navigation elements",
            context="Entire page",
            suggested_fix=(
                f"Consider consolidating the {count} navigation landmarks or "
                "add aria-label attributes to distinguish between different "
                "navigation sections (e.g., 'Main Navigation', 'Footer Navigation')."
            ),
            wcag_criteria=["1.3.1", "2.4.1"],
            additional_info={"navigation_landmark_count": count}
        )
    
    def _create_duplicate_banner_landmark_issue(self, count: int) -> AccessibilityIssue:
        """Create an issue for duplicate banner landmarks."""
        return self.create_issue(
            issue_type=IssueType.MISSING_LANDMARKS,
            severity=SeverityLevel.LOW,
            description=f"Page has {count} banner landmarks",
            element="Multiple header/banner elements",
            context="Entire page",
            suggested_fix=(
                f"Consider consolidating the {count} banner landmarks or "
                "add aria-label attributes to distinguish between different "
                "header sections."
            ),
            wcag_criteria=["1.3.1", "2.4.1"],
            additional_info={"banner_landmark_count": count}
        )
    
    def _create_duplicate_contentinfo_landmark_issue(self, count: int) -> AccessibilityIssue:
        """Create an issue for duplicate contentinfo landmarks."""
        return self.create_issue(
            issue_type=IssueType.MISSING_LANDMARKS,
            severity=SeverityLevel.LOW,
            description=f"Page has {count} contentinfo landmarks",
            element="Multiple footer/contentinfo elements",
            context="Entire page",
            suggested_fix=(
                f"Consider consolidating the {count} contentinfo landmarks or "
                "add aria-label attributes to distinguish between different "
                "footer sections."
            ),
            wcag_criteria=["1.3.1", "2.4.1"],
            additional_info={"contentinfo_landmark_count": count}
        )
    
    def _create_missing_skip_links_issue(self, soup: BeautifulSoup) -> AccessibilityIssue:
        """Create an issue for missing skip links."""
        return self.create_issue(
            issue_type=IssueType.MISSING_SKIP_LINKS,
            severity=SeverityLevel.MODERATE,
            description="Page missing skip links",
            element="<body>",
            context="Entire page",
            suggested_fix=(
                "Add skip links at the beginning of the page to allow keyboard users "
                "to jump directly to main content, navigation, or other important sections. "
                "Example: <a href='#main'>Skip to main content</a>"
            ),
            wcag_criteria=["2.4.1"],
            additional_info={"page_title": soup.title.string if soup.title else "No title"}
        )
    
    def _create_nested_main_landmark_issue(self, main_element) -> AccessibilityIssue:
        """Create an issue for nested main landmarks."""
        element_info = self.get_element_info(main_element)
        context = self.get_parent_context(main_element)
        
        return self.create_issue(
            issue_type=IssueType.MISSING_LANDMARKS,
            severity=SeverityLevel.MODERATE,
            description="Main landmark contains nested main landmarks",
            element=f"<{main_element.name}>",
            context=context,
            line_number=self.get_line_number(main_element),
            column_number=self.get_column_number(main_element),
            suggested_fix=(
                "Remove nested main landmarks from within the main content area. "
                "A page should have only one main landmark, and it should not "
                "contain other main landmarks."
            ),
            wcag_criteria=["1.3.1", "2.4.1"],
            additional_info=element_info
        )
    
    def _create_main_contains_nav_issue(self, main_element) -> AccessibilityIssue:
        """Create an issue for main landmark containing navigation."""
        element_info = self.get_element_info(main_element)
        context = self.get_parent_context(main_element)
        
        return self.create_issue(
            issue_type=IssueType.MISSING_LANDMARKS,
            severity=SeverityLevel.LOW,
            description="Main landmark contains navigation elements",
            element=f"<{main_element.name}>",
            context=context,
            line_number=self.get_line_number(main_element),
            column_number=self.get_column_number(main_element),
            suggested_fix=(
                "Consider moving navigation elements outside of the main landmark "
                "or add aria-label to distinguish navigation within main content. "
                "The main landmark should focus on the primary content."
            ),
            wcag_criteria=["1.3.1", "2.4.1"],
            additional_info=element_info
        )
