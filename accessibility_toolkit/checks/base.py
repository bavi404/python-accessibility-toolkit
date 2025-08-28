"""
Base class for all accessibility checks.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from ..models import AccessibilityIssue, IssueType, SeverityLevel


class BaseCheck(ABC):
    """Abstract base class for accessibility checks."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the check with optional configuration."""
        self.config = config or {}
        self.check_name = self.__class__.__name__
    
    @abstractmethod
    def check(self, soup: BeautifulSoup, url: str) -> List[AccessibilityIssue]:
        """
        Perform the accessibility check.
        
        Args:
            soup: BeautifulSoup object of the parsed HTML
            url: URL of the page being checked
            
        Returns:
            List of AccessibilityIssue objects found
        """
        pass
    
    def create_issue(
        self,
        issue_type: IssueType,
        severity: SeverityLevel,
        description: str,
        element: str,
        context: str = "",
        line_number: int = None,
        column_number: int = None,
        suggested_fix: str = "",
        wcag_criteria: List[str] = None,
        additional_info: Dict[str, Any] = None
    ) -> AccessibilityIssue:
        """
        Create an AccessibilityIssue with consistent formatting.
        
        Args:
            issue_type: Type of accessibility issue
            severity: Severity level of the issue
            description: Human-readable description of the issue
            element: HTML element or selector where issue was found
            context: Additional context about the issue
            line_number: Line number in HTML source
            column_number: Column number in HTML source
            suggested_fix: Suggested solution for the issue
            wcag_criteria: List of relevant WCAG criteria
            additional_info: Any additional metadata
            
        Returns:
            AccessibilityIssue object
        """
        return AccessibilityIssue(
            issue_type=issue_type,
            severity=severity,
            description=description,
            element=element,
            context=context,
            line_number=line_number,
            column_number=column_number,
            suggested_fix=suggested_fix,
            wcag_criteria=wcag_criteria or [],
            additional_info=additional_info or {}
        )
    
    def get_element_info(self, element) -> Dict[str, Any]:
        """
        Extract useful information from a BeautifulSoup element.
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Dictionary with element information
        """
        info = {
            "tag": element.name,
            "classes": element.get("class", []),
            "id": element.get("id", ""),
            "attributes": dict(element.attrs),
        }
        
        # Get text content (truncated if too long)
        text_content = element.get_text(strip=True)
        if text_content:
            info["text"] = text_content[:100] + "..." if len(text_content) > 100 else text_content
        
        return info
    
    def find_elements_by_tag(self, soup: BeautifulSoup, tag: str) -> List:
        """Find all elements of a specific tag type."""
        return soup.find_all(tag)
    
    def find_elements_by_class(self, soup: BeautifulSoup, class_name: str) -> List:
        """Find all elements with a specific class."""
        return soup.find_all(class_=class_name)
    
    def find_elements_by_id(self, soup: BeautifulSoup, element_id: str) -> List:
        """Find elements with a specific ID."""
        return soup.find_all(id=element_id)
    
    def get_parent_context(self, element, levels: int = 2) -> str:
        """
        Get context from parent elements.
        
        Args:
            element: BeautifulSoup element
            levels: Number of parent levels to check
            
        Returns:
            String describing the element's context
        """
        context_parts = []
        current = element
        
        for _ in range(levels):
            if current.parent and current.parent.name:
                context_parts.append(f"<{current.parent.name}>")
                current = current.parent
            else:
                break
        
        return " > ".join(reversed(context_parts)) if context_parts else "unknown"
    
    def is_visible_element(self, element) -> bool:
        """
        Check if an element is likely visible to users.
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            True if element is likely visible
        """
        # Check for common hidden attributes
        hidden_attrs = ["hidden", "aria-hidden", "style"]
        for attr in hidden_attrs:
            if element.get(attr):
                if attr == "style" and "display: none" in element.get(attr, ""):
                    return False
                elif attr in ["hidden", "aria-hidden"] and element.get(attr) == "true":
                    return False
        
        # Check if element has no content
        if not element.get_text(strip=True) and not element.find_all("img"):
            return False
        
        return True
    
    def get_line_number(self, element) -> int:
        """
        Get the approximate line number of an element.
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Line number (approximate)
        """
        try:
            # This is a rough approximation
            return element.sourceline or 0
        except AttributeError:
            return 0
    
    def get_column_number(self, element) -> int:
        """
        Get the approximate column number of an element.
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Column number (approximate)
        """
        try:
            # This is a rough approximation
            return element.sourcepos or 0
        except AttributeError:
            return 0
    
    def log_check_start(self, url: str):
        """Log that a check is starting."""
        print(f"🔍 Running {self.check_name} on {url}")
    
    def log_check_complete(self, url: str, issue_count: int):
        """Log that a check has completed."""
        status = "✅" if issue_count == 0 else f"⚠️  {issue_count} issues found"
        print(f"{status} {self.check_name} completed for {url}")
