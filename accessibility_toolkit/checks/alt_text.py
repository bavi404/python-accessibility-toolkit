"""
Alt text accessibility check implementation.
"""

from typing import List
from bs4 import BeautifulSoup
from .base import BaseCheck
from ..models import AccessibilityIssue, IssueType, SeverityLevel


class AltTextCheck(BaseCheck):
    """Check for missing or inadequate alt text on images."""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.ignore_decorative = config.get("ignore_decorative", True)
        self.require_descriptive = config.get("require_descriptive", True)
    
    def check(self, soup: BeautifulSoup, url: str) -> List[AccessibilityIssue]:
        """
        Check for alt text issues on images.
        
        Args:
            soup: BeautifulSoup object of the parsed HTML
            url: URL of the page being checked
            
        Returns:
            List of AccessibilityIssue objects found
        """
        self.log_check_start(url)
        issues = []
        
        # Find all image elements
        images = self.find_elements_by_tag(soup, "img")
        
        for img in images:
            if not self.is_visible_element(img):
                continue
                
            alt_text = img.get("alt", "")
            src = img.get("src", "")
            
            # Check for missing alt text
            if not alt_text:
                issues.append(self._create_missing_alt_issue(img, src))
            # Check for inadequate alt text
            elif self.require_descriptive and self._is_inadequate_alt(alt_text):
                issues.append(self._create_inadequate_alt_issue(img, alt_text, src))
            # Check for decorative images without proper marking
            elif self.ignore_decorative and self._is_decorative_image(img, alt_text):
                if alt_text != "":
                    issues.append(self._create_decorative_alt_issue(img, alt_text, src))
        
        self.log_check_complete(url, len(issues))
        return issues
    
    def _create_missing_alt_issue(self, img, src: str) -> AccessibilityIssue:
        """Create an issue for missing alt text."""
        element_info = self.get_element_info(img)
        context = self.get_parent_context(img)
        
        return self.create_issue(
            issue_type=IssueType.MISSING_ALT_TEXT,
            severity=SeverityLevel.CRITICAL,
            description=f"Image missing alt text: {src}",
            element=f"<img src='{src}'>",
            context=context,
            line_number=self.get_line_number(img),
            column_number=self.get_column_number(img),
            suggested_fix=(
                "Add descriptive alt text to the image. "
                "For decorative images, use alt='' (empty string). "
                "For informative images, provide a clear description of what the image shows."
            ),
            wcag_criteria=["1.1.1", "1.1.1"],
            additional_info=element_info
        )
    
    def _create_inadequate_alt_issue(self, img, alt_text: str, src: str) -> AccessibilityIssue:
        """Create an issue for inadequate alt text."""
        element_info = self.get_element_info(img)
        context = self.get_parent_context(img)
        
        return self.create_issue(
            issue_type=IssueType.MISSING_ALT_TEXT,
            severity=SeverityLevel.MODERATE,
            description=f"Inadequate alt text: '{alt_text}' for image {src}",
            element=f"<img src='{src}' alt='{alt_text}'>",
            context=context,
            line_number=self.get_line_number(img),
            column_number=self.get_column_number(img),
            suggested_fix=(
                "Improve the alt text to be more descriptive. "
                "Avoid generic terms like 'image', 'photo', or 'picture'. "
                "Describe what the image shows and its purpose in the context."
            ),
            wcag_criteria=["1.1.1"],
            additional_info=element_info
        )
    
    def _create_decorative_alt_issue(self, img, alt_text: str, src: str) -> AccessibilityIssue:
        """Create an issue for decorative images with non-empty alt text."""
        element_info = self.get_element_info(img)
        context = self.get_parent_context(img)
        
        return self.create_issue(
            issue_type=IssueType.MISSING_ALT_TEXT,
            severity=SeverityLevel.LOW,
            description=f"Decorative image should have empty alt text: {src}",
            element=f"<img src='{src}' alt='{alt_text}'>",
            context=context,
            line_number=self.get_line_number(img),
            column_number=self.get_column_number(img),
            suggested_fix=(
                "Since this image is decorative, change alt='{alt_text}' to alt='' "
                "(empty string). This tells screen readers to skip the image."
            ),
            wcag_criteria=["1.1.1"],
            additional_info=element_info
        )
    
    def _is_inadequate_alt(self, alt_text: str) -> bool:
        """Check if alt text is inadequate."""
        inadequate_patterns = [
            "image", "photo", "picture", "img", "graphic", "icon",
            "click here", "read more", "learn more", "more info"
        ]
        
        alt_lower = alt_text.lower().strip()
        
        # Check for generic terms
        for pattern in inadequate_patterns:
            if pattern in alt_lower:
                return True
        
        # Check for very short descriptions
        if len(alt_text.strip()) < 3:
            return True
        
        # Check for repetitive text
        if alt_text.lower() in ["image", "photo", "picture"]:
            return True
        
        return False
    
    def _is_decorative_image(self, img, alt_text: str) -> bool:
        """Determine if an image is decorative."""
        # Check for decorative indicators
        if alt_text == "":
            return True
        
        # Check for CSS classes that suggest decorative images
        classes = img.get("class", [])
        decorative_classes = ["decorative", "ornamental", "background", "bg", "decoration"]
        
        for class_name in classes:
            if any(dec in class_name.lower() for dec in decorative_classes):
                return True
        
        # Check for role attribute
        role = img.get("role", "")
        if role == "presentation" or role == "none":
            return True
        
        # Check for aria-hidden
        if img.get("aria-hidden") == "true":
            return True
        
        # Check if image is very small (likely decorative)
        width = img.get("width", "")
        height = img.get("height", "")
        if width and height:
            try:
                if int(width) <= 32 and int(height) <= 32:
                    return True
            except ValueError:
                pass
        
        return False
