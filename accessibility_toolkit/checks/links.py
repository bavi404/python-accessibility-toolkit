"""
Link accessibility check implementation.
"""

from typing import List
from bs4 import BeautifulSoup
from .base import BaseCheck
from ..models import AccessibilityIssue, IssueType, SeverityLevel
import re


class LinkAccessibilityCheck(BaseCheck):
    """Check for link accessibility issues."""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.check_descriptive_text = config.get("check_descriptive_text", True)
        self.check_empty_links = config.get("check_empty_links", True)
        self.check_image_links = config.get("check_image_links", True)
        self.check_same_text_links = config.get("check_same_text_links", True)
        self.check_context_awareness = config.get("check_context_awareness", True)
    
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
        """Check if link text is non-descriptive with enhanced heuristics."""
        text_content = link.get_text(strip=True)
        
        # Enhanced non-descriptive link text patterns
        vague_patterns = {
            # Generic action words
            "actions": [
                "click here", "click", "tap here", "tap", "press here", "press",
                "select here", "select", "choose", "browse", "view", "see", "show",
                "display", "open", "download", "get", "find", "search", "look",
                "check", "verify", "try", "start", "begin", "go", "submit"
            ],
            
            # Generic navigation
            "navigation": [
                "here", "there", "this", "that", "more", "more info", "more information",
                "more details", "details", "info", "information", "continue", "next",
                "previous", "back", "forward", "home", "about", "services", "products",
                "contact", "help", "support", "faq", "blog", "news", "events"
            ],
            
            # Generic content indicators
            "content": [
                "read more", "learn more", "see more", "view more", "show more",
                "expand", "full article", "full story", "complete", "entire",
                "all", "everything", "full list", "complete list"
            ],
            
            # Generic link indicators
            "link_indicators": [
                "link", "url", "page", "website", "site", "webpage", "web page",
                "web site", "webpage", "webpage", "web page", "web site"
            ],
            
            # Generic form actions
            "form_actions": [
                "submit", "send", "post", "upload", "save", "delete", "remove",
                "edit", "modify", "change", "update", "confirm", "cancel"
            ],
            
            # Generic social media
            "social": [
                "follow us", "follow", "like us", "like", "share", "tweet",
                "retweet", "comment", "reply", "message", "dm", "direct message"
            ]
        }
        
        # Flatten all patterns
        all_patterns = []
        for category in vague_patterns.values():
            all_patterns.extend(category)
        
        text_lower = text_content.lower().strip()
        
        # Check for exact matches (after stripping punctuation and extra spaces)
        text_sanitized = re.sub(r"[\s\-–—:;,.!?()\[\]{}]+", " ", text_lower).strip()
        
        # Check for exact matches
        if text_sanitized in all_patterns:
            return True
        
        # Check for patterns within text with context analysis
        for pattern in all_patterns:
            if pattern in text_sanitized:
                # Allow if it's part of a longer, more descriptive phrase
                if len(text_sanitized) > len(pattern) + 12:
                    # Check if the additional text provides meaningful context
                    if self._has_meaningful_context(text_sanitized, pattern):
                        continue
                return True
        
        # Check for very short text
        if len(text_sanitized) < 3:
            return True
        
        # Check for generic text with numbers only
        if re.match(r"^[\d\s\-–—:;,.!?()\[\]{}]+$", text_sanitized):
            return True
        
        # Check for generic text with common non-descriptive patterns
        if self._is_generic_without_context(text_sanitized):
            return True
        
        # Check for context-aware analysis
        if self.check_context_awareness and self._lacks_contextual_information(link):
            return True
        
        return False
    
    def _has_meaningful_context(self, text: str, pattern: str) -> bool:
        """Check if text has meaningful context beyond the vague pattern."""
        # Remove the vague pattern and check remaining text
        remaining = text.replace(pattern, "").strip()
        
        # Check if remaining text provides meaningful context
        meaningful_words = [
            "privacy", "policy", "terms", "conditions", "report", "document",
            "guide", "manual", "tutorial", "help", "support", "contact",
            "about", "company", "organization", "team", "product", "service",
            "download", "upload", "form", "application", "registration",
            "login", "signup", "account", "profile", "settings", "preferences"
        ]
        
        for word in meaningful_words:
            if word in remaining.lower():
                return True
        
        # Check if remaining text is substantial
        if len(remaining) > 8:
            return True
        
        return False
    
    def _is_generic_without_context(self, text: str) -> bool:
        """Check if text is generic without providing context."""
        # Common generic patterns that lack context
        generic_patterns = [
            r"^[a-z\s]+$",  # Only lowercase letters and spaces
            r"^[A-Z\s]+$",  # Only uppercase letters and spaces
            r"^[a-zA-Z\s]+$",  # Mixed case but only letters and spaces
        ]
        
        for pattern in generic_patterns:
            if re.match(pattern, text) and len(text) < 15:
                # Check if it's a common generic word
                generic_words = ["link", "page", "site", "web", "click", "here", "more"]
                if any(word in text.lower() for word in generic_words):
                    return True
        
        return False
    
    def _lacks_contextual_information(self, link) -> bool:
        """Check if link lacks contextual information from surrounding content."""
        # Get surrounding context
        parent = link.parent
        if not parent:
            return False
        
        # Check if parent has descriptive text
        parent_text = parent.get_text(strip=True)
        link_text = link.get_text(strip=True)
        
        # Remove link text from parent text
        context_text = parent_text.replace(link_text, "").strip()
        
        # Check if context provides meaningful information
        if len(context_text) < 20:
            return True
        
        # Check for common context patterns
        context_patterns = [
            "click here to", "click here for", "click here and", "click here in",
            "read more about", "learn more about", "see more of", "view more of",
            "more information on", "more details about", "continue reading about"
        ]
        
        for pattern in context_patterns:
            if pattern in context_text.lower():
                return False
        
        return True
    
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
        
        # Enhanced suggested fix based on the type of vague text
        suggested_fix = self._get_enhanced_suggested_fix(link_text, link)
        
        return self.create_issue(
            issue_type=IssueType.NON_DESCRIPTIVE_LINKS,
            severity=SeverityLevel.MODERATE,
            description=f"Link text is not descriptive: '{link_text}'",
            element=f"<a href='{link.get('href', '')}'>{link_text}</a>",
            context=context,
            line_number=self.get_line_number(link),
            column_number=self.get_column_number(link),
            suggested_fix=suggested_fix,
            wcag_criteria=["2.4.4", "2.4.9"],
            additional_info=element_info
        )
    
    def _get_enhanced_suggested_fix(self, link_text: str, link) -> str:
        """Get enhanced suggested fix based on link text and context."""
        link_text_lower = link_text.lower()
        href = link.get("href", "").lower()
        
        # Categorize the vague text and provide specific suggestions
        if any(word in link_text_lower for word in ["click here", "click", "tap", "press"]):
            if "privacy" in href or "policy" in href:
                return f"Replace '{link_text}' with 'Read our Privacy Policy' or 'View Privacy Policy'"
            elif "terms" in href or "conditions" in href:
                return f"Replace '{link_text}' with 'Read our Terms of Service' or 'View Terms and Conditions'"
            elif "contact" in href:
                return f"Replace '{link_text}' with 'Contact Us' or 'Get in Touch'"
            else:
                return f"Replace '{link_text}' with descriptive text that explains where the link goes. For example: 'Read the full article', 'Download the report', or 'View product details'"
        
        elif any(word in link_text_lower for word in ["read more", "learn more", "see more"]):
            return f"Replace '{link_text}' with specific information about what users will learn. For example: 'Read more about accessibility guidelines', 'Learn more about our services', or 'See more product options'"
        
        elif any(word in link_text_lower for word in ["more", "more info", "more information"]):
            return f"Replace '{link_text}' with specific details about what additional information is available. For example: 'More product details', 'More about our company', or 'More accessibility resources'"
        
        elif any(word in link_text_lower for word in ["here", "this", "that"]):
            return f"Replace '{link_text}' with descriptive text that explains what 'here', 'this', or 'that' refers to. For example: 'View our accessibility statement', 'Read the full report', or 'Download the guide'"
        
        elif any(word in link_text_lower for word in ["link", "url", "page"]):
            return f"Replace '{link_text}' with descriptive text that explains what the link contains. For example: 'Visit our homepage', 'Go to the contact page', or 'Access the help section'"
        
        elif len(link_text) < 5:
            return f"Replace the short text '{link_text}' with a longer, more descriptive phrase that explains the link's purpose and destination"
        
        else:
            return f"Replace the generic text '{link_text}' with more descriptive text that explains where the link goes or what it does. For example, instead of '{link_text}', use specific, action-oriented text like 'Read our privacy policy' or 'Download the accessibility report'."
    
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
