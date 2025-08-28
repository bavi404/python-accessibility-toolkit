"""
Keyboard navigation accessibility check implementation.
"""

from typing import List
from bs4 import BeautifulSoup
from .base import BaseCheck
from ..models import AccessibilityIssue, IssueType, SeverityLevel


class KeyboardNavigationCheck(BaseCheck):
    """Check for keyboard navigation accessibility issues."""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.check_focusable_elements = config.get("check_focusable_elements", True)
        self.check_tab_order = config.get("check_tab_order", True)
        self.check_skip_links = config.get("check_skip_links", True)
    
    def check(self, soup: BeautifulSoup, url: str) -> List[AccessibilityIssue]:
        """
        Check for keyboard navigation accessibility issues.
        
        Args:
            soup: BeautifulSoup object of the parsed HTML
            url: URL of the page being checked
            
        Returns:
            List of AccessibilityIssue objects found
        """
        self.log_check_start(url)
        issues = []
        
        # Check for focusable elements
        if self.check_focusable_elements:
            focusable_issues = self._check_focusable_elements(soup)
            issues.extend(focusable_issues)
        
        # Check for tab order issues
        if self.check_tab_order:
            tab_order_issues = self._check_tab_order(soup)
            issues.extend(tab_order_issues)
        
        # Check for skip links
        if self.check_skip_links:
            skip_link_issues = self._check_skip_links(soup)
            issues.extend(skip_link_issues)
        
        # Check for keyboard traps
        keyboard_trap_issues = self._check_keyboard_traps(soup)
        issues.extend(keyboard_trap_issues)
        
        self.log_check_complete(url, len(issues))
        return issues
    
    def _check_focusable_elements(self, soup: BeautifulSoup) -> List[AccessibilityIssue]:
        """Check for focusable elements issues."""
        issues = []
        
        # Find all interactive elements
        interactive_elements = self._find_interactive_elements(soup)
        
        # De-duplicate similar elements by signature (tag, id, name, role)
        seen = set()
        for element in interactive_elements:
            sig = (
                element.name,
                element.get('id', ''),
                element.get('name', ''),
                element.get('role', ''),
            )
            if sig in seen:
                continue
            seen.add(sig)
            
            # Check if element is focusable
            if not self._is_focusable(element):
                issues.append(self._create_non_focusable_element_issue(element))
            
            # Check for proper focus indicators
            if not self._has_focus_indicator(element):
                issues.append(self._create_missing_focus_indicator_issue(element))
        
        return issues
    
    def _check_tab_order(self, soup: BeautifulSoup) -> List[AccessibilityIssue]:
        """Check for tab order issues."""
        issues = []
        
        # Find all focusable elements
        focusable_elements = self._find_focusable_elements(soup)
        
        # Check for logical tab order
        tab_order_issues = self._check_logical_tab_order(focusable_elements)
        issues.extend(tab_order_issues)
        
        # Check for tabindex values
        tabindex_issues = self._check_tabindex_values(focusable_elements)
        issues.extend(tabindex_issues)
        
        return issues
    
    def _check_skip_links(self, soup: BeautifulSoup) -> List[AccessibilityIssue]:
        """Check for skip link issues."""
        issues = []
        
        # Check if skip links are present
        skip_links = self._find_skip_links(soup)
        
        if not skip_links:
            issues.append(self._create_missing_skip_links_issue(soup))
        else:
            # Check if skip links are properly positioned
            for skip_link in skip_links:
                if not self._is_skip_link_properly_positioned(skip_link):
                    issues.append(self._create_improperly_positioned_skip_link_issue(skip_link))
        
        return issues
    
    def _check_keyboard_traps(self, soup: BeautifulSoup) -> List[AccessibilityIssue]:
        """Check for potential keyboard traps."""
        issues = []
        
        # Check for elements that might trap keyboard focus
        potential_traps = self._find_potential_keyboard_traps(soup)
        
        for trap in potential_traps:
            issues.append(self._create_keyboard_trap_issue(trap))
        
        return issues
    
    def _find_interactive_elements(self, soup: BeautifulSoup) -> List:
        """Find all interactive elements."""
        interactive_elements = []
        
        # Standard interactive elements
        interactive_tags = ['a', 'button', 'input', 'select', 'textarea', 'label']
        for tag in interactive_tags:
            interactive_elements.extend(soup.find_all(tag))
        
        # Elements with click handlers
        clickable_elements = soup.find_all(attrs={"onclick": True})
        interactive_elements.extend(clickable_elements)
        
        # Elements with roles that make them interactive
        interactive_roles = ['button', 'link', 'menuitem', 'tab', 'checkbox', 'radio']
        for role in interactive_roles:
            role_elements = soup.find_all(attrs={"role": role})
            interactive_elements.extend(role_elements)
        
        return interactive_elements
    
    def _find_focusable_elements(self, soup: BeautifulSoup) -> List:
        """Find all focusable elements."""
        focusable_elements = []
        
        # Elements that are naturally focusable
        naturally_focusable = ['a', 'button', 'input', 'select', 'textarea', 'label']
        for tag in naturally_focusable:
            elements = soup.find_all(tag)
            for element in elements:
                if self._is_naturally_focusable(element):
                    focusable_elements.append(element)
        
        # Elements with tabindex
        tabindex_elements = soup.find_all(attrs={"tabindex": True})
        focusable_elements.extend(tabindex_elements)
        
        # Elements with contenteditable
        editable_elements = soup.find_all(attrs={"contenteditable": True})
        focusable_elements.extend(editable_elements)
        
        return focusable_elements
    
    def _is_naturally_focusable(self, element) -> bool:
        """Check if an element is naturally focusable."""
        tag = element.name
        
        if tag == 'a':
            return bool(element.get('href'))
        elif tag == 'button':
            return True
        elif tag == 'input':
            input_type = element.get('type', 'text')
            return input_type not in ['hidden', 'file']
        elif tag == 'select':
            return True
        elif tag == 'textarea':
            return True
        elif tag == 'label':
            # Labels are focusable if they have a 'for' attribute
            return bool(element.get('for'))
        
        return False
    
    def _is_focusable(self, element) -> bool:
        """Check if an element can receive focus."""
        # Check if element is hidden
        if element.get('hidden') or element.get('aria-hidden') == 'true':
            return False
        
        # Check if element has tabindex="-1" (not focusable)
        tabindex = element.get('tabindex')
        if tabindex == '-1':
            return False
        
        # Check if element is naturally focusable
        if self._is_naturally_focusable(element):
            return True
        
        # Check if element has tabindex
        if tabindex:
            return True
        
        # Check if element has contenteditable
        if element.get('contenteditable'):
            return True
        
        return False
    
    def _has_focus_indicator(self, element) -> bool:
        """Check if element has a focus indicator."""
        # Check for CSS focus styles
        style = element.get('style', '')
        if 'outline' in style or 'border' in style:
            return True
        
        # Check for focus-related classes
        classes = element.get('class', [])
        focus_classes = ['focus', 'focus-visible', 'focus-ring']
        if any(focus_class in str(classes) for focus_class in focus_classes):
            return True
        
        # Check for focus-related attributes
        if element.get('data-focus-visible'):
            return True
        
        return False
    
    def _check_logical_tab_order(self, focusable_elements: List) -> List[AccessibilityIssue]:
        """Check for logical tab order."""
        issues = []
        
        # Sort elements by their position in the document
        sorted_elements = sorted(focusable_elements, key=lambda x: self.get_line_number(x))
        
        # Check for elements that might break logical flow
        for i, element in enumerate(sorted_elements):
            # Check if element has a very high tabindex that might break flow
            tabindex = element.get('tabindex')
            if tabindex and tabindex.isdigit():
                tabindex_val = int(tabindex)
                if tabindex_val > 100:  # Arbitrary threshold
                    issues.append(self._create_high_tabindex_issue(element, tabindex_val))
        
        return issues
    
    def _check_tabindex_values(self, focusable_elements: List) -> List[AccessibilityIssue]:
        """Check for problematic tabindex values."""
        issues = []
        
        for element in focusable_elements:
            tabindex = element.get('tabindex')
            if tabindex:
                # Check for non-numeric tabindex values
                if not tabindex.replace('-', '').isdigit():
                    issues.append(self._create_invalid_tabindex_issue(element, tabindex))
                
                # Check for tabindex="0" (unnecessary)
                if tabindex == '0':
                    if self._is_naturally_focusable(element):
                        issues.append(self._create_unnecessary_tabindex_issue(element))
        
        return issues
    
    def _find_skip_links(self, soup: BeautifulSoup) -> List:
        """Find skip links on the page."""
        skip_links = []
        
        # Look for skip links
        skip_links.extend(soup.find_all("a", href="#main"))
        skip_links.extend(soup.find_all("a", href="#content"))
        skip_links.extend(soup.find_all("a", class_=lambda x: x and "skip" in x.lower()))
        skip_links.extend(soup.find_all("a", text=lambda x: x and "skip" in x.lower()))
        
        return skip_links
    
    def _is_skip_link_properly_positioned(self, skip_link) -> bool:
        """Check if skip link is properly positioned."""
        # Skip links should be among the first focusable elements
        # This is a simplified check - in practice you'd want to check actual focus order
        
        # Check if skip link is near the top of the page
        line_number = self.get_line_number(skip_link)
        if line_number and line_number > 50:  # Arbitrary threshold
            return False
        
        return True
    
    def _find_potential_keyboard_traps(self, soup: BeautifulSoup) -> List:
        """Find elements that might trap keyboard focus."""
        potential_traps = []
        
        # Check for elements with very restrictive focus management
        focus_restrictive = soup.find_all(attrs={"aria-hidden": "true"})
        for element in focus_restrictive:
            if self._is_focusable(element):
                potential_traps.append(element)
        
        # Check for elements with custom focus management
        custom_focus = soup.find_all(attrs={"data-focus-trap": True})
        potential_traps.extend(custom_focus)
        
        return potential_traps
    
    def _create_non_focusable_element_issue(self, element) -> AccessibilityIssue:
        """Create an issue for non-focusable interactive elements."""
        element_info = self.get_element_info(element)
        context = self.get_parent_context(element)
        
        return self.create_issue(
            issue_type=IssueType.KEYBOARD_NAVIGATION,
            severity=SeverityLevel.CRITICAL,
            description=f"Interactive element is not keyboard focusable: {element.name}",
            element=f"<{element.name}>",
            context=context,
            line_number=self.get_line_number(element),
            column_number=self.get_column_number(element),
            suggested_fix=(
                "Make this element keyboard focusable by adding tabindex='0' or "
                "ensuring it has proper focus management. All interactive elements "
                "should be accessible via keyboard navigation."
            ),
            wcag_criteria=["2.1.1", "2.4.3"],
            additional_info=element_info
        )
    
    def _create_missing_focus_indicator_issue(self, element) -> AccessibilityIssue:
        """Create an issue for missing focus indicators."""
        element_info = self.get_element_info(element)
        context = self.get_parent_context(element)
        
        return self.create_issue(
            issue_type=IssueType.KEYBOARD_NAVIGATION,
            severity=SeverityLevel.MODERATE,
            description=f"Focusable element missing focus indicator: {element.name}",
            element=f"<{element.name}>",
            context=context,
            line_number=self.get_line_number(element),
            column_number=self.get_column_number(element),
            suggested_fix=(
                "Add a visible focus indicator to this element using CSS (outline, border) "
                "or focus-related classes. Users need to see which element has focus."
            ),
            wcag_criteria=["2.4.7"],
            additional_info=element_info
        )
    
    def _create_high_tabindex_issue(self, element, tabindex_val: int) -> AccessibilityIssue:
        """Create an issue for very high tabindex values."""
        element_info = self.get_element_info(element)
        context = self.get_parent_context(element)
        
        return self.create_issue(
            issue_type=IssueType.KEYBOARD_NAVIGATION,
            severity=SeverityLevel.MODERATE,
            description=f"Element has very high tabindex value: {tabindex_val}",
            element=f"<{element.name} tabindex='{tabindex_val}'>",
            context=context,
            line_number=self.get_line_number(element),
            column_number=self.get_column_number(element),
            suggested_fix=(
                f"Consider reducing the tabindex value from {tabindex_val} to a lower number "
                "or remove tabindex entirely to use natural document order. "
                "Very high tabindex values can make keyboard navigation confusing."
            ),
            wcag_criteria=["2.4.3"],
            additional_info=element_info
        )
    
    def _create_invalid_tabindex_issue(self, element, tabindex: str) -> AccessibilityIssue:
        """Create an issue for invalid tabindex values."""
        element_info = self.get_element_info(element)
        context = self.get_parent_context(element)
        
        return self.create_issue(
            issue_type=IssueType.KEYBOARD_NAVIGATION,
            severity=SeverityLevel.MODERATE,
            description=f"Element has invalid tabindex value: {tabindex}",
            element=f"<{element.name} tabindex='{tabindex}'>",
            context=context,
            line_number=self.get_line_number(element),
            column_number=self.get_column_number(element),
            suggested_fix=(
                f"Change tabindex='{tabindex}' to a valid integer value. "
                "Valid values are: any positive integer, 0, or -1."
            ),
            wcag_criteria=["2.4.3"],
            additional_info=element_info
        )
    
    def _create_unnecessary_tabindex_issue(self, element) -> AccessibilityIssue:
        """Create an issue for unnecessary tabindex='0'."""
        element_info = self.get_element_info(element)
        context = self.get_parent_context(element)
        
        return self.create_issue(
            issue_type=IssueType.KEYBOARD_NAVIGATION,
            severity=SeverityLevel.LOW,
            description=f"Element has unnecessary tabindex='0': {element.name}",
            element=f"<{element.name} tabindex='0'>",
            context=context,
            line_number=self.get_line_number(element),
            column_number=self.get_column_number(element),
            suggested_fix=(
                "Remove tabindex='0' from this element. It's naturally focusable "
                "and doesn't need an explicit tabindex value."
            ),
            wcag_criteria=["2.4.3"],
            additional_info=element_info
        )
    
    def _create_missing_skip_links_issue(self, soup: BeautifulSoup) -> AccessibilityIssue:
        """Create an issue for missing skip links."""
        return self.create_issue(
            issue_type=IssueType.MISSING_SKIP_LINKS,
            severity=SeverityLevel.MODERATE,
            description="Page missing skip links for keyboard navigation",
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
    
    def _create_improperly_positioned_skip_link_issue(self, skip_link) -> AccessibilityIssue:
        """Create an issue for improperly positioned skip links."""
        element_info = self.get_element_info(skip_link)
        context = self.get_parent_context(skip_link)
        
        return self.create_issue(
            issue_type=IssueType.KEYBOARD_NAVIGATION,
            severity=SeverityLevel.LOW,
            description="Skip link is not properly positioned",
            element=f"<{skip_link.name}>",
            context=context,
            line_number=self.get_line_number(skip_link),
            column_number=self.get_column_number(skip_link),
            suggested_fix=(
                "Move this skip link to the very beginning of the page content "
                "so it's the first element keyboard users encounter."
            ),
            wcag_criteria=["2.4.1"],
            additional_info=element_info
        )
    
    def _create_keyboard_trap_issue(self, element) -> AccessibilityIssue:
        """Create an issue for potential keyboard traps."""
        element_info = self.get_element_info(element)
        context = self.get_parent_context(element)
        
        return self.create_issue(
            issue_type=IssueType.KEYBOARD_NAVIGATION,
            severity=SeverityLevel.MODERATE,
            description=f"Element may trap keyboard focus: {element.name}",
            element=f"<{element.name}>",
            context=context,
            line_number=self.get_line_number(element),
            column_number=self.get_column_number(element),
            suggested_fix=(
                "Ensure this element doesn't trap keyboard focus. Users should be able "
                "to navigate away using Tab, Shift+Tab, or Escape keys."
            ),
            wcag_criteria=["2.1.2"],
            additional_info=element_info
        )
