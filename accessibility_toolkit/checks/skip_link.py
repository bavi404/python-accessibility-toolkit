"""
Check for presence and validity of a Skip to main content link.
"""

from typing import List
from bs4 import BeautifulSoup
from .base import BaseCheck
from ..models import AccessibilityIssue, IssueType, SeverityLevel


class SkipLinkCheck(BaseCheck):
    """Detects missing or broken skip navigation links."""

    def check(self, soup: BeautifulSoup, url: str) -> List[AccessibilityIssue]:
        self.log_check_start(url)
        issues: List[AccessibilityIssue] = []

        # Find anchors that could be skip links
        candidates = []
        for a in soup.find_all("a"):
            text = (a.get_text(strip=True) or "").lower()
            href = (a.get("href") or "").lower()
            rel = (a.get("rel") or [])
            role = (a.get("role") or "").lower()
            if (
                "skip" in text or "skip" in href or role == "skiplink" or "skip" in " ".join(rel)
            ):
                candidates.append(a)

        # Is there a main content target?
        main_target_ids = set()
        main_el = soup.find("main")
        if main_el and main_el.get("id"):
            main_target_ids.add(main_el.get("id").lower())
        # Common main ids
        for common_id in ["main", "content", "primary", "maincontent", "primarycontent"]:
            el = soup.find(id=common_id)
            if el:
                main_target_ids.add(common_id)

        if not candidates:
            # No skip link at all
            issues.append(
                self.create_issue(
                    issue_type=IssueType.MISSING_SKIP_LINKS,
                    severity=SeverityLevel.LOW,
                    description="No 'Skip to main content' link found.",
                    element="<a>",
                    context="document head/body",
                    suggested_fix=(
                        "Add a visually-focusable skip link at the top linking to #main or the main region."
                    ),
                    wcag_criteria=["2.4.1"]
                )
            )
        else:
            # Validate that at least one candidate points to a real target
            valid = False
            for a in candidates:
                href = (a.get("href") or "")
                if href.startswith("#") and len(href) > 1:
                    target_id = href[1:].lower()
                    if target_id in main_target_ids or soup.find(id=target_id):
                        valid = True
                        break
            if not valid:
                issues.append(
                    self.create_issue(
                        issue_type=IssueType.MISSING_SKIP_LINKS,
                        severity=SeverityLevel.MODERATE,
                        description="Skip link present but target is missing or invalid.",
                        element="<a>",
                        context=self.get_parent_context(candidates[0]) if candidates else "",
                        suggested_fix=(
                            "Ensure skip link href points to an existing main content id (e.g., #main)."
                        ),
                        wcag_criteria=["2.4.1"]
                    )
                )

        self.log_check_complete(url, len(issues))
        return issues


