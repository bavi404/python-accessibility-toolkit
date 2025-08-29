"""
Link accessibility check implementation.
"""

from typing import List
from bs4 import BeautifulSoup
from .base import BaseCheck
from ..models import AccessibilityIssue, IssueType, SeverityLevel


class LinkAccessibilityCheck(BaseCheck):
    """Check for link accessibility issues."""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.check_descriptive_text = config.get("check_descriptive_text", True)
        self.check_empty_links = config.get("check_empty_links", True)
        self.check_image_links = config.get("check_image_links", True)
        self.check_same_text_links = config.get("check_same_text_links", True)
    
    def check(self, soup: BeautifulSoup, url: str) -> List[AccessibilityIssue]:
        """
        Check for link accessibility issues.
        
        Args:
            soup: BeautifulSoup object of the parsed HTML
            url: URL of the page being checked
            
        Returns:
            List of AccessibilityIssue objects found
        """
        self.log_check_start(url)
        issues = []
        
        # Find all links
        links = self.find_elements_by_tag(soup, "a")
        
        for link in links:
            # Skip hidden links
            if not self.is_visible_element(link):
                continue
            
            # Check for various link issues
            link_issues = self._check_link_element(link)
            issues.extend(link_issues)
        
        # Check for duplicate link text
        if self.check_same_text_links:
            duplicate_issues = self._check_duplicate_link_text(links)
            issues.extend(duplicate_issues)
        
        self.log_check_complete(url, len(issues))
        return issues
    
    def _check_link_element(self, link) -> List[AccessibilityIssue]:
        """Check a single link element for accessibility issues."""
        issues = []
        
        # Check for empty links
        if self.check_empty_links and self._is_empty_link(link):
            issues.append(self._create_empty_link_issue(link))
        
        # Check for non-descriptive link text
        if self.check_descriptive_text and self._is_non_descriptive_link(link):
            issues.append(self._create_non_descriptive_link_issue(link))
        
        # Check for image links without proper alt text
        if self.check_image_links and self._has_image_without_alt(link):
            issues.append(self._create_image_link_issue(link))
        
        # Check for missing aria-label on links with images
        if self._has_image_only_content(link):
            if not link.get("aria-label") and not link.get("aria-labelledby"):
                issues.append(self._create_missing_aria_label_issue(link))
        
        # Check for links that open in new windows without warning
        if link.get("target") == "_blank":
            if not self._has_new_window_warning(link):
                issues.append(self._create_new_window_warning_issue(link))
        
        return issues
    
    def _is_empty_link(self, link) -> bool:
        """Check if a link has no content."""
        # Check if link has no text content
        text_content = link.get_text(strip=True)
        if not text_content:
            # Check if it has images
            images = link.find_all("img")
            if not images:
                return True
        
        return False
    
    def _is_non_descriptive_link(self, link) -> bool:
        """Check if link text is non-descriptive."""
        text_content = link.get_text(strip=True)
        
        # Common non-descriptive link text patterns (expanded)
        non_descriptive_patterns = [
            "click here", "here", "more", "more info", "more information",
            "read more", "learn more", "continue", "next", "previous",
            "back", "forward", "submit", "go", "link", "this", "that",
            "click", "tap", "press", "select", "choose", "browse",
            "view", "see", "show", "display", "open", "download",
            "get", "find", "search", "look", "check", "verify",
            # additions
            "details", "info", "information", "more details", "start", "try",
            "home", "about", "services", "products"  # generic nav labels without context
        ]
        
        text_lower = text_content.lower().strip()
        
        # Check for exact matches (after stripping punctuation)
        import re
        text_sanitized = re.sub(r"[\s\-–—:;,.!?()\[\]{}]+", " ", text_lower).strip()
        if text_sanitized in non_descriptive_patterns:
            return True
        
        # Check for patterns within text
        for pattern in non_descriptive_patterns:
            if pattern in text_sanitized:
                # Allow if it's part of a longer, more descriptive phrase
                if len(text_sanitized) > len(pattern) + 8:
                    continue
                return True
        
        # Check for very short text
        if len(text_sanitized) < 3:
            return True
        
        # Check for generic text
        if text_sanitized in ["link", "url", "page"]:
            return True
        
        return False
    
    def _has_image_without_alt(self, link) -> bool:
        """Check if link contains images without proper alt text."""
        images = link.find_all("img")
        
        for img in images:
            alt_text = img.get("alt", "")
            if not alt_text:
                return True
        
        return False
    
    def _has_image_only_content(self, link) -> bool:
        """Check if link contains only images."""
        text_content = link.get_text(strip=True)
        images = link.find_all("img")
        
        return not text_content and len(images) > 0
    
    def _has_new_window_warning(self, link) -> bool:
        """Check if link has a warning about opening in new window."""
        text_content = link.get_text(strip=True).lower()
        title_attr = link.get("title", "").lower()
        
        warning_indicators = [
            "opens in new window", "new window", "external link",
            "opens in new tab", "new tab", "external site"
        ]
        
        for indicator in warning_indicators:
            if indicator in text_content or indicator in title_attr:
                return True
        
        return False
    
    def _check_duplicate_link_text(self, links: List) -> List[AccessibilityIssue]:
        """Check for links with the same text that go to different URLs."""
        issues = []
        
        # Group links by text content
        link_groups = {}
        for link in links:
            text = link.get_text(strip=True)
            if text:
                if text not in link_groups:
                    link_groups[text] = []
                link_groups[text].append(link)
        
        # Check for duplicate text with different URLs
        for text, link_list in link_groups.items():
            if len(link_list) > 1:
                urls = [link.get("href", "") for link in link_list]
                unique_urls = set(urls)
                
                if len(unique_urls) > 1:
                    # Create issue for the first link with this text
                    issues.append(self._create_duplicate_link_text_issue(link_list[0], text, len(link_list)))
        
        return issues
    
    def _create_empty_link_issue(self, link) -> AccessibilityIssue:
        """Create an issue for empty links."""
        element_info = self.get_element_info(link)
        context = self.get_parent_context(link)
        
        return self.create_issue(
            issue_type=IssueType.NON_DESCRIPTIVE_LINKS,
            severity=SeverityLevel.CRITICAL,
            description="Link has no content or descriptive text",
            element=f"<a href='{link.get('href', '')}'>",
            context=context,
            line_number=self.get_line_number(link),
            column_number=self.get_column_number(link),
            suggested_fix=(
                "Add descriptive text content to this link. If the link contains only an image, "
                "ensure the image has proper alt text, or add aria-label to the link."
            ),
            wcag_criteria=["2.4.4", "2.4.9"],
            additional_info=element_info
        )
    
    def _create_non_descriptive_link_issue(self, link) -> AccessibilityIssue:
        """Create an issue for non-descriptive link text."""
        element_info = self.get_element_info(link)
        context = self.get_parent_context(link)
        link_text = link.get_text(strip=True)
        
        return self.create_issue(
            issue_type=IssueType.NON_DESCRIPTIVE_LINKS,
            severity=SeverityLevel.MODERATE,
            description=f"Link text is not descriptive: '{link_text}'",
            element=f"<a href='{link.get('href', '')}'>{link_text}</a>",
            context=context,
            line_number=self.get_line_number(link),
            column_number=self.get_column_number(link),
            suggested_fix=(
                f"Replace the generic text '{link_text}' with more descriptive text that "
                "explains where the link goes or what it does. For example, instead of "
                "'Click here', use 'Read our privacy policy' or 'Download the report'."
            ),
            wcag_criteria=["2.4.4", "2.4.9"],
            additional_info=element_info
        )
    
    def _create_image_link_issue(self, link) -> AccessibilityIssue:
        """Create an issue for image links without proper alt text."""
        element_info = self.get_element_info(link)
        context = self.get_parent_context(link)
        
        return self.create_issue(
            issue_type=IssueType.NON_DESCRIPTIVE_LINKS,
            severity=SeverityLevel.CRITICAL,
            description="Link contains image without proper alt text",
            element=f"<a href='{link.get('href', '')}'>",
            context=context,
            line_number=self.get_line_number(link),
            column_number=self.get_column_number(link),
            suggested_fix=(
                "Add descriptive alt text to the image within this link, or add "
                "aria-label to the link itself to describe its purpose."
            ),
            wcag_criteria=["1.1.1", "2.4.4"],
            additional_info=element_info
        )
    
    def _create_missing_aria_label_issue(self, link) -> AccessibilityIssue:
        """Create an issue for image-only links missing aria-label."""
        element_info = self.get_element_info(link)
        context = self.get_parent_context(link)
        
        return self.create_issue(
            issue_type=IssueType.MISSING_ARIA_LABELS,
            severity=SeverityLevel.MODERATE,
            description="Image-only link missing accessible name",
            element=f"<a href='{link.get('href', '')}'>",
            context=context,
            line_number=self.get_line_number(link),
            column_number=self.get_column_number(link),
            suggested_fix=(
                "Add aria-label attribute to describe the purpose of this link, "
                "or ensure the image within the link has descriptive alt text."
            ),
            wcag_criteria=["2.4.4", "2.4.9"],
            additional_info=element_info
        )
    
    def _create_new_window_warning_issue(self, link) -> AccessibilityIssue:
        """Create an issue for links opening in new windows without warning."""
        element_info = self.get_element_info(link)
        context = self.get_parent_context(link)
        link_text = link.get_text(strip=True)
        
        return self.create_issue(
            issue_type=IssueType.NON_DESCRIPTIVE_LINKS,
            severity=SeverityLevel.LOW,
            description="Link opens in new window without warning",
            element=f"<a href='{link.get('href', '')}' target='_blank'>{link_text}</a>",
            context=context,
            line_number=self.get_line_number(link),
            column_number=self.get_column_number(link),
            suggested_fix=(
                "Add text indicating this link opens in a new window, or add "
                "aria-label with this information. For example: 'Privacy Policy (opens in new window)'"
            ),
            wcag_criteria=["3.2.2"],
            additional_info=element_info
        )
    
    def _create_duplicate_link_text_issue(self, link, text: str, count: int) -> AccessibilityIssue:
        """Create an issue for duplicate link text."""
        element_info = self.get_element_info(link)
        context = self.get_parent_context(link)
        
        return self.create_issue(
            issue_type=IssueType.NON_DESCRIPTIVE_LINKS,
            severity=SeverityLevel.MODERATE,
            description=f"Link text '{text}' appears {count} times with different destinations",
            element=f"<a href='{link.get('href', '')}'>{text}</a>",
            context=context,
            line_number=self.get_line_number(link),
            column_number=self.get_column_number(link),
            suggested_fix=(
                f"Make the link text more specific to distinguish between the {count} different destinations. "
                "For example, add context like 'Company Privacy Policy' vs 'Product Privacy Policy'."
            ),
            wcag_criteria=["2.4.4", "2.4.9"],
            additional_info=element_info
        )
