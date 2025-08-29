"""
Check responsive viewport configuration and zoom restrictions.
"""

from typing import List
from bs4 import BeautifulSoup
from .base import BaseCheck
from ..models import AccessibilityIssue, IssueType, SeverityLevel


class ResponsiveViewportCheck(BaseCheck):
    """Flags missing/invalid meta viewport and disallowed zoom."""

    def check(self, soup: BeautifulSoup, url: str) -> List[AccessibilityIssue]:
        self.log_check_start(url)
        issues: List[AccessibilityIssue] = []

        metas = soup.find_all("meta", attrs={"name": "viewport"})
        if not metas:
            issues.append(
                self.create_issue(
                    issue_type=IssueType.OTHER,
                    severity=SeverityLevel.LOW,
                    description="Missing meta viewport for responsive layout.",
                    element="<meta name='viewport'>",
                    context="document head",
                    suggested_fix=(
                        "Add <meta name='viewport' content='width=device-width, initial-scale=1'> for responsiveness."
                    ),
                    wcag_criteria=["1.4.4", "1.4.10"],
                )
            )
        else:
            content = (metas[0].get("content") or "").lower()
            # Disallow patterns that disable zoom
            if "user-scalable=no" in content or "maximum-scale=1" in content:
                issues.append(
                    self.create_issue(
                        issue_type=IssueType.OTHER,
                        severity=SeverityLevel.MODERATE,
                        description="Viewport disables zoom (user-scalable=no or maximum-scale=1).",
                        element="<meta name='viewport'>",
                        context="document head",
                        suggested_fix=(
                            "Allow pinch-zoom: remove user-scalable=no and avoid restricting maximum-scale."
                        ),
                        wcag_criteria=["1.4.4"],
                        additional_info={"content": content}
                    )
                )

        self.log_check_complete(url, len(issues))
        return issues


