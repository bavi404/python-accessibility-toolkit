"""
ARIA accessibility check implementation.
"""

from typing import List
from bs4 import BeautifulSoup
from .base import BaseCheck
from ..models import AccessibilityIssue, IssueType, SeverityLevel


class AriaCheck(BaseCheck):
    """Check for ARIA (Accessible Rich Internet Applications) issues."""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.check_required_attributes = config.get("check_required_attributes", True)
        self.check_invalid_attributes = config.get("check_invalid_attributes", True)
        self.check_missing_attributes = config.get("check_missing_attributes", True)
    
    def check(self, soup: BeautifulSoup, url: str) -> List[AccessibilityIssue]:
        """
        Check for ARIA accessibility issues.
        
        Args:
            soup: BeautifulSoup object of the parsed HTML
            url: URL of the page being checked
            
        Returns:
            List of AccessibilityIssue objects found
        """
        self.log_check_start(url)
        issues = []
        
        # Find all elements with ARIA attributes
        aria_elements = self._find_aria_elements(soup)
        
        for element in aria_elements:
            # Check for various ARIA issues
            aria_issues = self._check_aria_element(element)
            issues.extend(aria_issues)
        
        # Check for elements that should have ARIA attributes
        missing_aria_issues = self._check_missing_aria(soup)
        issues.extend(missing_aria_issues)
        
        self.log_check_complete(url, len(issues))
        return issues
    
    def _find_aria_elements(self, soup: BeautifulSoup) -> List:
        """Find all elements that have ARIA attributes."""
        aria_elements = []
        
        # Find elements with any aria-* attribute
        for element in soup.find_all():
            if any(attr.startswith('aria-') for attr in element.attrs.keys()):
                aria_elements.append(element)
        
        return aria_elements
    
    def _check_aria_element(self, element) -> List[AccessibilityIssue]:
        """Check a single element with ARIA attributes for issues."""
        issues = []
        
        # Check for invalid ARIA attributes
        if self.check_invalid_attributes:
            invalid_issues = self._check_invalid_aria_attributes(element)
            issues.extend(invalid_issues)
        
        # Check for missing required ARIA attributes
        if self.check_required_attributes:
            required_issues = self._check_required_aria_attributes(element)
            issues.extend(required_issues)
        
        # Check for ARIA attribute values
        value_issues = self._check_aria_attribute_values(element)
        issues.extend(value_issues)
        
        return issues
    
    def _check_invalid_aria_attributes(self, element) -> List[AccessibilityIssue]:
        """Check for invalid ARIA attributes."""
        issues = []
        
        # Valid ARIA attributes
        valid_aria_attrs = {
            'aria-label', 'aria-labelledby', 'aria-describedby', 'aria-hidden',
            'aria-expanded', 'aria-collapsed', 'aria-selected', 'aria-checked',
            'aria-pressed', 'aria-current', 'aria-required', 'aria-invalid',
            'aria-live', 'aria-atomic', 'aria-relevant', 'aria-busy',
            'aria-controls', 'aria-owns', 'aria-activedescendant', 'aria-posinset',
            'aria-setsize', 'aria-level', 'aria-sort', 'aria-valuemin',
            'aria-valuemax', 'aria-valuenow', 'aria-valuetext', 'aria-orientation',
            'aria-autocomplete', 'aria-multiline', 'aria-readonly', 'aria-placeholder',
            'aria-haspopup', 'aria-modal', 'aria-dialog', 'aria-tabindex',
            'aria-roledescription', 'aria-keyshortcuts', 'aria-details'
        }
        
        for attr in element.attrs.keys():
            if attr.startswith('aria-') and attr not in valid_aria_attrs:
                issues.append(self._create_invalid_aria_attribute_issue(element, attr))
        
        return issues
    
    def _check_required_aria_attributes(self, element) -> List[AccessibilityIssue]:
        """Check for missing required ARIA attributes."""
        issues = []
        
        # Check role-based requirements
        role = element.get('role')
        if role:
            required_attrs = self._get_required_aria_for_role(role)
            for required_attr in required_attrs:
                if not element.get(required_attr):
                    issues.append(self._create_missing_required_aria_issue(element, role, required_attr))
        
        # Check for aria-label or aria-labelledby on interactive elements
        if self._is_interactive_element(element):
            if not element.get('aria-label') and not element.get('aria-labelledby'):
                if not self._has_visible_text(element):
                    issues.append(self._create_missing_aria_label_issue(element))
        
        return issues
    
    def _check_aria_attribute_values(self, element) -> List[AccessibilityIssue]:
        """Check for invalid ARIA attribute values."""
        issues = []
        
        # Check boolean attributes
        boolean_attrs = ['aria-hidden', 'aria-required', 'aria-invalid', 'aria-busy']
        for attr in boolean_attrs:
            value = element.get(attr)
            if value and value not in ['true', 'false']:
                issues.append(self._create_invalid_aria_value_issue(element, attr, value))
        
        # Check enumerated attributes
        enumerated_attrs = {
            'aria-expanded': ['true', 'false', 'undefined'],
            'aria-selected': ['true', 'false', 'undefined'],
            'aria-checked': ['true', 'false', 'mixed', 'undefined'],
            'aria-current': ['page', 'step', 'location', 'date', 'time', 'true', 'false'],
            'aria-live': ['off', 'polite', 'assertive'],
            'aria-orientation': ['horizontal', 'vertical'],
            'aria-sort': ['ascending', 'descending', 'none', 'other']
        }
        
        for attr, valid_values in enumerated_attrs.items():
            value = element.get(attr)
            if value and value not in valid_values:
                issues.append(self._create_invalid_aria_value_issue(element, attr, value))
        
        return issues
    
    def _check_missing_aria(self, soup: BeautifulSoup) -> List[AccessibilityIssue]:
        """Check for elements that should have ARIA attributes."""
        issues = []
        
        # Check for elements that should have roles
        elements_needing_roles = self._find_elements_needing_roles(soup)
        for element in elements_needing_roles:
            issues.append(self._create_missing_role_issue(element))
        
        # Check for custom interactive elements
        custom_interactive = self._find_custom_interactive_elements(soup)
        for element in custom_interactive:
            if not element.get('role') and not element.get('aria-label'):
                issues.append(self._create_missing_aria_label_issue(element))
        
        return issues
    
    def _get_required_aria_for_role(self, role: str) -> List[str]:
        """Get required ARIA attributes for a specific role."""
        role_requirements = {
            'button': [],
            'checkbox': ['aria-checked'],
            'combobox': ['aria-expanded'],
            'dialog': ['aria-labelledby', 'aria-describedby'],
            'grid': ['aria-rowcount', 'aria-colcount'],
            'gridcell': ['aria-rowindex', 'aria-colindex'],
            'listbox': ['aria-expanded'],
            'menuitem': ['aria-haspopup'],
            'menuitemcheckbox': ['aria-checked'],
            'menuitemradio': ['aria-checked'],
            'option': ['aria-selected'],
            'progressbar': ['aria-valuemin', 'aria-valuemax', 'aria-valuenow'],
            'radio': ['aria-checked'],
            'scrollbar': ['aria-valuemin', 'aria-valuemax', 'aria-valuenow'],
            'searchbox': ['aria-expanded'],
            'slider': ['aria-valuemin', 'aria-valuemax', 'aria-valuenow'],
            'spinbutton': ['aria-valuemin', 'aria-valuemax', 'aria-valuenow'],
            'tab': ['aria-selected'],
            'tabpanel': ['aria-labelledby'],
            'textbox': ['aria-multiline'],
            'toolbar': ['aria-label', 'aria-labelledby'],
            'tooltip': ['aria-describedby'],
            'tree': ['aria-multiselectable'],
            'treeitem': ['aria-expanded', 'aria-level']
        }
        
        return role_requirements.get(role, [])
    
    def _is_interactive_element(self, element) -> bool:
        """Check if an element is interactive."""
        interactive_tags = ['button', 'a', 'input', 'select', 'textarea']
        interactive_roles = ['button', 'link', 'menuitem', 'tab', 'checkbox', 'radio']
        
        if element.name in interactive_tags:
            return True
        
        role = element.get('role')
        if role in interactive_roles:
            return True
        
        # Check for click handlers
        onclick = element.get('onclick')
        if onclick:
            return True
        
        return False
    
    def _has_visible_text(self, element) -> bool:
        """Check if an element has visible text content."""
        text_content = element.get_text(strip=True)
        return len(text_content) > 0
    
    def _find_elements_needing_roles(self, soup: BeautifulSoup) -> List:
        """Find elements that should have ARIA roles."""
        elements = []
        
        # Custom buttons (div/span with click handlers)
        custom_buttons = soup.find_all(['div', 'span'], onclick=True)
        elements.extend(custom_buttons)
        
        # Custom form controls
        custom_inputs = soup.find_all(['div', 'span'], class_=lambda x: x and 'input' in x.lower())
        elements.extend(custom_inputs)
        
        return elements
    
    def _find_custom_interactive_elements(self, soup: BeautifulSoup) -> List:
        """Find custom interactive elements that need ARIA labels."""
        elements = []
        
        # Elements with click handlers but no semantic meaning
        clickable_divs = soup.find_all('div', onclick=True)
        for div in clickable_divs:
            if not div.get('role') and not div.get('aria-label'):
                elements.append(div)
        
        return elements
    
    def _create_invalid_aria_attribute_issue(self, element, attr: str) -> AccessibilityIssue:
        """Create an issue for invalid ARIA attributes."""
        element_info = self.get_element_info(element)
        context = self.get_parent_context(element)
        
        return self.create_issue(
            issue_type=IssueType.MISSING_ARIA_LABELS,
            severity=SeverityLevel.MODERATE,
            description=f"Invalid ARIA attribute: {attr}",
            element=f"<{element.name} {attr}='{element.get(attr)}'>",
            context=context,
            line_number=self.get_line_number(element),
            column_number=self.get_column_number(element),
            suggested_fix=(
                f"Remove the invalid ARIA attribute '{attr}' or replace it with a valid one. "
                "Check the ARIA specification for valid attributes and values."
            ),
            wcag_criteria=["4.1.2"],
            additional_info=element_info
        )
    
    def _create_missing_required_aria_issue(self, element, role: str, required_attr: str) -> AccessibilityIssue:
        """Create an issue for missing required ARIA attributes."""
        element_info = self.get_element_info(element)
        context = self.get_parent_context(element)
        
        return self.create_issue(
            issue_type=IssueType.MISSING_ARIA_LABELS,
            severity=SeverityLevel.MODERATE,
            description=f"Missing required ARIA attribute '{required_attr}' for role '{role}'",
            element=f"<{element.name} role='{role}'>",
            context=context,
            line_number=self.get_line_number(element),
            column_number=self.get_column_number(element),
            suggested_fix=(
                f"Add the required ARIA attribute '{required_attr}' to this element with role '{role}'. "
                f"This attribute is required for proper accessibility support."
            ),
            wcag_criteria=["4.1.2"],
            additional_info=element_info
        )
    
    def _create_invalid_aria_value_issue(self, element, attr: str, value: str) -> AccessibilityIssue:
        """Create an issue for invalid ARIA attribute values."""
        element_info = self.get_element_info(element)
        context = self.get_parent_context(element)
        
        return self.create_issue(
            issue_type=IssueType.MISSING_ARIA_LABELS,
            severity=SeverityLevel.LOW,
            description=f"Invalid ARIA attribute value: {attr}='{value}'",
            element=f"<{element.name} {attr}='{value}'>",
            context=context,
            line_number=self.get_line_number(element),
            column_number=self.get_column_number(element),
            suggested_fix=(
                f"Change the value of '{attr}' from '{value}' to a valid value. "
                "Check the ARIA specification for valid values for this attribute."
            ),
            wcag_criteria=["4.1.2"],
            additional_info=element_info
        )
    
    def _create_missing_role_issue(self, element) -> AccessibilityIssue:
        """Create an issue for elements missing ARIA roles."""
        element_info = self.get_element_info(element)
        context = self.get_parent_context(element)
        
        return self.create_issue(
            issue_type=IssueType.MISSING_ARIA_LABELS,
            severity=SeverityLevel.MODERATE,
            description=f"Interactive element missing ARIA role: {element.name}",
            element=f"<{element.name}>",
            context=context,
            line_number=self.get_line_number(element),
            column_number=self.get_column_number(element),
            suggested_fix=(
                "Add an appropriate ARIA role to this element to indicate its purpose. "
                "For example, add role='button' for clickable elements."
            ),
            wcag_criteria=["4.1.2"],
            additional_info=element_info
        )
    
    def _create_missing_aria_label_issue(self, element) -> AccessibilityIssue:
        """Create an issue for elements missing ARIA labels."""
        element_info = self.get_element_info(element)
        context = self.get_parent_context(element)
        
        return self.create_issue(
            issue_type=IssueType.MISSING_ARIA_LABELS,
            severity=SeverityLevel.MODERATE,
            description=f"Interactive element missing accessible name: {element.name}",
            element=f"<{element.name}>",
            context=context,
            line_number=self.get_line_number(element),
            column_number=self.get_column_number(element),
            suggested_fix=(
                "Add aria-label or aria-labelledby attribute to provide "
                "an accessible name for this interactive element."
            ),
            wcag_criteria=["2.4.6", "4.1.2"],
            additional_info=element_info
        )
