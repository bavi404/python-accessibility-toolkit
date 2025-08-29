"""
Checks for autoplaying media and missing accessible controls on <audio>/<video>.
"""

from typing import List
from bs4 import BeautifulSoup
from .base import BaseCheck
from ..models import AccessibilityIssue, IssueType, SeverityLevel


class AutoplayControlsCheck(BaseCheck):
    """Flags autoplaying media and media elements missing visible controls."""

    def check(self, soup: BeautifulSoup, url: str) -> List[AccessibilityIssue]:
        self.log_check_start(url)
        issues: List[AccessibilityIssue] = []

        media_elements = list(soup.find_all("audio")) + list(soup.find_all("video"))

        for el in media_elements:
            tag = el.name
            has_controls = el.has_attr("controls")
            is_autoplay = el.has_attr("autoplay") or (el.get("data-autoplay") == "true")
            is_muted = el.has_attr("muted") or (el.get("aria-muted") == "true")

            # Missing controls
            if not has_controls:
                issues.append(
                    self.create_issue(
                        issue_type=IssueType.OTHER,
                        severity=SeverityLevel.MODERATE,
                        description=f"<{tag}> element is missing user controls.",
                        element=f"<{tag}>",
                        context=self.get_parent_context(el),
                        line_number=self.get_line_number(el),
                        column_number=self.get_column_number(el),
                        suggested_fix=f"Add the 'controls' attribute to the <{tag}> element to expose play/pause.",
                        wcag_criteria=["1.4.2", "2.1.1"],
                    )
                )

            # Autoplay without controls (or unmuted audio) is high risk
            if is_autoplay:
                severity = SeverityLevel.CRITICAL if (tag == "audio" and not is_muted) or not has_controls else SeverityLevel.MODERATE
                issues.append(
                    self.create_issue(
                        issue_type=IssueType.OTHER,
                        severity=severity,
                        description=f"Autoplaying <{tag}> detected without guaranteed user control.",
                        element=f"<{tag} autoplay>",
                        context=self.get_parent_context(el),
                        line_number=self.get_line_number(el),
                        column_number=self.get_column_number(el),
                        suggested_fix=(
                            f"Avoid autoplay on <{tag}> or ensure controls and an obvious pause/stop mechanism; "
                            "mute audio by default if autoplay is required."
                        ),
                        wcag_criteria=["1.4.2", "2.2.2"],
                    )
                )

        self.log_check_complete(url, len(issues))
        return issues


