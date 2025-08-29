"""
Detect keyboard traps and tabindex misuse heuristically.
"""

from typing import List
from bs4 import BeautifulSoup
from .base import BaseCheck
from ..models import AccessibilityIssue, IssueType, SeverityLevel


class KeyboardTrapsCheck(BaseCheck):
    """Flags tabindex>0 usage and suspicious inline handlers that may trap focus."""

    def check(self, soup: BeautifulSoup, url: str) -> List[AccessibilityIssue]:
        self.log_check_start(url)
        issues: List[AccessibilityIssue] = []

        # 1) Tabindex greater than 0 (anti-pattern)
        for el in soup.find_all(attrs={"tabindex": True}):
            try:
                tabindex_val = int(str(el.get("tabindex")).strip())
            except Exception:
                continue

            if tabindex_val > 0:
                issues.append(
                    self.create_issue(
                        issue_type=IssueType.KEYBOARD_NAVIGATION,
                        severity=SeverityLevel.MODERATE,
                        description=f"Element uses tabindex={tabindex_val} (>0), which can create confusing focus order.",
                        element=f"<{el.name}>",
                        context=self.get_parent_context(el),
                        line_number=self.get_line_number(el),
                        column_number=self.get_column_number(el),
                        suggested_fix="Use tabindex=0 for custom widgets or manage focus programmatically in DOM order.",
                        wcag_criteria=["2.4.3", "2.1.1"],
                        additional_info=self.get_element_info(el)
                    )
                )

        # 2) Suspicious inline handlers that may prevent default Tab behavior (heuristic)
        # Look for onkeydown / onkeypress handlers mentioning 'tabKey' or keyCode 9
        for el in soup.find_all(True):
            for attr in ["onkeydown", "onkeypress", "onkeyup"]:
                handler = el.get(attr)
                if not handler:
                    continue
                lowered = handler.lower()
                if "keycode" in lowered and "9" in lowered or "tabkey" in lowered:
                    issues.append(
                        self.create_issue(
                            issue_type=IssueType.KEYBOARD_NAVIGATION,
                            severity=SeverityLevel.LOW,
                            description="Inline key handler may interfere with Tab navigation (keyCode 9).",
                            element=f"<{el.name} {attr}=...>",
                            context=self.get_parent_context(el),
                            line_number=self.get_line_number(el),
                            column_number=self.get_column_number(el),
                            suggested_fix="Avoid intercepting Tab navigation unless restoring expected focus movement.",
                            wcag_criteria=["2.1.2"],
                            additional_info=self.get_element_info(el)
                        )
                    )

        self.log_check_complete(url, len(issues))
        return issues


