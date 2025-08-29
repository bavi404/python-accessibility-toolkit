"""
Check that <html> has lang attribute and <title> is present and meaningful.
"""

from typing import List
from bs4 import BeautifulSoup
from .base import BaseCheck
from ..models import AccessibilityIssue, IssueType, SeverityLevel


class LangTitleCheck(BaseCheck):
    """Flags missing/empty html lang and missing/empty <title>."""

    def check(self, soup: BeautifulSoup, url: str) -> List[AccessibilityIssue]:
        self.log_check_start(url)
        issues: List[AccessibilityIssue] = []

        # html lang
        html = soup.find("html")
        lang = (html.get("lang") if html else None)
        if not lang or not str(lang).strip():
            issues.append(
                self.create_issue(
                    issue_type=IssueType.OTHER,
                    severity=SeverityLevel.MODERATE,
                    description="Missing or empty html lang attribute.",
                    element="<html>",
                    context="document root",
                    suggested_fix="Set <html lang='en'> (or appropriate BCP 47 language tag).",
                    wcag_criteria=["3.1.1"],
                )
            )

        # title presence/meaningfulness
        title_el = soup.find("title")
        title_text = (title_el.get_text(strip=True) if title_el else "")
        if not title_text:
            issues.append(
                self.create_issue(
                    issue_type=IssueType.OTHER,
                    severity=SeverityLevel.MODERATE,
                    description="Missing or empty document title.",
                    element="<title>",
                    context="document head",
                    suggested_fix="Provide a concise, descriptive <title> for the page.",
                    wcag_criteria=["2.4.2"],
                )
            )
        else:
            low_info_titles = {"home", "homepage", "untitled", "index", "page", "document"}
            if title_text.strip().lower() in low_info_titles or len(title_text) < 4:
                issues.append(
                    self.create_issue(
                        issue_type=IssueType.OTHER,
                        severity=SeverityLevel.LOW,
                        description=f"Title may be too generic: '{title_text}'.",
                        element="<title>",
                        context="document head",
                        suggested_fix=(
                            "Make the title specific to the page's purpose/content (e.g., 'Pricing – Acme')."
                        ),
                        wcag_criteria=["2.4.2"],
                        additional_info={"title": title_text}
                    )
                )

        self.log_check_complete(url, len(issues))
        return issues


