"""
Detect auto-animations and absence of prefers-reduced-motion fallbacks (heuristic).
"""

from typing import List
from bs4 import BeautifulSoup
from .base import BaseCheck
from ..models import AccessibilityIssue, IssueType, SeverityLevel


class ReducedMotionCheck(BaseCheck):
    """Flags CSS animations without a prefers-reduced-motion override."""

    def check(self, soup: BeautifulSoup, url: str) -> List[AccessibilityIssue]:
        self.log_check_start(url)
        issues: List[AccessibilityIssue] = []

        css_texts = []
        for style_tag in soup.find_all("style"):
            css = style_tag.get_text() or ""
            if css:
                css_texts.append(css)

        has_animations = False
        has_prm_override = False

        for css in css_texts:
            low = css.lower()
            if any(k in low for k in ["animation:", "animation-name:", "transition:"]):
                has_animations = True
            if "@media (prefers-reduced-motion: reduce)" in low:
                has_prm_override = True

        if has_animations and not has_prm_override:
            snippet = ("\n\n").join(t.strip()[:160] for t in css_texts[:1])
            issues.append(
                self.create_issue(
                    issue_type=IssueType.OTHER,
                    severity=SeverityLevel.LOW,
                    description="Animations/transitions detected without prefers-reduced-motion override.",
                    element="<style>",
                    context="document head",
                    suggested_fix=(
                        "Provide @media (prefers-reduced-motion: reduce) rules to disable/limit motion effects."
                    ),
                    wcag_criteria=["2.3.3", "2.2.2"],
                    additional_info={"snippet": snippet}
                )
            )

        self.log_check_complete(url, len(issues))
        return issues


