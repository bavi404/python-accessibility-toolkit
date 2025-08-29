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
        self.check_error_handling = config.get("check_error_handling", True)
    
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
            
            # Check error handling and validation
            if self.check_error_handling:
                error_issues = self._check_error_handling(form)
                issues.extend(error_issues)
        
        self.log_check_complete(url, len(issues))
        return issues
    
    def _check_form_elements(self, form) -> List[AccessibilityIssue]:
        """Check individual form elements for accessibility issues."""
        issues = []
        
        # Check input elements
        inputs = form.find_all("input")
        seen = set()
        for input_elem in inputs:
            sig = (
                input_elem.name,
                input_elem.get("type", "text"),
                input_elem.get("id", ""),
                input_elem.get("name", ""),
            )
            if sig in seen:
                continue
            seen.add(sig)
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
    
    def _check_error_handling(self, form) -> List[AccessibilityIssue]:
        """Check form error handling and validation accessibility."""
        issues = []
        
        # Check for form elements with validation errors
        invalid_elements = form.find_all(attrs={"aria-invalid": "true"})
        
        for element in invalid_elements:
            # Check if error message is properly associated
            if not self._has_error_message_association(element):
                issues.append(self._create_missing_error_association_issue(element))
            
            # Check if error message is descriptive
            error_msg = self._get_error_message(element)
            if error_msg and not self._is_descriptive_error(error_msg):
                issues.append(self._create_non_descriptive_error_issue(element, error_msg))
        
        # Check for required fields without clear indication
        required_fields = form.find_all(attrs={"required": True})
        for field in required_fields:
            if not self._has_clear_required_indication(field):
                issues.append(self._create_missing_required_indication_issue(field))
        
        # Check for form submission errors without clear messaging
        error_containers = form.find_all(class_=lambda x: x and any(word in x.lower() for word in ["error", "alert", "warning", "invalid"]))
        for container in error_containers:
            if not self._has_accessible_error_content(container):
                issues.append(self._create_inaccessible_error_content_issue(container))
        
        return issues
    
    def _has_error_message_association(self, element) -> bool:
        """Check if an element has proper error message association."""
        # Check for aria-describedby pointing to error message
        if element.get("aria-describedby"):
            describedby_ids = element.get("aria-describedby").split()
            for error_id in describedby_ids:
                error_element = element.find_parent().find(id=error_id)
                if error_element and self._is_error_message(error_element):
                    return True
        
        # Check for aria-errormessage (newer standard)
        if element.get("aria-errormessage"):
            error_id = element.get("aria-errormessage")
            error_element = element.find_parent().find(id=error_id)
            if error_element and self._is_error_message(error_element):
                return True
        
        # Check for nearby error message (heuristic)
        if self._has_nearby_error_message(element):
            return True
        
        return False
    
    def _is_error_message(self, element) -> bool:
        """Check if an element appears to be an error message."""
        # Check for error-related classes
        classes = element.get("class", [])
        if isinstance(classes, str):
            classes = [classes]
        
        error_classes = ["error", "alert", "warning", "invalid", "danger", "text-danger"]
        if any(error_class in " ".join(classes).lower() for error_class in error_classes):
            return True
        
        # Check for error-related ARIA roles
        if element.get("role") in ["alert", "alertdialog", "status"]:
            return True
        
        # Check for error-related text content
        text = element.get_text(strip=True).lower()
        error_keywords = ["error", "invalid", "required", "missing", "incorrect", "failed"]
        if any(keyword in text for keyword in error_keywords):
            return True
        
        return False
    
    def _has_nearby_error_message(self, element) -> bool:
        """Check if there's an error message near the form element."""
        # Look for error messages in the same container or nearby
        parent = element.parent
        if parent:
            # Check siblings for error messages
            siblings = parent.find_all(recursive=False)
            for sibling in siblings:
                if self._is_error_message(sibling):
                    return True
            
            # Check parent's siblings
            grandparent = parent.parent
            if grandparent:
                parent_siblings = grandparent.find_all(recursive=False)
                for sibling in parent_siblings:
                    if self._is_error_message(sibling):
                        return True
        
        return False
    
    def _get_error_message(self, element) -> str:
        """Get the error message text for an element if available."""
        # Try to get error message via aria-describedby
        if element.get("aria-describedby"):
            describedby_ids = element.get("aria-describedby").split()
            for error_id in describedby_ids:
                error_element = element.find_parent().find(id=error_id)
                if error_element:
                    return error_element.get_text(strip=True)
        
        # Try to get error message via aria-errormessage
        if element.get("aria-errormessage"):
            error_id = element.get("aria-errormessage")
            error_element = element.find_parent().find(id=error_id)
            if error_element:
                return error_element.get_text(strip=True)
        
        return ""
    
    def _is_descriptive_error(self, error_text: str) -> bool:
        """Check if an error message is descriptive and helpful."""
        if not error_text:
            return False
        
        # Check for generic error messages
        generic_errors = [
            "error", "invalid", "incorrect", "wrong", "failed", "not valid",
            "please fix", "try again", "something went wrong"
        ]
        
        error_lower = error_text.lower()
        if any(generic in error_lower for generic in generic_errors):
            # If it's generic, check if it provides additional context
            if len(error_text) < 20:  # Too short to be helpful
                return False
        
        return True
    
    def _has_clear_required_indication(self, element) -> bool:
        """Check if a required field has clear indication."""
        # Check for visual required indicator
        label = self._get_associated_label(element)
        if label:
            label_text = label.get_text(strip=True)
            if "*" in label_text or "required" in label_text.lower():
                return True
        
        # Check for aria-required
        if element.get("aria-required") == "true":
            return True
        
        # Check for required attribute
        if element.get("required"):
            return True
        
        return False
    
    def _has_accessible_error_content(self, container) -> bool:
        """Check if error container has accessible content."""
        # Check for proper ARIA role
        if container.get("role") in ["alert", "status"]:
            return True
        
        # Check for descriptive text content
        text_content = container.get_text(strip=True)
        if text_content and len(text_content) > 10:
            return True
        
        # Check for aria-live attribute
        if container.get("aria-live"):
            return True
        
        return False
    
    def _get_associated_label(self, element) -> BeautifulSoup:
        """Get the label associated with a form element."""
        element_id = element.get("id")
        if element_id:
            # Find label with matching for attribute
            label = element.find_parent().find("label", attrs={"for": element_id})
            if label:
                return label
        
        # Check for wrapped label
        parent = element.parent
        if parent and parent.name == "label":
            return parent
        
        return None
    
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
    
    def _create_missing_error_association_issue(self, element) -> AccessibilityIssue:
        """Create an issue for missing error message association."""
        element_info = self.get_element_info(element)
        context = self.get_parent_context(element)
        
        return self.create_issue(
            issue_type=IssueType.INACCESSIBLE_FORMS,
            severity=SeverityLevel.MODERATE,
            description=f"Form element with validation error missing error message association: {element.name}",
            element=f"<{element.name} {self._get_element_attributes(element)}>",
            context=context,
            line_number=self.get_line_number(element),
            column_number=self.get_column_number(element),
            suggested_fix=(
                "Associate the error message with this field using aria-describedby or aria-errormessage. "
                "This ensures screen readers announce the error when the field is focused."
            ),
            wcag_criteria=["3.3.1", "3.3.3"],
            additional_info=element_info
        )
    
    def _create_non_descriptive_error_issue(self, element, error_text: str) -> AccessibilityIssue:
        """Create an issue for non-descriptive error messages."""
        element_info = self.get_element_info(element)
        context = self.get_parent_context(element)
        
        return self.create_issue(
            issue_type=IssueType.INACCESSIBLE_FORMS,
            severity=SeverityLevel.LOW,
            description=f"Form element has non-descriptive error message: '{error_text}'",
            element=f"<{element.name} {self._get_element_attributes(element)}>",
            context=context,
            line_number=self.get_line_number(element),
            column_number=self.get_column_number(element),
            suggested_fix=(
                "Provide a specific, actionable error message that explains what went wrong "
                "and how to fix it. Avoid generic messages like 'Error' or 'Invalid'."
            ),
            wcag_criteria=["3.3.1"],
            additional_info=element_info
        )
    
    def _create_missing_required_indication_issue(self, element) -> AccessibilityIssue:
        """Create an issue for missing required field indication."""
        element_info = self.get_element_info(element)
        context = self.get_parent_context(element)
        
        return self.create_issue(
            issue_type=IssueType.INACCESSIBLE_FORMS,
            severity=SeverityLevel.MODERATE,
            description=f"Required form element missing clear indication: {element.name}",
            element=f"<{element.name} {self._get_element_attributes(element)}>",
            context=context,
            line_number=self.get_line_number(element),
            column_number=self.get_column_number(element),
            suggested_fix=(
                "Clearly indicate this field is required by: "
                "1. Adding an asterisk (*) to the label, "
                "2. Including 'required' in the label text, or "
                "3. Adding aria-required='true' attribute."
            ),
            wcag_criteria=["3.3.2"],
            additional_info=element_info
        )
    
    def _create_inaccessible_error_content_issue(self, container) -> AccessibilityIssue:
        """Create an issue for inaccessible error content."""
        element_info = self.get_element_info(container)
        context = self.get_parent_context(container)
        
        return self.create_issue(
            issue_type=IssueType.INACCESSIBLE_FORMS,
            severity=SeverityLevel.MODERATE,
            description="Error container missing accessible content or proper ARIA attributes",
            element=f"<{container.name}>",
            context=context,
            line_number=self.get_line_number(container),
            column_number=self.get_column_number(container),
            suggested_fix=(
                "Make error content accessible by: "
                "1. Adding role='alert' for dynamic errors, "
                "2. Including descriptive text content, "
                "3. Using aria-live for live regions, or "
                "4. Ensuring proper focus management."
            ),
            wcag_criteria=["3.3.1", "4.1.2"],
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
