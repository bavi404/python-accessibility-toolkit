"""
Form accessibility check implementation.
"""

from typing import List
from bs4 import BeautifulSoup
from .base import BaseCheck
from ..models import AccessibilityIssue, IssueType, SeverityLevel


class FormAccessibilityCheck(BaseCheck):
    """Check for form accessibility issues."""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.require_labels = config.get("require_labels", True)
        self.require_placeholders = config.get("require_placeholders", False)
        self.check_required_fields = config.get("check_required_fields", True)
    
    def check(self, soup: BeautifulSoup, url: str) -> List[AccessibilityIssue]:
        """
        Check for form accessibility issues.
        
        Args:
            soup: BeautifulSoup object of the parsed HTML
            url: URL of the page being checked
            
        Returns:
            List of AccessibilityIssue objects found
        """
        self.log_check_start(url)
        issues = []
        
        # Find all forms
        forms = self.find_elements_by_tag(soup, "form")
        
        for form in forms:
            # Check form elements
            form_issues = self._check_form_elements(form)
            issues.extend(form_issues)
            
            # Check form structure
            structure_issues = self._check_form_structure(form)
            issues.extend(structure_issues)
        
        self.log_check_complete(url, len(issues))
        return issues
    
    def _check_form_elements(self, form) -> List[AccessibilityIssue]:
        """Check individual form elements for accessibility issues."""
        issues = []
        
        # Check input elements
        inputs = form.find_all("input")
        for input_elem in inputs:
            input_issues = self._check_input_element(input_elem)
            issues.extend(input_issues)
        
        # Check select elements
        selects = form.find_all("select")
        for select_elem in selects:
            select_issues = self._check_select_element(select_elem)
            issues.extend(select_issues)
        
        # Check textarea elements
        textareas = form.find_all("textarea")
        for textarea_elem in textareas:
            textarea_issues = self._check_textarea_element(textarea_elem)
            issues.extend(textarea_issues)
        
        return issues
    
    def _check_input_element(self, input_elem) -> List[AccessibilityIssue]:
        """Check a single input element for accessibility issues."""
        issues = []
        input_type = input_elem.get("type", "text")
        
        # Skip hidden inputs
        if input_type == "hidden":
            return issues
        
        # Check for missing labels
        if self.require_labels and not self._has_proper_label(input_elem):
            issues.append(self._create_missing_label_issue(input_elem))
        
        # Check for missing placeholders (if required)
        if self.require_placeholders and not input_elem.get("placeholder"):
            if input_type in ["text", "email", "password", "search", "tel", "url"]:
                issues.append(self._create_missing_placeholder_issue(input_elem))
        
        # Check for required fields without aria-required
        if self.check_required_fields and input_elem.get("required"):
            if not input_elem.get("aria-required"):
                issues.append(self._create_missing_aria_required_issue(input_elem))
        
        # Check for missing aria-describedby on error messages
        if input_elem.get("aria-invalid") == "true":
            if not input_elem.get("aria-describedby"):
                issues.append(self._create_missing_aria_describedby_issue(input_elem))
        
        return issues
    
    def _check_select_element(self, select_elem) -> List[AccessibilityIssue]:
        """Check a select element for accessibility issues."""
        issues = []
        
        # Check for missing labels
        if self.require_labels and not self._has_proper_label(select_elem):
            issues.append(self._create_missing_label_issue(select_elem))
        
        # Check for missing aria-label or aria-labelledby
        if not self._has_proper_label(select_elem):
            if not select_elem.get("aria-label") and not select_elem.get("aria-labelledby"):
                issues.append(self._create_missing_aria_label_issue(select_elem))
        
        # Check for required fields without aria-required
        if self.check_required_fields and select_elem.get("required"):
            if not select_elem.get("aria-required"):
                issues.append(self._create_missing_aria_required_issue(select_elem))
        
        return issues
    
    def _check_textarea_element(self, textarea_elem) -> List[AccessibilityIssue]:
        """Check a textarea element for accessibility issues."""
        issues = []
        
        # Check for missing labels
        if self.require_labels and not self._has_proper_label(textarea_elem):
            issues.append(self._create_missing_label_issue(textarea_elem))
        
        # Check for missing aria-label or aria-labelledby
        if not self._has_proper_label(textarea_elem):
            if not textarea_elem.get("aria-label") and not textarea_elem.get("aria-labelledby"):
                issues.append(self._create_missing_aria_label_issue(textarea_elem))
        
        # Check for required fields without aria-required
        if self.check_required_fields and textarea_elem.get("required"):
            if not textarea_elem.get("aria-required"):
                issues.append(self._create_missing_aria_required_issue(textarea_elem))
        
        return issues
    
    def _check_form_structure(self, form) -> List[AccessibilityIssue]:
        """Check form structure for accessibility issues."""
        issues = []
        
        # Check for missing form labels
        if not form.find("label") and not form.find(attrs={"aria-label": True}):
            issues.append(self._create_missing_form_label_issue(form))
        
        # Check for missing fieldset/legend on complex forms
        if self._is_complex_form(form):
            if not form.find("fieldset"):
                issues.append(self._create_missing_fieldset_issue(form))
        
        # Check for missing submit button
        submit_buttons = form.find_all("input", type="submit")
        submit_buttons.extend(form.find_all("button", type="submit"))
        
        if not submit_buttons:
            issues.append(self._create_missing_submit_button_issue(form))
        
        return issues
    
    def _has_proper_label(self, element) -> bool:
        """Check if an element has a proper label."""
        # Check for explicit label association
        element_id = element.get("id")
        if element_id:
            label = element.find_parent().find("label", attrs={"for": element_id})
            if label:
                return True
        
        # Check for wrapped label
        parent = element.parent
        if parent and parent.name == "label":
            return True
        
        # Check for aria-label
        if element.get("aria-label"):
            return True
        
        # Check for aria-labelledby
        if element.get("aria-labelledby"):
            return True
        
        # Check for title attribute
        if element.get("title"):
            return True
        
        return False
    
    def _is_complex_form(self, form) -> bool:
        """Determine if a form is complex enough to need fieldset/legend."""
        # Count form controls
        controls = len(form.find_all("input")) + len(form.find_all("select")) + len(form.find_all("textarea"))
        
        # Consider it complex if it has more than 3 controls
        return controls > 3
    
    def _create_missing_label_issue(self, element) -> AccessibilityIssue:
        """Create an issue for missing form labels."""
        element_info = self.get_element_info(element)
        context = self.get_parent_context(element)
        
        return self.create_issue(
            issue_type=IssueType.MISSING_FORM_LABELS,
            severity=SeverityLevel.CRITICAL,
            description=f"Form element missing label: {element.name}",
            element=f"<{element.name} {self._get_element_attributes(element)}>",
            context=context,
            line_number=self.get_line_number(element),
            column_number=self.get_column_number(element),
            suggested_fix=(
                "Add a label for this form element. You can: "
                "1. Use a <label> element with 'for' attribute matching the element's 'id', "
                "2. Wrap the element in a <label> element, "
                "3. Add aria-label attribute, or "
                "4. Add aria-labelledby attribute pointing to a descriptive element."
            ),
            wcag_criteria=["1.3.1", "3.3.2"],
            additional_info=element_info
        )
    
    def _create_missing_placeholder_issue(self, element) -> AccessibilityIssue:
        """Create an issue for missing placeholders."""
        element_info = self.get_element_info(element)
        context = self.get_parent_context(element)
        
        return self.create_issue(
            issue_type=IssueType.MISSING_FORM_LABELS,
            severity=SeverityLevel.LOW,
            description=f"Form element missing placeholder text: {element.name}",
            element=f"<{element.name} {self._get_element_attributes(element)}>",
            context=context,
            line_number=self.get_line_number(element),
            column_number=self.get_column_number(element),
            suggested_fix=(
                "Add a placeholder attribute with helpful text that describes "
                "what the user should enter in this field."
            ),
            wcag_criteria=["1.3.1"],
            additional_info=element_info
        )
    
    def _create_missing_aria_required_issue(self, element) -> AccessibilityIssue:
        """Create an issue for missing aria-required attribute."""
        element_info = self.get_element_info(element)
        context = self.get_parent_context(element)
        
        return self.create_issue(
            issue_type=IssueType.INACCESSIBLE_FORMS,
            severity=SeverityLevel.MODERATE,
            description=f"Required form element missing aria-required attribute: {element.name}",
            element=f"<{element.name} {self._get_element_attributes(element)}>",
            context=context,
            line_number=self.get_line_number(element),
            column_number=self.get_column_number(element),
            suggested_fix=(
                "Add aria-required='true' to this required form element "
                "to ensure screen readers announce it as required."
            ),
            wcag_criteria=["3.3.2"],
            additional_info=element_info
        )
    
    def _create_missing_aria_describedby_issue(self, element) -> AccessibilityIssue:
        """Create an issue for missing aria-describedby on error messages."""
        element_info = self.get_element_info(element)
        context = self.get_parent_context(element)
        
        return self.create_issue(
            issue_type=IssueType.INACCESSIBLE_FORMS,
            severity=SeverityLevel.MODERATE,
            description=f"Form element with error missing aria-describedby: {element.name}",
            element=f"<{element.name} {self._get_element_attributes(element)}>",
            context=context,
            line_number=self.get_line_number(element),
            column_number=self.get_column_number(element),
            suggested_fix=(
                "Add aria-describedby attribute pointing to the error message element. "
                "This ensures screen readers announce the error when the field is focused."
            ),
            wcag_criteria=["3.3.1"],
            additional_info=element_info
        )
    
    def _create_missing_aria_label_issue(self, element) -> AccessibilityIssue:
        """Create an issue for missing aria-label on form elements."""
        element_info = self.get_element_info(element)
        context = self.get_parent_context(element)
        
        return self.create_issue(
            issue_type=IssueType.MISSING_ARIA_LABELS,
            severity=SeverityLevel.MODERATE,
            description=f"Form element missing accessible name: {element.name}",
            element=f"<{element.name} {self._get_element_attributes(element)}>",
            context=context,
            line_number=self.get_line_number(element),
            column_number=self.get_column_number(element),
            suggested_fix=(
                "Add aria-label or aria-labelledby attribute to provide "
                "an accessible name for this form element."
            ),
            wcag_criteria=["1.3.1", "3.3.2"],
            additional_info=element_info
        )
    
    def _create_missing_form_label_issue(self, form) -> AccessibilityIssue:
        """Create an issue for forms missing overall labels."""
        element_info = self.get_element_info(form)
        context = self.get_parent_context(form)
        
        return self.create_issue(
            issue_type=IssueType.MISSING_FORM_LABELS,
            severity=SeverityLevel.MODERATE,
            description="Form missing overall label or description",
            element=f"<{form.name}>",
            context=context,
            line_number=self.get_line_number(form),
            column_number=self.get_column_number(form),
            suggested_fix=(
                "Add a descriptive label or heading above the form, or use "
                "aria-label or aria-labelledby to describe the form's purpose."
            ),
            wcag_criteria=["1.3.1", "2.4.6"],
            additional_info=element_info
        )
    
    def _create_missing_fieldset_issue(self, form) -> AccessibilityIssue:
        """Create an issue for complex forms missing fieldset/legend."""
        element_info = self.get_element_info(form)
        context = self.get_parent_context(form)
        
        return self.create_issue(
            issue_type=IssueType.INACCESSIBLE_FORMS,
            severity=SeverityLevel.LOW,
            description="Complex form missing fieldset/legend grouping",
            element=f"<{form.name}>",
            context=context,
            line_number=self.get_line_number(form),
            column_number=self.get_column_number(form),
            suggested_fix=(
                "Group related form fields using <fieldset> and <legend> elements "
                "to improve form structure and accessibility."
            ),
            wcag_criteria=["1.3.1", "2.4.6"],
            additional_info=element_info
        )
    
    def _create_missing_submit_button_issue(self, form) -> AccessibilityIssue:
        """Create an issue for forms missing submit buttons."""
        element_info = self.get_element_info(form)
        context = self.get_parent_context(form)
        
        return self.create_issue(
            issue_type=IssueType.INACCESSIBLE_FORMS,
            severity=SeverityLevel.MODERATE,
            description="Form missing submit button",
            element=f"<{form.name}>",
            context=context,
            line_number=self.get_line_number(form),
            column_number=self.get_column_number(form),
            suggested_fix=(
                "Add a submit button (<input type='submit'> or <button type='submit'>) "
                "to allow users to submit the form."
            ),
            wcag_criteria=["2.1.1", "3.2.2"],
            additional_info=element_info
        )
    
    def _get_element_attributes(self, element) -> str:
        """Get a string representation of element attributes."""
        attrs = []
        for key, value in element.attrs.items():
            if key in ["id", "name", "type", "required"]:
                attrs.append(f'{key}="{value}"')
        return " ".join(attrs)
