"""
Utility functions for the accessibility toolkit.
"""

from typing import List, Dict, Any
from .models import AccessibilityIssue, IssueType, SeverityLevel


def deduplicate_issues(issues: List[AccessibilityIssue]) -> List[AccessibilityIssue]:
    """
    Remove duplicate accessibility issues by grouping similar ones.
    
    Args:
        issues: List of AccessibilityIssue objects
        
    Returns:
        List of deduplicated AccessibilityIssue objects
    """
    if not issues:
        return []
    
    # Group issues by their signature (type, severity, description, element pattern)
    issue_groups: Dict[str, List[AccessibilityIssue]] = {}
    
    for issue in issues:
        # Create a signature for grouping
        signature = _create_issue_signature(issue)
        
        if signature not in issue_groups:
            issue_groups[signature] = []
        issue_groups[signature].append(issue)
    
    # Create consolidated issues
    consolidated_issues = []
    
    for signature, group in issue_groups.items():
        if len(group) == 1:
            # Single issue, keep as is
            consolidated_issues.append(group[0])
        else:
            # Multiple similar issues, consolidate them
            consolidated_issue = _consolidate_issue_group(group)
            consolidated_issues.append(consolidated_issue)
    
    return consolidated_issues


def _create_issue_signature(issue: AccessibilityIssue) -> str:
    """
    Create a signature for grouping similar issues.
    
    Args:
        issue: AccessibilityIssue object
        
    Returns:
        String signature for grouping
    """
    # Base signature includes type, severity, and description
    base_signature = f"{issue.issue_type.value}:{issue.severity.value}:{issue.description}"
    
    # For element-specific issues, include element pattern
    if issue.element:
        element_pattern = _extract_element_pattern(issue.element)
        base_signature += f":{element_pattern}"
    
    return base_signature


def _extract_element_pattern(element_str: str) -> str:
    """
    Extract a pattern from element string for grouping.
    
    Args:
        element_str: Element string like "<input name='btnG' type='submit'>"
        
    Returns:
        Pattern string like "input:submit"
    """
    if not element_str or not element_str.startswith('<'):
        return element_str
    
    # Extract tag name
    tag_start = element_str.find('<') + 1
    tag_end = element_str.find(' ', tag_start)
    if tag_end == -1:
        tag_end = element_str.find('>', tag_start)
    
    if tag_end == -1:
        return element_str
    
    tag_name = element_str[tag_start:tag_end]
    
    # Extract type attribute if present
    type_start = element_str.find("type='")
    if type_start != -1:
        type_start += 6
        type_end = element_str.find("'", type_start)
        if type_end != -1:
            input_type = element_str[type_start:type_end]
            return f"{tag_name}:{input_type}"
    
    return tag_name


def _consolidate_issue_group(group: List[AccessibilityIssue]) -> AccessibilityIssue:
    """
    Consolidate a group of similar issues into one.
    
    Args:
        group: List of similar AccessibilityIssue objects
        
    Returns:
        Consolidated AccessibilityIssue object
    """
    if not group:
        return group[0]
    
    # Use the first issue as the base
    base_issue = group[0]
    
    # Update description to indicate multiple instances
    count = len(group)
    if count > 1:
        if "missing label" in base_issue.description.lower():
            base_issue.description = f"{count} form elements missing labels"
        elif "missing alt" in base_issue.description.lower():
            base_issue.description = f"{count} images missing alt text"
        elif "missing heading" in base_issue.description.lower():
            base_issue.description = f"{count} heading elements missing or improperly structured"
        else:
            base_issue.description = f"{count} instances: {base_issue.description}"
    
    # Update element info to show multiple elements
    if count > 1:
        elements = [issue.element for issue in group if issue.element]
        if elements:
            # Show first few elements and count
            if len(elements) <= 3:
                base_issue.element = ", ".join(elements)
            else:
                base_issue.element = f"{elements[0]}, {elements[1]}, ... and {len(elements) - 2} more"
    
    # Add count to additional info
    if not hasattr(base_issue, 'additional_info'):
        base_issue.additional_info = {}
    base_issue.additional_info['count'] = count
    base_issue.additional_info['all_elements'] = [issue.element for issue in group if issue.element]
    
    return base_issue


def filter_visible_elements(soup, viewport_size: tuple = (1920, 1080)) -> List:
    """
    Filter to only include elements that are likely visible on screen.
    
    Args:
        soup: BeautifulSoup object
        viewport_size: Tuple of (width, height) for viewport
        
    Returns:
        List of visible elements
    """
    visible_elements = []
    
    # Common visible element types
    visible_tags = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',  # Headings
        'p', 'div', 'span', 'a', 'button', 'input', 'textarea', 'select',  # Text and form elements
        'img', 'svg', 'canvas',  # Media elements
        'nav', 'main', 'section', 'article', 'aside', 'header', 'footer',  # Semantic elements
        'ul', 'ol', 'li', 'table', 'tr', 'td', 'th'  # List and table elements
    ]
    
    for tag in visible_tags:
        elements = soup.find_all(tag)
        for element in elements:
            if _is_element_visible(element):
                visible_elements.append(element)
    
    return visible_elements


def _is_element_visible(element) -> bool:
    """
    Check if an element is likely visible.
    
    Args:
        element: BeautifulSoup element
        
    Returns:
        True if element is likely visible
    """
    # Check for hidden attributes
    if element.get('hidden') or element.get('aria-hidden') == 'true':
        return False
    
    # Check for display:none or visibility:hidden in style
    style = element.get('style', '')
    if 'display: none' in style or 'visibility: hidden' in style:
        return False
    
    # Check for common hidden classes
    classes = element.get('class', [])
    hidden_classes = ['hidden', 'invisible', 'sr-only', 'visually-hidden']
    if any(cls in classes for cls in hidden_classes):
        return False
    
    # Check if element has content
    if not element.get_text(strip=True) and not element.find('img'):
        return False
    
    return True
