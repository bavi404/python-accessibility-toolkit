"""
Heuristic check for missing/hidden keyboard focus indicators via CSS.
Flags global outline suppression and elements with inline styles hiding focus.
"""

from typing import List
from bs4 import BeautifulSoup
from .base import BaseCheck
from ..models import AccessibilityIssue, IssueType, SeverityLevel


class FocusIndicatorCheck(BaseCheck):
    """Detect CSS patterns that hide focus indicators."""

    def check(self, soup: BeautifulSoup, url: str) -> List[AccessibilityIssue]:
        self.log_check_start(url)
        issues: List[AccessibilityIssue] = []

        # 1) Scan <style> blocks for outline suppression on :focus
        for style_tag in soup.find_all("style"):
            css_text = style_tag.get_text() or ""
            lowered = css_text.lower()
            if ":focus" in lowered and ("outline: none" in lowered or "outline: 0" in lowered):
                snippet = css_text.strip()[:160] + ("..." if len(css_text.strip()) > 160 else "")
                issues.append(
                    self.create_issue(
                        issue_type=IssueType.KEYBOARD_NAVIGATION,
                        severity=SeverityLevel.MODERATE,
                        description="Stylesheet hides focus outlines on :focus selectors.",
                        element="<style>",
                        context="document head",
                        suggested_fix=(
                            "Avoid removing focus outlines. If customizing, replace with a visible, high-contrast focus style."
                        ),
                        wcag_criteria=["2.4.7"],
                        additional_info={"snippet": snippet}
                    )
                )

        # 2) Check inline styles that remove outlines on common interactive elements
        interactive_tags = ["a", "button", "input", "textarea", "select", "summary"]
        for el in soup.find_all(interactive_tags):
            style = (el.get("style") or "").lower()
            if "outline: none" in style or "outline: 0" in style:
                issues.append(
                    self.create_issue(
                        issue_type=IssueType.KEYBOARD_NAVIGATION,
                        severity=SeverityLevel.LOW,
                        description="Inline style removes focus outline on interactive element.",
                        element=f"<{el.name}>",
                        context=self.get_parent_context(el),
                        line_number=self.get_line_number(el),
                        column_number=self.get_column_number(el),
                        suggested_fix=(
                            "Remove outline suppression and provide a visible focus style (e.g., outline or box-shadow)."
                        ),
                        wcag_criteria=["2.4.7"],
                        additional_info=self.get_element_info(el)
                    )
                )

        self.log_check_complete(url, len(issues))
        return issues


