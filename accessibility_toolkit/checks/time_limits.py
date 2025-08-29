"""
Detect time limits: meta refresh and potential auto-logout notices.
"""

from typing import List
from bs4 import BeautifulSoup
from .base import BaseCheck
from ..models import AccessibilityIssue, IssueType, SeverityLevel


class TimeLimitsCheck(BaseCheck):
    """Flags meta refresh and heuristic time-limit warnings without controls."""

    def check(self, soup: BeautifulSoup, url: str) -> List[AccessibilityIssue]:
        self.log_check_start(url)
        issues: List[AccessibilityIssue] = []

        # 1) meta http-equiv="refresh"
        for meta in soup.find_all("meta", attrs={"http-equiv": True}):
            http_equiv = (meta.get("http-equiv") or "").lower()
            if http_equiv == "refresh":
                content = (meta.get("content") or "").lower()
                issues.append(
                    self.create_issue(
                        issue_type=IssueType.OTHER,
                        severity=SeverityLevel.MODERATE,
                        description="Page uses meta refresh (time-limited refresh/redirect).",
                        element="<meta http-equiv='refresh'>",
                        context="document head",
                        suggested_fix=(
                            "Avoid meta refresh; provide user controls to extend time or trigger navigation explicitly."
                        ),
                        wcag_criteria=["2.2.1", "2.2.4"],
                        additional_info={"content": content}
                    )
                )

        # 2) Heuristic: visible text warning of auto-logout/session timeout without controls nearby
        timeout_keywords = [
            "session will expire", "session timeout", "auto logout", "auto-logout",
            "log out in", "timed out", "expires in"
        ]
        body_text = soup.get_text(" ", strip=True).lower()
        if any(k in body_text for k in timeout_keywords):
            issues.append(
                self.create_issue(
                    issue_type=IssueType.OTHER,
                    severity=SeverityLevel.LOW,
                    description="Page mentions session timeout; verify extend-time or save controls are provided.",
                    element="<body>",
                    context="document body",
                    suggested_fix=(
                        "Provide a mechanism to extend time, save progress, or disable time limit per WCAG 2.2.1."
                    ),
                    wcag_criteria=["2.2.1"]
                )
            )

        self.log_check_complete(url, len(issues))
        return issues


